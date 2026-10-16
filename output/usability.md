# Campus Customs — Usability Improvements

> Problem 9: Usability Improvements.

### How to read this file

| Label | When it was written |
|---|---|
| 📝 **Plan** | **Before** anything was built. All text in sections 1–6 without another label is the original plan. |
| 🔧 **Added during build** | **While** the features were being built: my decisions (separate promotions database, model names, Apply button) and the strikethrough-price follow-up. |
| ✅ **After testing** | **After** I tested the running app: my test results (in my own words) and the manager fix. |

## Summary 📝 Plan

| # | Improvement | Where | Helps |
|---|---|---|---|
| 1 | Welcome popup: "Register and get 10% off" | Front end | Shoppers and business |
| 2 | Coupon tab in the navigation bar | Front end | Shoppers and business |
| 3 | Promo code generation tool (unique code per user) | Backend | Shoppers and business |
| 4 | One-time-use check for promo codes | Backend | Business |
| 5 | Preload all store data on first page open | Backend + front end | Shoppers |
| 6 | "Manager" model escalation for frustrated, repeated questions | Backend agent | Shoppers and business |

---

## 1. Welcome popup: register for 10% off 📝 Plan

**What I added:** when a shopper first arrives on the site, a popup says that if they create an account they get a 10% off promo code. It has a **Create account** button and a close (×) button. It's shown once per visit, not to logged-in shoppers, and not again after it's closed.

**Why it helps:**
- **Shoppers:** the deal is clear right away, and Campus Customs exists to keep Yale merch affordable. 10% off fits that goal.
- **Business:** turns one-time visitors into registered accounts. Registered shoppers get saved chat history, personal help from the assistant, and a reason to come back and buy.

## 2. Coupon tab 📝 Plan

**What I added:** a **Coupon** tab in the top navigation, so shoppers who closed the popup can still find the offer.
- **Guests** see the offer and links to create an account or log in.
- **Logged-in shoppers** see their own promo code, whether it has been used, and a button to apply it to an order.

**Why it helps:**
- **Shoppers:** closing the popup doesn't lose the deal, and there's one obvious place to find their code later.
- **Business:** the offer stays visible on every page without being pushy (the popup only appears once).

## 3. Backend tool: promo code generation 📝 Plan

**What I added:** a backend tool that gives each registered user **one unique code that belongs only to them** (for example `CC10-7KQ4-M9XD`).
- It's created the first time the user signs up or logs in, then shown to them after logging in (in a banner and on the Coupon tab).
- Codes are random, cannot be guessed from the user's name or email, and are stored with that user's account, so they're tracked in the users part of the database.
- The chat assistant can also tell a logged-in shopper their own code, and never anyone else's.
- 🔧 **Added during build:** I chose to track codes in a **new, separate database**, `data/promotions.db`: table `promo_codes` with `user_id` (the `users.id`), `code`, `discount_percent`, `created_at` and `used_at`. One code per user is enforced by the database. The original `campus_customs.db` tables stay unchanged, as the harness requires.

**Why it helps:**
- **Shoppers:** they don't have to hunt for a code or type a generic one. It's waiting for them as soon as they log in.
- **Business:** each code is tied to one account, so codes can't be shared on social media or reused by strangers, and every discount can be traced to a real customer.

## 4. Backend tool: prevent more than one use 📝 Plan

**What I added:** a backend tool that checks and redeems a code.
- It confirms the code belongs to the logged-in user and hasn't been used.
- It marks the code as used, with the date, in that user's record. Any second attempt is refused.
- The check-and-mark happens in a single database step, so two clicks at the same time can't both succeed.
- 🔧 **Added during build:** the used date is stored as `used_at` in that user's row of `promo_codes`. Since the site has no checkout (by design for this assignment), I chose a **Use my code** button on the Coupon tab to apply the code. A future checkout will call the same tool.
- 🔧 **Added during build:** (follow-up request) **once applied, the discount shows sitewide.** Every price on the site (product cards, item pages, chat-search results and the small cards in the chat) shows the list price ~~struck through~~ next to the new price, 10% lower, with a "10% off" tag. The chat assistant quotes both prices too. The discount stays on for that shopper whenever they're logged in.

**Why it helps:**
- **Business:** protects margins. The 10% discount is given once per customer, as intended, and can't be stacked or reused.
- **Shoppers:** a clear answer ("applied" or "already used") instead of a confusing failure at checkout.
- 🔧 **Added during build:** **Shoppers:** seeing the struck-through price next to their lower price everywhere makes the saving obvious and confirms the code worked.

## 5. Preload all store data on first open 📝 Plan

**What I added:** a backend endpoint that returns the whole catalogue in one request when the site first opens: products, prices, stock for every size, categories and popular items. The front end keeps it in memory, so Home, Products, filters, pages of results and single item pages all open instantly, with no waiting on the network.
- The chat assistant still checks live stock and prices with its own tools, so its answers are always current.
- The data refreshes on the next page reload.

**Why it helps:**
- **Shoppers:** clicking between pages and filters feels instant, which makes browsing more pleasant.
- **Business:** faster sites keep shoppers browsing longer and leaving less, and the server handles one request per visit instead of one per click.

## 6. The "manager": smarter model for frustrated shoppers 📝 Plan

**What I added:** the assistant normally runs on the everyday model (**Luna**). If a shopper asks **the same question more than three times**, or sounds frustrated ("that's not what I asked", "this isn't helping"), that one request is handed to a stronger model (**Sol**), the "manager". The next request goes back to Luna.
- The manager follows the same prompt, tools, honesty rules and safety rules.
- It stays within the same $0.10-per-request spending limit; its token caps are adjusted for its higher price.
- 🔧 **Added during build:** model names `gpt-6-luna` (Luna) and `gpt-6-sol` (Sol). The chat shows "The manager stepped in" on that reply. The $0.10 limit is enforced by tracking the cost of each step.
- ✅ **After testing:** fixed (see "Manager fix" at the end of this file).

**Why it helps:**
- **Shoppers:** when the regular assistant isn't getting it, they get a better answer instead of going in circles.
- **Business:** spends extra on a stronger model only when a sale or a customer's goodwill is at risk, not on every message. That keeps costs low while protecting the experience.

---

## My test results ✅ After testing

> In my own words, after testing the improvements in the running app. (Spelling errors corrected.)

For the test results - it needed an exact same prompt instead of a similar one to get the manager to step in, and the manager didn't really recommend a better product when I asked it to give me the best product. The page is definitely fast. And the coupon works for the pop up and the coupon tab. The promo code generate feature worked and then prevented it from being used twice if you tried to apply it again. Overall the features seem to have worked, except for the slight hiccup with the manager.

### Manager fix ✅ After testing

For the manager retest it worked - not exact same words, and the manager stepped in. It was actually a clarification with a slight gimmick to help out the customer.
