from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import market_data_service, strategy_engine
from app.schemas.trading import BacktestRequest, BacktestResponse
from app.services.backtester import Backtester

router = APIRouter(prefix="/api", tags=["backtest"])


@router.get("/strategies")
def strategies() -> list[str]:
    return strategy_engine.list_names()


@router.post("/backtest", response_model=BacktestResponse)
def backtest(payload: BacktestRequest, db: Session = Depends(get_db)) -> dict:
    try:
        strategy = strategy_engine.get(payload.strategy)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    df = market_data_service.get_kbars(db, payload.symbol, payload.start, payload.end, payload.interval)
    return Backtester().run(df, strategy, payload.initial_cash)
