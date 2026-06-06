from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import WatchlistItem
from app.schemas.trading import WatchlistIn, WatchlistOut

router = APIRouter(prefix="/api", tags=["watchlist"])


@router.get("/watchlist", response_model=list[WatchlistOut])
def list_watchlist(db: Session = Depends(get_db)):
    return db.query(WatchlistItem).order_by(WatchlistItem.group_name, WatchlistItem.sort_order).all()


@router.post("/watchlist", response_model=WatchlistOut)
def add_watchlist_item(payload: WatchlistIn, db: Session = Depends(get_db)):
    item = WatchlistItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/watchlist/{item_id}")
def delete_watchlist_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WatchlistItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="watchlist item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
