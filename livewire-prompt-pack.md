# LIVEWIRE — MVP Prompt Pack v1.0
### 25 sequenced prompts to build Phases 0–3 with a coding agent, tests after every step

Companion to `livewire-handbook.md`. This file is written so a **lower-tier coding model** can execute it: every prompt is self-contained, names exact files, signatures, numbers, and forbids improvisation. You are the QA gate — after each prompt you run the TEST block and check PASS criteria before moving on.

---

## 0. How to use this pack

1. One prompt = one working session. Paste **the Global Context Block (§1)** + **one numbered prompt**. Nothing else.
2. After the agent finishes, run the TEST commands yourself. Green = commit (`git commit -m "P<number>: <title>"`) and move on. Red = use the Debug Prompt (§2). Never continue on red.
3. Never let the agent "improve" earlier work unless a prompt says so. If it suggests refactors, answer: *"Out of scope. Add it to docs/icebox.md."*
4. Numbers in prompts are canonical (they mirror the handbook). If the agent invents different numbers, reject the change.

**Runtime AI-call policy (the whole point):** the finished MVP runs on **zero required LLM calls**. All flavor content is authored or generated at build time, embedded once with a local CPU model, stored in SQLite, and **retrieved** at runtime (vector similarity or SQL). LLM "polish" features exist only behind feature flags with budget caps. If a prompt result adds an API call to a hot path, it fails review automatically.

**Vector stack (fast, modern, serverless):**
- `sqlite-vec` — vector index inside SQLite itself. No extra service.
- `fastembed` — ONNX CPU embeddings, model `BAAI/bge-small-en-v1.5` (384 dims). Runs fine on a $5 VPS, no GPU.
- Migration path: Postgres + `pgvector` in Phase 4 (same 384-dim columns).

---

## 1. GLOBAL CONTEXT BLOCK — paste at the top of EVERY session

```
PROJECT: "Livewire" — a browser text crime MMO (Torn-style). Python 3.12, FastAPI,
SQLAlchemy 2.x, SQLite (dev), React+Vite+Tailwind frontend, APScheduler worker.
Repo layout (do not deviate):
  api/ core/ agents/ llm/ models/ web/ jobs/ tests/ docs/
NON-NEGOTIABLE RULES:
R1. Server-authoritative. The client NEVER computes outcomes, timers, or money.
R2. All game logic lives in core/ as PURE functions: (state_in, rng, now) -> result
    dataclass. api/ and agents/ only call core/ and persist results.
R3. Humans and AI citizens share ONE `characters` table (is_ai flag) and the SAME
    core/ functions. No special-cased game logic for AI.
R4. agents/ must contain ZERO imports from llm/. No LLM calls in the tick loop, ever.
R5. Every LLM call (only in llm/ and jobs/) goes through llm/gateway.py:
    generate(purpose, prompt, tier, cache_key) with cache, logging, feature-flag
    kill switch, and a daily budget cap. Keys come from env only.
R6. Every state-changing action writes one row to `events` (append-only).
R7. RNG is injected (random.Random instance) so tests can seed it. Never call
    random.* at module level in core/.
R8. All timestamps UTC, stored as ISO strings or aware datetimes. Bars use LAZY
    regen computed from bars_updated_at on read — no cron for bars.
R9. Write pytest tests for everything you add, in tests/, mirroring module paths.
    Do not modify existing tests to make new code pass.
R10. Do not add dependencies beyond: fastapi, uvicorn, sqlalchemy, pydantic,
    passlib[bcrypt], apscheduler, httpx, pytest, pytest-asyncio, sqlite-vec,
    fastembed, python-dotenv. Ask before adding anything else — the answer is
    usually no.
R11. Mobile-first UI: every core action reachable in <=2 taps from the home screen.
R12. If a spec detail is missing, choose the simplest option, add a TODO comment,
    and list it at the end of your reply. Do not silently invent systems.
STYLE: type hints everywhere; dataclasses for results; small functions; no
comments that restate code; error responses are JSON {"error": str, "code": str}.
```

---

## 2. Debug Prompt (use whenever a TEST fails)

```
The following test failed. Fix the CODE, not the test. Do not change any file
outside the ones involved in this failure. Explain the root cause in two
sentences, then show the diff.
--- failing command ---
<paste command>
--- output ---
<paste full output>
```

---

## 3. Test conventions (set up once in Prompt 1)

- `make check` runs: `ruff check . && pytest -q`
- `pytest -q` must stay green at every commit. `tests/conftest.py` provides: an in-memory SQLite session fixture, a `rng` fixture = `random.Random(42)`, a `now` fixture = fixed datetime, and an authed `client` fixture (httpx.AsyncClient against the app).
- Money is integer cents internally? **No — integer whole dollars** (simpler, Torn-like). All money fields are `int`.

---
---

# STAGE 0 — FOUNDATION (Phase 0: weekend one)

