from __future__ import annotations

from datetime import datetime

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KBar
from app.services.indicators import add_all_indicators
from app.services.shioaji_client import ShioajiClient

FREQUENCY_MAP = {"1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min", "60m": "60min", "1d": "1D"}


class MarketDataService:
    def __init__(self, client: ShioajiClient) -> None:
        self.client = client

    def get_kbars(
        self,
        db: Session,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str,
        security_type: str = "stock",
        with_indicators: bool = False,
    ) -> pd.DataFrame:
        cached = self._load_cached(db, symbol, start, end, interval)
        if cached.empty:
            daily = self.client.kbars(symbol, start, end, security_type)
            resampled = self._resample(daily, interval)
            self._store(db, symbol, security_type, interval, resampled)
            cached = resampled
        if with_indicators:
            cached = add_all_indicators(cached)
        return cached

    def _load_cached(self, db: Session, symbol: str, start: datetime, end: datetime, interval: str) -> pd.DataFrame:
        rows = db.execute(
            select(KBar)
            .where(KBar.symbol == symbol, KBar.interval == interval, KBar.datetime >= start, KBar.datetime <= end)
            .order_by(KBar.datetime)
        ).scalars()
        records = [
            {"datetime": row.datetime, "open": row.open, "high": row.high, "low": row.low, "close": row.close, "volume": row.volume}
            for row in rows
        ]
        return pd.DataFrame(records)

    def _store(self, db: Session, symbol: str, security_type: str, interval: str, df: pd.DataFrame) -> None:
        for row in df.to_dict(orient="records"):
            existing = db.execute(
                select(KBar).where(KBar.symbol == symbol, KBar.interval == interval, KBar.datetime == row["datetime"])
            ).scalar_one_or_none()
            if existing is None:
                db.add(KBar(symbol=symbol, security_type=security_type, interval=interval, **row))
            else:
                for field in ("open", "high", "low", "close", "volume"):
                    setattr(existing, field, row[field])
        db.commit()

    @staticmethod
    def _resample(df: pd.DataFrame, interval: str) -> pd.DataFrame:
        freq = FREQUENCY_MAP[interval]
        frame = df.copy()
        frame["datetime"] = pd.to_datetime(frame["datetime"])
        frame = frame.set_index("datetime")
        if interval == "1d":
            return frame.reset_index()
        return (
            frame.resample(freq)
            .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
            .dropna()
            .reset_index()
        )
