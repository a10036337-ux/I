# 台股專業量化交易系統

本專案提供一套模組化台股看盤、下單、策略與回測系統，支援永豐 Shioaji API、FastAPI、SQLite、React、TypeScript、TradingView Lightweight Charts 與 Ant Design。

> 安全提醒：請勿把真實 API_KEY / SECRET_KEY 寫入程式或提交到 Git。請使用 `.env` 或登入畫面輸入。

## 專案結構

```text
backend/      FastAPI、Shioaji、WebSocket、SQLAlchemy、Pandas/Numpy
frontend/     React、TypeScript、Vite、Lightweight Charts、Ant Design
database/     SQLite 資料庫掛載目錄
strategies/   策略擴充說明
services/     部署/服務說明
```

## 功能

- 永豐 API 登入：`POST /api/login`，登入成功回傳帳號、股票帳戶與期貨帳戶。
- 歷史資料：`GET /api/kbars?symbol=2330&start=...&end=...&interval=1d`，支援股票、期貨、指數與 1m/5m/15m/30m/60m/1d。
- 即時行情：`/ws/market` 推送 Tick、BidAsk、成交價、成交量、五檔與漲跌幅。
- K 線圖：日 K、60 分 K、5 分 K 切換，支援十字線、縮放、拖曳與成交量。
- 技術指標：後端內建 MA、EMA、BBANDS、RSI、MACD、KD。
- 自選股：新增、刪除、排序欄位、群組並存入 SQLite。
- 下單：`POST /api/order` 支援股票/期貨、市價/限價、ROD/IOC/FOK、買進/賣出。
- 庫存與損益：`GET /api/positions`、`GET /api/pnl`。
- 委託回報：`GET /api/orders`。
- 策略與回測：RSI、MACD、KD、布林通道與可插拔 Strategy Engine。

## 本機安裝

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

開啟 http://localhost:5173。

## Docker 部署

```bash
cp .env.example .env
# 將 SHIOAJI_API_KEY / SHIOAJI_SECRET_KEY 寫入 .env；模擬模式可維持 true。
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## API 範例

```bash
curl 'http://localhost:8000/api/kbars?symbol=2330&start=2025-01-01T00:00:00&end=2025-12-31T00:00:00&interval=1d'
```

```bash
curl -X POST 'http://localhost:8000/api/order' \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"2330","action":"buy","price":600,"quantity":1000,"price_type":"limit","order_type":"ROD","security_type":"stock"}'
```

## 策略擴充

新增策略時繼承 `backend/app/strategies/base.py` 的 `Strategy`，實作 `generate_signals()` 回傳 `signal` 欄位：`1` 買進、`-1` 賣出、`0` 觀望，並在 `backend/app/services/strategy_engine.py` 註冊。
