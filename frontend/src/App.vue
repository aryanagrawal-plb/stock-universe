<script setup lang="ts">
import { onMounted } from "vue";
import TopBar from "./components/TopBar.vue";
import FilterBar from "./components/FilterBar.vue";
import AiChat from "./components/AiChat.vue";
import ScatterChart from "./components/ScatterChart.vue";
import StockTable from "./components/StockTable.vue";
import { useStocks } from "./composables/useStocks";

const {
  stocks,
  filteredStocks,
  filterChips,
  isLoading,
  error,
  fetchStocks,
  pinnedCodes,
  togglePin,
} = useStocks();

onMounted(() => fetchStocks());
</script>

<template>
  <div class="pl-app">
    <TopBar />
    <div class="pl-main">
      <div class="pl-chart-chat-row">
        <section class="pl-chart-section">
          <ScatterChart :stocks="filteredStocks" />
        </section>
        <aside class="pl-sidebar-section">
          <FilterBar
            :stocks="stocks"
            :filter-chips="filterChips"
            :result-count="filteredStocks.length"
            @update:filter-chips="filterChips = $event"
          />
          <AiChat />
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
</style>
