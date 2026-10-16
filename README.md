# Campus Customs — Yale Merch Shop with an AI Shopping Assistant

A Yale-themed store for Campus Customs. Shoppers can browse products, create an account, and chat with a shopping assistant that gives honest answers about price and stock from a local database. Matching items appear on the page as product cards.

- **Front end:** React + Vite + TypeScript (`frontend/`)
- **Back end:** FastAPI (`backend/main.py`), with a PydanticAI agent as its brain
- **AI calls:** routed through Portkey; the model is set in `.env` (`gpt-6-luna`, with `gpt-6-sol` as the "manager")

## Project layout

```text
hw4/
├── AI_prompts.md            # prompts used for each problem
├── README.md
├── requirements.txt         # Python dependencies
├── .env.example             # variable names only; copy to .env
├── .gitignore
├── export_db_viewer.py      # builds HTML viewers of the databases (optional)
├── frontend/                # Vite React TypeScript app
├── backend/
│   ├── main.py              # FastAPI app: uvicorn main:app --reload --port 8000
│   ├── prompts/prompt.md    # agent: system prompt, voice, safety rules
│   ├── agent.py             # agent: entry and wiring (model, Portkey, limits, audit)
│   ├── tools.py             # agent: tools the agent can call (read-only database)
│   ├── models.py            # agent: Pydantic / PydanticAI structured types
│   ├── auth.py              # sign-up, log-in, sessions (PBKDF2-HMAC-SHA256)
│   ├── promotions.py        # promo codes: one unique, single-use 10% code per user
│   ├── safety.py            # code-level safety checks
│   └── audit.py             # append-only audit trail writer
└── output/
    ├── harness.md           # how the system works: rules, tools, models, safety, specs
    ├── design.md            # styling
    ├── usability.md         # usability improvements and test results
    ├── app_check.html       # live-site test with screenshots (double-click to open)
    ├── app_check_images/    # screenshots linked from app_check.html
    └── audit_trail.json     # append-only log of agent activity
```

The **agent** is the four files under `backend/`: `prompts/prompt.md`, `agent.py`, `tools.py` and `models.py`. The other backend files support features added along the way (accounts, promo codes, safety checks and the audit trail).

### Local-only data pack (not in git)

```text
data/
├── campus_customs.db        # product catalogue, inventory, users, chat history
└── products/                # product images referenced by the catalogue
```

`.env`, `campus_customs.db` and the product images are **never committed** (see `.gitignore`). The promo code database, `data/promotions.db`, **is** in the repo (it's also created automatically if missing).

## How to run

### 1. Place the data pack

Put the `data/` folder (with `campus_customs.db` and `products/`) inside `hw4/`, so you have `hw4/data/campus_customs.db` and `hw4/data/products/`. `promotions.db` is created automatically.

### 2. Set up the environment (once)

From the `hw4/` folder:

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm install
```

(On macOS/Linux, use `.venv/bin/python` instead of `.venv\Scripts\python.exe`.)

Copy `.env.example` to `.env` in `hw4/` and fill in your own key:

```text
PORTKEY_API_KEY=your-portkey-key
OPENAI_MODEL=gpt-6-luna
MANAGER_MODEL=gpt-6-sol
```

### 3. Start the back end (terminal 1)

From `hw4/backend/`:

```bash
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

### 4. Start the front end (terminal 2)

From `hw4/frontend/`:

```bash
npm run dev
```

### 5. Open the site

Go to **http://localhost:5173**. The front end forwards `/api` and `/media` requests to the back end on port 8000.

- Test account: `test@campuscustoms.yale.edu` / `password`
- Restart the back end after editing `backend/prompts/prompt.md`, because the prompt is loaded at startup.

## Features

- Home (popular items), Products (filters, sorting, 20 per page) and single item pages with stock by size; **out of stock** in bold red
- Create account / log in with securely hashed passwords
- Floating chat assistant: honest price and stock answers, chat search results shown as product cards on the page, memory for logged-in shoppers, and page context (it knows which product you're viewing)
- 10%-off promo popup, Coupon tab, unique single-use codes, and struck-through prices once a code is applied
- A "manager" model that steps in for repeated or frustrated questions
- Safety rules, a $0.10-per-request spending limit, and an append-only audit trail

See [`output/harness.md`](output/harness.md) for full details.
