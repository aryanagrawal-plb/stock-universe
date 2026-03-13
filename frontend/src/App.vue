<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import TopBar from "./components/TopBar.vue";
import FilterBar from "./components/FilterBar.vue";
import AiChat from "./components/AiChat.vue";
import ScatterChart from "./components/ScatterChart.vue";
import StockTable from "./components/StockTable.vue";
import AlertManagement from "./components/AlertManagement.vue";
import { useStocks, aiFiltersToChips } from "./composables/useStocks";
import type { UniverseFilters, FilterChip } from "./types/stock";

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

const currentView = ref("universe");

function handleNavigate(view: string): void {
  currentView.value = view;
}

onMounted(() => {
  restoreFilters();
  fetchStocks();
});
</script>

<template>
  <div class="pl-app">
    <TopBar :current-view="currentView" @navigate="handleNavigate" />
    <div class="pl-main">
      <template v-if="currentView === 'universe'">
        <div class="pl-chart-chat-row">
          <section class="pl-chart-section">
            <ScatterChart :stocks="filteredStocks" />
          </section>
          <aside class="pl-sidebar-section">
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
        <main class="pl-content">
          <section class="pl-table-card">
            <StockTable
              :stocks="filteredStocks"
              :is-loading="isLoading"
              :error="error"
              :pinned-codes="pinnedCodes"
              @toggle-pin="togglePin"
            />
          </section>
        </main>
      </template>

      <template v-else-if="currentView === 'alerts'">
        <AlertManagement />
      </template>

      <template v-else>
        <div class="pl-placeholder">
          <p>{{ currentView.replace(/-/g, ' ').toUpperCase() }} — Coming soon</p>
        </div>
      </template>
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
  overflow-y: auto;
  padding: 16px;
}

.pl-table-card {
  background: #fff;
  border: 1px solid #d8dde2;
  border-radius: 0.25rem;
  min-height: 400px;
  height: calc(100vh - 75px - 420px - 64px);
  display: flex;
  flex-direction: column;
}

.pl-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-family: "Fira Sans", sans-serif;
  font-size: 1.2rem;
  color: #9ca3af;
}
</style>
