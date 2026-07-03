from models.tables import Crime, Item, FeatureFlag


def test_crimes_seeded(db):
    from jobs.seed import seed_crimes
    seed_crimes(db)
    assert db.query(Crime).count() == 15


def test_items_seeded(db):
    from jobs.seed import seed_items
    seed_items(db)
    assert db.query(Item).count() == 13


def test_flags_seeded(db):
    from jobs.seed import seed_flags
    seed_flags(db)
    assert db.query(FeatureFlag).count() == 4


def test_idempotent(db):
    from jobs.seed import seed_all
    seed_all(db)
    first = db.query(Crime).count()
    seed_all(db)
    assert db.query(Crime).count() == first