## PROMPT 1 — Repo scaffold, models, migrations, seeds
```
Create the project scaffold exactly per the Global Context Block.

1) Files: pyproject.toml (deps from R10), Makefile (targets: dev, worker, check,
   seed), .env.example (DATABASE_URL=sqlite:///livewire.db, SECRET_KEY,
   LLM_* placeholders), .gitignore, README.md (3 lines).
2) models/__init__.py + models/tables.py — SQLAlchemy 2.x declarative tables:
   users(id PK, username unique, pw_hash, email nullable, created_at, flags int default 0)
   characters(id PK, user_id FK nullable, is_ai bool default false, name,
     level int default 1, xp int default 0, strength/speed/defense/dexterity int default 10,
     energy int default 100, nerve int default 15, health int default 100,
     bars_updated_at datetime, cash int default 500, bank int default 0,
     heat int default 0, heat_updated_at datetime, notoriety int default 0,
     job_id nullable, faction_id nullable, hospital_until nullable,
     jail_until nullable, crime_skill float default 0,
     persona_json nullable, next_tick_at nullable, created_at)
   items(id, name, slot enum[weapon,armor,consumable], bonus int, base_price int,
     daily_cap int nullable)
   inventory(id, char_id FK, item_id FK, qty int, equipped bool default false)
   market_listings(id, seller_id FK, item_id FK, price int, qty int, created_at)
   market_bands(item_id PK, floor int, ceiling int, mm_daily_cap int)
   crimes(id PK string like 'crime_t1_a', tier int, name, nerve_cost int,
     base_success float, payout_min int, payout_max int)
   events(id, ts, type string, actor_id, target_id nullable, payload_json,
     weight int, seen_by_target bool default false)  -- append-only
   nemesis(char_id PK, ai_id, stage int default 0, assigned_at, defeats int default 0)
   factions(id, name, boss_id nullable, is_ai_led bool, points int default 0)
   faction_members(faction_id, char_id, rank)
   newspaper_issues(id, date unique, content_md)
   digests_cache(char_id PK, last_event_id int, content, ts)
   llm_cache(purpose, key_hash, output, ts, PK(purpose,key_hash))
   llm_log(id, ts, purpose, tier, tokens_in int, tokens_out int, cost_est float)
   feature_flags(name PK, enabled bool, config_json)
   metrics_events(id, ts, char_id nullable, name, props_json)
   content_lines(id, kind string, key string, text, embedding blob nullable)
     -- generic bank for outcome texts, taunts, digest templates
3) models/db.py — engine/session factory from DATABASE_URL; init_db() creates all.
4) jobs/seed.py — inserts feature_flags rows: llm_digest_polish(false),
   llm_newspaper_polish(false), llm_enrichment(false), talkdowns(false);
   inserts the 13 items from handbook Appendix B with base_price = bonus*100
   (consumables: Medkit 500/cap 5, Energy Drink 400/cap 2, Adrenaline 800/cap 1);
   inserts 15 crimes per this exact table:
     t1 (nerve 2, success .85): crime_t1_a Pickpocket 50-150,
       crime_t1_b Shoplift 60-140, crime_t1_c Scam a Tourist 70-150
     t2 (nerve 3, success .70): crime_t2_a Mug a Drunk 150-400,
       crime_t2_b Boost a Bike 180-380, crime_t2_c Sell Knock-offs 160-400
     t3 (nerve 5, success .55): crime_t3_a Burgle a Flat 400-1200,
       crime_t3_b Hack a Terminal 450-1150, crime_t3_c Chop-shop Run 420-1200
     t4 (nerve 8, success .40): crime_t4_a Armed Robbery 1200-4000,
       crime_t4_b Data Heist 1300-3800, crime_t4_c Protection Racket 1250-4000
     t5 (nerve 12, success .25): crime_t5_a Bank Job 4000-15000,
       crime_t5_b Syndicate Hit 4500-14000, crime_t5_c Warehouse Raid 4200-15000
5) tests/conftest.py per §3 conventions; tests/test_seed.py asserting: 15 crimes,
   13 items, 4 flags, tiers/nerve/success match the table above.
Do not build any API endpoints yet.
```
**TEST**
```bash
make check
python -c "from models.db import init_db; init_db()"
python -m jobs.seed && sqlite3 livewire.db "select count(*) from crimes;"
```
**PASS:** tests green; crimes count = 15; re-running seed is idempotent (no duplicates).

---

## PROMPT 2 — Auth + app skeleton + React shell
```
Implement authentication and the app skeleton.
1) api/main.py — FastAPI app factory, CORS for http://localhost:5173,
   routers mounted under /api. api/deps.py — get_db, get_current_character.
2) api/auth.py — POST /api/auth/register {username(3-20 chars, [a-z0-9_]),
   password(>=8)} -> creates user + character (same name, defaults from schema),
   sets httpOnly session cookie (signed with SECRET_KEY, 30-day expiry).
   POST /api/auth/login, POST /api/auth/logout. Passwords via passlib bcrypt.
   Duplicate username -> 409 {"error":"username taken","code":"USERNAME_TAKEN"}.
3) GET /api/me -> character public state (see R8: apply lazy regen on read —
   for now return raw values; regen lands in Prompt 3).
4) web/: Vite+React+TS+Tailwind app. Screens: Login/Register (one page, tabs),
   Home (shows character name + placeholder bars). Fetch wrapper sending
   credentials. Mobile-first: max-w-md centered column, bottom nav stub with
   5 icons (Home, Crimes, Fight, Market, City).
5) tests/test_auth.py: register->200+cookie; duplicate->409; login wrong pw->401;
   /api/me without cookie->401, with cookie->200 and correct username.
```
**TEST**
```bash
make check
make dev &  # uvicorn
curl -i -X POST localhost:8000/api/auth/register -H 'content-type: application/json' -d '{"username":"apoorv","password":"password123"}'
```
**PASS:** tests green; register returns Set-Cookie; /api/me with that cookie returns the character; React login screen works in browser against the API.

---

## PROMPT 3 — Bars + lazy regen (pure) + Home screen
```
Implement bars with lazy regen as pure functions.
1) core/regen.py:
   @dataclass BarsState: energy:int; nerve:int; health:int; updated_at:datetime
   def apply_regen(b:BarsState, now:datetime, max_energy:int, max_nerve:int,
                   max_health:int) -> BarsState
   Rates (per handbook §4.1): energy +5 per full 10 min; nerve +1 per full 5 min;
   health +1 per full 3 min. Clamp at max. Partial intervals carry over ONLY via
   updated_at advancing in whole intervals consumed (i.e., set updated_at to
   old + consumed_intervals*interval; do NOT lose fractional time).
   def max_bars(level:int) -> (max_energy, max_nerve, max_health):
     energy = min(150, 100 + 5*(level-1)); nerve = min(25, 15 + (level-1)//2);
     health = 100.
2) core/state.py — load_character(session, id, now) helper that reads the row,
   applies apply_regen, persists updated bars, returns a CharacterState dataclass.
   Every endpoint from now on uses this.
3) Wire into GET /api/me. Home screen renders three bars with fill %, numeric
   x/y, and a countdown to next tick per bar.
4) tests/test_regen.py — table-driven cases:
   (a) 0 min elapsed -> unchanged; (b) 9m59s -> energy unchanged, updated_at
   unchanged for energy interval accounting; (c) 25 min -> +10 energy, +5 nerve,
   +8 health; (d) huge elapsed -> clamped at max, updated_at == now;
   (e) fractional carry: 15 min then 5 min later -> total +10 energy not +5.
```
**TEST:** `make check`
**PASS:** all regen table cases green, including the fractional-carry case (e). UI bars tick down a live countdown.

---
---

# STAGE 1 — THE TORN CORE (Phase 1: weeks 1–2)

