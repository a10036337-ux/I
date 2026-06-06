from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import shioaji_client
from app.models import OrderRecord
from app.schemas.trading import OrderRequest, OrderResponse

router = APIRouter(prefix="/api", tags=["orders"])


@router.post("/order", response_model=OrderResponse)
def place_order(payload: OrderRequest, db: Session = Depends(get_db)) -> OrderResponse:
    result = shioaji_client.place_order(payload.model_dump())
    db.add(OrderRecord(order_id=result["order_id"], status=result["status"], **payload.model_dump()))
    db.commit()
    return OrderResponse(**result)


@router.get("/orders")
def list_orders(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(OrderRecord).order_by(OrderRecord.created_at.desc()).limit(100).all()
    return [
        {
            "order_id": row.order_id,
            "symbol": row.symbol,
            "action": row.action,
            "price": row.price,
            "quantity": row.quantity,
            "price_type": row.price_type,
            "order_type": row.order_type,
            "status": row.status,
            "created_at": row.created_at,
        }
        for row in rows
    ]
