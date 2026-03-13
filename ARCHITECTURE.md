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
│  │  │   ScatterChart  (70%)      │   [chips | search...]    │  │   │
│  │  │   1Y Volatility vs        ├──────────────────────────┤  │   │
│  │  │   1Y Return               │ AiChat                   │  │   │
│  │  │   (amcharts5, grouped     │   message history        │  │   │
│  │  │    by industry)           │   filter chip previews   │  │   │
│  │  │                            │   [Apply] [Dismiss]      │  │   │
│  │  │                            │   [input] [Send]  [🗑]   │  │   │
│  │  ├────────────────────────────┴──────────────────────────┤  │   │
│  │  │ StockTable (AG Grid — sortable, paginated)             │  │   │
│  │  │   Show [10][50][100]       1-50 of 500     ‹ 1/10 ›   │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                          │                     │                    │
│                   GET /api/stocks        POST /api/chat             │
│                                    {messages: [...history]}        │
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
│  ┌──────────────┐  ┌──────────────┐                                │
│  │ universe_    │  │  agent.py    │───────┐                        │
│  │ master.json  │  │  (DeepSeek) │       │                        │
│  │ (40k stocks) │  └──────────────┘       ▼                        │
│  └──────────────┘                  ┌──────────────┐                │
│                                    │ DeepSeek API │                │
│                                    │ (OpenAI-     │                │
│                                    │  compatible) │                │
│                                    └──────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Stock Data Pipeline

```
                     ┌───────────────────┐
                     │ universe_master   │
                     │ .json (40k rows)  │
                     └────────┬──────────┘
                              │ cached in memory on first load
                              ▼
                     ┌───────────────────┐
                     │ GET /api/stocks   │  (FastAPI router)
                     │ response_model_   │
                     │ by_alias=False    │  → snake_case JSON
                     └────────┬──────────┘
                              │ JSON response
                              ▼
                  ┌──────────────────────────┐
                  │ useStocks.ts             │
                  │  stocks (ref)            │
                  │  filterChips (manual)    │
                  │  aiFilters (AI-driven)   │
                  │  filteredStocks (computed)│  ← chips + AI + numeric ranges
                  │  displayChips (computed)  │  ← merged manual + AI chips
                  └──────────┬───────────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
     ┌──────────────┐ ┌───────────┐ ┌──────────────┐
     │ FilterBar    │ │ Scatter   │ │ StockTable   │
     │ (all stocks  │ │ Chart     │ │ (filtered    │
     │  for search, │ │ (filtered)│ │  + sorted    │
     │  displayChips│ │           │ │  + paginated)│
     │  shown)      │ └───────────┘ └──────────────┘
     └──────────────┘
```

### 2. Filter Flow (Manual + AI Combined)

```
  ┌──────────────────────────────────────────────────────┐
  │                  Two filter sources                   │
  │                                                       │
  │   filterChips[]  ←── manual (FilterBar selections)   │
  │   aiFilters{}    ←── AI-confirmed filters            │
  │                                                       │
  │   filteredStocks = stocks                             │
  │     .filter(chip groups: OR within, AND across)      │
  │     .filter(AI: categorical + numeric ranges)        │
  │                                                       │
  │   displayChips = [...manual, ...aiFiltersToChips()]  │
  └──────────────────────────────────────────────────────┘

  Manual path:
    User types "tech" → FilterBar suggestions → clicks "Industry: Technology"
      → emit update:filterChips → App.vue sets filterChips
      → filteredStocks recomputes → ScatterChart + StockTable re-render

  AI path:
    User asks "Show US tech stocks under $50"
      → AiChat → useChat → POST /api/chat (full history)
      → DeepSeek returns { reply, action: "add", filters: {...} }
      → Message shown with chip preview + [Apply] [Dismiss]
      → User confirms → emit apply-filters → App.vue calls applyAiFilters()
      → aiFilters merged → filteredStocks recomputes
      → displayChips includes AI chips → FilterBar shows them
```

### 3. AI Chat Flow (with Persistence and Confirmation)

