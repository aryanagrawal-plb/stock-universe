<script setup lang="ts">
import { ref, computed, watch } from "vue";
import type { Stock } from "../types/stock";

type SortKey = keyof Stock;
type SortDir = "asc" | "desc";

const PAGE_SIZES = [10, 50, 100] as const;

const props = defineProps<{
  stocks: Stock[];
  isLoading: boolean;
  error: string | null;
}>();

const sortKey = ref<SortKey>("code");
const sortDir = ref<SortDir>("asc");
const pageSize = ref<number>(50);
const currentPage = ref(1);

// Reset to page 1 when the input dataset changes
watch(() => props.stocks, () => { currentPage.value = 1; });

const columns: { key: SortKey; label: string; numeric: boolean }[] = [
  { key: "code", label: "Ticker", numeric: false },
  { key: "name", label: "Name", numeric: false },
  { key: "country", label: "Country", numeric: false },
  { key: "industry", label: "Industry", numeric: false },
  { key: "currency", label: "Ccy", numeric: false },
  { key: "price", label: "Price", numeric: true },
  { key: "market_cap", label: "Mkt Cap", numeric: true },
  { key: "pe_ratio", label: "P/E", numeric: true },
  { key: "pb_ratio", label: "P/B", numeric: true },
  { key: "dividend_yield", label: "Div Yld", numeric: true },
  { key: "return_ytd", label: "YTD %", numeric: true },
  { key: "volatility_1y", label: "Vol 1Y", numeric: true },
];

const sortedStocks = computed<Stock[]>(() => {
  const key = sortKey.value;
  const dir = sortDir.value === "asc" ? 1 : -1;
  const data = props.stocks;
  if (data.length === 0) return data;

  return data.slice().sort((a, b) => {
    const av = a[key];
    const bv = b[key];
    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;
    if (typeof av === "string") return av.localeCompare(bv as string) * dir;
    return ((av as number) - (bv as number)) * dir;
  });
});

const totalPages = computed(() =>
  Math.max(1, Math.ceil(sortedStocks.value.length / pageSize.value))
);

const pagedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return sortedStocks.value.slice(start, start + pageSize.value);
});

const pageStart = computed(() =>
  sortedStocks.value.length === 0
    ? 0
    : (currentPage.value - 1) * pageSize.value + 1
);

const pageEnd = computed(() =>
  Math.min(currentPage.value * pageSize.value, sortedStocks.value.length)
);

function toggleSort(key: SortKey): void {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
  } else {
    sortKey.value = key;
    sortDir.value = "asc";
  }
  currentPage.value = 1;
}

function changePageSize(size: number): void {
  pageSize.value = size;
  currentPage.value = 1;
}

function formatMarketCap(value: number | null): string {
  if (value == null) return "—";
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}T`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}B`;
  return `$${value.toFixed(0)}M`;
}

function formatPct(value: number | null): string {
  if (value == null) return "—";
  return `${value >= 0 ? "+" : ""}${(value * 100).toFixed(1)}%`;
}

function formatNum(value: number | null, decimals = 1): string {
  if (value == null) return "—";
  return value.toFixed(decimals);
}
</script>

