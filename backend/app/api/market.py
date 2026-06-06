from fastapi import APIRouter

from app.dependencies import ws_manager

router = APIRouter(prefix="/api", tags=["market"])


@router.post("/market/subscribe/{symbol}")
def subscribe(symbol: str) -> dict[str, str]:
    ws_manager.symbols.add(symbol)
    return {"status": "subscribed", "symbol": symbol}


@router.delete("/market/subscribe/{symbol}")
def unsubscribe(symbol: str) -> dict[str, str]:
    ws_manager.symbols.discard(symbol)
    return {"status": "unsubscribed", "symbol": symbol}