```
  User types "Show me US tech stocks under $50"
        │
        ▼
  ┌─────────────────────────────────┐
  │ AiChat.vue                      │
  │  handleSend() / Enter key       │
  └──────────┬──────────────────────┘
             │
             ▼
  ┌─────────────────────────────────┐
  │ useChat.ts                      │
  │  push user msg to messages[]    │
  │  persist to localStorage        │◄─── "stock-universe-chat"
  │  POST /api/chat                 │
  │    body: { messages: [...] }    │──── full conversation history
  └──────────┬──────────────────────┘
             │
             ▼
  ┌─────────────────────────────────┐     ┌──────────────────┐
  │ chat.py router                  │────▶│ agent.py         │
  │  extract messages[]             │     │  SYSTEM_PROMPT   │
  │  call process_message()         │     │  + last 20 msgs  │
  └─────────────────────────────────┘     │  → DeepSeek API  │
                                          └────────┬─────────┘
             ┌─────────────────────────────────────┘
             ▼
  ┌─────────────────────────────────┐
  │ DeepSeek returns JSON:          │
  │  {                              │
  │    reply: "I'll filter for...", │
  │    action: "add",               │
  │    filters: {                   │
  │      countries: ["US"],         │
  │      industries: ["Technology"],│
  │      price: { max: 50 }        │
  │    }                            │
  │  }                              │
  └──────────┬──────────────────────┘
             │
             ▼
  ┌─────────────────────────────────┐
  │ useChat.ts                      │
  │  push assistant msg with:       │
  │    pendingFilters = filters     │
  │    action = "add"               │
  │    filterStatus = "pending"     │
  │  persist to localStorage        │
  └──────────┬──────────────────────┘
             │
             ▼
  ┌─────────────────────────────────┐
  │ AiChat.vue renders:             │
  │  "I'll filter for..."           │
  │  ┌──────────────────────────┐  │
  │  │ ADD: [Country: US]       │  │  ← chip preview
  │  │      [Industry: Tech]    │  │
  │  │      [Price: ≤ 50]       │  │
  │  ├──────────────────────────┤  │
  │  │ [Apply]  [Dismiss]       │  │  ← or Enter / Esc
  │  └──────────────────────────┘  │
  └─────────────────────────────────┘
```

### 4. Action Types

| Action   | Trigger Example              | What Happens on Confirm                        |
|----------|------------------------------|------------------------------------------------|
| `add`    | "Show US tech stocks"        | `applyAiFilters()` — merges into `aiFilters`   |
| `remove` | "Remove the country filter"  | `removeAiFilters()` — subtracts from `aiFilters`|
| `clear`  | "Clear all filters"          | `clearAllFilters()` — resets chips + aiFilters  |
| `none`   | "What is a P/E ratio?"       | No filter buttons shown, just a text reply      |

---

## Frontend Components

### Component Responsibilities

| Component | Role | Props In | Events Out |
|-----------|------|----------|------------|
| **App.vue** | Root orchestrator. Owns stock state via `useStocks()`, fetches on mount, restores persisted filters, wires all children. | — | — |
| **TopBar** | App header with logo, title, navigation buttons. | — | — |
| **FilterBar** | Expandable panel (max 50% sidebar height) with autocomplete search input containing inline tag chips. Shows merged manual + AI chips. Scrollable when many chips. | `stocks`, `filterChips`, `resultCount` | `update:filterChips` |
| **ScatterChart** | amcharts5 scatter plot: 1Y Volatility (x) vs 1Y Return (y), color-coded by industry, logarithmic x-axis. | `stocks` (filtered) | — |
| **StockTable** | AG Grid data table with sortable columns and pagination (10/50/100 rows). Optimised for 40k+ rows. | `stocks` (filtered), `isLoading`, `error`, `pinnedCodes` | `toggle-pin` |
| **AiChat** | Sidebar chat panel with persistent message history, filter chip previews, confirm/dismiss workflow, keyboard shortcuts, and clear-chat button. | — | `apply-filters`, `remove-filters`, `clear-filters` |

### Component Tree

```
App.vue
 ├── TopBar
 ├── [chart-chat-row]                    ← flex row (70/30 split, 420px height)
 │    ├── ScatterChart                   ← receives filteredStocks
 │    └── [sidebar-section]              ← flex column, overflow: hidden
 │         ├── FilterBar                 ← max 50% height, scrollable body
 │         └── AiChat                    ← flex: 1, shrinks when filters expand
 └── [content]
      └── StockTable                     ← receives filteredStocks
```

---

## Composables (State Management)

### `useStocks()`

Centralised stock data, filtering, and persistence logic. Called once in `App.vue`.

