import pytest

pd = pytest.importorskip("pandas")

from app.services.indicators import add_all_indicators


def test_add_all_indicators_creates_expected_columns():
    df = pd.DataFrame(
        {
            "datetime": pd.date_range("2025-01-01", periods=40),
            "open": range(40),
            "high": range(1, 41),
            "low": range(40),
            "close": range(1, 41),
            "volume": range(100, 140),
        }
    )
    out = add_all_indicators(df)
    assert {"ma5", "ema20", "bb_upper", "rsi", "macd", "k", "d"}.issubset(out.columns)
