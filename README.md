# Livewire

[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![React](https://img.shields.io/badge/react-18.2-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)]()

> A browser-based text crime MMO in the spirit of Torn — except the city is populated by AI citizens who remember what you did to them, hold grudges, run businesses, fight wars, and make the world feel alive from the first day.

## Features

### Phase 0 + Phase 1 ✓

- **Authentication system** — Register, login, logout with session cookies
- **Crimes** — 18 crimes across 5 tiers, success chance based on skill, nerve cost, payouts, heat gain, jail risk
- **Gym** — Train strength, speed, defense, dexterity (energy-gated)
- **Jail & Hospital** — Bust out jailed players, status system (ok/jail/hospital)
- **Combat** — Attack other players (mug, hospitalize, or leave), PvP with stat-based odds
- **Banking** — Deposit/withdraw cash with 1.5% fee
- **Items** — 15+ items (weapons, armor, consumables) with shop, inventory, equip/unequip/use
- **Player Market** — List items for sale, buy from others, cancel listings, concurrent-safety guard
- **Jobs** — 5 jobs with daily pay and stat perks (Clinic Aide heals, repo grants speed, etc.)
- **XP & Levels** — Gain XP from crimes and combat, level up for higher bar caps
- **Heat System** — Heat decays over time; cross 40 for a shakedown (cash fine), cross 70 for a raid (cash loss + jail)
- **Bribe** — Pay to reduce heat ($100 per point)
- **Events Feed** — Real-time activity feed showing crimes, attacks, trades, level-ups, shakedowns, raids
- **Mobile-first UI** — 5-tab bottom navigation, every action reachable in ≤2 taps from home screen
- **Toast error handling** — User-friendly error messages for all game actions

### Phase 2 (In Progress)

- LLM-powered dialogue and world events
- AI citizen population (800+ personas)
- Tick engine for AI actions
- Targets ladder with new-player protection
- Grudge & revenge system
- Content bank (outcome text, retrieval-based)
- "While You Were Gone" digest

## Screenshots

| Home Screen | Crimes | Combat |
|---|---|---|
| ![Home](screenshots/home.png) | ![Crimes](screenshots/crimes.png) | ![Combat](screenshots/combat.png) |

| Market | Gym | City |
|---|---|---|
| ![Market](screenshots/market.png) | ![Gym](screenshots/gym.png) | ![City](screenshots/city.png) |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, SQLite |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, React Router |
| Auth | Session-based (itsdangerous signed cookies) |
| Testing | pytest, pytest-asyncio, Playwright |
| Code Quality | Ruff (linter + formatter) |
| CI | Makefile-based workflows |

## How to Run Locally

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm

### 1. Clone and install

```bash
git clone https://github.com/your-username/livewire.git
cd livewire

# Backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Frontend
cd web && npm install && cd ..
```

### 2. Set up environment

```bash
cp .env.example .env
# Edit .env with a random SECRET_KEY
```

### 3. Seed the database

```bash
make seed
```

This populates crimes, items, jobs, and feature flags.

### 4. Start the backend

```bash
make dev
```

API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 5. Start the frontend

In a separate terminal:

```bash
make web
```

Frontend runs at `http://localhost:5173` with API proxy to the backend.

### 6. Play

Open `http://localhost:5173`, register an account, and start your crime career.

### Run tests

```bash
make check        # Ruff + pytest (116 tests)
make e2e          # Playwright smoke test (requires backend + frontend running)
```

## Game Mechanics

### Bars (Regenerate Over Time)
- **Energy** — Used for gym training and combat. Regenerates 1 point per 5 minutes.
- **Nerve** — Used for committing crimes. Regenerates 1 point per 10 minutes.
- **Health** — Lost in combat. Regenerates 1 point per 3 minutes. If it hits 0, you're hospitalized.

### Crimes
18 crimes across 5 tiers. Higher tiers pay more but require more nerve and have lower base success. Your crime skill (gained from successful crimes) improves success rates.

### Combat
Attack other players with three choices:
- **Mug** — Steal their cash (up to a portion of their on-hand cash)
- **Hospitalize** — Send them to the hospital, gain notoriety
- **Leave** — Low-risk attack, gain XP with minimal consequences

### Items
- **Weapons** — Boost your attack power when equipped
- **Armor** — Reduce damage taken when equipped
- **Consumables** — Medkits (heal), Energy Drinks (restore energy), Adrenaline Shots (temporary buff)

### Player Market
List items for sale with a listing fee. Buy from other players. Cancel listings to return items to inventory.

### Jobs
Choose a job for daily income. Each job provides a unique perk:
- **Clinic Aide** — Restores health on collect
- **Repo Agent** — +speed per collect
- **Security Guard** — +defense per collect
- **Street Dealer** — +crime skill per collect
- **Escort** — +dexterity per collect

### Heat & Bribes
Committing crimes and winning attacks increases heat. Heat decays by 1 per hour.
- **Heat ≥ 40** — Trigger shakedown (5% cash fine, up to $500)
- **Heat ≥ 70** — Trigger raid (10% cash loss + 10 min jail)
- **Bribe** — Pay $100 per point to reduce heat instantly

### XP & Levels
Gain XP from crimes and combat. Level up every ~100 XP (scaling curve). Higher levels unlock larger energy/nerve/health caps.

### Events Feed
Every action writes to the events log. See what's happening in the city — crimes, attacks, trades, shakedowns, raids, level-ups, and more.

## Project Structure

```
livewire/
├── api/              # FastAPI routes (auth, crimes, combat, gym, items, market, jobs, heat, feed, jail)
│   ├── main.py       # App factory, CORS, router registration
│   ├── deps.py       # Dependency injection (get_db, get_current_character)
│   ├── auth.py       # Register, login, logout
│   ├── crimes.py     # List crimes, attempt crime
│   ├── combat.py     # Attack, bank deposit/withdraw
│   ├── gym.py        # Train stats
│   ├── items.py      # Shop, buy, inventory, equip/unequip/use
│   ├── market.py     # List, buy, cancel listings
│   ├── jobs.py       # List, select, collect job
│   ├── heat.py       # Bribe endpoint
│   ├── feed.py       # Activity feed
│   └── jail.py       # Jail list, bust out
├── core/             # Pure game logic functions
│   ├── crimes.py     # attempt_crime(), CrimeResult
│   ├── combat.py     # resolve_attack(), CombatResult
│   ├── items.py      # use_consumable(), ITEM_EFFECTS
│   ├── market.py     # calculate_fee()
│   ├── progression.py# xp_to_level()
│   ├── heat.py       # apply_heat_decay(), check_threshold(), bribe_cost()
│   ├── gym.py        # train()
│   ├── regen.py      # apply_regen(), max_bars()
│   ├── state.py      # CharacterState, load_character(), derive_status()
│   ├── exceptions.py # DomainError
│   └── event_weights.py  # Event weight table
├── models/
│   ├── db.py          # Engine, session factory, init_db()
│   └── tables.py      # All SQLAlchemy ORM models
├── jobs/
│   └── seed.py        # Database seeding (crimes, items, jobs, flags)
├── agents/            # AI citizen logic (Phase 2)
├── llm/               # LLM gateway (Phase 2)
├── tests/             # 116 pytest tests
├── web/               # React frontend
│   └── src/
│       ├── pages/     # Login, Home, Crimes, Gym, Fight, City, Market
│       ├── components/# BottomNav, Bars, HeatGauge, ActivityFeed
│       └── api.ts     # All API client methods
├── worker.py          # Background tick worker
├── Makefile           # dev, web, check, seed, e2e, clean
└── pyproject.toml     # Python project config
```

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new account |
| POST | /api/auth/login | Login |
| GET | /api/me | Current character state |
| GET | /api/crimes | List crimes |
| POST | /api/crimes/{id}/attempt | Attempt a crime |
| POST | /api/gym/train/{stat} | Train a stat |
| GET | /api/jail/list | List jailed players |
| POST | /api/jail/{id}/bust | Bust someone out |
| POST | /api/attack | Attack a target |
| POST | /api/bank/deposit | Deposit cash |
| POST | /api/bank/withdraw | Withdraw cash |
| GET | /api/shop | List shop items |
| POST | /api/shop/buy | Buy from shop |
| GET | /api/inventory | View inventory |
| POST | /api/inventory/{id}/equip | Equip item |
| POST | /api/inventory/{id}/unequip | Unequip item |
| POST | /api/inventory/{id}/use | Use consumable |
| POST | /api/market/list | List item for sale |
| GET | /api/market/my | My listings |
| GET | /api/market/{item_id} | Order book for item |
| POST | /api/market/buy/{id} | Buy a listing |
| POST | /api/market/cancel/{id} | Cancel listing |
| GET | /api/jobs | List jobs |
| POST | /api/jobs/select | Select a job |
| POST | /api/jobs/collect | Collect job pay |
| POST | /api/heat/bribe | Pay to reduce heat |
| GET | /api/feed | Activity feed |

## Design Philosophy

- **Server-authoritative** — The client never computes outcomes, timers, or money. All game logic lives in `core/` as pure functions.
- **RNG-injected** — Randomness is passed as a `random.Random` instance, never called at module level.
- **Event-sourced** — Every state-changing action writes exactly one row to the `events` table (append-only).
- **Mobile-first** — Every core action is reachable in ≤2 taps from the home screen.

## Contributing

This is a vibe-coded project. Contributions welcome via pull requests.

## License

MIT
