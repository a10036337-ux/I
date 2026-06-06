from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Interval = Literal["1m", "5m", "15m", "30m", "60m", "1d"]
Action = Literal["buy", "sell"]
PriceType = Literal["market", "limit"]
OrderType = Literal["ROD", "IOC", "FOK"]
SecurityType = Literal["stock", "future", "index"]


class LoginRequest(BaseModel):
    api_key: str = Field(min_length=1)
    secret_key: str = Field(min_length=1)


class LoginResponse(BaseModel):
    success: bool
    account: str
    stock_account: str | None = None
    future_account: str | None = None
    simulation: bool


class KBarOut(BaseModel):
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class KBarQuery(BaseModel):
    symbol: str
    start: datetime
    end: datetime
    interval: Interval = "1d"
    security_type: SecurityType = "stock"


class WatchlistIn(BaseModel):
    symbol: str
    name: str = ""
    group_name: str = "Default"
    sort_order: int = 0


class WatchlistOut(WatchlistIn):
    id: int

    model_config = {"from_attributes": True}


class OrderRequest(BaseModel):
    symbol: str
    action: Action
    price: float | None = None
    quantity: int = Field(gt=0)
    price_type: PriceType
    order_type: OrderType
    security_type: Literal["stock", "future"] = "stock"


class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: str


class PositionOut(BaseModel):
    symbol: str
    quantity: int
    average_price: float
    last_price: float | None = None
    realized_pnl: float
    unrealized_pnl: float

    model_config = {"from_attributes": True}


class BacktestRequest(BaseModel):
    symbol: str
    start: datetime
    end: datetime
    strategy: str
    interval: Interval = "1d"
    initial_cash: float = 1_000_000


class BacktestResponse(BaseModel):
    total_return: float
    annualized_return: float
    sharpe: float
    max_drawdown: float
    trades: list[dict]
