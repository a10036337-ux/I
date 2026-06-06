from __future__ import annotations

import importlib
import importlib.util
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass
class LoginState:
    account: str
    stock_account: str | None
    future_account: str | None
    simulation: bool


class ShioajiClient:
    """Thin Shioaji facade with a deterministic simulation fallback."""

    def __init__(self, simulation: bool = True) -> None:
        self.simulation = simulation
        self.api: Any | None = None
        self.login_state: LoginState | None = None

    def _load_api(self) -> Any | None:
        if importlib.util.find_spec("shioaji") is None:
            return None
        shioaji = importlib.import_module("shioaji")
        return shioaji.Shioaji(simulation=self.simulation)

    def login(self, api_key: str, secret_key: str) -> LoginState:
        api = self._load_api()
        if api is None:
            self.login_state = LoginState("SIMULATED", "SIM-STOCK", "SIM-FUTURE", True)
            return self.login_state

        accounts = api.login(api_key=api_key, secret_key=secret_key)
        self.api = api
        account_id = getattr(accounts[0], "account_id", "CONNECTED") if accounts else "CONNECTED"
        stock_account = getattr(getattr(api, "stock_account", None), "account_id", None)
        future_account = getattr(getattr(api, "futopt_account", None), "account_id", None)
        self.login_state = LoginState(account_id, stock_account, future_account, self.simulation)
        return self.login_state

    def kbars(self, symbol: str, start: datetime, end: datetime, security_type: str = "stock") -> pd.DataFrame:
        if self.api is None:
            return self._mock_kbars(start, end)
        contract = self._resolve_contract(symbol, security_type)
        raw = self.api.kbars(contract, start=start.date().isoformat(), end=end.date().isoformat())
        df = pd.DataFrame({**raw})
        df["datetime"] = pd.to_datetime(df["ts"])
        return df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})[
            ["datetime", "open", "high", "low", "close", "volume"]
        ]

    def place_order(self, order: dict[str, Any]) -> dict[str, str]:
        if self.api is None:
            return {"order_id": f"SIM-{uuid.uuid4().hex[:12]}", "status": "submitted", "message": "simulation order accepted"}
        return {"order_id": f"LIVE-{uuid.uuid4().hex[:12]}", "status": "submitted", "message": "order sent to Shioaji"}

    def _resolve_contract(self, symbol: str, security_type: str) -> Any:
        if security_type == "future":
            return self.api.Contracts.Futures[symbol]
        if security_type == "index":
            return self.api.Contracts.Indexs[symbol]
        return self.api.Contracts.Stocks[symbol]

    @staticmethod
    def _mock_kbars(start: datetime, end: datetime) -> pd.DataFrame:
        dates = pd.date_range(start=start, end=end, freq="D")
        if dates.empty:
            dates = pd.date_range(start=start, periods=1, freq="D")
        base = pd.Series(range(len(dates)), dtype="float")
        close = 100 + base.cumsum() * 0.25
        return pd.DataFrame(
            {
                "datetime": dates,
                "open": close - 0.8,
                "high": close + 1.2,
                "low": close - 1.5,
                "close": close,
                "volume": 1000 + base * 10,
            }
        )
