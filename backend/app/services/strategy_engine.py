from __future__ import annotations

from app.strategies.base import Strategy
from app.strategies.builtins import BollingerStrategy, KDStrategy, MACDStrategy, RSIStrategy


class StrategyEngine:
    def __init__(self) -> None:
        self._strategies: dict[str, Strategy] = {}
        for strategy in (RSIStrategy(), MACDStrategy(), KDStrategy(), BollingerStrategy()):
            self.register(strategy)

    def register(self, strategy: Strategy) -> None:
        self._strategies[strategy.name] = strategy

    def get(self, name: str) -> Strategy:
        if name not in self._strategies:
            raise KeyError(f"unknown strategy: {name}")
        return self._strategies[name]

    def list_names(self) -> list[str]:
        return sorted(self._strategies)
