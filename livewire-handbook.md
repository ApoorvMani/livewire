# PROJECT LIVEWIRE — Build Handbook
### A Torn-style text crime MMO where the city is actually alive

**Owner:** Apoorv · **Version:** 1.0 · **Status:** Pre-build
**Working title:** LIVEWIRE (placeholder — see §2 Theme)

This is the working handbook for vibe-coding the entire game with Claude Code / OpenCode. It contains the design, the numbers, the architecture, the build order, and example prompts for each phase. Treat it as a living document: update numbers after playtests, tick off phase checklists, and paste relevant sections into your coding agent's context when starting a phase.

---

## 0. The pitch

**One-liner:** A free, browser-based, text crime MMO in the spirit of Torn — except the city is populated by AI citizens who remember what you did to them, hold grudges, run businesses, fight wars, and make the world feel alive from the first day, even with 50 real players online.

**Why it can win where every Torn clone died:**
1. Torn clones die of empty-world syndrome at launch. Our AI population kills the cold-start problem.
2. Torn's #1 complaint is that new players can never catch up. Our AI ladder guarantees everyone a beatable rival.
3. Torn's content is fully wiki-solved. Our generated outcomes and world director keep the meta unsolvable.
4. Nobody in the market has shipped a persistent multiplayer crime MMO with an AI-simulated population (verified July 2026 — closest neighbors are single-player: Instantale, Wanderfolk, Suck Up!, or platforms: Voyage, wilds.ai, or social sims: Status).

**Design pillars (check every feature against these):**
- **P1 — One click, never an essay.** Players tap buttons and timers, like Torn. AI generates consequences, memory, and population — never mandatory conversation.
- **P2 — The city remembers you.** Every meaningful action is logged and comes back around: grudges, gossip, headlines, nemeses.
- **P3 — Always a rung to climb.** Matchmaking and the AI ladder guarantee a slightly-stronger rival at every level. No 5000-day wall.
- **P4 — AI is the design, not the dressing.** If removing the AI wouldn't break a feature, the feature doesn't need AI.
- **P5 — Free tier is the full game.** Monetize convenience and identity, never power. Don't strangle energy regen (Status got 1-starred for exactly this).

**Anti-scope (things we are NOT building, ever, for v1):**
- Real-time free-chat NPCs everywhere (cost bomb, jailbreak bait)
- Graphics beyond CSS/icons/avatars, 3D, maps with movement
- Mobile native apps before the web version proves retention (wrap later with Capacitor)
- Crypto/NFTs
- Voice anything
- Player-generated free text visible to other players at MVP (moderation burden) — profiles use dropdowns/presets first

---

## 1. Honesty policy (decide once, never violate)

The game world contains simulated citizens. We say so openly — in the FAQ, in the ToS, and (if we pick the synth theme) in the lore itself. What we never do is claim a specific AI character is a human, or pad "online now" counters with fake humans presented as real. The mystery of *which* citizen is simulated can be part of the fun; the existence of simulation is never hidden. This protects us legally (dark-pattern/deception rules), protects the community's trust (Torn players despise bots precisely because bots pretend), and it's simply the right call.

Rule of thumb: AI citizens are honest fiction, like NPCs always were — they just behave like players now.

---

## 2. Theme (open decision — pick before Phase 3 art/copy)

The mechanics below are theme-agnostic on purpose. Code names things generically (`character`, `crime`, `district`, `faction`) so the theme is a content layer you can swap.

| Option | What it looks like | Pros | Cons |
|---|---|---|---|
| **A. Gritty modern crime** | Pure Torn vibe. Muggings, docks, dive bars, cartels. | Proven appetite; nostalgia market from Torn/Mafia Wars refugees; easiest copywriting. | "Torn clone" accusations; AI citizens need a fig leaf. |
| **B. Near-future synth city** (recommended) | 2040s megacity. Licensed synthetic citizens live and work alongside humans. Neon, rain, ramen stalls, black-market chrome. | AI population is *diegetic* — the honesty policy becomes lore; unique marketing hook ("half this city is really AI"); room for signature mechanics later (synth-detection, memory hacking); visually distinct identity. | Slightly narrower nostalgia pull; needs a little more world-building copy. |
| **C. Indian underworld** | Mumbai/Delhi-inspired syndicates, hawala networks, local flavor. | Underserved theme; personal authenticity; strong differentiation. | Smaller initial English-market resonance; higher sensitivity/moderation care needed. |

**Recommendation:** B, with C's flavors folded in as one district/faction culture (a hawala-style money system is a genuinely great mechanic). B turns your biggest technical constraint into your identity. But A is the safe default if in doubt — decide by end of Phase 2.

**Name candidates:** Livewire, Static City, Gridlock, The Sprawl District, Neon Racket, Wiretown, Circuit City (check trademark + domain before attaching to anything public).

