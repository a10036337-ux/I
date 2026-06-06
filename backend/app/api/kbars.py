from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import market_data_service
from app.schemas.trading import KBarOut

router = APIRouter(prefix="/api", tags=["kbars"])


@router.get("/kbars", response_model=list[KBarOut])
def get_kbars(
    symbol: str,
    start: datetime,
    end: datetime,
    interval: str = Query("1d", pattern="^(1m|5m|15m|30m|60m|1d)$"),
    security_type: str = Query("stock", pattern="^(stock|future|index)$"),
    db: Session = Depends(get_db),
) -> list[dict]:
    df = market_data_service.get_kbars(db, symbol, start, end, interval, security_type)
    return df.to_dict(orient="records")
