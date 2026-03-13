# Stock Universe

A single-page stock universe explorer with autocomplete tag-based filters, an interactive scatter chart, a sortable paginated table, and an AI-powered chat assistant.

## Architecture

| Layer    | Stack                             |
| -------- | --------------------------------- |
| Frontend | Vue 3 (Composition API) + Vite    |
| Backend  | Python FastAPI + Pydantic v2      |
| Data     | Static JSON (`backend/data/stocks.json`) |

## Features

- **Autocomplete filter bar** — type to search across all stock fields (sector, ticker, name, price, market cap, P/E, dividend yield, volume). Matching values appear in a grouped dropdown; selected values become tag chips inside the search input. Multiple filters within the same category use OR logic; across categories they use AND.
- **Scatter chart** — interactive Chart.js scatter plot of Market Cap vs P/E Ratio, color-coded by sector. Reacts live to active filters.
- **Sortable paginated table** — click any column header to sort ascending/descending. Page size selector (10 / 50 / 100) keeps the DOM light even with 40k+ rows.
- **AI chat assistant** — sidebar panel with full message history. Ask natural-language questions to help filter or analyze stocks.

## Page Layout

```
+----------------------------------------------------------+
|  TopBar                                                   |
+------------------------------------------+---------------+
|                                          | ▼ Filters     |
|                                          |  [tags|search]|
|         Scatter Chart (70%)              |---------------|
|         Market Cap vs P/E               | AI Assistant  |
|                                          | [messages...] |
|                                          | [input][Send] |
+------------------------------------------+---------------+
|  StockTable (sortable, paginated)                         |
|  Show: [10] [50] [100]        1–50 of 500    ‹ 1/10 ›   |
+----------------------------------------------------------+
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Key endpoints:

- `GET  /api/stocks` — list all stocks
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
│   │   ├── components/
│   │   │   ├── TopBar.vue        # App header with logo & nav
│   │   │   ├── FilterBar.vue     # Expandable autocomplete filter with inline tag chips
│   │   │   ├── AiChat.vue        # Sidebar AI chat panel with message history
│   │   │   ├── ScatterChart.vue  # Chart.js scatter plot (Market Cap vs P/E)
│   │   │   └── StockTable.vue    # Sortable, paginated data table
│   │   ├── composables/
│   │   │   ├── useStocks.ts      # Fetch stocks, chip-based client-side filtering
│   │   │   └── useChat.ts        # AI chat message state & API calls
│   │   └── types/
│   │       └── stock.ts          # Stock, FilterChip, ChatMessage interfaces
│   └── ...
├── backend/                  # Python FastAPI
│   ├── routers/              # stocks.py, chat.py
│   ├── services/             # agent.py (AI stub)
│   ├── models/               # Pydantic schemas
│   ├── data/                 # stocks.json
│   └── tests/                # pytest tests
└── README.md
```
