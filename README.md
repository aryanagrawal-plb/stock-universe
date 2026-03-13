# Stock Universe

A single-page stock universe explorer with manual filters, an interactive scatter chart, and an AI-powered chat assistant.

## Architecture

| Layer    | Stack                             |
| -------- | --------------------------------- |
| Frontend | Vue 3 (Composition API) + Vite    |
| Backend  | Python FastAPI + Pydantic v2      |
| Data     | Static JSON (`backend/data/stocks.json`) |

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Key endpoints:

- `GET  /api/stocks` — list stocks (query params: `sector`, `min_price`, `max_price`, `search`)
- `POST /api/chat`   — send a message to the AI agent
- `GET  /api/health`  — health check

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`. API requests are proxied to the backend via Vite config.

### Run Tests

```bash
cd backend
pytest
```

## Project Structure

```
stock-universe/
├── frontend/                 # Vue 3 + Vite + TypeScript
│   ├── src/
│   │   ├── components/       # TopBar, StockTable, ScatterChart, AiChat
│   │   ├── composables/      # useStocks, useChat
│   │   └── types/            # TypeScript interfaces
│   └── ...
├── backend/                  # Python FastAPI
│   ├── routers/              # stocks.py, chat.py
│   ├── services/             # agent.py (AI stub)
│   ├── models/               # Pydantic schemas
│   ├── data/                 # stocks.json
│   └── tests/                # pytest tests
└── README.md
```
