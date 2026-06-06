from __future__ import annotations

import pandas as pd

from app.services.indicators import add_bbands, add_kd, add_macd, add_rsi
from app.strategies.base import Strategy


class RSIStrategy(Strategy):
    name = "rsi"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        out = add_rsi(df)
        out["signal"] = 0
        out.loc[out["rsi"] < 30, "signal"] = 1
        out.loc[out["rsi"] > 70, "signal"] = -1
        return out


class MACDStrategy(Strategy):
    name = "macd"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        out = add_macd(df)
        out["signal"] = 0
        out.loc[out["macd"] > out["macd_signal"], "signal"] = 1
        out.loc[out["macd"] < out["macd_signal"], "signal"] = -1
        return out


class KDStrategy(Strategy):
    name = "kd"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        out = add_kd(df)
        out["signal"] = 0
        out.loc[out["k"] > out["d"], "signal"] = 1
        out.loc[out["k"] < out["d"], "signal"] = -1
        return out


class BollingerStrategy(Strategy):
    name = "bbands"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        out = add_bbands(df)
        out["signal"] = 0
        out.loc[out["close"] < out["bb_lower"], "signal"] = 1
        out.loc[out["close"] > out["bb_upper"], "signal"] = -1
        return out
