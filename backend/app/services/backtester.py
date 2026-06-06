from __future__ import annotations

import math

import pandas as pd

from app.strategies.base import Strategy


class Backtester:
    def run(self, df: pd.DataFrame, strategy: Strategy, initial_cash: float) -> dict:
        signals = strategy.generate_signals(df).dropna().copy()
        cash = initial_cash
        shares = 0
        equity_curve: list[float] = []
        trades: list[dict] = []

        for row in signals.itertuples():
            price = float(row.close)
            signal = int(row.signal)
            if signal == 1 and shares == 0:
                shares = math.floor(cash / price)
                cash -= shares * price
                trades.append({"datetime": row.datetime.isoformat(), "action": "buy", "price": price, "quantity": shares})
            elif signal == -1 and shares > 0:
                cash += shares * price
                trades.append({"datetime": row.datetime.isoformat(), "action": "sell", "price": price, "quantity": shares})
                shares = 0
            equity_curve.append(cash + shares * price)

        equity = pd.Series(equity_curve or [initial_cash])
        returns = equity.pct_change().fillna(0)
        total_return = equity.iloc[-1] / initial_cash - 1
        annualized_return = (1 + total_return) ** (252 / max(len(equity), 1)) - 1
        sharpe = float((returns.mean() / returns.std() * (252**0.5)) if returns.std() else 0)
        drawdown = equity / equity.cummax() - 1
        return {
            "total_return": float(total_return),
            "annualized_return": float(annualized_return),
            "sharpe": sharpe,
            "max_drawdown": float(drawdown.min()),
            "trades": trades,
        }
