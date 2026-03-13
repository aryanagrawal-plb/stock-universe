# Stock Universe — Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Browser (SPA)                              │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ App.vue                                                      │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │ TopBar                                                 │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────┬──────────────────────────┐  │   │
│  │  │                            │ FilterBar (expandable)   │  │   │
│  │  │   ScatterChart  (70%)      │   [tags | search...]     │  │   │
│  │  │   Market Cap vs P/E        ├──────────────────────────┤  │   │
│  │  │                            │ AiChat                   │  │   │
│  │  │                            │   message history        │  │   │
│  │  │                            │   [input] [Send]         │  │   │
│  │  ├────────────────────────────┴──────────────────────────┤  │   │
│  │  │ StockTable (sortable, paginated)                       │  │   │
│  │  │   Show [10][50][100]       1-50 of 500     ‹ 1/10 ›   │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                          │                     │                    │
│                   GET /api/stocks        POST /api/chat             │
└──────────────────────────┼─────────────────────┼────────────────────┘
                           │  Vite proxy :5173   │
                           │  → :8000            │
┌──────────────────────────┼─────────────────────┼────────────────────┐
│                     FastAPI Backend                                  │
│                                                                     │
│  ┌─────────────┐   ┌──────────────┐   ┌───────────────────────┐   │
│  │ stocks.py   │   │  chat.py     │   │  main.py              │   │
│  │ GET /stocks │   │  POST /chat  │   │  CORS, router mount   │   │
│  └──────┬──────┘   └──────┬───────┘   └───────────────────────┘   │
│         │                 │                                         │
│         ▼                 ▼                                         │
│  ┌─────────────┐   ┌──────────────┐                                │
│  │ stocks.json │   │  agent.py    │                                │
│  │ (data)      │   │  (AI stub)   │                                │
│  └─────────────┘   └──────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Stock Data Pipeline

```
                        ┌────────────┐
                        │ stocks.json│
                        └──────┬─────┘
                               │ load on request
                               ▼
                        ┌────────────┐
                        │ GET /stocks│  (FastAPI router)
                        └──────┬─────┘
                               │ JSON response
                               ▼
                     ┌──────────────────┐
                     │ useStocks.ts     │
                     │  stocks (ref)    │
                     │  filterChips     │
                     │  filteredStocks  │  ← computed from stocks + chips
                     └────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌──────────────┐ ┌───────────┐ ┌──────────────┐
      │ FilterBar    │ │ Scatter   │ │ StockTable   │
      │ (all stocks  │ │ Chart     │ │ (filtered    │
      │  for search) │ │ (filtered)│ │  + sorted    │
      └──────────────┘ └───────────┘ │  + paginated)│
                                      └──────────────┘
```

### 2. Filter Flow

```
  User types "tech"
        │
        ▼
  ┌──────────────────────────────┐
  │ FilterBar                    │
  │  suggestions = computed()    │  ← matches across all stock fields
  │  grouped dropdown appears    │
  └──────────┬───────────────────┘
             │ user clicks "Sector: Technology"
             ▼
  emit("update:filterChips", [...chips, { category: "Sector", value: "Technology" }])
             │
             ▼
  ┌──────────────────────────────┐
  │ App.vue                      │
  │  filterChips = $event        │  ← updates the ref in useStocks
  └──────────┬───────────────────┘
             │ triggers recompute
             ▼
  ┌──────────────────────────────┐
  │ useStocks.filteredStocks     │
  │  group chips by category     │
  │  AND across categories       │
  │  OR within same category     │
  └──────────┬───────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
  ScatterChart   StockTable
  (re-renders)   (re-renders)
```

### 3. Chat Flow

```
  User types "What are the top tech stocks?"
        │
        ▼
  ┌──────────────────────────┐
  │ AiChat.vue               │
  │  handleSend()            │
  └──────────┬───────────────┘
             │
             ▼
  ┌──────────────────────────┐
  │ useChat.ts               │
  │  messages.push(user msg) │
  │  POST /api/chat          │──────────┐
  │  messages.push(reply)    │          │
  └──────────────────────────┘          ▼
                              ┌──────────────────┐
                              │ chat.py router   │
                              │  → agent.py      │
                              │  process_message │
                              │  → reply string  │
                              └──────────────────┘
```

---

## Frontend Components

### Component Responsibilities

| Component | Role | Props In | Events Out |
|-----------|------|----------|------------|
| **App.vue** | Root orchestrator. Owns stock state via `useStocks()`, fetches on mount, wires all children. | — | — |
| **TopBar** | App header with logo, title, navigation buttons. | — | — |
| **FilterBar** | Expandable panel with autocomplete search input containing inline tag chips. Computes suggestions from all stock fields. | `stocks`, `filterChips`, `resultCount` | `update:filterChips` |
| **ScatterChart** | Chart.js scatter plot: Market Cap (x) vs P/E Ratio (y), color-coded by sector. | `stocks` (filtered) | — |
| **StockTable** | Sortable, paginated data table. Sorts client-side; only renders the current page (10/50/100 rows). | `stocks` (filtered), `isLoading`, `error` | — |
| **AiChat** | Sidebar chat panel with full message history, input, and send button. | — | — |

### Component Tree