```
┌──────────────────────────────────────────────────────────┐
│ useStocks()                                               │
│                                                           │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ stocks   │  │ filterChips  │  │ aiFilters         │  │
│  │ ref<[]>  │  │ ref<[]>      │  │ ref<Filters|null> │  │
│  └────┬─────┘  └──────┬───────┘  └────────┬──────────┘  │
│       │               │                   │              │
│       └───────────────┼───────────────────┘              │
│                       ▼                                   │
│  ┌──────────────────────────────────────┐                │
│  │ filteredStocks (computed)             │                │
│  │  1. chip groups: OR within, AND across│                │
│  │  2. AI filters: categorical + numeric │                │
│  └──────────────────────────────────────┘                │
│                                                           │
│  fetchStocks()      → GET /api/stocks → stocks.value     │
│  applyAiFilters()   → merge incoming into aiFilters      │
│  removeAiFilters()  → subtract matching from aiFilters   │
│  clearAllFilters()  → reset filterChips + aiFilters      │
│  restoreFilters()   → load aiFilters from localStorage   │
│  _persistFilters()  → save aiFilters to localStorage     │
│                       (key: "stock-universe-filters")    │
│                                                           │
│  aiFiltersToChips() → convert UniverseFilters to chips   │
│  isLoading, error, pinnedCodes, pinnedStocks             │
└──────────────────────────────────────────────────────────┘
```

### `useChat(onFilterAction)`

Chat state with localStorage persistence and confirmation workflow. Called inside `AiChat.vue`.

```
┌──────────────────────────────────────────────────────────┐
│ useChat(onFilterAction)                                   │
│                                                           │
│  messages: ref<ChatMessage[]>                            │
│    ← loaded from localStorage on init                    │
│    → persisted on every mutation                         │
│    (key: "stock-universe-chat")                          │
│                                                           │
│  isSending: ref<boolean>                                 │
│                                                           │
│  sendMessage(text)                                       │
│    → push user msg                                       │
│    → POST /api/chat { messages: full history }           │
│    → push assistant msg with:                            │
│        pendingFilters, action, filterStatus="pending"    │
│                                                           │
│  confirmFilters(index)                                   │
│    → set filterStatus = "applied"                        │
│    → call onFilterAction(action, filters)                │
│                                                           │
│  dismissFilters(index)                                   │
│    → set filterStatus = "dismissed"                      │
│                                                           │
│  clearMessages()                                         │
│    → wipe messages ref + localStorage                    │
└──────────────────────────────────────────────────────────┘
```

### `ChatMessage` Interface

```typescript
interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  pendingFilters?: UniverseFilters | null;   // filters the AI wants to apply/remove
  action?: "add" | "remove" | "clear" | "none";
  filterStatus?: "pending" | "applied" | "dismissed";
}
```

---

## Keyboard Shortcuts (AiChat)

| Key     | Condition                     | Action                              |
|---------|-------------------------------|-------------------------------------|
| `Enter` | Input has text                | Send message                        |
| `Enter` | Input empty + pending suggestion | Accept (apply) the suggestion    |
| `Esc`   | Input empty + pending suggestion | Dismiss the suggestion            |

- The last pending suggestion is **highlighted** with a green glow when the input is empty
- Highlight disappears when the user starts typing
- Input placeholder changes to "Enter to apply · Esc to dismiss" when a suggestion is pending

---

## Backend

### Request Routing

```
main.py
 ├── CORSMiddleware (allow localhost origins)
 ├── GET  /api/health → { status: "ok" }
 ├── routers/stocks.py
 │    └── GET /api/stocks
 │         → load universe_master.json (cached in memory)
 │         → list[Stock] (snake_case via response_model_by_alias=False)
 └── routers/chat.py
      └── POST /api/chat
           → accept { messages: [{role, content}, ...] }
           → agent.process_message(messages)
           → ChatResponse { reply, action, filters }
```

### Pydantic Schemas

```
┌────────────────────────────────────────┐
│ Stock                                  │
│  code, name, ticker, currency          │
│  country, industry, sub_industry       │
│  exchange, ric, isin                   │
│  price, market_cap, pe_ratio, pb_ratio │
│  dividend_yield, eps, roe, turnover    │
│  return_1m/3m/6m/1y/ytd               │
│  volatility_1y, sharpe_1y,            │
│  max_drawdown_1y                       │
└────────────────────────────────────────┘

┌──────────────────────┐   ┌──────────────────────────────┐
│ ChatRequest          │   │ ChatResponse                 │
│  messages: list[     │   │  reply: str                  │
│    {role, content}   │   │  action: str                 │
│  ]                   │   │    ("add"|"remove"|"clear"|  │
│                      │   │     "none")                  │
└──────────────────────┘   │  filters: UniverseFilters?   │
                           └──────────────────────────────┘

┌────────────────────────────────────────┐
│ UniverseFilters                        │
│  countries, industries,                │
│  sub_industries, currencies, exchanges │
│  search                               │
│  price, market_cap, pe_ratio, ...      │  ← NumericRange {min, max}
│  return_1m, ..., volatility_1y, ...    │
└────────────────────────────────────────┘
```

