# LIVEWIRE — Phase 0: Walking Skeleton Design

**Date:** 2026-07-03
**Project:** Livewire (browser text crime MMO, Torn-style)
**Phase Goal:** A deployed URL where you can register, see bars regen, do one crime, train once.

---

## Approach

Follow the prompt pack (`docs/livewire-prompt-pack.md`, Prompts 1–3) sequentially: scaffold + models + seeds → auth + React shell → bars + regen + home screen. Each step has a TEST block gate — green before moving on.

---

## Section 1 — Repo Layout & Tech Stack

```
livewire/
  api/            # FastAPI routers: auth, character, crimes, gym
  core/           # Pure game logic functions (regen, crime, training)
  agents/         # Tick engine (empty until Phase 2)
  llm/            # LLM gateway (stub until Phase 2)
  models/         # SQLAlchemy tables + db.py
  web/            # React + Vite + TypeScript + Tailwind app
  jobs/           # seed.py, nightly tasks
  tests/          # pytest tests, conftest.py
  docs/           # handbook, prompt pack, specs, tuning log
```

| Layer | Choice |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Database | SQLAlchemy 2.x + SQLite (dev), Postgres later |
| Frontend | React + Vite + TypeScript + Tailwind, mobile-first |
| Auth | bcrypt + httpOnly session cookies (30-day) |
| Background | APScheduler (not used until Phase 2) |
| Server-authoritative | Client NEVER computes outcomes, timers, or money |
| Money | Integer whole dollars (not cents) |
| Bars | Lazy regen computed from `bars_updated_at` on read |

---

## Section 2 — Database Models & Seeds

All 17 tables defined in `models/tables.py`, created via `init_db()`:

- **users** — id, username (unique 3-20 chars `[a-z0-9_]`), pw_hash, email?, created_at, flags
- **characters** — One table for humans + AI (`is_ai` flag). Fields: id, user_id (nullable), name, level, xp, strength/speed/defense/dexterity, energy/nerve/health, bars_updated_at, cash (500 start), bank, heat, heat_updated_at, notoriety, job_id, faction_id, hospital_until, jail_until, crime_skill, persona_json, next_tick_at, created_at
- **items** — id, name, slot (weapon/armor/consumable), bonus, base_price, daily_cap
- **inventory** — id, char_id, item_id, qty, equipped
- **market_listings** — id, seller_id, item_id, price, qty, created_at
- **market_bands** — item_id (PK), floor, ceiling, mm_daily_cap
- **crimes** — id (string like 'crime_t1_a'), tier, name, nerve_cost, base_success, payout_min, payout_max
- **events** — id, ts, type, actor_id, target_id?, payload_json, weight, seen_by_target — append-only
- **nemesis** — char_id (PK), ai_id, stage, assigned_at, defeats
- **factions** — id, name, boss_id, is_ai_led, points
- **faction_members** — faction_id, char_id, rank
- **newspaper_issues** — id, date (unique), content_md
- **digests_cache** — char_id (PK), last_event_id, content, ts
- **llm_cache** — purpose, key_hash, output, ts — PK(purpose, key_hash)
- **llm_log** — id, ts, purpose, tier, tokens_in, tokens_out, cost_est
- **feature_flags** — name (PK), enabled, config_json
- **metrics_events** — id, ts, char_id?, name, props_json
- **content_lines** — id, kind, key, text, embedding?

Seeds (`jobs/seed.py`, idempotent):
- 4 feature flags: `llm_digest_polish`, `llm_newspaper_polish`, `llm_enrichment`, `talkdowns` — all default OFF
- 13 items from handbook Appendix B: 5 weapons (Knuckles +5, Blade +12, Pistol +22, SMG +35, Custom Rifle +50), 5 armors (Padded Jacket +5, Kevlar Vest +12, Tactical Vest +22, Composite Plate +35, Exo Weave +50), 3 consumables (Medkit 500/cap 5, Energy Drink 400/cap 2, Adrenaline 800/cap 1)
- 15 crimes across 5 tiers (tier 1: Pickpocket/Shoplift/Scam a Tourist, etc.)

---

## Section 3 — Auth, API & React Shell

### Auth
- POST /api/auth/register — creates user + character, sets httpOnly session cookie
- POST /api/auth/login, POST /api/auth/logout
- Duplicate username → 409 `{"error":"username taken","code":"USERNAME_TAKEN"}`
- Passwords via passlib bcrypt

### Lazy Regen
- `core/regen.apply_regen(bars, now, max)` — energy +5/10min, nerve +1/5min, health +1/3min
- Advances `bars_updated_at` by whole intervals consumed (no fractional loss)
- `core/regen.max_bars(level)` — energy = min(150, 100 + 5*(level-1)), nerve = min(25, 15 + (level-1)//2), health = 100

### Core Functions (pure)
- `core/state.load_character(session, id, now)` — reads row, applies regen, persists updated bars, returns CharacterState dataclass
- `core/crimes.attempt_crime(char, crime, rng, now)` — nerve check, success roll, payout, xp, event
- `core/gym.train(char, stat, rng, now)` — energy cost, stat gain with diminishing returns

### API Endpoints
- GET /api/me — character with regen applied
- GET /api/crimes — list crimes with current success %
- POST /api/crimes/{id}/attempt — execute crime
- POST /api/gym/train/{stat} — train a stat

### React Frontend
- Mobile-first, max-w-md centered column, dark theme
- Bottom nav: Home, Crimes, Fight, Market, City (placeholder icons)
- Login/Register as single page with tab toggle
- Home screen: character name + 3 bars with numeric x/y + live countdown
- Crimes screen: tier-grouped list with Attempt button
- Gym screen: stat training buttons

### Testing
- `tests/conftest.py` — in-memory SQLite session, seeded rng fixture (random.Random(42)), fixed now fixture, authed client fixture
- `make check` — ruff check + pytest -q
- Tests: regen table-driven cases (0 min, 9m59s, 25 min, huge elapsed, fractional carry), crime result determinism with seeded rng, auth flows (register, duplicate, login wrong pw, unauth access)

---

## Phase 0 Definition of Done

- [ ] `make check` green
- [ ] Register, login, see bars
- [ ] Do one crime (Pickpocket) — nerve deducted, cash +XP gained, event written
- [ ] Train Strength at gym — energy deducted, stat increases
- [ ] Bars regen correctly on reload
- [ ] Mobile-first UI works on phone screen
- [ ] Deployed on VPS behind Cloudflare, HTTPS
