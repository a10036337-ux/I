from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, backtest, kbars, market, orders, portfolio, watchlist, websocket
from app.core.config import get_settings
from app.db.init_db import init_db
from app.dependencies import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(ws_manager.simulation_loop())
    yield
    task.cancel()


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth.router, kbars.router, market.router, orders.router, portfolio.router, watchlist.router, backtest.router, websocket.router):
    app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
