from __future__ import annotations

import asyncio
import random
from datetime import datetime

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active: set[WebSocket] = set()
        self.symbols: set[str] = {"2330"}

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        disconnected: list[WebSocket] = []
        for websocket in self.active:
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                disconnected.append(websocket)
        for websocket in disconnected:
            self.disconnect(websocket)

    async def simulation_loop(self) -> None:
        while True:
            for symbol in self.symbols:
                price = round(500 + random.uniform(-5, 5), 2)
                await self.broadcast(
                    {
                        "type": "tick",
                        "symbol": symbol,
                        "datetime": datetime.utcnow().isoformat(),
                        "price": price,
                        "volume": random.randint(1, 50),
                        "change_percent": round(random.uniform(-2, 2), 2),
                        "bidask": {
                            "bids": [[price - i * 0.5, random.randint(1, 20)] for i in range(1, 6)],
                            "asks": [[price + i * 0.5, random.randint(1, 20)] for i in range(1, 6)],
                        },
                    }
                )
            await asyncio.sleep(1)
