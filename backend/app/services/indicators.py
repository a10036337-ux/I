from __future__ import annotations

import numpy as np
import pandas as pd


def add_moving_averages(df: pd.DataFrame, windows: tuple[int, ...] = (5, 10, 20, 60)) -> pd.DataFrame:
    out = df.copy()
    for window in windows:
        out[f"ma{window}"] = out["close"].rolling(window).mean()
        out[f"ema{window}"] = out["close"].ewm(span=window, adjust=False).mean()
    return out


def add_bbands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    out = df.copy()
    middle = out["close"].rolling(window).mean()
    std = out["close"].rolling(window).std()
    out["bb_mid"] = middle
    out["bb_upper"] = middle + num_std * std
    out["bb_lower"] = middle - num_std * std
    return out


def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    out = df.copy()
    delta = out["close"].diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = -delta.clip(upper=0).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    out["rsi"] = 100 - (100 / (1 + rs))
    return out


def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ema12 = out["close"].ewm(span=12, adjust=False).mean()
    ema26 = out["close"].ewm(span=26, adjust=False).mean()
    out["macd"] = ema12 - ema26
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]
    return out


def add_kd(df: pd.DataFrame, window: int = 9) -> pd.DataFrame:
    out = df.copy()
    low_min = out["low"].rolling(window).min()
    high_max = out["high"].rolling(window).max()
    rsv = (out["close"] - low_min) / (high_max - low_min).replace(0, np.nan) * 100
    out["k"] = rsv.ewm(com=2, adjust=False).mean()
    out["d"] = out["k"].ewm(com=2, adjust=False).mean()
    return out


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    return add_kd(add_macd(add_rsi(add_bbands(add_moving_averages(df)))))
