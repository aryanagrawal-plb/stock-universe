<script setup lang="ts">
import { onMounted, computed, ref } from "vue";
import TopBar from "./components/TopBar.vue";
import FilterBar from "./components/FilterBar.vue";
import AiChat from "./components/AiChat.vue";
import ScatterChart from "./components/ScatterChart.vue";
import StockTable from "./components/StockTable.vue";
import { useStocks, aiFiltersToChips } from "./composables/useStocks";
import type { UniverseFilters, FilterChip } from "./types/stock";

const selectedUniverse = ref<string>("Equities");

const {
  stocks,
  filteredStocks,
  filterChips,
  aiFilters,
  isLoading,
  error,
  fetchStocks,
  pinnedCodes,
  togglePin,
  applyAiFilters,
  removeAiFilters,
  clearAiFilters,
  clearAllFilters,
  restoreFilters,
} = useStocks();

const displayChips = computed<FilterChip[]>(() => {
  const manual = filterChips.value;
  const ai = aiFilters.value ? aiFiltersToChips(aiFilters.value) : [];
  return [...manual, ...ai];
});

const totalResultCount = computed(() => filteredStocks.value.length);

function handleUpdateFilterChips(chips: FilterChip[]): void {
  clearAiFilters();
  filterChips.value = chips;
}

function handleAiFilters(filters: UniverseFilters): void {
  applyAiFilters(filters);
}

function handleRemoveFilters(filters: UniverseFilters): void {
  removeAiFilters(filters);
}

function handleClearFilters(): void {
  clearAllFilters();
}

onMounted(() => {
  restoreFilters();
  fetchStocks();
});
</script>

<template>
  <div class="pl-app">
    <TopBar />
    <div class="pl-main">
      <div class="pl-chart-chat-row">
        <section class="pl-chart-section">
          <ScatterChart
            :stocks="filteredStocks"
            :selected-universe="selectedUniverse"
            @update:universe="selectedUniverse = $event"
          />
        </section>
        <aside v-if="selectedUniverse === 'Equities'" class="pl-sidebar-section">
          <FilterBar
            :stocks="stocks"
            :filter-chips="displayChips"
            :result-count="totalResultCount"
            @update:filter-chips="handleUpdateFilterChips"
          />
          <AiChat
            @apply-filters="handleAiFilters"
            @remove-filters="handleRemoveFilters"
            @clear-filters="handleClearFilters"
          />
        </aside>
      </div>
      <main
        :class="[
          'pl-content',
          selectedUniverse !== 'Equities' ? 'pl-content--empty' : '',
        ]"
      >
        <template v-if="selectedUniverse === 'Equities'">
          <section class="pl-table-card">
            <StockTable
              :stocks="filteredStocks"
              :is-loading="isLoading"
              :error="error"
              :pinned-codes="pinnedCodes"
              @toggle-pin="togglePin"
            />
          </section>
        </template>
        <template v-else>
          <div class="pl-empty-page">
            <p class="pl-empty-message">This page is not implemented yet.</p>
            <p class="pl-empty-hint">Select Equities from the dropdown to return.</p>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<style lang="scss">
.pl-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.pl-main {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding-top: 75px;
  overflow: hidden;
}

.pl-chart-chat-row {
  display: flex;
  height: 420px;
  flex-shrink: 0;
  background: #fff;
  border-bottom: 1px solid #d8dde2;
}

.pl-chart-section {
  flex: 7;
  min-width: 0;
  border-right: 1px solid #d8dde2;
}

.pl-sidebar-section {
  flex: 3;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pl-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
}

.pl-table-card {
  background: #f5f7fa;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.pl-content--empty {
  display: flex;
  align-items: center;
  justify-content: center;
}

.pl-empty-page {
  text-align: center;
  color: #495057;
}

.pl-empty-message {
  font-family: 'Fira Sans', sans-serif;
  font-size: 16px;
  margin-bottom: 8px;
}

.pl-empty-hint {
  font-size: 13px;
  color: #8b8fa3;
}
</style>
