<script setup lang="ts">
import { ref, computed } from "vue";
import type { Stock, FilterChip } from "../types/stock";

const props = defineProps<{
  stocks: Stock[];
  filterChips: FilterChip[];
  resultCount: number;
}>();

const emit = defineEmits<{
  "update:filterChips": [chips: FilterChip[]];
}>();

const isExpanded = ref(false);
const searchText = ref("");
const showDropdown = ref(false);
const inputEl = ref<HTMLInputElement | null>(null);

interface Suggestion {
  category: string;
  value: string;
  display: string;
}

function formatMktCap(value: number): string {
  if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  return `$${value}`;
}

function formatVol(value: number): string {
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
  return String(value);
}

const suggestions = computed<Suggestion[]>(() => {
  const query = searchText.value.toLowerCase().trim();
  if (!query) return [];

  const allStocks = props.stocks;
  const results: Suggestion[] = [];

  const categoryValues: {
    category: string;
    entries: { value: string; display: string }[];
  }[] = [
    {
      category: "Sector",
      entries: [...new Set(allStocks.map((s) => s.sector))].map((v) => ({
        value: v,
        display: v,
      })),
    },
    {
      category: "Ticker",
      entries: [...new Set(allStocks.map((s) => s.ticker))].map((v) => ({
        value: v,
        display: v,
      })),
    },
    {
      category: "Name",
      entries: [...new Set(allStocks.map((s) => s.name))].map((v) => ({
        value: v,
        display: v,
      })),
    },
    {
      category: "Price",
      entries: [...new Set(allStocks.map((s) => s.price.toFixed(2)))].map(
        (v) => ({ value: v, display: `$${v}` })
      ),
    },
    {
      category: "Market Cap",
      entries: [
        ...new Set(allStocks.map((s) => formatMktCap(s.market_cap))),
      ].map((v) => ({ value: v, display: v })),
    },
    {
      category: "P/E",
      entries: [
        ...new Set(
          allStocks
            .filter((s) => s.pe_ratio != null)
            .map((s) => s.pe_ratio!.toFixed(1))
        ),
      ].map((v) => ({ value: v, display: v })),
    },
    {
      category: "Div Yield",
      entries: [
        ...new Set(
          allStocks
            .filter((s) => s.dividend_yield != null)
            .map((s) => s.dividend_yield!.toFixed(2) + "%")
        ),
      ].map((v) => ({ value: v, display: v })),
    },
    {
      category: "Volume",
      entries: [...new Set(allStocks.map((s) => formatVol(s.volume)))].map(
        (v) => ({ value: v, display: v })
      ),
    },
  ];

  for (const { category, entries } of categoryValues) {
    for (const { value, display } of entries) {
      if (
        display.toLowerCase().includes(query) ||
        value.toLowerCase().includes(query)
      ) {
        const alreadySelected = props.filterChips.some(
          (c) => c.category === category && c.value === value
        );
        if (!alreadySelected) {
          results.push({ category, value, display });
        }
      }
    }
  }

  return results.slice(0, 25);
});

const groupedSuggestions = computed(() => {
  const groups = new Map<string, Suggestion[]>();
  for (const s of suggestions.value) {
    const list = groups.get(s.category) ?? [];
    list.push(s);
    groups.set(s.category, list);
  }
  return groups;
});

function selectSuggestion(suggestion: Suggestion): void {
  emit("update:filterChips", [
    ...props.filterChips,
    { category: suggestion.category, value: suggestion.value },
  ]);
  searchText.value = "";
  showDropdown.value = false;
  inputEl.value?.focus();
}

function removeChip(index: number): void {
  emit(
    "update:filterChips",
    props.filterChips.filter((_, i) => i !== index)
  );
  inputEl.value?.focus();
}

function clearAll(): void {
  emit("update:filterChips", []);
  inputEl.value?.focus();
}

function focusInput(): void {
  inputEl.value?.focus();
}

function handleFocus(): void {
  if (searchText.value.trim()) {
    showDropdown.value = true;
  }
}

function handleBlur(): void {
  setTimeout(() => {
    showDropdown.value = false;
  }, 200);
}

function handleInput(): void {
  showDropdown.value = searchText.value.trim().length > 0;
}

function handleBackspace(): void {
  if (searchText.value === "" && props.filterChips.length > 0) {
    removeChip(props.filterChips.length - 1);
  }
}
</script>

