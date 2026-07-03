from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    app = FastAPI(title="Livewire")
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    from api.auth import router as auth_router
    from api.crimes import router as crimes_router
    from api.gym import router as gym_router
    app.include_router(auth_router, prefix="/api")
    app.include_router(crimes_router, prefix="/api")
    app.include_router(gym_router, prefix="/api")
    return app

app = create_app()
