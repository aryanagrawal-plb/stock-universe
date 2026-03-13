<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import TopBar from "./components/TopBar.vue";
import FilterBar from "./components/FilterBar.vue";
import AiChat from "./components/AiChat.vue";
import ScatterChart from "./components/ScatterChart.vue";
import StockTable from "./components/StockTable.vue";
import AlertManagement from "./components/AlertManagement.vue";
import ShortcutHelpOverlay from "./components/ShortcutHelpOverlay.vue";
import SplashScreen from "./components/SplashScreen.vue";
import { useStocks, aiFiltersToChips } from "./composables/useStocks";
import { getShortcutCommand, executeShortcutCommand } from "./composables/shortcuts";
import type { UniverseFilters, FilterChip } from "./types/stock";

const selectedUniverse = ref<string>("Equities");

const {
  stocks,
  filteredStocks,
  filterChips,
  aiFilters,
  universeViewMode,
  isLoading,
  error,
  fetchStocks,
  pinnedCodes,
  togglePin,
  setAiFilters,
  applyAiFilters,
  removeAiFilters,
  clearAiFilters,
  clearAllFilters,
  setUniverseViewMode,
  restoreFilters,
} = useStocks();

const showHelp = ref(false);
const chatRef = ref<InstanceType<typeof AiChat> | null>(null);

function runCommand(code: string): void {
  const command = getShortcutCommand(code);
  if (!command) return;
  executeShortcutCommand(command, {
    clearAllFilters,
    applyAiFilters,
    setUniverseViewMode,
    focusChat: () => chatRef.value?.focusInput(),
    clearChat: () => chatRef.value?.clearHistory(),
    openHelp: () => (showHelp.value = true),
  });
}

function handleCommandBarCommand(code: string): void {
  runCommand(code);
}

function handleGlobalKeydown(e: KeyboardEvent): void {
  if (e.key === "Escape" && showHelp.value) {
    showHelp.value = false;
    e.preventDefault();
    return;
  }

  const target = e.target as HTMLElement;
  const isInput = /^(INPUT|TEXTAREA|SELECT)$/.test(target?.tagName ?? "") || target?.isContentEditable;
  if (isInput) return;

  const key = e.key;
  const command = getShortcutCommand(key);
  if (!command) return;
  e.preventDefault();
  runCommand(key);
}
const showSplash = ref(true);

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

function handleSetFilters(filters: UniverseFilters): void {
  setAiFilters(filters);
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

function handleApplyAlert(filters: UniverseFilters): void {
  setAiFilters(filters);
  currentView.value = "universe";
  selectedUniverse.value = "Equities";
}

onMounted(() => {
  restoreFilters();
  fetchStocks();
  document.addEventListener("keydown", handleGlobalKeydown);
});

onBeforeUnmount(() => {
  document.removeEventListener("keydown", handleGlobalKeydown);
});
</script>

<template>
  <SplashScreen v-if="showSplash" @done="showSplash = false" />
  <div class="pl-app">
    <ShortcutHelpOverlay v-model="showHelp" />
    <TopBar
      :current-view="currentView"
      @navigate="handleNavigate"
      @command="handleCommandBarCommand"
      @apply-alert="handleApplyAlert"
    />
    <div class="pl-main">
      <template v-if="currentView === 'universe'">
        <div class="pl-chart-chat-row">
          <section class="pl-chart-section">
            <ScatterChart
              :stocks="filteredStocks"
              :selected-universe="selectedUniverse"
              :view-mode="universeViewMode"
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
              ref="chatRef"
              @set-filters="handleSetFilters"
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
                :view-mode="universeViewMode"
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
