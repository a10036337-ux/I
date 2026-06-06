from app.core.config import get_settings
from app.services.market_data import MarketDataService
from app.services.shioaji_client import ShioajiClient
from app.services.strategy_engine import StrategyEngine
from app.services.websocket_manager import ConnectionManager

settings = get_settings()
shioaji_client = ShioajiClient(simulation=settings.shioaji_simulation)
market_data_service = MarketDataService(shioaji_client)
strategy_engine = StrategyEngine()
ws_manager = ConnectionManager()
