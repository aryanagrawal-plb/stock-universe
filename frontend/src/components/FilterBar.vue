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

const categoryIndex = computed(() => {
  const allStocks = props.stocks;
  return [
    { category: "Country", values: [...new Set(allStocks.map((s) => s.country ?? ""))].sort() },
    { category: "Industry", values: [...new Set(allStocks.map((s) => s.industry ?? ""))].sort() },
    { category: "Sub-Industry", values: [...new Set(allStocks.map((s) => s.sub_industry ?? ""))].sort() },
    { category: "Exchange", values: [...new Set(allStocks.map((s) => s.exchange ?? ""))].sort() },
    { category: "Currency", values: [...new Set(allStocks.map((s) => s.currency ?? ""))].sort() },
    { category: "Ticker", values: allStocks.map((s) => s.code) },
    { category: "Name", values: [...new Set(allStocks.map((s) => s.name ?? ""))] },
  ];
});

const suggestions = computed<Suggestion[]>(() => {
  const query = searchText.value.toLowerCase().trim();
  if (!query) return [];

  const results: Suggestion[] = [];

  for (const { category, values } of categoryIndex.value) {
    for (const value of values) {
      if (value.toLowerCase().includes(query)) {
        const alreadySelected = props.filterChips.some(
          (c) => c.category === category && c.value === value
        );
        if (!alreadySelected) {
          results.push({ category, value, display: value });
        }
      }
      if (results.length >= 25) break;
    }
    if (results.length >= 25) break;
  }

  return results;
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
  <div class="pl-filter-panel" :class="{ expanded: isExpanded }">
    <div class="pl-filter-toggle-wrapper">
      <button class="pl-filter-toggle" @click="isExpanded = !isExpanded">
        <icon icon="filter" class="pl-filter-icon" />
        <span class="pl-filter-label">Filters</span>
        <span v-if="filterChips.length > 0" class="pl-filter-badge">{{
          filterChips.length
        }}</span>
        <icon
          :icon="isExpanded ? 'chevron-up' : 'chevron-down'"
          class="pl-filter-chevron"
        />
      </button>
      <span class="pl-result-popover">{{ resultCount.toLocaleString() }} results</span>
    </div>

    <div v-if="isExpanded" class="pl-filter-body">
      <div class="pl-search-wrapper">
        <div class="pl-input-box" @click="focusInput">
          <span
            v-for="(chip, i) in filterChips"
            :key="`${chip.category}:${chip.value}:${i}`"
            class="pl-chip"
          >
            <span class="pl-chip-cat">{{ chip.category }}:</span>
            <span class="pl-chip-val">{{ chip.value }}</span>
            <button
              class="pl-chip-remove"
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
            class="pl-search-input"
            :placeholder="filterChips.length === 0 ? 'Country, Industry, Ticker...' : ''"
            @input="handleInput"
            @focus="handleFocus"
            @blur="handleBlur"
            @keydown.delete="handleBackspace"
          />
          <button
            v-if="filterChips.length > 0"
            class="pl-clear-all"
            title="Clear all filters"
            @mousedown.prevent="clearAll"
          >
            &times;
          </button>
        </div>
        <div v-if="showDropdown && suggestions.length > 0" class="pl-dropdown shadow">
          <template
            v-for="[category, items] of groupedSuggestions"
            :key="category"
          >
            <div class="pl-dropdown-cat">{{ category }}</div>
            <button
              v-for="item in items"
              :key="`${item.category}:${item.value}`"
              class="pl-dropdown-item"
              @mousedown.prevent="selectSuggestion(item)"
            >
              <span class="pl-dropdown-item-cat">{{ item.category }}:</span>
              <span class="pl-dropdown-item-val">{{ item.display }}</span>
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.pl-filter-panel {
  flex-shrink: 0;
  border-bottom: 1px solid #d8dde2;
  background: #fff;
  max-height: 50%;
  display: flex;
  flex-direction: column;
  overflow: visible;
  position: relative;
  z-index: 10;
}

.pl-filter-toggle-wrapper {
  position: relative;

  &:hover .pl-result-popover {
    opacity: 1;
    visibility: visible;
  }
}

.pl-result-popover {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 400;
  color: #495057;
  background: #fff;
  border: 1px solid #d8dde2;
  border-radius: 0.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.15s, visibility 0.15s;
  pointer-events: none;
  z-index: 10;
}

.pl-filter-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 16px;
  font-size: 13px;
  font-family: 'Fira Sans', sans-serif;
  font-weight: 600;
  color: #495057;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.1s;

  &:hover {
    background: #eff2f6;
  }
}

.pl-filter-icon {
  color: #495057;
  font-size: 12px;
}

.pl-filter-label {
  flex-shrink: 0;
}

.pl-filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  background: #1a85a1;
  border-radius: 99px;
}

.pl-filter-chevron {
  flex-shrink: 0;
  font-size: 10px;
  color: #bbc1c7;
}

.pl-filter-body {
  padding: 0 16px 12px;
  min-height: 0;
}

.pl-search-wrapper {
  position: relative;
}

.pl-input-box {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  padding: 5px 8px;
  max-height: 80px;
  overflow-y: auto;
  background: #f5f7fa;
  border: 1px solid #d8dde2;
  border-radius: 0.25rem;
  cursor: text;
  transition: border-color 0.15s, box-shadow 0.15s;

  &:focus-within {
    border-color: #1a85a1;
    box-shadow: 0 0 0 3px rgba(26, 133, 161, 0.15);
  }
}

.pl-search-input {
  flex: 1;
  min-width: 60px;
  padding: 3px 0;
  font-size: 13px;
  font-family: 'Fira Sans', sans-serif;
  color: #4b4b4b;
  background: transparent;
  border: none;
  outline: none;

  &::placeholder {
    color: #bbc1c7;
  }
}

.pl-chip {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 8px;
  font-size: 11px;
  color: #1a85a1;
  background: rgba(26, 133, 161, 0.08);
  border: 1px solid rgba(26, 133, 161, 0.15);
  border-radius: 99px;
  white-space: nowrap;
  flex-shrink: 0;
}

.pl-chip-cat {
  color: #bbc1c7;
  font-weight: 500;
}

.pl-chip-val {
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.pl-chip-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  font-size: 13px;
  line-height: 1;
  color: #bbc1c7;
  background: none;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
  transition: color 0.15s, background 0.15s;

  &:hover {
    color: #d9534f;
    background: rgba(217, 83, 79, 0.1);
  }
}

.pl-clear-all {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  margin-left: auto;
  font-size: 14px;
  line-height: 1;
  color: #bbc1c7;
  background: none;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: color 0.15s, background 0.15s;

  &:hover {
    color: #d9534f;
    background: rgba(217, 83, 79, 0.1);
  }
}

.pl-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 220px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #d8dde2;
  border-radius: 0.25rem;
  z-index: 200;
}

.pl-dropdown-cat {
  padding: 6px 10px 2px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #bbc1c7;
}

.pl-dropdown-item {
  display: flex;
  align-items: center;
  gap: 5px;
  width: 100%;
  padding: 6px 10px;
  font-size: 12px;
  font-family: 'Fira Sans', sans-serif;
  color: #4b4b4b;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.1s;

  &:hover {
    background: #eff2f6;
  }
}

.pl-dropdown-item-cat {
  color: #bbc1c7;
  font-size: 10px;
  flex-shrink: 0;
}

.pl-dropdown-item-val {
  color: #4b4b4b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
