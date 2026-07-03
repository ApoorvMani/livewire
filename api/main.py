from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app():
    app = FastAPI(title="Livewire")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from api.auth import router as auth_router
    from api.crimes import router as crimes_router
    from api.gym import router as gym_router
    from api.jail import router as jail_router
    from api.combat import router as combat_router
    from api.items import router as items_router
    from api.market import router as market_router
    from api.jobs import router as jobs_router
    from api.heat import router as heat_router
    from api.feed import router as feed_router

    app.include_router(auth_router, prefix="/api")
    app.include_router(crimes_router, prefix="/api")
    app.include_router(gym_router, prefix="/api")
    app.include_router(jail_router, prefix="/api")
    app.include_router(combat_router, prefix="/api")
    app.include_router(items_router, prefix="/api")
    app.include_router(market_router, prefix="/api")
    app.include_router(jobs_router, prefix="/api")
    app.include_router(heat_router, prefix="/api")
    app.include_router(feed_router, prefix="/api")
    return app


app = create_app()
