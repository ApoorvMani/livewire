from models.tables import Crime, Item, FeatureFlag, Job
from models.db import engine, init_db
from sqlalchemy.orm import Session


def seed_crimes(session: Session):
    crimes = [
        {
            "id": "crime_t1_a",
            "tier": 1,
            "name": "Pickpocket",
            "nerve_cost": 2,
            "base_success": 0.85,
            "payout_min": 50,
            "payout_max": 150,
        },
        {
            "id": "crime_t1_b",
            "tier": 1,
            "name": "Shoplift",
            "nerve_cost": 2,
            "base_success": 0.85,
            "payout_min": 60,
            "payout_max": 140,
        },
        {
            "id": "crime_t1_c",
            "tier": 1,
            "name": "Scam a Tourist",
            "nerve_cost": 2,
            "base_success": 0.85,
            "payout_min": 70,
            "payout_max": 150,
        },
        {
            "id": "crime_t2_a",
            "tier": 2,
            "name": "Mug a Drunk",
            "nerve_cost": 3,
            "base_success": 0.70,
            "payout_min": 150,
            "payout_max": 400,
        },
        {
            "id": "crime_t2_b",
            "tier": 2,
            "name": "Boost a Bike",
            "nerve_cost": 3,
            "base_success": 0.70,
            "payout_min": 180,
            "payout_max": 380,
        },
        {
            "id": "crime_t2_c",
            "tier": 2,
            "name": "Sell Knock-offs",
            "nerve_cost": 3,
            "base_success": 0.70,
            "payout_min": 160,
            "payout_max": 400,
        },
        {
            "id": "crime_t3_a",
            "tier": 3,
            "name": "Burgle a Flat",
            "nerve_cost": 5,
            "base_success": 0.55,
            "payout_min": 400,
            "payout_max": 1200,
        },
        {
            "id": "crime_t3_b",
            "tier": 3,
            "name": "Hack a Terminal",
            "nerve_cost": 5,
            "base_success": 0.55,
            "payout_min": 450,
            "payout_max": 1150,
        },
        {
            "id": "crime_t3_c",
            "tier": 3,
            "name": "Chop-shop Run",
            "nerve_cost": 5,
            "base_success": 0.55,
            "payout_min": 420,
            "payout_max": 1200,
        },
        {
            "id": "crime_t4_a",
            "tier": 4,
            "name": "Armed Robbery",
            "nerve_cost": 8,
            "base_success": 0.40,
            "payout_min": 1200,
            "payout_max": 4000,
        },
        {
            "id": "crime_t4_b",
            "tier": 4,
            "name": "Data Heist",
            "nerve_cost": 8,
            "base_success": 0.40,
            "payout_min": 1300,
            "payout_max": 3800,
        },
        {
            "id": "crime_t4_c",
            "tier": 4,
            "name": "Protection Racket",
            "nerve_cost": 8,
            "base_success": 0.40,
            "payout_min": 1250,
            "payout_max": 4000,
        },
        {
            "id": "crime_t5_a",
            "tier": 5,
            "name": "Bank Job",
            "nerve_cost": 12,
            "base_success": 0.25,
            "payout_min": 4000,
            "payout_max": 15000,
        },
        {
            "id": "crime_t5_b",
            "tier": 5,
            "name": "Syndicate Hit",
            "nerve_cost": 12,
            "base_success": 0.25,
            "payout_min": 4500,
            "payout_max": 14000,
        },
        {
            "id": "crime_t5_c",
            "tier": 5,
            "name": "Warehouse Raid",
            "nerve_cost": 12,
            "base_success": 0.25,
            "payout_min": 4200,
            "payout_max": 15000,
        },
    ]
    for c in crimes:
        session.merge(Crime(**c))