<template>
  <div class="filter-panel" :class="{ expanded: isExpanded }">
    <button class="filter-toggle" @click="isExpanded = !isExpanded">
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
      </svg>
      <span class="filter-toggle-text">Filters</span>
      <span v-if="filterChips.length > 0" class="filter-badge">{{
        filterChips.length
      }}</span>
      <span class="result-count">{{ resultCount }} results</span>
      <svg
        class="filter-chevron"
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </button>

    <div v-if="isExpanded" class="filter-body">
      <div class="search-wrapper">
        <div class="input-box" @click="focusInput">
          <span
            v-for="(chip, i) in filterChips"
            :key="`${chip.category}:${chip.value}:${i}`"
            class="chip"
          >
            <span class="chip-cat">{{ chip.category }}:</span>
            <span class="chip-val">{{ chip.value }}</span>
            <button
              class="chip-remove"
              title="Remove filter"
              @mousedown.prevent="removeChip(i)"
            >
              &times;
            </button>
          </span>
          <input
            ref="inputEl"
            v-model="searchText"
            type="text"
            class="search-input"
            :placeholder="filterChips.length === 0 ? 'Search filters...' : ''"
            @input="handleInput"
            @focus="handleFocus"
            @blur="handleBlur"
            @keydown.delete="handleBackspace"
          />
          <button
            v-if="filterChips.length > 0"
            class="clear-all"
            title="Clear all filters"
            @mousedown.prevent="clearAll"
          >
            &times;
          </button>
        </div>
        <div v-if="showDropdown && suggestions.length > 0" class="dropdown">
          <template
            v-for="[category, items] of groupedSuggestions"
            :key="category"
          >
            <div class="dropdown-category">{{ category }}</div>
            <button
              v-for="item in items"
              :key="`${item.category}:${item.value}`"
              class="dropdown-item"
              @mousedown.prevent="selectSuggestion(item)"
            >
              <span class="dropdown-item-cat">{{ item.category }}:</span>
              <span class="dropdown-item-val">{{ item.display }}</span>
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-panel {
  flex-shrink: 0;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.filter-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 14px;
  font-size: 13px;
  font-family: var(--font-sans);
  font-weight: 600;
  color: var(--color-text);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.1s;
}

.filter-toggle:hover {
  background: var(--color-surface-hover);
}

.filter-toggle-text {
  flex-shrink: 0;
}

.filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 10px;
  font-weight: 700;
  color: white;
  background: var(--color-primary);
  border-radius: 99px;
}

.result-count {
  flex: 1;
  text-align: right;
  font-size: 11px;
  font-weight: 400;
  color: var(--color-text-muted);
}

.filter-chevron {
  flex-shrink: 0;
  transition: transform 0.2s;
}

.expanded .filter-chevron {
  transform: rotate(180deg);
}

.filter-body {
  padding: 0 14px 10px;
}

.search-wrapper {
  position: relative;
}

.input-box {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  padding: 5px 8px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  cursor: text;
  transition: border-color 0.15s;
}

.input-box:focus-within {
  border-color: var(--color-primary);
}

.search-input {
  flex: 1;
  min-width: 60px;
  padding: 2px 0;
  font-size: 12px;
  font-family: var(--font-sans);
  color: var(--color-text);
  background: transparent;
  border: none;
  outline: none;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 1px 6px;
  font-size: 11px;
  color: var(--color-text);
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  border-radius: 99px;
  white-space: nowrap;
  flex-shrink: 0;
}

.chip-cat {
  color: var(--color-text-muted);
}

.chip-val {
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chip-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  font-size: 13px;
  line-height: 1;
  color: var(--color-text-muted);
  background: none;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
  transition: color 0.15s, background 0.15s;
}

.chip-remove:hover {
  color: var(--color-danger);
  background: rgba(255, 107, 107, 0.15);
}

.clear-all {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  margin-left: auto;
  font-size: 14px;
  line-height: 1;
  color: var(--color-text-muted);
  background: none;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: color 0.15s, background 0.15s;
}

.clear-all:hover {
  color: var(--color-danger);
  background: rgba(255, 107, 107, 0.15);
}

.dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 220px;
  overflow-y: auto;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 200;
}

.dropdown-category {
  padding: 5px 10px 2px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 5px;
  width: 100%;
  padding: 5px 10px;
  font-size: 12px;
  font-family: var(--font-sans);
  color: var(--color-text);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.1s;
}

.dropdown-item:hover {
  background: var(--color-surface-hover);
}

.dropdown-item-cat {
  color: var(--color-text-muted);
  font-size: 10px;
  flex-shrink: 0;
}

.dropdown-item-val {
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