```
App.vue
 ├── TopBar
 ├── [chart-chat-row]                    ← flex row (70/30 split)
 │    ├── ScatterChart                   ← receives filteredStocks
 │    └── [chat-section]                 ← flex column
 │         ├── FilterBar                 ← receives stocks + filterChips
 │         └── AiChat                    ← independent, uses useChat()
 └── [content]
      └── StockTable                     ← receives filteredStocks
```

---

## Composables (State Management)

### `useStocks()`

Centralised stock data and filtering logic. Called once in `App.vue`.

```
┌─────────────────────────────────────────────────────┐
│ useStocks()                                          │
│                                                      │
│  ┌──────────┐    ┌──────────────┐                   │
│  │ stocks   │    │ filterChips  │                   │
│  │ ref<[]>  │    │ ref<[]>      │                   │
│  └────┬─────┘    └──────┬───────┘                   │
│       │                 │                            │
│       └────────┬────────┘                            │
│                ▼                                     │
│  ┌───────────────────────┐                           │
│  │ filteredStocks        │  (computed)               │
│  │  • group chips by cat │                           │
│  │  • OR within category │                           │
│  │  • AND across cats    │                           │
│  └───────────────────────┘                           │
│                                                      │
│  fetchStocks() → GET /api/stocks → stocks.value      │
│  isLoading, error                                    │
└─────────────────────────────────────────────────────┘
```

### `useChat()`

Independent chat state. Called inside `AiChat.vue`.

```
┌─────────────────────────────────────────┐
│ useChat()                                │
│                                          │
│  messages: ref<ChatMessage[]>            │
│  isSending: ref<boolean>                 │
│                                          │
│  sendMessage(text)                       │
│    → push { role: "user", content }      │
│    → POST /api/chat                      │
│    → push { role: "assistant", content } │
└─────────────────────────────────────────┘
```

---

## Backend

### Request Routing

```
main.py
 ├── CORSMiddleware (allow localhost:5173)
 ├── GET  /api/health → { status: "ok" }
 ├── routers/stocks.py
 │    └── GET /api/stocks → load stocks.json → filter → list[Stock]
 └── routers/chat.py
      └── POST /api/chat → agent.process_message() → ChatResponse
```

### Pydantic Schemas

```
┌────────────────────────────────────┐
│ Stock                              │
│  ticker: str                       │
│  name: str                         │
│  sector: str                       │
│  price: float                      │
│  market_cap: float                 │
│  pe_ratio: float | None            │
│  dividend_yield: float | None      │
│  volume: int                       │
└────────────────────────────────────┘

┌─────────────────┐  ┌──────────────────┐
│ ChatRequest     │  │ ChatResponse     │
│  message: str   │  │  reply: str      │
└─────────────────┘  └──────────────────┘
```

### Data Source

`backend/data/stocks.json` — static JSON array of stock objects. Loaded on each request (suitable for the current dataset; for 40k+ rows, consider loading once at startup or using a database).

---

## Filter Chip System

### Type

```typescript
interface FilterChip {
  category: string;   // "Sector", "Ticker", "Name", "Price", etc.
  value: string;      // "Technology", "AAPL", "$178.72", etc.
}
```

### Category → Stock Field Mapping

| Category   | Stock Field      | Format             | Example Value |
|------------|------------------|--------------------|---------------|
| Sector     | `sector`         | raw string         | Technology    |
| Ticker     | `ticker`         | raw string         | AAPL          |
| Name       | `name`           | raw string         | Apple Inc.    |
| Price      | `price`          | `.toFixed(2)`      | 178.72        |
| Market Cap | `market_cap`     | `$2.8T` / `$150B`  | $2.8T         |
| P/E        | `pe_ratio`       | `.toFixed(1)`      | 28.5          |
| Div Yield  | `dividend_yield` | `.toFixed(2)%`     | 0.55%         |
| Volume     | `volume`         | `45.2M` / `1.2K`   | 45.2M         |

### Filtering Logic

```
chips = [
  { category: "Sector", value: "Technology" },
  { category: "Sector", value: "Financials" },
  { category: "Price",  value: "178.72" }
]

→ Group by category:
  Sector: ["Technology", "Financials"]   ← OR (match either)
  Price:  ["178.72"]                     ← AND with above

→ Result: stocks where
     (sector = "Technology" OR sector = "Financials")
  AND price = 178.72
```

---

## Performance Considerations

| Concern | Strategy |
|---------|----------|
| **40k rows in table** | Only the current page (10/50/100 rows) is rendered to the DOM. Sorting uses native `Array.sort()` on the filtered set via a Vue `computed`. |
| **Sorting speed** | `computed` caches until data or sort state changes. `Array.sort()` on 40k items is ~5–10ms in modern browsers. |
| **Filter recomputation** | `filteredStocks` is a `computed` — only recalculates when `stocks` or `filterChips` change. Single pass through the array. |
| **Autocomplete suggestions** | Capped at 25 results to keep the dropdown responsive. |
| **Chart re-renders** | Chart.js receives the filtered dataset; only re-renders when `filteredStocks` changes. |

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend framework | Vue 3 (Composition API) | Reactive UI components |
| Build tool | Vite | Fast dev server with HMR, API proxy |
| Charts | Chart.js + vue-chartjs | Scatter plot visualisation |
| Language | TypeScript | Type safety across frontend |
| Backend framework | FastAPI | High-performance async API |
| Validation | Pydantic v2 | Request/response schema validation |
| Server | Uvicorn | ASGI server with hot reload |
| Data | Static JSON | Stock universe dataset |