## PROMPT 4 — Crimes end-to-end
```
Implement the crime system.
1) core/crimes.py:
   @dataclass CrimeResult: success:bool; payout:int; xp:int; skill_gain:float;
     jailed:bool; jail_minutes:int; heat_gain:int; text_key:str
   def attempt_crime(char:CharacterState, crime:CrimeRow, rng:Random,
                     now:datetime) -> CrimeResult
   Rules (handbook §4.3, Appendix C):
   - success_p = clamp(0.05, 0.95, base_success + char.crime_skill*0.005 - 0)
   - nerve_cost deducted before roll; insufficient nerve -> raise DomainError
     ("NOT_ENOUGH_NERVE").
   - payout uniform int in [payout_min, payout_max] on success; 0 on fail.
   - xp: success tier*10, fail tier*2. skill_gain: success 1.0, fail 0.2.
   - jail: only on fail when tier>=3, probability 0.35; jail_minutes uniform
     10..45.
   - heat_gain: tier4 success +6, tier5 success +10, else 0.
   - text_key = f"crime:{crime.id}:{'success'|'fail'|'jail'}" (used by content
     bank later).
   - Blocked if char is in hospital or jail -> DomainError("INCAPACITATED").
2) api/crimes.py — GET /api/crimes (list with your current success % per crime),
   POST /api/crimes/{id}/attempt -> applies result transactionally: bars, cash,
   xp, crime_skill, heat (+ heat_updated_at), jail_until; writes events row
   type='crime', weight = tier*2 (success) or tier (fail), payload {crime_id,
   success, payout}.
3) web: Crimes screen — 15 rows grouped by tier, each shows nerve cost, payout
   range, live success %, one Attempt button; result renders returned text_key
   as plain text for now.
4) tests/test_crimes.py: seeded-rng determinism; clamp bounds at extreme
   crime_skill; nerve deduction and NOT_ENOUGH_NERVE; jail only possible for
   tier>=3 fails; heat applied for t4/t5 success; event row written with
   correct type/weight.
```
**TEST:** `make check`, then in browser: commit 3 crimes, watch nerve drop and cash rise.
**PASS:** deterministic tests green; event rows appear (`sqlite3 livewire.db "select type,weight from events order by id desc limit 5;"`); UI success % matches API.

---

## PROMPT 5 — Jail & hospital states + bust-out
```
Implement incapacitation states.
1) core/state.py: derive status: 'ok'|'hospital'|'jail' from *_until vs now.
   All action endpoints must call require_ok(char) (raises INCAPACITATED with
   seconds_remaining in payload).
2) POST /api/jail/{char_id}/bust — any OK character may attempt to bust
   another out of jail. Cost 10 energy. success_p = clamp(.05,.95,
   .30 + buster.crime_skill*0.004). Success frees target (jail_until=None),
   events type='bust' weight 6, busting friend-maker! Fail: buster jailed
   5-15 min, event weight 3.
3) GET /api/city/jail — list jailed characters (name, level, minutes left).
4) web: City screen tab "Jail" with Bust buttons; own-status banner with
   countdown when hospitalized/jailed (blocks action buttons client-side too).
5) tests/test_jail.py: cannot act while jailed; bust success frees target and
   writes event; bust fail jails the buster; energy deducted both ways.
```
**TEST:** `make check`; manual: jail yourself via t3 crime fails (temporarily set rng seed in a dev route? No — use pytest to verify; manual via luck).
**PASS:** tests green; banner countdown works; busting flow works between two browser sessions (register a second account).

---

## PROMPT 6 — Combat + banking
```
Implement attacks and the bank.
1) core/combat.py:
   @dataclass CombatResult: won:bool; p_win:float; damage_dealt:int;
     hospital_minutes_target:int; hospital_minutes_attacker:int; mug_amount:int;
     xp:int; heat_gain:int; notoriety_gain:int; text_key:str
   def resolve_attack(att:CharacterState, dfn:CharacterState, choice:str,
                      rng:Random) -> CombatResult
   Formula (handbook §4.4 + Appendix C):
     atk = att.strength*1.0 + att.speed*0.4 + att.weapon_bonus
     dfn_p = dfn.defense*1.0 + dfn.dexterity*0.4 + dfn.armor_bonus
     scale = 0.25 * ((atk + dfn_p) / 2); p_win = clamp(.10,.90,
       1/(1+exp(-(atk-dfn_p)/max(scale,1))))
   Costs/effects: attacker spends 25 energy. Win -> choice in
     {'mug','hospitalize','leave'}: mug steals uniform 3-10% of target CASH
     (not bank), target hospital 15-60 min, heat +4;
     hospitalize: target hospital 15-60, heat +8, notoriety +3;
     leave: heat +1, notoriety +1. Loss -> attacker hospital 10-30 min.
     xp: win 15, loss 5.
   text_key = f"attack:{'win'|'loss'}:{choice}".
2) Banking: POST /api/bank/deposit {amount} fee 1.5% (rounded up, min 1);
   POST /api/bank/withdraw {amount} free. Mug can never touch bank.
3) api/combat.py — POST /api/attack/{target_id} {choice}. Validations: target
   not self, not incapacitated (either side), attacker has 25 energy.
   Events: type='attack' weight = 8 (hospitalize) / 6 (mug) / 3 (leave/loss),
   payload {p_win, choice, mug_amount}.
4) web: Fight screen: enter/select target (by exact name for now), shows both
   power estimates BLURRED (ranges, not exact), three buttons appear on win.
   Actually simpler: choice is selected BEFORE attacking via radio (mug default).
   Bank card on Home: balance, deposit/withdraw.
5) tests/test_combat.py: p_win clamps; equal stats -> p_win ~0.5 +-0.02;
   mug % within 3-10 of cash only; bank untouched by mug; energy cost enforced;
   fee math (deposit 1000 -> bank +985); events weights correct.
```
**TEST:** `make check`; two browser accounts fight.
**PASS:** all formula tests green; a mugged player's bank is intact; hospital timers show on both profiles.

---

