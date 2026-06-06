from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Position
from app.schemas.trading import PositionOut

router = APIRouter(prefix="/api", tags=["portfolio"])


@router.get("/positions", response_model=list[PositionOut])
def positions(db: Session = Depends(get_db)):
    return db.query(Position).order_by(Position.symbol).all()


@router.get("/pnl")
def pnl(db: Session = Depends(get_db)) -> dict[str, float]:
    rows = db.query(Position).all()
    realized = sum(row.realized_pnl for row in rows)
    unrealized = sum(row.unrealized_pnl for row in rows)
    return {"realized_pnl": realized, "unrealized_pnl": unrealized, "total_equity_delta": realized + unrealized}
