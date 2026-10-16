"""Agent entry point: builds the PydanticAI shopping agent from prompts/prompt.md + the model.

LLM calls go through Portkey (PORTKEY_API_KEY). The model name comes from OPENAI_MODEL.
"""

from __future__ import annotations

import os
import re
import uuid
from functools import lru_cache
from pathlib import Path

import httpx2
from dotenv import find_dotenv, load_dotenv
from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.messages import (
    ModelMessage, ModelRequest, ModelResponse, TextPart, ToolCallPart, ToolReturnPart, UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider

import audit
from models import MAX_HISTORY_MESSAGES, AgentOutput, ChatReply, ChatTurn
from safety import SAFE_REPLY, has_profanity, redact_financial
from tools import AGENT_TOOLS, ShopDeps, cards_for

# Finds the nearest .env walking up from this folder. Values are never printed or logged.
load_dotenv(find_dotenv())
os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "prompt.md"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"
DEFAULT_MODEL = "gpt-6-luna"     # everyday model
DEFAULT_MANAGER_MODEL = "gpt-6-sol"  # the "manager": stronger model for one request when a shopper is stuck

# Stopping rule: one shopper request may not spend more than $0.10 on LLM calls.
# Spend is tracked step by step (input + output tokens x price); the agent stops before a
# step that would go over. Prices are placeholders: set them to the real prices in .env.
MAX_COST_PER_REQUEST = 0.10
INPUT_PRICE_PER_MILLION = float(os.getenv("INPUT_PRICE_PER_MILLION", "2.50"))
OUTPUT_PRICE_PER_MILLION = float(os.getenv("OUTPUT_PRICE_PER_MILLION", "15.00"))
MANAGER_INPUT_PRICE_PER_MILLION = float(os.getenv("MANAGER_INPUT_PRICE_PER_MILLION", "5.00"))
MANAGER_OUTPUT_PRICE_PER_MILLION = float(os.getenv("MANAGER_OUTPUT_PRICE_PER_MILLION", "30.00"))

# Extra instructions for the manager, added only when it is answering.
MANAGER_INSTRUCTIONS = (
    "You are the manager, stepping in because the shopper has asked this several times or is frustrated. "
    "Read the whole conversation and work out exactly what they want (item type, color, size, budget). "
    "Briefly acknowledge the runaround once. Then:\n"
    "1. Search with every filter they gave (pass `size` if they named one).\n"
    "2. If they want the best or a recommendation, call `compare_products` on the top matches and choose ONE "
    "clear **top pick**. Explain in one or two sentences why, using only the data: in stock in their size, "
    "price, and shopper interest (how often other shoppers were shown it). Then give up to two alternatives "
    "with a short reason each (e.g. lower price, more stock).\n"
    "3. Put the top pick first in `product_ids`.\n"
    "Never invent ratings, reviews, sales numbers or quality claims the data doesn't show."
)

# Manager trigger: the same question asked more than 3 times, or clear frustration.
MANAGER_REPEAT_THRESHOLD = 3
FRUSTRATION = re.compile(
    r"\b(not what i (asked|meant|want)|(that'?s|this is|you'?re) (wrong|useless|not helping|not helpful)|"
    r"(doesn'?t|does not|isn'?t|is not|not) (help|helping|working)|frustrat\w*|annoy\w*|ridiculous|"
    r"i (already|just) (said|asked|told you)|again\?*!)\b",
    re.IGNORECASE,
)


def _prices(manager: bool) -> tuple[float, float]:
    if manager:
        return MANAGER_INPUT_PRICE_PER_MILLION, MANAGER_OUTPUT_PRICE_PER_MILLION
    return INPUT_PRICE_PER_MILLION, OUTPUT_PRICE_PER_MILLION


def cost_of(usage, manager: bool = False) -> float:
    """Dollar cost of the tokens used so far."""
    in_price, out_price = _prices(manager)
    return (usage.input_tokens * in_price + usage.output_tokens * out_price) / 1_000_000


def usage_limits(manager: bool = False) -> UsageLimits:
    """Hard backstops. Even if all of the budget went to one token type, it couldn't exceed $0.10."""
    in_price, out_price = _prices(manager)
    return UsageLimits(
        request_limit=6,
        tool_calls_limit=12,
        input_tokens_limit=int(MAX_COST_PER_REQUEST / in_price * 1_000_000),
        output_tokens_limit=int(MAX_COST_PER_REQUEST / out_price * 1_000_000),
    )


# Words that don't change what a question is about.
STOPWORDS = set(
    "a an the i im i'm me my you your we us our it its is are was be do does did can could would should will "
    "please pls want wanted need looking look show find get give tell any some one ones that this these those "
    "what whats which who how much many for of to in on at with and or but just still again really now so yes no "
    "hey hi ok okay thanks thank like have has got there here about size sized".split()
)
# Different ways of saying the same thing.
SYNONYMS = {
    "grey": "gray", "large": "l", "medium": "m", "small": "s", "xlarge": "xl", "hoody": "hoodie",
    "sweatshirt": "hoodie", "tee": "tshirt", "shirt": "tshirt", "recommend": "best", "recommendation": "best",
    "top": "best", "good": "best", "great": "best", "favorite": "best", "cost": "price", "costs": "price",
    "available": "stock", "availability": "stock", "left": "stock",
}


def _keywords(text: str) -> set[str]:
    """The words that carry a question's meaning: no filler, simple plural endings removed, synonyms merged."""
    words = set()
    for w in re.findall(r"[a-z0-9]+", text.lower().replace("t-shirt", "tshirt")):
        if w in STOPWORDS:
            continue
        if len(w) > 3 and w.endswith("ies"):
            w = w[:-3] + "y"
        elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        words.add(SYNONYMS.get(w, w))
    return words


def _same_question(a: str, b: str) -> bool:
    """Two messages ask the same question when most of the shorter one's key words are in the other.

    Catches rewordings ("best grey hoodie in large?" vs "which gray hoodie would you recommend in L"),
    not just identical text.
    """
    ka, kb = _keywords(a), _keywords(b)
    if not ka or not kb:
        return a.strip().lower() == b.strip().lower()
    return len(ka & kb) / min(len(ka), len(kb)) >= 0.8


def needs_manager(message: str, history: list[ChatTurn]) -> bool:
    """True when the shopper has asked this more than 3 times already, or sounds frustrated."""
    if FRUSTRATION.search(message):
        return True
    repeats = sum(1 for t in history if t.role == "user" and _same_question(t.content, message))
    return repeats >= MANAGER_REPEAT_THRESHOLD


class ChatNotConfigured(RuntimeError):
    """Raised when PORTKEY_API_KEY is missing."""


@lru_cache(maxsize=1)
def _provider() -> OpenAIProvider:
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise ChatNotConfigured("PORTKEY_API_KEY is not set")
    return OpenAIProvider(
        api_key=api_key,
        base_url=PORTKEY_BASE_URL,
        http_client=httpx2.AsyncClient(
            timeout=60,
            headers={
                "x-portkey-api-key": api_key,
                "x-portkey-provider": "openai",
                # Don't serve cached Responses payloads; Portkey rewrites their item ids.
                "x-portkey-cache-force-refresh": "true",
            },
        ),
    )


def _model(name: str) -> OpenAIResponsesModel:
    # GPT-6 models need the Responses API to use tools (Chat Completions refuses tools with reasoning).
    return OpenAIResponsesModel(
        name, provider=_provider(),
        settings=OpenAIResponsesModelSettings(openai_send_reasoning_ids=False),
    )


@lru_cache(maxsize=1)
def manager_model() -> OpenAIResponsesModel:
    return _model(os.getenv("MANAGER_MODEL", DEFAULT_MANAGER_MODEL))


@lru_cache(maxsize=1)
def get_agent() -> Agent[ShopDeps, AgentOutput]:
    model = _model(os.getenv("OPENAI_MODEL", DEFAULT_MODEL))
    agent = Agent(
        model,
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        deps_type=ShopDeps,
        output_type=AgentOutput,
        tools=AGENT_TOOLS,
        retries=1,
    )
    agent.instructions(shopper_and_page_context)
    return agent


def shopper_and_page_context(ctx: RunContext[ShopDeps]) -> str:
    """Per-request agent context: who the shopper is and which page they're looking at."""
    d = ctx.deps
    lines = ["## Current shopper"]
    if d.user_id is None:
        lines.append("A guest (not logged in). Chat history is not saved for guests.")
    else:
        name = " ".join(part for part in (d.first_name, d.last_name) if part)
        lines.append(f"Logged in as {name} ({d.email}), user id {d.user_id}. Their past chat is in the message history.")
        if d.discount_percent:
            factor = (100 - d.discount_percent) / 100
            lines.append(
                f"They have applied their {d.discount_percent}% promo code, so the site shows every price marked down. "
                f"When you quote a price, give the list price from the tools and their price "
                f"(list price x {factor:.2f}, rounded to the cent), e.g. \"$68.00, your price $61.20\"."
            )
    lines.append("")
    lines.append("## Current page")
    if d.viewing_product_id:
        lines.append(
            f'The shopper is on the item page for "{d.viewing_product_name}" (product_id: {d.viewing_product_id}). '
            'If they say "this", "it" or ask about price, sizes or stock without naming an item, they mean this product. '
            "Use this product_id with get_product_info and check_stock."
        )
    else:
        lines.append(f"The shopper is on {d.page_path}. They are not viewing a single item.")
    if d.manager:
        lines += ["", "## Manager mode", MANAGER_INSTRUCTIONS]
    return "\n".join(lines)


def to_model_history(turns: list[ChatTurn]) -> list[ModelMessage]:
    """Convert recent chat turns into PydanticAI message history."""
    messages: list[ModelMessage] = []
    for turn in turns[-MAX_HISTORY_MESSAGES:]:
        if turn.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        else:
            messages.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return messages


def _audit_tools(request_id: str, messages: list[ModelMessage]) -> int:
    """Log each tool call and its result from this run. Returns the number of tool calls."""
    calls = 0
    stamp = lambda t: t.isoformat(timespec="seconds") if t else audit.now()
    for msg in messages:
        msg_time = getattr(msg, "timestamp", None)
        for part in msg.parts:
            if isinstance(part, ToolCallPart) and part.tool_name != "final_result":
                calls += 1
                audit.log(request_id, "tool_call", time=stamp(msg_time), tool=part.tool_name,
                          args=audit.short(part.args))
            elif isinstance(part, ToolReturnPart) and part.tool_name != "final_result":
                audit.log(request_id, "tool_result", time=stamp(getattr(part, "timestamp", None)),
                          tool=part.tool_name, result=audit.short(part.content))
    return calls


async def run_chat(message: str, history: list[ChatTurn], deps: ShopDeps) -> ChatReply:
    request_id = uuid.uuid4().hex[:12]
    # The manager answers this one request only; the next request goes back to the everyday model.
    manager = needs_manager(message, history)
    deps.manager = manager
    model_name = manager_model().model_name if manager else os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    # Safety: card numbers / SSNs typed by the shopper never reach the model or the log.
    message, redacted = redact_financial(message)
    audit.log(request_id, "run_start", user=deps.user_id or "guest", model=model_name, manager=manager,
              page=deps.page_path, message=audit.short(message, 100))
    if redacted:
        audit.log(request_id, "safety", rule="financial_info_redacted")

    agent = get_agent()
    run = None
    stop_reason = "final_answer"
    reply: ChatReply | None = None
    try:
        async with agent.iter(
            message, deps=deps, message_history=to_model_history(history), usage_limits=usage_limits(manager),
            model=manager_model() if manager else None,
        ) as run:
            last_step_cost = 0.0
            async for node in run:
                if Agent.is_model_request_node(node):
                    spent = cost_of(run.usage, manager)
                    # Stop before a model call that would likely push this request over $0.10.
                    if spent + last_step_cost > MAX_COST_PER_REQUEST:
                        stop_reason = "budget_limit"
                        raise UsageLimitExceeded(f"Request budget of ${MAX_COST_PER_REQUEST:.2f} reached")
                    before = spent
                elif Agent.is_call_tools_node(node) or Agent.is_end_node(node):
                    last_step_cost = max(last_step_cost, cost_of(run.usage, manager) - before)
            result = run.result
        output = result.output
        # Only show cards for products the tools actually returned this turn (no invented items).
        allowed = [pid for pid in output.product_ids if pid in deps.seen_product_ids]
        products = cards_for(allowed)
        reply = ChatReply(reply=output.reply, products=products, manager=manager,
                          results_title=output.results_title if products else None)
        if has_profanity(reply.reply):
            stop_reason = "safety_filtered"
            audit.log(request_id, "safety", rule="profanity_blocked")
            reply = ChatReply(reply=SAFE_REPLY, manager=manager)
        return reply
    except UsageLimitExceeded as e:
        if stop_reason == "final_answer":
            stop_reason = "usage_limit"
        audit.log(request_id, "limit", detail=audit.short(str(e)))
        reply = ChatReply(
            reply="That one's a big bone to chew! Could you narrow it down a bit, like a style, color or size?",
            stopped=True, manager=manager,
        )
        return reply
    except Exception as e:
        stop_reason = "error"
        audit.log(request_id, "error", detail=audit.short(f"{type(e).__name__}: {e}"))
        raise
    finally:
        tool_calls = _audit_tools(request_id, run.new_messages()) if run is not None else 0
        usage = run.usage if run is not None else None
        audit.log(
            request_id, "run_end", stop_reason=stop_reason, model=model_name,
            requests=usage.requests if usage else 0, tool_calls=tool_calls,
            input_tokens=usage.input_tokens if usage else 0, output_tokens=usage.output_tokens if usage else 0,
            est_cost_usd=round(cost_of(usage, manager), 4) if usage else 0,
            products_shown=len(reply.products) if reply else 0,
        )