## PROMPT 7 — Items, inventory, equip, shop
```
1) core/items.py — equip rules: max one weapon + one armor equipped;
   weapon_bonus/armor_bonus loaded into CharacterState (0 if none).
   Consumables: use applies effect (Medkit +40 health, Energy Drink +25 energy,
   Adrenaline sets buff_until = now+1h stored in persona_json['buffs'] for
   humans too -> simpler: add columns? NO — add table buffs(char_id, kind,
   until). Adrenaline effect: +10% atk in resolve_attack when active.)
   Daily caps per item enforced via events count (type='use_item') since
   00:00 UTC.
2) api/items.py — GET /api/shop (items+prices), POST /api/shop/buy {item_id,qty},
   GET /api/inventory, POST /api/inventory/{id}/equip|unequip,
   POST /api/inventory/{id}/use.
3) web: Market screen tab "Shop" + "Inventory". Equipped badge. Use button with
   remaining daily cap shown.
4) tests/test_items.py: buy deducts cash; equip swaps (equipping second weapon
   unequips first); combat uses bonuses (attack with Pistol vs none changes
   p_win as expected); daily cap blocks the N+1th use; Adrenaline modifies atk
   only while active.
```
**TEST:** `make check`
**PASS:** green incl. the p_win-with-weapon assertion; caps reset logic verified by a frozen-time test at 23:59 -> 00:01.

---

## PROMPT 8 — Player market (order book)
```
1) api/market.py + core/market.py:
   POST /api/market/list {item_id, price(1..10_000_000), qty} — moves qty from
   inventory into a listing; listing fee 2% of price*qty charged immediately
   (rounded up); insufficient inventory/cash -> DomainError.
   GET /api/market/{item_id} — order book: listings ascending by price, plus
   band info if present.
   POST /api/market/buy/{listing_id} {qty} — transactional: buyer pays
   price*qty cash, seller receives price*qty (no second fee), inventory moves,
   listing qty decrements/deletes. MUST be safe under concurrent buys:
   use a single UPDATE ... WHERE qty >= :qty guard and check rowcount.
   POST /api/market/cancel/{listing_id} — returns items, fee not refunded.
   Events: type='trade' weight 2 on buy, payload {item_id, qty, price}.
2) web: Market tab "Bazaar": per-item order book, list-item form, my listings.
3) tests/test_market.py: fee math; cannot buy own listing? (allowed, but test
   money conservation anyway); concurrency test: two sessions buy qty=1 of a
   qty=1 listing -> exactly one succeeds; cancel returns items.
```
**TEST:** `make check`
**PASS:** concurrency test green (this one matters — rerun 20×: `pytest tests/test_market.py -q -k concurrent --count 20` if pytest-repeat available, else loop in bash).

---

## PROMPT 9 — Jobs, XP/levels, heat thresholds
```
1) core/progression.py — xp_to_level(xp): level = floor((xp/100)**0.6)+1
   (write the inverse table in a docstring for levels 1-30). On level-up:
   recompute max bars (core/regen.max_bars), event type='levelup' weight 4.
2) Jobs: hardcode 5 jobs in models seed: Courier(pay 120, perk speed+1/day),
   Bouncer(140, strength+1/day), Clinic Aide(110, heals you 20 on collect),
   Mechanic(130, dexterity+1/day), Junior Fixer(150, crime_skill+0.3/day).
   POST /api/jobs/select {job_id}; POST /api/jobs/collect — once per UTC day
   (track via events type='job_pay'); applies pay + perk.
3) Heat: core/heat.py — lazy decay 1 per hour from heat_updated_at (same
   pattern as bars). Threshold events, checked after any heat gain:
   crossing 40 upward -> 'shakedown': lose min(cash*0.05, 500) fine, event
   weight 5; crossing 70 -> 'raid': lose 10% cash + jail 10 min, weight 9.
   Crossing means old<threshold<=new. POST /api/heat/bribe — pay 100*heat cash
   to set heat = max(0, heat-30), event weight 2.
4) web: Home shows Job card (collect button w/ cooldown) + Heat gauge with
   color bands and Bribe button >=40.
5) tests: level curve spot checks (0xp->1, 100->2? verify with formula and
   FIX the formula if degenerate — requirement: level 2 at ~100xp, level 10 at
   ~4600xp, monotonic); job collect once/day enforced across frozen midnight;
   heat decay math; threshold fires exactly once per crossing; bribe math.
```
**TEST:** `make check`
**PASS:** green; heat crossing test proves no double-fire when gaining heat twice above 40.

---

## PROMPT 10 — Events feed + weights audit
```
1) Ensure EVERY mutating action writes exactly one events row (audit: grep
   core/ and api/ for session.commit and verify). Add any missing.
2) Canonical weight table (create core/event_weights.py, single source):
   crime success tier*2 | crime fail tier | attack hospitalize 8 | attack mug 6 |
   attack leave/loss 3 | bust 6/3 | trade 2 | levelup 4 | shakedown 5 | raid 9 |
   job_pay 1 | use_item 1 | bribe 2 | deposit/withdraw 0 (no event).
3) GET /api/feed?since_id= — your events (actor or target), newest first,
   limit 50, marks seen_by_target=true for rows where you're target.
4) web: Home "Recent activity" list (icon + one-line rendering per type — write
   a small renderer map in TS; placeholder wording is fine, content bank
   replaces it in Prompt 17).
5) tests/test_events.py: one row per action for a scripted sequence of 8
   different actions; weights match the canonical table exactly.
```
**TEST:** `make check`
**PASS:** the scripted-sequence test asserts 8 rows with exact (type, weight) tuples.

---

## PROMPT 11 — Mobile UI pass (gate: the game must be playable & pleasant)
```
Polish web/ for mobile. No new backend.
- Bottom nav final: Home, Crimes, Fight, Market, City. Active states.
- Every action <=2 taps from Home (Crimes list IS the action screen, etc.).
- Bars pinned in a compact header on all screens with live countdowns.
- Optimistic-free: after any POST, refetch /api/me and the local list. Buttons
  disable while pending; DomainError codes map to human toasts (write the map).
- Empty/loading states for all lists. Dark theme default, system font stack,
  44px min touch targets.
- Add a tiny Playwright smoke (web/tests/smoke.spec.ts): register -> commit
  crime -> see cash increase -> train once. Runnable via `make e2e` (starts
  api+vite, runs headless chromium).
```
**TEST:** `make check && make e2e`; then play on your actual phone via LAN for 15 minutes.
**PASS:** e2e green; phone session: nothing requires pinch-zoom, no action needs >2 taps, you personally want to keep playing. **This is the Phase 1 gate — spend 2 days here before continuing.**

---

# STAGE 2 — THE CITY COMES ALIVE (Phase 2: weeks 3–4)