---

## 3. The player experience (design the minutes first)

### 3.1 The 5-minute session (the atom of the game)
1. Open the site → **"While You Were Gone"** digest (3–6 lines): what your crew earned, who hit you, what your nemesis did, one hook ("Rico got arrested. He knows about the warehouse job.")
2. Spend **nerve** on 2–4 crimes (tap, result text, money/XP).
3. Spend **energy**: train at gym OR attack a suggested target (the ladder shows 3 targets near your level).
4. Collect job pay / crew earnings. Maybe list an item on the market.
5. One decision hook waits: an offer, a threat, a newspaper mention. Accept/Decline.
6. Bars are empty → leave. Total time: 3–7 minutes. Everything meaningful fits a phone screen.

### 3.2 The daily loop
2–4 sessions/day (bars refill in ~3–4 h), one daily login reward, one newspaper issue, job pay once/day, crew report every session.

### 3.3 The weekly loop
Faction events, market cycles (AI market makers shift prices), world-director event (crackdown, shortage, festival), leaderboard reset for weekly boards.

### 3.4 Week-1 new player arc (retention lives or dies here)
| Day | What the game does |
|---|---|
| 1 | 60-second tutorial-by-doing: one crime, one gym session, one easy AI mugging victim (they always win this one). A generated contact ("the Fixer") messages them with a 3-step starter arc. Full bars refill instantly twice on day 1. |
| 2 | First "While You Were Gone" digest. The Fixer's arc step 2. An AI citizen retaliates *weakly* for day-1's mugging — player wins again, learns grudges exist. |
| 3 | **Nemesis assigned** (an AI citizen ~15% stronger). Nemesis mugs them once — first loss, with a taunt. The game immediately shows the path: "Train Strength. You're 2 sessions away from beating Dex 'Half-Smile' Marlow." |
| 4 | First faction invite (AI-led faction with 2–3 real players if any exist). Small faction perk unlocks. |
| 5 | First newspaper mention if they've done anything notable (the paper is generous to newbies by design). Share button. |
| 6 | Beat the nemesis for the first time → big dopamine, loot, headline. New nemesis seeded at +15%. |
| 7 | Day-7 reward chest + a one-screen "your first week" recap (stats gained, money made, enemies created) — shareable image. |

New-player protection: for the first 7 days, players lose max 5% cash-on-hand when mugged, hospital timers are halved, and AI aggression against them is capped at 2 attacks/day.

---

## 4. Core game systems (the boring-but-vital Torn core)

Build this COMPLETELY before touching the AI layer. If this loop isn't fun with zero AI, stop and fix it. All numbers below are starting values — tune after playtests, don't debate them in advance.

### 4.1 Bars
| Bar | Max (start) | Regen | Used for |
|---|---|---|---|
| Energy | 100 | +5 / 10 min (full in ~3.3 h) | Gym training, attacks |
| Nerve | 15 | +1 / 5 min (full in 75 min) | Crimes |
| Health | 100 | +1 / 3 min, instant on hospital exit | Combat pool |

Max bar sizes grow slightly with level (Energy +5/level up to 150; Nerve +1/2 levels up to 25). Daily login gives one 25% energy refill token (stackable to 3) — generous free energy is a pillar.

### 4.2 Stats and training
Four battle stats: **Strength** (damage), **Speed** (hit first / flee), **Defense** (damage taken), **Dexterity** (dodge/crit). Gym: spend 5 energy per session on one stat.

Gain per session = `base_gain * gym_tier * diminishing(stat_total)` where `diminishing = 1 / (1 + stat_total/5000)`. This is the anti-Torn move: soft diminishing returns mean a 2-year player is maybe 5–8× a 3-month player, not 500×. Veterans stay ahead on breadth (money, items, property, faction power), not on an unbeatable stat wall. Gym tiers unlock by total stats + cash fee (money sink #1).

### 4.3 Crimes
15 crimes across 5 tiers. Success = `clamp(5%, 95%, base + crime_skill*0.5% − tier_penalty)`. Each attempt raises hidden `crime_skill` (even on failure, +0.2 vs +1.0 on success). Failure at tier 3+ risks **jail** (10–45 min timer; other players can bust you out — social hook).

| Tier | Nerve | Examples (theme-skinnable) | Payout range | Base success |
|---|---|---|---|---|
| 1 | 2 | Pickpocket, shoplift, scam a tourist | $50–150 | 85% |
| 2 | 3 | Mug a drunk, boost a bike, sell knock-offs | $150–400 | 70% |
| 3 | 5 | Burgle a flat, hack a terminal, chop-shop run | $400–1,200 | 55% |
| 4 | 8 | Armed robbery, data heist, protection racket | $1,200–4,000 | 40% |
| 5 | 12 | Bank job, syndicate hit, warehouse raid | $4,000–15,000 | 25% |

Every crime outcome renders as a generated micro-story line (see A6) instead of a static string.

### 4.4 Combat (attacks)
One-tap attack from a target's profile or the ladder. Resolution is instant (no turn UI at MVP — Torn's turn viewer is a growth feature).

