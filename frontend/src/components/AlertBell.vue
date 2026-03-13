<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue";
import type { TriggeredAlert, UniverseFilters, NumericRange } from "../types/stock";

const emit = defineEmits<{
  (e: "apply-alert", filters: UniverseFilters): void;
  (e: "navigate", view: string): void;
}>();

const triggered = ref<TriggeredAlert[]>([]);
const isOpen = ref(false);
const bellRef = ref<HTMLElement | null>(null);

const LABEL_MAP: Record<string, string> = {
  countries: "Country",
  industries: "Industry",
  sub_industries: "Sub-Industry",
  currencies: "Currency",
  exchanges: "Exchange",
  search: "Search",
  price: "Price",
  market_cap: "Mkt Cap",
  pe_ratio: "P/E",
  pb_ratio: "P/B",
  dividend_yield: "Div Yld",
  earnings_per_share: "EPS",
  return_on_equity: "ROE",
  return_1m: "1M Ret",
  return_3m: "3M Ret",
  return_6m: "6M Ret",
  return_1y: "1Y Ret",
  return_3y: "3Y Ret",
  return_5y: "5Y Ret",
  return_ytd: "YTD Ret",
  volatility_1y: "1Y Vol",
  sharpe_1y: "Sharpe",
  sortino_1y: "Sortino",
  max_drawdown_1y: "Max DD",
};

function formatRange(range: NumericRange): string {
  if (range.min != null && range.max != null) return `${range.min}–${range.max}`;
  if (range.min != null) return `≥ ${range.min}`;
  if (range.max != null) return `≤ ${range.max}`;
  return "";
}

function getFilterChips(
  filters: UniverseFilters,
): { label: string; value: string }[] {
  const chips: { label: string; value: string }[] = [];
  const data = filters as Record<string, unknown>;
  for (const [key, val] of Object.entries(data)) {
    if (val == null) continue;
    const label = LABEL_MAP[key] ?? key;
    if (Array.isArray(val)) {
      chips.push({ label, value: val.join(", ") });
    } else if (typeof val === "string") {
      chips.push({ label, value: val });
    } else if (typeof val === "object" && val !== null) {
      const rangeStr = formatRange(val as NumericRange);
      if (rangeStr) chips.push({ label, value: rangeStr });
    }
  }
  return chips;
}

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.round(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

function toggleDropdown(): void {
  isOpen.value = !isOpen.value;
}

function handleClickOutside(event: MouseEvent): void {
  if (bellRef.value && !bellRef.value.contains(event.target as Node)) {
    isOpen.value = false;
  }
}

function applyAlert(t: TriggeredAlert): void {
  emit("apply-alert", t.alert.filters);
  isOpen.value = false;
}

function viewAllAlerts(): void {
  emit("navigate", "alerts");
  isOpen.value = false;
}

async function fetchTriggered(): Promise<void> {
  try {
    const res = await fetch("/api/alerts/triggered");
    if (res.ok) triggered.value = await res.json();
  } catch {
    /* silently ignore for PoC */
  }
}

onMounted(() => {
  fetchTriggered();
  document.addEventListener("click", handleClickOutside, true);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside, true);
});
</script>

<template>
  <div ref="bellRef" class="alert-bell">
    <button
      class="bell-btn squared-center-fa-btn"
      title="Triggered Alerts"
      @click="toggleDropdown"
    >
      <icon icon="bell" />
      <span v-if="triggered.length" class="bell-badge">{{ triggered.length }}</span>
    </button>

    <Transition name="dropdown">
      <div v-if="isOpen" class="bell-dropdown">
        <div class="dropdown-header">
          <span class="dropdown-title">Triggered Alerts</span>
          <button class="dropdown-close" @click="isOpen = false">
            <icon icon="times" />
          </button>
        </div>

        <div v-if="triggered.length === 0" class="dropdown-empty">
          No alerts triggered right now.
        </div>

        <div v-else class="dropdown-list">
          <div
            v-for="item in triggered"
            :key="item.alert.id"
            class="triggered-card"
          >
            <div class="triggered-top">
              <span class="triggered-name">{{ item.alert.name }}</span>
              <span class="triggered-time">{{ relativeTime(item.triggered_at) }}</span>
            </div>
            <span class="triggered-match">
              {{ item.match_count }} stock{{ item.match_count !== 1 ? "s" : "" }} match
            </span>
            <div class="triggered-chips">
              <span
                v-for="chip in getFilterChips(item.alert.filters)"
                :key="chip.label"
                class="t-chip"
              >
                <strong>{{ chip.label }}:</strong> {{ chip.value }}
              </span>
            </div>
            <button class="apply-btn" @click="applyAlert(item)">
              Apply Filters
              <icon icon="arrow-right" class="apply-icon" />
            </button>
          </div>
        </div>

        <button class="dropdown-footer" @click="viewAllAlerts">
          View all alerts
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped lang="scss">
.alert-bell {
  position: relative;
}

.bell-btn {
  position: relative;
  color: #fff;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.bell-badge {
  position: absolute;
  top: -4px;
  right: -6px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #ef4444;
  color: #fff;
  font-family: "Fira Sans", sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  line-height: 18px;
  text-align: center;
  border-radius: 9px;
  pointer-events: none;
}

.bell-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 360px;
  max-height: 460px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1050;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  border-bottom: 1px solid #f0f0f4;
}

.dropdown-title {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.88rem;
  font-weight: 600;
  color: #0c1743;
}

.dropdown-close {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 2px 4px;
  border-radius: 4px;
  transition: color 0.15s;

  &:hover {
    color: #374151;
  }
}

.dropdown-empty {
  padding: 32px 16px;
  text-align: center;
  font-family: "Fira Sans", sans-serif;
  font-size: 0.85rem;
  color: #9ca3af;
}

.dropdown-list {
  overflow-y: auto;
  flex: 1;
  padding: 8px;
}

.triggered-card {
  padding: 12px;
  border-radius: 8px;
  background: #f9fafb;
  border: 1px solid #f0f2f8;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color 0.15s;

  & + & {
    margin-top: 8px;
  }

  &:hover {
    border-color: #c7cad9;
  }
}

.triggered-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.triggered-name {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  color: #0c1743;
}

.triggered-time {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.72rem;
  color: #9ca3af;
  white-space: nowrap;
}

.triggered-match {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.75rem;
  color: #16a34a;
  font-weight: 500;
}

.triggered-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.t-chip {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.68rem;
  background: #e8ebf4;
  color: #0c1743;
  padding: 2px 8px;
  border-radius: 10px;
  word-break: break-word;

  strong {
    font-weight: 600;
  }
}

.apply-btn {
  align-self: flex-end;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 2px;
  padding: 5px 12px;
  font-family: "Fira Sans", sans-serif;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  background: #0c1743;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: #1a2a5e;
  }
}

.apply-icon {
  font-size: 0.65rem;
}

.dropdown-footer {
  display: block;
  width: 100%;
  padding: 10px;
  text-align: center;
  font-family: "Fira Sans", sans-serif;
  font-size: 0.78rem;
  font-weight: 500;
  color: #0c1743;
  background: #f9fafb;
  border: none;
  border-top: 1px solid #f0f0f4;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: #eef0f6;
  }
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