def seed_items(session: Session):
    items = [
        {
            "id": 1,
            "name": "Knuckles",
            "slot": "weapon",
            "bonus": 5,
            "base_price": 500,
            "daily_cap": None,
        },
        {
            "id": 2,
            "name": "Blade",
            "slot": "weapon",
            "bonus": 12,
            "base_price": 1200,
            "daily_cap": None,
        },
        {
            "id": 3,
            "name": "Pistol",
            "slot": "weapon",
            "bonus": 22,
            "base_price": 2200,
            "daily_cap": None,
        },
        {
            "id": 4,
            "name": "SMG",
            "slot": "weapon",
            "bonus": 35,
            "base_price": 3500,
            "daily_cap": None,
        },
        {
            "id": 5,
            "name": "Custom Rifle",
            "slot": "weapon",
            "bonus": 50,
            "base_price": 5000,
            "daily_cap": None,
        },
        {
            "id": 6,
            "name": "Padded Jacket",
            "slot": "armor",
            "bonus": 5,
            "base_price": 500,
            "daily_cap": None,
        },
        {
            "id": 7,
            "name": "Kevlar Vest",
            "slot": "armor",
            "bonus": 12,
            "base_price": 1200,
            "daily_cap": None,
        },
        {
            "id": 8,
            "name": "Tactical Vest",
            "slot": "armor",
            "bonus": 22,
            "base_price": 2200,
            "daily_cap": None,
        },
        {
            "id": 9,
            "name": "Composite Plate",
            "slot": "armor",
            "bonus": 35,
            "base_price": 3500,
            "daily_cap": None,
        },
        {
            "id": 10,
            "name": "Exo Weave",
            "slot": "armor",
            "bonus": 50,
            "base_price": 5000,
            "daily_cap": None,
        },
        {
            "id": 11,
            "name": "Medkit",
            "slot": "consumable",
            "bonus": 40,
            "base_price": 500,
            "daily_cap": 5,
        },
        {
            "id": 12,
            "name": "Energy Drink",
            "slot": "consumable",
            "bonus": 25,
            "base_price": 400,
            "daily_cap": 2,
        },
        {
            "id": 13,
            "name": "Adrenaline",
            "slot": "consumable",
            "bonus": 10,
            "base_price": 800,
            "daily_cap": 1,
        },
    ]
    for i in items:
        session.merge(Item(**i))


def seed_flags(session: Session):
    flags = ["llm_digest_polish", "llm_newspaper_polish", "llm_enrichment", "talkdowns"]
    for name in flags:
        session.merge(FeatureFlag(name=name, enabled=False, config_json="{}"))


def seed_jobs(session: Session):
    jobs = [
        {
            "id": 1,
            "name": "Courier",
            "description": "Deliver packages across the city",
            "pay": 120,
            "perk_stat": "speed",
            "perk_amount": 1.0,
        },
        {
            "id": 2,
            "name": "Bouncer",
            "description": "Keep the peace at nightclubs",
            "pay": 140,
            "perk_stat": "strength",
            "perk_amount": 1.0,
        },
        {
            "id": 3,
            "name": "Clinic Aide",
            "description": "Assist at a underground clinic",
            "pay": 110,
            "perk_stat": "health",
            "perk_amount": 20.0,
        },
        {
            "id": 4,
            "name": "Mechanic",
            "description": "Fix cars at a chop shop",
            "pay": 130,
            "perk_stat": "dexterity",
            "perk_amount": 1.0,
        },
        {
            "id": 5,
            "name": "Junior Fixer",
            "description": "Run errands for the underworld",
            "pay": 150,
            "perk_stat": "crime_skill",
            "perk_amount": 0.3,
        },
    ]
    for j in jobs:
        session.merge(Job(**j))


def seed_all(session: Session):
    seed_crimes(session)
    seed_items(session)
    seed_flags(session)
    seed_jobs(session)
    session.commit()


if __name__ == "__main__":
    init_db()
    session = Session(bind=engine)
    try:
        seed_all(session)
        print("Seed complete.")
    finally:
        session.close()
