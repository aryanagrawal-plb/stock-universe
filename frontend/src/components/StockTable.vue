<script setup lang="ts">
import { onMounted } from "vue";
import { useStocks } from "../composables/useStocks";

const { stocks, filters, isLoading, error, fetchStocks } = useStocks();

const sectors = [
  "",
  "Technology",
  "Financials",
  "Healthcare",
  "Energy",
  "Consumer Discretionary",
  "Consumer Staples",
];

function formatMarketCap(value: number): string {
  if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  return `$${value}`;
}

function formatVolume(value: number): string {
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
  return String(value);
}

onMounted(() => fetchStocks());
</script>

<template>
  <div class="stock-table-container">
    <div class="filters">
      <input
        v-model="filters.search"
        type="text"
        placeholder="Search ticker or name..."
        class="filter-input"
      />
      <select v-model="filters.sector" class="filter-select">
        <option value="">All Sectors</option>
        <option v-for="s in sectors.slice(1)" :key="s" :value="s">{{ s }}</option>
      </select>
      <input
        v-model.number="filters.minPrice"
        type="number"
        placeholder="Min price"
        class="filter-input filter-input--small"
      />
      <input
        v-model.number="filters.maxPrice"
        type="number"
        placeholder="Max price"
        class="filter-input filter-input--small"
      />
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="isLoading" class="loading-msg">Loading...</div>

    <div class="table-wrapper">
      <table class="stock-table">
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Name</th>
            <th>Sector</th>
            <th class="num">Price</th>
            <th class="num">Mkt Cap</th>
            <th class="num">P/E</th>
            <th class="num">Div Yield</th>
            <th class="num">Volume</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="stock in stocks" :key="stock.ticker">
            <td class="ticker">{{ stock.ticker }}</td>
            <td>{{ stock.name }}</td>
            <td>
              <span class="sector-badge">{{ stock.sector }}</span>
            </td>
            <td class="num">${{ stock.price.toFixed(2) }}</td>
            <td class="num">{{ formatMarketCap(stock.market_cap) }}</td>
            <td class="num">{{ stock.pe_ratio?.toFixed(1) ?? "—" }}</td>
            <td class="num">{{ stock.dividend_yield != null ? stock.dividend_yield.toFixed(2) + "%" : "—" }}</td>
            <td class="num">{{ formatVolume(stock.volume) }}</td>
          </tr>
          <tr v-if="!isLoading && stocks.length === 0">
            <td colspan="8" class="empty-msg">No stocks match filters</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.stock-table-container {
  padding: 16px;
}

.filters {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.filter-input,
.filter-select {
  padding: 7px 12px;
  font-size: 13px;
  font-family: var(--font-sans);
  color: var(--color-text);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  outline: none;
  transition: border-color 0.15s;
}

.filter-input:focus,
.filter-select:focus {
  border-color: var(--color-primary);
}

.filter-input--small {
  width: 110px;
}

.filter-select {
  cursor: pointer;
}

.filter-select option {
  background: var(--color-surface);
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
  padding: 8px 12px;
  font-weight: 500;
  color: var(--color-text-muted);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.stock-table td {
  padding: 10px 12px;
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

.sector-badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 11px;
  border-radius: 99px;
  background: var(--color-surface-hover);
  color: var(--color-text-muted);
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
</style>