<template>
  <div class="stock-table-container">
    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="isLoading" class="loading-msg">Loading...</div>

    <div class="table-wrapper">
      <table class="stock-table">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :class="{ num: col.numeric, sortable: true, active: sortKey === col.key }"
              @click="toggleSort(col.key)"
            >
              <span class="th-content">
                {{ col.label }}
                <span v-if="sortKey === col.key" class="sort-arrow">
                  {{ sortDir === "asc" ? "▲" : "▼" }}
                </span>
                <span v-else class="sort-arrow muted">▲</span>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="stock in pagedStocks" :key="stock.code">
            <td class="ticker">{{ stock.code }}</td>
            <td class="name-cell">{{ stock.name }}</td>
            <td>{{ stock.country }}</td>
            <td>
              <span class="sector-badge">{{ stock.industry }}</span>
            </td>
            <td>{{ stock.currency }}</td>
            <td class="num">{{ stock.price != null ? stock.price.toFixed(2) : "—" }}</td>
            <td class="num">{{ formatMarketCap(stock.market_cap) }}</td>
            <td class="num">{{ formatNum(stock.pe_ratio) }}</td>
            <td class="num">{{ formatNum(stock.pb_ratio) }}</td>
            <td class="num">{{ stock.dividend_yield != null ? stock.dividend_yield.toFixed(2) + "%" : "—" }}</td>
            <td class="num" :class="{ positive: (stock.return_ytd ?? 0) > 0, negative: (stock.return_ytd ?? 0) < 0 }">
              {{ formatPct(stock.return_ytd) }}
            </td>
            <td class="num">{{ formatNum(stock.volatility_1y, 2) }}</td>
          </tr>
          <tr v-if="!isLoading && stocks.length === 0">
            <td :colspan="columns.length" class="empty-msg">No stocks match filters</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="sortedStocks.length > 0" class="table-footer">
      <div class="page-size-picker">
        <span class="footer-label">Show</span>
        <button
          v-for="size in PAGE_SIZES"
          :key="size"
          class="size-btn"
          :class="{ active: pageSize === size }"
          @click="changePageSize(size)"
        >
          {{ size }}
        </button>
      </div>

      <span class="page-info">
        {{ pageStart }}–{{ pageEnd }} of {{ sortedStocks.length.toLocaleString() }}
      </span>

      <div class="page-nav">
        <button
          class="nav-btn"
          :disabled="currentPage <= 1"
          @click="currentPage--"
        >
          ‹
        </button>
        <span class="page-num">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="nav-btn"
          :disabled="currentPage >= totalPages"
          @click="currentPage++"
        >
          ›
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stock-table-container {
  padding: 16px;
}

.table-wrapper {
  overflow-x: auto;
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.stock-table th {
  text-align: left;
  padding: 8px 10px;
  font-weight: 500;
  color: var(--color-text-muted);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.stock-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: color 0.15s;
}

.stock-table th.sortable:hover {
  color: var(--color-text);
}

.stock-table th.active {
  color: var(--color-accent);
}

.th-content {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.sort-arrow {
  font-size: 8px;
  line-height: 1;
}

.sort-arrow.muted {
  opacity: 0;
}

.stock-table th.sortable:hover .sort-arrow.muted {
  opacity: 0.3;
}

.stock-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.stock-table tbody tr:hover {
  background: var(--color-surface-hover);
}

.stock-table .num {
  text-align: right;
  font-family: var(--font-mono);
  font-size: 12px;
}

.ticker {
  font-weight: 600;
  color: var(--color-accent);
  font-family: var(--font-mono);
}

.name-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sector-badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 11px;
  border-radius: 99px;
  background: var(--color-surface-hover);
  color: var(--color-text-muted);
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.positive {
  color: var(--color-success);
}

.negative {
  color: var(--color-danger);
}

.error-msg {
  padding: 8px 12px;
  margin-bottom: 8px;
  color: var(--color-danger);
  font-size: 13px;
}

.loading-msg {
  padding: 8px 12px;
  margin-bottom: 8px;
  color: var(--color-text-muted);
  font-size: 13px;
}

.empty-msg {
  text-align: center;
  color: var(--color-text-muted);
  padding: 24px 12px !important;
}

.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0 0;
  border-top: 1px solid var(--color-border);
  margin-top: 4px;
}

.page-size-picker {
  display: flex;
  align-items: center;
  gap: 4px;
}

.footer-label {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-right: 2px;
}

.size-btn {
  padding: 3px 8px;
  font-size: 11px;
  font-family: var(--font-sans);
  color: var(--color-text-muted);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.size-btn:hover {
  color: var(--color-text);
  border-color: var(--color-text-muted);
}

.size-btn.active {
  color: white;
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.page-info {
  font-size: 11px;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.page-nav {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-family: var(--font-sans);
  color: var(--color-text-muted);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.nav-btn:hover:not(:disabled) {
  color: var(--color-text);
  border-color: var(--color-text-muted);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-num {
  font-size: 11px;
  color: var(--color-text-muted);
  white-space: nowrap;
  min-width: 40px;
  text-align: center;
}
</style>