```
attack_power  = STR*1.0 + SPD*0.4 + weapon_atk
defense_power = DEF*1.0 + DEX*0.4 + armor_def
p_win = sigmoid((attack_power − defense_power) / scale)   # scale ≈ 0.25 * avg(power)
```
Clamp p_win to [10%, 90%] so upsets always possible. Winner picks (or auto-picks): **Mug** (steal 3–10% of target's cash-on-hand), **Hospitalize** (target in hospital 15–60 min, you gain XP + notoriety), **Leave** (XP only, less heat). Loser goes to hospital 10–30 min. Attacking costs 25 energy. Banked cash can't be mugged (bank has a small deposit fee — money sink #2).

### 4.5 Economy
- **Faucets:** crime payouts, job daily pay, crew earnings, mugging (transfer, not creation), market sales.
- **Sinks:** gym tier fees, bank fees, item shop (weapons/armor tiers 1–5, consumables: medkits, energy drinks with daily cap), market listing fee 2%, hospital "skip timer" cash option, property (growth phase), crew wages (growth phase).
- **Item market:** player+AI listings, lowest-ask order book per item. AI market makers (A11) keep every item liquid inside a price band.
- **Jobs:** pick one of 5 jobs (Courier, Bouncer, Clinic Aide, Mechanic, Junior Fixer). Daily pay + one tiny stat perk. One tap/day. Companies/player-owned jobs = growth phase.

### 4.6 Levels, XP, notoriety, heat
- **XP** from crimes/attacks → **Level** (cosmetic gates + bar growth + ladder banding).
- **Notoriety** = public fame score. Earned by wins, headlines, high-tier crimes. Unlocks titles, better contacts, faction rank eligibility. It's the "number that goes up" for bragging.
- **Heat** = police attention, 0–100, decays 1/h. High-tier crimes and hospitalizations add heat. Thresholds: 40 = random shakedown events (small fines), 70 = raid risk (lose stash cash %, short lockup), 90 = the Director may target you personally. Lying low or bribes (money sink #3) reduce heat. Heat is the risk axis that makes the crime loop a decision instead of a button.

---

## 5. The AI layer (the differentiators)

For every feature: what it does, how it works, when an LLM is actually called, which model tier, and its phase. **Tier S** = small/cheap (Gemini Flash-class, Groq Llama-class, Haiku-class). **Tier M** = mid (Sonnet-class) — used rarely. Every LLM call goes through one function (`llm.generate(purpose, prompt, tier, cache_key)`) with caching, logging, per-feature kill switches, and a per-day budget cap. That module is the only place API keys live.

### A1 — AI citizen population (Phase 2) ★ the foundation
**What:** 500–2,000 simulated citizens with profiles, stats, schedules, jobs, factions, market activity. They play through the *same server API as humans* — one `characters` table, `is_ai` flag, zero special-cased game logic.

**Persona schema (generated once per citizen, batched 25/call, Tier S):**
```json
{
  "name": "Dex 'Half-Smile' Marlow",
  "archetype": "bruiser",        // 10 archetypes, see Appendix D
  "traits": ["vindictive", "lazy", "flashy"],
  "bio": "one-line backstory",
  "schedule": {"active_hours": [7,9,12,19,22], "days_off": [0]},
  "aggression": 0.7, "greed": 0.5, "loyalty": 0.3, "risk": 0.8,
  "stat_curve": "combat_heavy",  // governs training choices
  "wealth_curve": "hand_to_mouth",
  "avatar_seed": 8123
}
```
**Behavior:** utility-based decision table — **no LLM per action** (see §6 tick engine). LLM is used only at creation, and occasionally for flavor (a market listing note, a profile status line) — cached and rare.
**Population lifecycle:** launch with ~800. Target ratio ≈ 8–15 AI per human early, decaying as humans grow (at 5k humans, ~1:1; at 50k humans, AI are mostly specialists: market makers, faction bosses, nemeses). Citizens "move away" (retire) and new ones arrive weekly so the roster breathes.
**Cost:** creation ≈ 800 citizens / 25 per call = 32 Tier-S calls, one-off. Runtime ≈ $0.

### A2 — Ladder of rivals / matchmaking (Phase 2)
**What:** the Targets screen always shows 5 suggestions: 2 slightly weaker, 2 near-equal, 1 slightly stronger (mix of AI and humans, humans only within ±1 level band and not under new-player protection).
**How:** SQL over stat totals + online-recency + protection flags. AI targets at your band are tuned to lose ≈55% of the time to you early (their effective power sampled from a band below yours). Pure logic, zero LLM.
**Why it matters:** this is the direct fix for Torn's "5000-day Joe" complaint. Nobody ever opens the game and sees only unbeatable opponents.

### A3 — "While You Were Gone" digest (Phase 2) ★ highest value per token
**What:** the login screen narrativizes what happened to *you* since last session.
**How:** query `events` where you're actor/target since `last_seen`, rank by weight, take top 5, one Tier-S call turns them into 3–6 punchy lines (strict system prompt: no questions, no fluff, ≤90 words, end with the hook line). Cache per (user, last_event_id) so refreshes are free. If zero events: template lines, no LLM call.
**Cost:** ≤1 Tier-S call per player per day (~250 output tokens). At 10k DAU ≈ 10k calls/day ≈ single-digit $/day on cheap tiers. This is the feature that makes the game "feel aware" — the exact loop Status's addictiveness analysis identified.

### A4 — Grudge & memory system (Phase 2)
**What:** every AI citizen remembers what you did to them and responds later.
**How:** `events` log is the single source of truth (see Appendix E). Grudge score per (ai_citizen → character) = Σ event weights with time decay (half-life 7 days). Mugging = +8, hospitalizing = +15, busting them from jail = −10 (yes, kindness registers). When grudge > threshold and the tick engine rolls revenge, a scheduler looks for *your vulnerable moments* — hospital exit, low health, market cash-out — and strikes then, with a one-line generated taunt (Tier S, cached per grudge-tier).
**Why:** memory + accountability is the single most-requested AI behavior across every game studied (Wanderfolk's top-praised feature; Status's top complaint is its absence).

### A5 — Nemesis system (Phase 3) ★ the headline feature
**What:** every player has a personal recurring antagonist.
**How:** assignment day 3 (AI citizen ~15% stronger, archetype countering your playstyle). Escalation ladder: taunt → mug → steal a market listing → hospitalize → headline insult in the newspaper. Mercy rules: never attacks the same player >2×/day, never within protection, backs off 48 h after hospitalizing you. When you finally beat them 3 times: they "retire" with a generated farewell (loot + headline + achievement), a new nemesis seeds at +15%. All logic; LLM writes only the taunts and the retirement note.
**Marketing note:** this is the clip/screenshot generator. "My nemesis waited for me outside the hospital" is the tweet that sells the game.

### A6 — Generated outcome text (Phase 2)
**What:** crime/attack results are one-line micro-stories, not recycled strings.
**How:** pre-generate 40 variants per (crime, outcome) pair offline into an `outcome_texts` table (~15 crimes × 3 outcomes × 40 = 1,800 rows, a few dozen batched Tier-S calls, one-off). At runtime: random pick + variable substitution ({name}, {district}, {loot}). A nightly job tops up variants for the most-seen pairs. Runtime LLM cost: zero.

### A7 — The daily newspaper (Phase 3)
**What:** one issue/day reporting *real* events: biggest heist, top chain, market swings, faction moves, notable newbie, nemesis drama. Personal mentions get a share button (og-image card with the headline).
**How:** nightly job aggregates top-weighted events → 1 Tier-M call (quality matters here, it's public-facing) → stored issue. Personal-mention detection = simple name match on the issue + your events.
**Cost:** 1 call/day total. The cheapest viral loop you will ever build.

### A8 — Heat & the police AI (Phase 3)
Mechanics in §4.6. The "police" is not an agent — it's threshold logic + event templates. The world director (A12) can raise city-wide heat sensitivity for a week ("crackdown") as a meta event.

### A9 — AI crew management (Phase 4)
**What:** hire AI specialists (Scout, Pickpocket, Dealer, Muscle, Fence — one slot free, more via progression, +1 purchasable capped at 2 paid). Assign via dropdown (rob district X / guard me / work the market). They act on the hourly tick; results appear in your digest. Wages = money sink.
**How:** same tick engine, crew members are citizens with an `employer_id`. Outcomes are stat rolls; flavor from the outcome-text bank.

### A10 — Talk-your-way-out encounters (Phase 5, feature-flagged experiment)
**What:** the ONE place free text exists. Optional, rare, high-stakes 5-turn scenes: talk down a cop at heat 70+, con a fence for +20% price, bluff your nemesis. Costs 5 nerve to attempt.
**How:** Tier-S conversation with a strict system prompt (persona + hidden pass conditions + contradiction tracking); a final Tier-S "judge" call scores pass/fail against a rubric. Hard caps: 5 turns, 60 tokens/turn out, 3 attempts/day/player, profanity/injection filter on input, and the encounter NPC knows nothing about other players (no data to leak).
**Security note (your home turf):** treat player input as hostile. Delimit it, instruct the model that the delimited block is untrusted, validate the judge's output schema, and log every encounter for audit. If abuse cost/moderation exceeds fun, kill the flag — the game loses nothing.

### A11 — AI market makers (Phase 4, sleeper-critical)
**What:** 5–10 trader citizens per item category who buy below band-floor and sell above band-ceiling.
**How:** config table `market_bands(item, floor, ceiling, max_daily_volume)`. Pure logic on the tick. Solves dead-market liquidity AND gives you a macro-economy tuning knob (widen bands = more player-driven prices as population grows). Zero LLM.

### A12 — World director (Phase 4)
**What:** one weekly batch job that reads KPIs (money supply growth, crime success rates, market indices, PvP volume, retention) and picks 1–2 events from a hand-authored menu: police crackdown (+heat sensitivity), supply shortage (item X band up 40%), festival (+happy/energy), gang war (2 AI factions fight, players pick sides for payouts), amnesty (jail timers halved).
**How:** the *selection* can be a Tier-M call with the KPI summary (or plain rules at first); the *events* are pre-built and parameterized. Announced via the newspaper. This keeps the meta from being solved and gives the game a heartbeat.

### A13 — AI faction bosses (Phase 4)
**What:** 4–6 factions led by persistent AI bosses with personalities. They recruit (auto-invite promising players), declare rivalries, run weekly territory pushes (a simple points contest), and — critically — **yield**: when a human member out-earns the boss's leadership score for 2 weeks, the boss "steps down" to advisor and the human takes over. AI scaffolds the social layer, then hands it to humans (Pillar: AI is scaffolding).
**How:** weekly faction tick (one Tier-S call per faction for the boss's "communiqué" — 6 calls/week), everything else is points math.

---

## 6. The tick engine (the heart — keep it boring)

One background worker. No frameworks, no LangGraph, no message queues at MVP. You've built harder orchestrators (AutoRedTeam) — this is simpler because agents don't reason, they roll dice against personality weights.

```python
# worker.py — runs alongside the API (APScheduler), every 5 minutes
def tick():
    now = utcnow()
    citizens = db.due_citizens(now)          # schedule window + per-citizen jitter
    for c in citizens:
        action = pick_action(c)              # utility table below
        perform(action, c)                   # SAME functions the human API calls
        schedule_next(c, now)                # next act in 20–90 min, persona-based

def pick_action(c):
    w = base_weights[c.archetype]            # e.g. bruiser: attack .35, train .3, crime .2 ...
    w = adjust(w, c)                         # low cash -> crime up; grudge hot -> revenge up;
                                             # heat high -> lie low; employer order -> obey
    return weighted_choice(w)
```

Action menu: `train, crime, attack(target), revenge(grudge_target), trade(list/buy), deposit, rest, socialize(join faction / bust jail)`. Revenge target selection = highest grudge with a vulnerability window open (A4).

**Scale math:** 2,000 citizens × 1 action / 30–60 min ≈ 0.5–1.1 actions/sec peak. SQLite handles this in dev; Postgres yawns at it in prod. **LLM calls inside the tick loop: zero.** That single sentence is the whole cost strategy.

### 6.1 LLM budget model (estimates — verify against current pricing before launch)

| Feature | Calls | Tier | 1k DAU /day | 10k DAU /day | 100k DAU /day |
|---|---|---|---|---|---|
| Digest (A3) | 1/player/day | S | 1k | 10k | 100k |
| Taunts/flavor (A4/A5) | cached, ~0.2/player/day | S | 200 | 2k | 20k |
| Newspaper (A7) | 1/day | M | 1 | 1 | 1 |
| Persona/outcome top-ups | batched nightly | S | ~20 | ~50 | ~200 |
| Faction communiqués (A13) | 6/week | S | ~1 | ~1 | ~1 |
| Talk-downs (A10, flagged) | ≤3/player/day opt-in | S | small | capped | capped |

Order of magnitude at cheap-tier pricing (fractions of a dollar per million tokens): **1k DAU ≈ pocket change; 10k DAU ≈ a few $/day; 100k DAU ≈ tens of $/day** — assuming caching works and nothing chatty ships. Build the per-feature kill switches and a daily budget cap into the `llm` module from day one; if spend spikes, features degrade to templates instead of taking the game down.

Dev: your existing free-tier cascade (Gemini/Groq/Cerebras/Mistral) is fine. Production: free tiers violate ToS at scale and will rate-limit you mid-launch — budget for one paid cheap-tier provider + one fallback.

---

## 7. Tech stack (boring on purpose — you know all of this already)

| Layer | Choice | Why |
|---|---|---|
| Backend | **Python + FastAPI** | Your ResearchPilot stack; async fits timers. |
| DB | **SQLite (dev) → Postgres (prod)** via SQLAlchemy | One `DATABASE_URL` swap. |
| Background work | **APScheduler** in a second process | Ticks, regen sweep, nightly jobs. Celery only if you ever outgrow it. |
| Frontend | **React + Vite + Tailwind**, mobile-first | Your stack. Server is the only source of truth; the client renders state and posts actions. |
| Auth | Username/password (bcrypt) + httpOnly session cookie; email optional at signup | Low friction; add OAuth later. |
| LLM | Single `llm.py` gateway: cascade, cache table, purpose logging, kill switches, budget cap | Only file with keys. Langfuse optional (you know it). |
| Hosting | 1 VPS (DigitalOcean via GitHub Student Pack credit, or Hetzner ~€5) + Cloudflare free tier in front | API + worker + Postgres on one box until ~5k DAU. |
| Assets | Icon set + procedural avatars (e.g. DiceBear-style seeded avatars) | No artists needed for MVP. |

**Repo layout:**
```
livewire/
  api/            # FastAPI routers: auth, character, crimes, combat, market, faction, feed
  core/           # game logic (pure functions!): combat.py, crimes.py, economy.py, regen.py
  agents/         # tick.py, utility.py, personas.py, grudges.py, nemesis.py, director.py
  llm/            # gateway.py, prompts/, cache
  models/         # SQLAlchemy tables
  web/            # React app
  jobs/           # nightly: newspaper.py, outcome_topup.py, population.py
  tests/          # core/ gets real tests; the rest gets smoke tests
  docs/           # THIS handbook + tuning-log.md
```
Keep `core/` as pure functions (state in, state out). It makes vibe-coded logic testable, and both humans (via api/) and AI citizens (via agents/) call the same core — that's what keeps the world consistent.

### 7.1 Security & anti-cheat basics (non-negotiable, and your CV candy)
- Server authoritative for everything: bars, timers, money, RNG. The client never computes an outcome.
- Every action endpoint validates cost + cooldown server-side; per-account and per-IP rate limits.
- Append-only `events` log doubles as your audit trail — you get cheat forensics for free.
- Parameterized queries only; never build SQL or shell from user input.
- LLM hygiene: user-controlled strings (names, presets) are delimited as untrusted data in every prompt; model output is treated as display text only — never parsed into game effects except through strict schema validation (A10 judge). Log every prompt/response purpose-tagged.
- Multi-account is THE cheat in this genre (self-mugging mules). Mitigate at MVP: same-IP transfer caps, new-account trade limits (<7 days can't send money/items), flag rings via the events log. Don't over-build; just log enough to catch it later.
- Secrets in env only; weekly `pg_dump` to object storage; feature flags table from day one.

---

## 8. Build phases

Each phase has a goal, a checklist (definition of done), and a starter prompt for Claude Code. Paste the prompt plus the relevant handbook sections into the agent. Work feature-by-feature; commit when each checklist line passes.

### Phase 0 — Walking skeleton (weekend 1)
**Goal:** a deployed URL where you can register, see bars regen, do one crime, train once.
- [ ] Repo scaffold per §7; FastAPI + SQLite; React shell with login + one game screen
- [ ] `characters` table + bars + lazy regen (compute from `last_update` on read — no cron needed for bars)
- [ ] One crime (tier 1) end-to-end: nerve check → RNG → payout → event row
- [ ] Gym: one stat trainable
- [ ] Deployed on the VPS behind Cloudflare, HTTPS
**Prompt:** *"Read docs/handbook §4 and §7. Scaffold the repo exactly per the layout. Implement characters with energy/nerve/health using lazy regen computed from last_update. Implement crime 'Pickpocket' and gym training for Strength as pure functions in core/ with FastAPI routes and minimal React screens. Server-authoritative; write pytest tests for regen math and crime resolution."*

### Phase 1 — The Torn core, complete-but-small (weeks 1–2)
**Goal:** the game is a real (if quiet) Torn-like for a solo human.
- [ ] All 15 crimes (§4.3 table), crime_skill progression, jail + bust-out
- [ ] Combat per §4.4 with mug/hospitalize/leave, hospital timers, banking + fees
- [ ] Items: 5 weapons, 5 armors, 3 consumables; inventory; equip
- [ ] Market: list/buy with 2% fee; order-book per item
- [ ] Jobs (5), daily pay; levels/XP; heat meter with 40/70/90 thresholds
- [ ] Mobile-first UI pass: every action reachable in ≤2 taps
**Definition of done:** you personally enjoy two full days of play with bars as the only limit.

### Phase 2 — The city comes alive (weeks 3–4) ★ the magic milestone
**Goal:** log in and the world moved without you.
- [ ] `is_ai` citizens play through core/ via the tick engine (§6); 800 personas generated (A1)
- [ ] Targets ladder (A2) with new-player protection rules (§3.4)
- [ ] Events log finalized (Appendix E); grudge scores + revenge scheduling (A4)
- [ ] While-You-Were-Gone digest (A3) with cache + kill switch
- [ ] Outcome text bank generated and wired (A6)
- [ ] Tuning pass: AI mug/attack frequency feels alive, not abusive (protection caps hold)
**Prompt:** *"Read handbook §5 A1–A4, A6 and §6. Implement agents/tick.py with APScheduler: due-citizen selection, utility-based pick_action per archetype weights in Appendix D, executing ONLY core/ functions. No LLM calls in the tick loop. Then implement llm/gateway.py with provider cascade, sqlite cache, purpose logging, per-feature kill switches, and a daily budget cap; use it for batched persona generation and the digest."*

### Phase 3 — Identity & drama (weeks 5–6) → **closed alpha**
**Goal:** the features people screenshot.
- [ ] Nemesis system (A5) full ladder + mercy rules + retirement
- [ ] Daily newspaper (A7) + personal-mention share cards
- [ ] Week-1 arc scripted (§3.4): Fixer contact, day-3 nemesis, day-7 recap
- [ ] Heat events (shakedown/raid) + bribe sink
- [ ] Daily login rewards; achievements v1; leaderboards (weekly + all-time, AI marked with a subtle badge)
- [ ] Onboarding polish; FAQ incl. honesty policy (§1)
- [ ] **Alpha: 20–50 players** (friends, 1–2 subreddits like r/incremental_games / r/WebGames / Torn-adjacent Discords). Instrument everything (§10).
**Launch gate:** D1 ≥ 30% and 3+ unprompted "is Dex a real person?" messages. That question is product-market fit.

### Phase 4 — Growth systems (months 2–3)
- [ ] Human factions (create/join, bank, chat via preset+emote first; free chat only with moderation plan)
- [ ] AI faction bosses + yield mechanic (A13); weekly territory contest
- [ ] Market makers (A11) + market_bands config; crews (A9) with wages
- [ ] World director (A12) with 5 authored events; property v1 (regen perks, big sink)
- [ ] Postgres migration; worker split to its own process; backups verified
- [ ] **Open beta + monetization ON (§9)**

### Phase 5 — Scale & experiments (month 3+)
- [ ] Talk-downs (A10) behind flag for 10% of users; measure fun vs abuse vs cost
- [ ] Capacitor mobile wrapper + push notifications ("Your nemesis just landed in your district")
- [ ] Seasonal event #1 with limited cosmetics; referral rewards
- [ ] Perf: hot-path caching, read replicas only if metrics demand

---

## 9. Monetization (fair F2P)

Free = full game, forever. Paying buys convenience and identity, capped so whales can't buy the ladder.

| Product | Price (test) | Cap / guardrail |
|---|---|---|
| Energy/Nerve refill | $0.99–1.99 | Max 2/day purchasable; free daily token exists |
| Citizen+ subscription | $4.99/mo | Queue slots (train while away), stat history, newspaper archive, name color, +1 market slot. Zero combat power. |
| Cosmetics | $1–5 | Avatar frames, profile themes, title colors |
| Extra AI crew slot | $2.99 one-time | Max +2 paid; crew capped so paid crews ≈ +10–15% idle income, not PvP power |
| Season pass (Phase 5) | $4.99 | Cosmetic track + refill tokens |

Rough viability: browser-MMO benchmarks suggest ~2–5% payer conversion; at 10k DAU and ~$0.03–0.08 ARPDAU that's ~$300–800/day potential against single-digit $/day AI costs and ~$20–50/mo servers. Torn sustains ~$80k/mo on this exact fairness model — the model is proven; execution is the variable.

Never: loot boxes, pay-to-attack, paid stat gains, energy prices that make free feel broken.

---

## 10. Metrics (instrument in Phase 3, judge in alpha)

Log from day one into `metrics_events`: signup, tutorial steps, session start/end, crime, attack, digest viewed, share clicked, purchase. Targets for a text MMO:

| Metric | OK | Good | Great |
|---|---|---|---|
| D1 retention | 30% | 40% | 50%+ |
| D7 | 12% | 18% | 25%+ |
| D30 | 6% | 10% | 15%+ |
| Sessions/day (active) | 2 | 3 | 4+ |
| Digest→action rate | 50% | 70% | 85% |
| Share rate (newspaper mention) | 2% | 5% | 10% |

The single question to ask every alpha tester: "which citizen do you hate?" If they name a name instantly, the AI layer works.

---

## 11. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Core loop is boring without AI | Phase 1 gate: don't proceed until YOU play it 2 days happily. |
| AI citizens feel botty | Variance in schedules/typos-free-but-flawed behavior (lazy days, dumb trades), mystery + subtle badge only on leaderboards, diegetic framing if theme B. |
| LLM cost spike | Kill switches + budget cap degrade to templates; nothing user-facing breaks. |
| Solo scope creep | Phase gates + Anti-scope list (§0). New ideas go to docs/icebox.md, not the sprint. |
| "Torn clone" backlash | Distinct theme/name, original headline systems (nemesis, digest, newspaper), never copy Torn text/assets/UI. Mechanics genres aren't protectable; expression is — write everything fresh. |
| Multi-account abuse | §7.1 caps + events forensics; tighten post-alpha. |
| Free-text abuse (A10/chat) | Feature-flagged, capped, filtered, logged; presets-first for social. |
| Burnout | The alpha gate is 6 weeks of work, not 6 months. Ship the small thing. |

---

## Appendix A — Starter crime list
Use §4.3 tiers; name 3 crimes per tier in your chosen theme. Keep IDs stable (`crime_t1_a`...) so theme re-skins are content-only.

## Appendix B — Starter items
Weapons: Knuckles(+5), Blade(+12), Pistol(+22), SMG(+35), Custom Rifle(+50). Armor: Padded Jacket(+5), Kevlar Vest(+12), Tactical Vest(+22), Composite Plate(+35), Exo Weave(+50). Consumables: Medkit (heal 40, 5/day), Energy Drink (+25 energy, 2/day), Adrenaline (+10% attack 1h, 1/day). Shop prices ≈ 100× their bonus; market will find real prices.

## Appendix C — Combat & crime constants (tuning-log these)
`sigmoid_scale = 0.25*avg_power · p_win clamp [.10,.90] · mug 3–10% cash · hospital 10–60m · attack cost 25E · train cost 5E · diminishing k = 5000 · heat: T4 crime +6, T5 +10, hospitalize +8, decay 1/h · bank fee 1.5% · market fee 2%`

## Appendix D — Citizen archetypes & base utility weights
| Archetype | train | crime | attack | trade | rest/social |
|---|---|---|---|---|---|
| Bruiser | .30 | .15 | .35 | .05 | .15 |
| Hustler | .10 | .40 | .10 | .30 | .10 |
| Ghost (stealth crimes) | .15 | .45 | .10 | .10 | .20 |
| Trader | .05 | .10 | .05 | .60 | .20 |
| Climber (status-chaser) | .30 | .25 | .20 | .10 | .15 |
| Loyalist (faction-first) | .20 | .20 | .20 | .10 | .30 |
| Wildcard | random walk between rows | | | | |
| Slumlord (property, ph4) | .10 | .15 | .05 | .45 | .25 |
| Enforcer (revenge-heavy) | .25 | .10 | .40 | .05 | .20 |
| Drifter (low activity) | .15 | .25 | .10 | .10 | .40 |
Modifiers: cash < rent → crime +.2; grudge hot → attack becomes revenge; heat > 60 → crime −.2 rest +.2; employer order overrides.

## Appendix E — Database sketch (core tables)
```
users(id, username, pw_hash, email?, created_at, flags)
characters(id, user_id?, is_ai, name, level, xp, str, spd, def, dex,
           energy, nerve, health, bars_updated_at, cash, bank,
           heat, notoriety, job_id, faction_id, hospital_until, jail_until,
           persona_json?, next_tick_at?)          -- humans and AI in ONE table
items(id, slot, bonus, base_price) · inventory(char_id, item_id, qty, equipped)
market_listings(id, seller_id, item_id, price, qty, created_at)
market_bands(item_id, floor, ceiling, mm_daily_cap)
crimes(id, tier, nerve_cost, base_success, payout_min, payout_max)
events(id, ts, type, actor_id, target_id?, payload_json, weight, seen_by_target)
grudges = view/materialization over events (decayed sum per pair)
nemesis(char_id, ai_id, stage, assigned_at, defeats)
factions(id, name, boss_id, is_ai_led, points) · faction_members(faction_id, char_id, rank)
newspaper_issues(id, date, content_md) · digests_cache(char_id, last_event_id, content, ts)
llm_cache(purpose, key_hash, output, ts) · llm_log(ts, purpose, tier, tokens_in, tokens_out, cost_est)
feature_flags(name, enabled, config_json) · metrics_events(ts, char_id?, name, props_json)
```

## Appendix F — Prompt style for LLM features (paste into llm/prompts/)
Rules that keep Tier-S output good: give the model 3 example outputs in the exact voice; hard word caps; forbid questions and emojis; instruct "second person, past tense, street register, no proper nouns except the ones provided"; wrap all user/world data in `<data>` tags declared untrusted; require plain text (or a JSON schema for judges) and validate before display.

---

*End of handbook v1.0. Next revision after Phase 1 playtest: update Appendix C with real tuning values and log every change in docs/tuning-log.md.*