### AI Agent (agent.py)

- Uses **DeepSeek API** (OpenAI-compatible client) with `DEEPSEEK_API_KEY` from `.env`
- **JSON-object mode** for reliable structured output
- System prompt instructs the LLM to return `{ reply, action, filters }`
- Accepts full conversation history (capped at 20 messages) for context
- Detects four action types: `add`, `remove`, `clear`, `none`
- Validates filter output against `UniverseFilters` via Pydantic

### Data Source

`universe_master.json` — 40k+ stock records loaded from the project root. Cached in memory (`_stocks_cache`) on first request for fast subsequent access.

---

## Persistence (localStorage)

| Key                      | Contents                        | Managed By     |
|--------------------------|---------------------------------|----------------|
| `stock-universe-chat`    | Full chat message history (including pendingFilters, action, filterStatus) | `useChat.ts` |
| `stock-universe-filters` | Current `aiFilters` object      | `useStocks.ts` |

- Chat history survives page reloads; cleared via the trash icon button
- AI filters are restored on mount via `restoreFilters()`
- Both are wiped when the user clicks "clear chat" (which also emits `clear-filters`)

---

## Filter Chip System

### Types

```typescript
interface FilterChip {
  category: string;   // "Country", "Industry", "Price", etc.
  value: string;      // "United States", "≤ 50", etc.
}

interface UniverseFilters {
  countries?: string[];         // categorical
  industries?: string[];
  sub_industries?: string[];
  currencies?: string[];
  exchanges?: string[];
  search?: string;              // text search
  price?: NumericRange;         // { min, max }
  market_cap?: NumericRange;
  pe_ratio?: NumericRange;
  // ... 15+ numeric range fields
}
```

### Filtering Logic

```
Manual chips (FilterBar):
  Group by category → OR within category, AND across categories

AI filters (UniverseFilters):
  Categorical: array membership check
  Numeric: range bounds (min/max)
  Text: substring match on code/name

Combined: stocks must pass BOTH manual chips AND AI filters
```

### Filter Merge / Subtract (AI)

```
applyAiFilters(incoming):
  Categorical → union (deduplicated)
  Numeric     → overwrite with incoming range
  
removeAiFilters(toRemove):
  Categorical → set difference
  Numeric     → clear the range
  If nothing remains → aiFilters = null
```

---

## Performance Considerations

| Concern | Strategy |
|---------|----------|
| **40k rows in table** | AG Grid with client-side row model. Only visible rows rendered to DOM. Pagination (10/50/100). |
| **Sorting speed** | AG Grid handles sorting internally. `computed` caches filtered data. |
| **Filter recomputation** | `filteredStocks` is a `computed` — single pass through array, only recalculates on change. |
| **Large JSON load** | Backend caches `universe_master.json` in memory after first load (`_stocks_cache`). |
| **Autocomplete suggestions** | Capped at 25 results. Category index computed once from all stocks. |
| **Chart re-renders** | amcharts5 receives filtered dataset; re-renders only on data change. |
| **Chat history** | localStorage-based. History sent to DeepSeek capped at 20 messages. |

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend framework | Vue 3 (Composition API) | Reactive UI components |
| Build tool | Vite | Fast dev server with HMR, API proxy |
| Charts | amcharts5 | Scatter plot with industry grouping |
| Data table | AG Grid | Sortable, paginated stock table |
| Styling | SCSS + Bootstrap (overrides) | Layout and component styles |
| Icons | FontAwesome | UI icons |
| Language | TypeScript | Type safety across frontend |
| Backend framework | FastAPI | High-performance async API |
| Validation | Pydantic v2 | Request/response schema validation |
| AI/LLM | DeepSeek (via OpenAI client) | Natural-language filter extraction |
| Server | Uvicorn | ASGI server with hot reload |
| Data | Static JSON (40k records) | Stock universe dataset |
| Persistence | localStorage | Chat history + AI filter state |