## PROMPT 12 — LLM gateway (built early, used rarely)
```
Implement llm/gateway.py. NOTE: the MVP must run fully with all LLM flags OFF;
this module exists for optional polish/enrichment jobs only (rules R4, R5).
1) Providers: read from env a priority list LLM_PROVIDERS="gemini,groq" with
   per-provider LLM_<NAME>_KEY, LLM_<NAME>_BASE_URL, LLM_<NAME>_MODEL_S,
   LLM_<NAME>_MODEL_M. All calls via httpx to OpenAI-compatible
   /chat/completions (Gemini has an OpenAI-compatible endpoint; keep provider
   adapters trivial).
2) def generate(purpose:str, prompt:str, tier:Literal['S','M'],
                cache_key:str|None, max_tokens:int=300) -> str|None
   Order of checks: (a) feature_flags[f'llm_{purpose}'].enabled else return None;
   (b) llm_cache hit -> return cached; (c) daily budget: sum(llm_log.cost_est
   today) < float(env LLM_DAILY_BUDGET_USD, default 1.0) else log a
   'budget_exceeded' metrics_event and return None; (d) try providers in order,
   3s timeout, on failure try next; all fail -> return None.
   Log every call to llm_log with rough cost_est from env-configured per-1k
   token prices. Write cache on success.
3) Callers MUST handle None by falling back to templates (enforced by
   convention; add this to README).
4) tests/test_gateway.py with a mocked transport: flag off -> None, no HTTP;
   cache hit -> no HTTP; budget exceeded -> None; provider 1 fails ->
   provider 2 used; success writes llm_cache + llm_log.
```
**TEST:** `make check`
**PASS:** all five behaviors proven with zero real network calls (assert on the mock).

---

## PROMPT 13 — Offline persona factory + seed 800 citizens (ZERO LLM calls)
```
Implement agents/personas.py — pure-code citizen generation.
1) Hardcode content lists in agents/name_parts.py:
   FIRST (>=120 diverse names), LAST (>=120), NICKNAMES (>=60 like 'Half-Smile',
   'Two-Phones', 'the Ledger'), DISTRICTS (8). Write them yourself, varied and
   theme-neutral.
2) Archetypes: encode handbook Appendix D exactly as
   ARCHETYPES: dict[str, dict[str, float]] (train/crime/attack/trade/rest
   weights) for: bruiser, hustler, ghost, trader, climber, loyalist, wildcard,
   enforcer, drifter. (Slumlord is Phase 4 — exclude.)
3) def make_persona(rng) -> dict with keys: name ("First 'Nick' Last", 30%
   chance of nickname), archetype (weighted: hustler .18, bruiser .15,
   drifter .15, ghost .12, trader .12, climber .10, loyalist .08,
   enforcer .06, wildcard .04), traits (sample 3 of 24 hardcoded), schedule
   {active_hours: sample 3-6 of 0-23 biased to 7-23, days_off: sample 0-1},
   aggression/greed/loyalty/risk: beta(2,2) floats, stat_curve in
   [combat_heavy, balanced, sneak, money], wealth_curve in
   [hand_to_mouth, saver, flashy], avatar_seed int.
4) def spawn_citizen(session, rng, target_level:int) -> character row with
   is_ai=True, persona_json, level=target_level, stats rolled so total stats ≈
   40*level^1.15 distributed per stat_curve (write the distribution table),
   cash ≈ 200*level*wealth_multiplier, a plausible equipped weapon/armor for
   level (tier = clamp(1,5, level//6+1)), next_tick_at = now + jitter(0-60m).
5) jobs/population.py — seed_population(n=800): level distribution
   1-3:35%, 4-7:30%, 8-12:20%, 13-18:10%, 19-25:5%. Idempotent via a
   metrics_event marker. Add `make seed-city`.
6) tests/test_personas.py: 800 spawned; every persona validates against a
   pydantic Persona model; archetype distribution within +-4% of spec over
   n=800 with seeded rng; stat totals within 15% of the level formula;
   ZERO imports of llm anywhere under agents/ — write
   tests/test_no_llm_in_agents.py that walks agents/*.py AST and fails on any
   import of llm.
```
**TEST**
```bash
make check && make seed-city
sqlite3 livewire.db "select count(*) from characters where is_ai=1;"
```
**PASS:** count = 800; AST guard test exists and is green; distribution assertions green.

---

## PROMPT 14 — The tick engine
```
Implement agents/tick.py + agents/utility.py per handbook §6. Reminder R3/R4:
citizens act through core/ functions only; zero llm imports (guard test exists).
1) worker.py at repo root: APScheduler BackgroundScheduler, job every 60s
   calling tick(session_factory, rng, now). Makefile target `worker`.
2) tick(): select is_ai characters where next_tick_at <= now AND status ok AND
   current hour in schedule.active_hours AND weekday not in days_off,
   LIMIT 200 per tick (fairness: order by next_tick_at). For each: action =
   pick_action(citizen); execute; write next_tick_at = now + minutes(20..90,
   skewed by 1/aggression); commit per citizen (isolation).
3) pick_action(c) in agents/utility.py:
   start from ARCHETYPES[c.archetype]; modifiers:
   cash < 100 -> crime +0.20; heat > 60 -> crime -0.20, rest +0.20;
   grudge_ready(c) -> convert attack weight into revenge(target);
   energy < 25 -> attack weight to 0; nerve < 5 -> crime weight to 0;
   normalize; weighted_choice(rng).
   Action executors: train -> core train on stat per stat_curve;
   crime -> pick crime tier = clamp(1,5, level//5+1) minus (1 if risk<0.4);
   attack -> pick target via ladder query (Prompt 15) preferring humans 30%
   of the time; trade -> if wealth_curve==saver deposit 50% cash, else list or
   buy a random reasonable item within +-20% of base_price; rest -> heal via
   time (no-op) or bust a random jailed character if loyalty > .7.
   Revenge target = highest grudge (Prompt 16) — until then, stub returns None.
4) Safety rails inside executors: respect new-player protection flags (stub
   until Prompt 15), never attack a target already in hospital, never attack
   same target twice within 6h (check events).
5) tests/test_tick.py: with seeded rng and a fixed city of 50 citizens,
   (a) tick processes only due+scheduled citizens; (b) action frequencies over
   500 simulated picks per archetype within +-5% of modified weights;
   (c) a full tick of 200 citizens completes < 2.0s against in-memory sqlite;
   (d) after 20 simulated ticks, events table contains crime/attack/trade/
   levelup rows from AI actors (the city visibly "moved").
```
**TEST**
```bash
make check
make worker &  # leave running
sleep 180 && sqlite3 livewire.db "select type,count(*) from events where actor_id in (select id from characters where is_ai=1) group by type;"
```
**PASS:** perf test (c) green; after ~3 min of worker, AI events of ≥3 distinct types exist. Log in as a human: your feed shows the world moving (you may already have been attacked — check protection stub didn't fail).

---

## PROMPT 15 — Targets ladder + new-player protection (for real)
```
1) core/ladder.py — suggest_targets(char, session, now) -> 5 rows:
   2 with power_total in [0.75,0.95]x yours, 2 in [0.95,1.05]x, 1 in
   [1.05,1.25]x, where power_total = str+spd+def+dex+equip bonuses.
   Mix: prefer humans active in last 24h within +-1 level; fill remainder with
   AI. Exclude: hospitalized, jailed, protected (below), attacked-by-you<6h,
   self. Return name, level, blurred power band (e.g. "600-800"), is_online-ish
   ("seen recently" bool), never exact stats.
2) Protection (handbook §3.4) — core/protection.py, enforced INSIDE
   core/combat.resolve_attack callers and agents executors:
   account_age < 7d targets: mug capped at 5% cash; hospital minutes halved;
   AI attackers limited to 2 attacks/day/target (count events).
   Also global AI mercy: an AI never attacks the same human >2x/day.
3) AI-vs-human tuning: when an AI within +-1 band attacks OR is attacked by a
   human with account_age < 14d, sample the AI's effective power from
   U[0.80,0.95]x its real power (they fumble). Implement as a multiplier arg
   into resolve_attack; document it.
4) GET /api/targets -> ladder; web Fight screen now shows the 5 suggestions
   as cards with Attack button (choice radio persists).
5) tests: band composition; exclusions; protection caps enforced when an AI
   attacks a 2-day-old account 3 times (3rd blocked); mug on protected = max
   5%; tuning multiplier applied only under the stated conditions.
```
**TEST:** `make check`; new browser account, open Fight.
**PASS:** a fresh level-1 account sees 5 sensible targets and wins roughly half its fights vs same-band AI (play 10 fights; 3–7 wins acceptable).

---

## PROMPT 16 — Grudges + revenge scheduling
```
1) core/grudges.py — grudge scores computed from events (no new write path):
   score(ai_id -> char_id) = sum over events(actor=char, target=ai) of
   base_points * 0.5^(age_days/7), where base_points: attack-hospitalize 15,
   attack-mug 8, attack-leave 3, bust(actor freed ai) -10 (negative =
   goodwill). Provide get_top_grudge(ai_id) and a nightly materialized cache
   table grudge_cache(ai_id, target_id, score, computed_at) refreshed by
   jobs/nightly.py (create it; runs from worker at 03:00 UTC).
2) agents/utility.grudge_ready(c): top grudge score >= 20 AND target
   vulnerability window open: target hospital_until within last 30m (just got
   out), OR health < 40, OR cash > 3000 (juicy). Respect protection rules.
3) Revenge executor: attack with choice = 'hospitalize' if score>=35 else
   'mug'. On execution write additional event type='revenge' weight 10 payload
   {grudge_score}. After revenge, decay that grudge by 60%.
4) Taunt hook: revenge event payload includes text_key='taunt:revenge' for the
   content bank (Prompt 17/19).
5) tests: decay math (15 pts, 7 days -> 7.5); goodwill subtracts; window
   detection cases; post-revenge decay; protection blocks revenge on
   protected accounts (event NOT written).
```
**TEST:** `make check`; then: mug the same AI twice, get yourself hospitalized by anyone, wait for exit + a few worker ticks.
**PASS:** the wronged AI hits you within ~30 min of your hospital exit (check events for type='revenge' targeting you). This is the first "whoa" moment — screenshot it.

---

## PROMPT 17 — Content bank + vectors (retrieval replaces generation)
```
Runtime flavor via retrieval, zero LLM calls. Uses sqlite-vec + fastembed
(BAAI/bge-small-en-v1.5, 384 dims).
1) llm/embeddings.py — embed_texts(list[str]) -> list[list[float]] via
   fastembed (lazy singleton; first call downloads the ONNX model — document
   ~100MB disk). No network at inference beyond first download.
2) content_lines usage: kind='outcome', key=text_key from Prompts 4/6 (e.g.
   'crime:crime_t3_a:success'). AUTHOR the lines yourself NOW, in
   jobs/content_seed.py as Python literals: for each of the 15 crimes x
   {success, fail, jail} write 8 distinct one-liners (second person, past
   tense, street register, <=140 chars, use slots {payout} {district} where
   natural), and for the 6 attack text_keys write 10 each. Style examples:
   'You lifted a fat wallet outside the metro — {payout} richer, heart still
   hammering.' / 'The terminal spat an alarm. You walked, hands in pockets,
   like it was somebody else's problem.' Quality bar: no two lines share an
   opening 3 words within a key.
3) jobs/embed_content.py — embeds all content_lines lacking embeddings, stores
   float32 blobs, builds a sqlite-vec virtual table vec_content(rowid ->
   embedding). `make embed`.
4) core/flavor.py — pick_line(char_id, text_key, context:dict) -> str:
   candidates = lines for key; last5 = this player's last 5 served line ids
   (new table served_lines(char_id, line_id, ts) ring-buffered); choose the
   candidate MOST DISSIMILAR (min max-cosine vs last5 embeddings, via
   sqlite-vec); fallback rng choice if vec unavailable. Fill slots from
   context; record served.
5) Wire pick_line into crime/attack/bust/heat responses and the feed renderer
   (API returns final text; web drops its placeholder map).
6) tests: bank completeness (15*3*8 + 6*10 rows, all keys covered — a test
   enumerates text_keys emitted by core/ and asserts coverage!); anti-repeat:
   serving 6 lines for one key yields >=5 distinct; slot filling; graceful
   fallback when vec tables absent.
```
**TEST**
```bash
make check && python -m jobs.content_seed && make embed
```
**PASS:** the coverage test (any text_key without lines = failure) is green — this test is your safety net forever; in-game crime results now read like a game, not a spreadsheet.

---

## PROMPT 18 — "While You Were Gone" digest (template-first)
```
1) core/digest.py — build_digest(char, session, now) -> str (markdown, <=90
   words): query events where target=char (or actor=char with weight>=6) AND
   id > digests_cache.last_event_id; rank by weight desc, take 5; render each
   via hardcoded sentence templates per event type (write them; reuse
   pick_line where a text_key exists, else template). Always end with ONE hook
   line chosen by priority: active revenge threat > nemesis stage-up (later) >
   heat>=40 > market: your listing sold > default rotating tip (bank of 12).
   Zero events -> 'Quiet night in the city.' + hook. Cache in digests_cache.
2) Optional polish: if generate('digest_polish', prompt, 'S', cache_key)
   returns text, use it; else template output. Flag default OFF (R5 fallback
   pattern).
3) GET /api/digest -> {content, since}; web: Home shows it as the top card
   after >=6h away (dismissable).
4) tests: ranking picks top-5 by weight; word cap; hook priority order (craft
   fixtures for each); cache prevents recompute; flag off -> gateway never
   called (assert via mock).
```
**TEST:** `make check`; play, wait for worker activity (or simulate 6h by editing digests_cache ts), reload.
**PASS:** digest reads coherently for a fixture with mixed events; with all LLM flags off the feature is fully functional.

---
---

# STAGE 3 — IDENTITY & DRAMA (Phase 3: weeks 5–6 → closed alpha)

## PROMPT 19 — Nemesis system
```
1) agents/nemesis.py + state machine on nemesis table.
   Assignment: nightly job assigns to any human with account_age>=3d and no
   active nemesis: pick an AI with power 1.10-1.20x theirs, archetype
   countering their most-used action (attacker->enforcer, criminal->ghost,
   trader->hustler; default bruiser). Event 'nemesis_assigned' weight 8.
   Stages: 0 taunt -> 1 mug -> 2 undercut (if target has a market listing,
   nemesis lists same item 10% cheaper; else skip) -> 3 hospitalize ->
   repeat 1-3. One stage action max per day, executed via the tick when the
   nemesis's schedule allows; mercy: skip if target protected, hospitalized,
   or nemesis already hit them 2x today; after a stage-3 hospitalization,
   48h cooldown.
   Defeats: each time the human beats THEIR nemesis in combat, defeats+=1,
   event weight 10; at 3: retirement — event 'nemesis_retired' weight 12,
   loot drop (cash 500*level + a consumable), nemesis AI gets flag
   persona_json['retired_from']=char_id (stops targeting), new assignment
   next nightly at 1.15x current power.
2) Taunt bank: add kind='taunt' lines in content_seed: 12 per stage key
   (taunt:stage0..3, taunt:defeated, taunt:retired), with slots {name}
   {district}. Selection: embed the triggering event sentence, retrieve the
   most SIMILAR taunt (opposite of anti-repeat — we want relevance), still
   excluding last-served. Delivered as event payload text; feed + digest
   surface it.
3) GET /api/nemesis -> current nemesis card (name, blurred power, stage,
   defeats, 'path to victory' line: which stat gap is largest and how many
   gym sessions ≈ close it — compute from diminishing formula).
4) web: Nemesis card on Home + Fight screen shortcut.
5) tests: assignment power band + counter-archetype; stage progression with
   frozen days; mercy rules (protected/2-a-day/cooldown); retirement at 3 and
   reseed at +15%; 'path to victory' session math.
```
**TEST:** `make check`; set your test account age to 3d in DB, run nightly job, watch two days of worker (or advance stages via frozen-time tests).
**PASS:** full lifecycle proven in tests: assigned → taunted → mugged → beaten ×3 → retired with loot → new nemesis stronger.

---

## PROMPT 20 — The daily newspaper
```
1) jobs/newspaper.py (worker @ 05:00 UTC): build issue from yesterday's
   events: sections in order — CRIME DESK (top-3 weight>=8), STREET TALK
   (2 random weight 4-7), MARKET WATCH (top item by volume + biggest price
   move vs prior day), RISING STAR (highest-notoriety-gain account_age<14d,
   if any), NEMESIS WATCH (a retirement or a stage-3, if any).
   Headline templates per section (write 6 variants each, slots {name}
   {amount} {item} {district}); anonymize targets of muggings if human and
   account_age<7d ('a newcomer'). Optional generate('newspaper_polish',...,
   'M') rewrites the assembled markdown — flag OFF by default.
2) GET /api/newspaper/today + /api/newspaper/{date}; personal-mention:
   response includes mentions:[{line, share_slug}].
3) Share page: GET /paper/{date}/{slug} — public, server-rendered minimal HTML
   (FastAPI template, no auth) with OG meta tags so the headline unfurls on
   social; links to signup. web: Newspaper tab in City; mention banner with
   Share button (copies URL).
4) tests: section assembly from fixtures; anonymization rule; mention
   detection; share page renders w/o auth and contains og:title.
```
**TEST:** `make check`; run job manually against your dev events; open the share URL in an incognito window.
**PASS:** issue reads like a paper (fixtures snapshot test); share URL unfurls title correctly (check with a link-preview tool or curl the OG tags).

---

## PROMPT 21 — Week-1 arc (the Fixer) + day-7 recap
```
1) Hardcode the Fixer arc in core/arc.py as data: 6 steps, each {day_min,
   trigger, message (write the copy: terse, street-wise mentor, 2-3 lines),
   task {type: crime_tier|train|attack_ai|deposit, n}, reward {cash|item|
   energy_token}}: d1 tutorial x3 (t1 crime, train once, attack the planted
   pushover — spawn one designated weak AI per new account), d2 'do 3 t2
   crimes' -> Blade, d4 'join... nothing yet' -> deposit 500 -> cash, d6
   'beat your nemesis once' -> Medkit x2.
2) Delivery as events type='fixer' weight 7 surfacing in feed + a dedicated
   Home card with the current task + progress + Claim button (server
   validates via events counts).
3) Day-1 refills: two free full-bar refill buttons (events-tracked).
4) Day-7 recap: on first login after day 7, GET /api/recap7 -> totals (cash
   earned, crimes, fights W-L, enemies made = distinct AI with grudge>0,
   headline if any) rendered as a share-page like Prompt 20's (slugged,
   public, OG tags).
5) tests: step gating by day+trigger; claim validation (can't claim twice /
   early); pushover AI spawned once; recap math from fixtures.
```
**TEST:** `make check`; fresh account walkthrough on your phone, faking days by editing created_at.
**PASS:** a brand-new player is never without a visible next goal during week 1 (walk it yourself and confirm at every step the Home screen shows exactly one clear task).

---

## PROMPT 22 — Login rewards, achievements, leaderboards
```
1) Daily login: first /api/me of a UTC day grants day-streak reward
   (d1 $200, d2 $300, d3 energy token, d4 $500, d5 nerve refill, d6 $800,
   d7 Adrenaline + $1000, then repeat at d4-7 values). Streak resets after
   48h gap. Toast on grant.
2) Achievements: hardcode 20 in core/achievements.py (first blood, 100 crimes,
   t5 success, nemesis retired, $100k banked, bust 10 people, survive raid,
   7-day streak, level 10/20, etc.) checked event-driven (a checker map by
   event type — no polling). Grant = event weight 4 + notoriety +2 + badge on
   profile.
3) Leaderboards: GET /api/boards/{kind} for kind in [notoriety, wealth(bank+
   cash), level, weekly_xp] — top 50, cached 5 min. AI citizens included and
   marked with a small chip 'CITIZEN' (honesty policy §1 of handbook —
   subtle, not shameful). weekly_xp resets Monday 00:00 UTC via nightly job.
4) web: City tab gains Boards + Achievements; profile screen (public) shows
   level, notoriety, badges, faction (later), W-L, 'wanted' if heat>=70.
5) tests: streak math incl. 48h reset & UTC boundaries; achievement triggers
   (parameterized over 6 of them); board ordering + AI chip flag in payload;
   weekly reset.
```
**TEST:** `make check`
**PASS:** frozen-time streak tests green across a month simulation; boards show a healthy AI/human mix with chips.

---

## PROMPT 23 — Metrics + admin stats
```
1) Instrument: write metrics_events for signup, session_start (first request
   after 30m idle), crime, attack, digest_viewed, share_clicked,
   fixer_claim, purchase_stub. Frontend fires digest_viewed/share_clicked via
   POST /api/metrics {name, props}.
2) GET /api/admin/stats (guard: users.flags & 1 == admin; make yourself admin
   via a documented SQL one-liner): DAU today, D1/D7 retention cohorts (from
   signup vs session days), sessions/DAU, digest->action rate (action within
   10m of digest_viewed), AI event volume by type (24h), llm spend today,
   worker lag (max now-next_tick_at overdue).
3) tests: cohort math on fixtures (build a tiny 3-user, 8-day fixture and
   assert D1/D7 numbers by hand); digest->action window logic.
```
**TEST:** `make check`; curl the admin endpoint.
**PASS:** the hand-computed fixture cohort matches the endpoint exactly (if you can't verify retention math by hand, you can't trust the alpha numbers).

---

## PROMPT 24 — Alpha hardening + deploy
```
1) Rate limits (in-process token bucket keyed by user AND ip): auth 5/min/ip,
   actions 30/min/user, market 10/min/user -> 429 {"code":"RATE_LIMITED"}.
2) Economy locks: account_age<7d cannot list on market above 2x base_price,
   cannot receive listings bought by same-IP accounts (log + block, event
   'abuse_flag'); document limitations in docs/abuse.md.
3) Ops: scripts/backup.sh (sqlite .backup -> timestamped file, keep 14; cron
   line documented); /api/health (db + worker heartbeat row updated each
   tick); structured logging (one line JSON per request: path, user, ms).
4) Deploy: write docs/deploy.md — single VPS: uvicorn (systemd unit),
   worker (systemd unit), Caddy or nginx reverse proxy w/ HTTPS, .env,
   Cloudflare in front, vite build served as static. Provide the actual unit
   files and Caddyfile in ops/.
5) tests: rate limiter unit tests (burst then 429, refill); new-account
   market caps; health endpoint reflects a stale worker (heartbeat > 5 min ->
   status degraded).
```
**TEST:** `make check`; then actually deploy to the VPS and run the Playwright smoke against production URL.
**PASS:** prod smoke green over HTTPS; `kill` the worker → /api/health flips to degraded within 5 min; backup script produces a restorable file (restore it into a scratch db and count tables). **This is the alpha gate: invite 20–50 players.**

---

## PROMPT 25 — OPTIONAL: LLM enrichment batch (flags on, budget capped)
```
Only after alpha is stable. All three are jobs/, all via gateway (R5), all
resumable and idempotent, all obey the daily budget.
1) jobs/enrich_bios.py — for AI citizens lacking persona_json['bio']: batch 25
   personas/call (tier S), prompt returns STRICT JSON array of one-line bios
   (<=120 chars, street register, no proper nouns beyond the given name);
   validate with pydantic, reject+retry batch once on invalid, then skip.
2) jobs/enrich_outcomes.py — for the 20 most-served text_keys (from
   served_lines), generate +10 variants each (tier S), enforce the style rules
   from Prompt 17 in the prompt, validate length/slots, insert + embed.
3) Turn on llm_digest_polish for 10% of users (flag config_json
   {"pct":10}, gateway respects it via hash(char_id)%100): measure
   digest->action rate delta in admin stats after 7 days. Keep only if it
   wins by >5 points.
4) tests (mock transport): JSON validation rejects malformed batch; budget
   stops mid-run cleanly and resumes; pct rollout hashing is stable per user.
```
**TEST:** `make check`; run each job with LLM_DAILY_BUDGET_USD=0.10 and watch it stop at the cap.
**PASS:** with flags ON the game is nicer; with flags OFF (or budget 0) the game is IDENTICAL in function. That property is the architecture working.

---
---

## Final audit checklist (run before inviting anyone)

- [ ] `grep -rn "import llm" agents/` returns nothing (and the AST test exists)
- [ ] With `LLM_PROVIDERS=""` and all flags off: full Playwright smoke passes — the game runs on **zero AI calls**
- [ ] `pytest -q` green; coverage on core/ ≥ 85% (`pytest --cov=core`)
- [ ] Text-key coverage test green (no action can emit flavorless output)
- [ ] Fresh phone playthrough: register → week-1 day-1 tasks → first fight, all ≤2 taps each, nothing broken
- [ ] Admin stats show worker lag < 2 min and AI events flowing
- [ ] Backup + restore rehearsed once for real

## Prompt order recap
Foundation 1–3 → Torn core 4–11 (**gate: 2 fun days**) → City alive 12–18 (**gate: revenge screenshot**) → Drama 19–24 (**gate: alpha invite**) → 25 optional.

*Pack v1.0 — keep it in docs/ next to the handbook; update prompts in place when reality disagrees with the spec, and note why in docs/tuning-log.md.*
