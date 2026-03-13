<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import type { Alert, UniverseFilters, NumericRange } from "../types/stock";

const alerts = ref<Alert[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

const LABEL_MAP: Record<string, string> = {
  countries: "Country",
  industries: "Industry",
  sub_industries: "Sub-Industry",
  currencies: "Currency",
  exchanges: "Exchange",
  search: "Search",
  price: "Price",
  market_cap: "Market Cap",
  pe_ratio: "P/E",
  pb_ratio: "P/B",
  dividend_yield: "Div Yield",
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
  sharpe_1y: "1Y Sharpe",
  sortino_1y: "1Y Sortino",
  max_drawdown_1y: "1Y Max DD",
};

function formatRange(range: NumericRange): string {
  if (range.min != null && range.max != null) return `${range.min} – ${range.max}`;
  if (range.min != null) return `≥ ${range.min}`;
  if (range.max != null) return `≤ ${range.max}`;
  return "";
}

function filterChips(filters: UniverseFilters): { label: string; value: string }[] {
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

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

async function fetchAlerts(): Promise<void> {
  isLoading.value = true;
  error.value = null;
  try {
    const res = await fetch("/api/alerts");
    if (!res.ok) throw new Error(`Failed to fetch alerts (${res.status})`);
    alerts.value = await res.json();
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    isLoading.value = false;
  }
}

async function deleteAlert(id: string): Promise<void> {
  try {
    await fetch(`/api/alerts/${id}`, { method: "DELETE" });
    alerts.value = alerts.value.filter((a) => a.id !== id);
  } catch (e) {
    console.error("Failed to delete alert:", e);
  }
}

async function toggleStatus(alert: Alert): Promise<void> {
  const newStatus = alert.status === "active" ? "paused" : "active";
  try {
    const res = await fetch(`/api/alerts/${alert.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    if (res.ok) {
      const updated: Alert = await res.json();
      const idx = alerts.value.findIndex((a) => a.id === alert.id);
      if (idx !== -1) alerts.value[idx] = updated;
    }
  } catch (e) {
    console.error("Failed to toggle alert status:", e);
  }
}

const activeCount = computed(() => alerts.value.filter((a) => a.status === "active").length);
const pausedCount = computed(() => alerts.value.filter((a) => a.status === "paused").length);

onMounted(fetchAlerts);
</script>

<template>
  <div class="alert-management">
    <div class="alert-header">
      <h1 class="alert-title">Alert Management</h1>
      <p class="alert-subtitle">
        Manage your stock watchlists and alerts.
        <span v-if="!isLoading && alerts.length" class="alert-stats">
          {{ alerts.length }} alert{{ alerts.length !== 1 ? "s" : "" }}
          &middot; {{ activeCount }} active &middot; {{ pausedCount }} paused
        </span>
      </p>
    </div>

    <div v-if="isLoading" class="alert-loading">Loading alerts...</div>
    <div v-else-if="error" class="alert-error">{{ error }}</div>
    <div v-else-if="alerts.length === 0" class="alert-empty">
      <p>No alerts created yet. Use the AI chat to create your first watchlist alert.</p>
    </div>

    <div v-else class="alert-grid">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        class="alert-card"
        :class="{ 'alert-card--paused': alert.status === 'paused' }"
      >
        <div class="alert-card-header">
          <div class="alert-card-title-row">
            <h3 class="alert-card-name">{{ alert.name }}</h3>
            <span
              class="alert-status-badge"
              :class="alert.status === 'active' ? 'badge-active' : 'badge-paused'"
            >
              {{ alert.status }}
            </span>
          </div>
          <span class="alert-card-date">Created {{ formatDate(alert.created_at) }}</span>
        </div>

        <div class="alert-card-filters">
          <span
            v-for="chip in filterChips(alert.filters)"
            :key="chip.label"
            class="filter-chip"
          >
            <span class="chip-label">{{ chip.label }}:</span> {{ chip.value }}
          </span>
        </div>

        <div class="alert-card-actions">
          <button class="btn-action btn-toggle" @click="toggleStatus(alert)">
            {{ alert.status === "active" ? "Pause" : "Resume" }}
          </button>
          <button class="btn-action btn-delete" @click="deleteAlert(alert.id)">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.alert-management {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 24px;
}

.alert-header {
  margin-bottom: 28px;
}

.alert-title {
  font-family: "Fira Sans", sans-serif;
  font-size: 1.6rem;
  font-weight: 600;
  color: #0c1743;
  margin: 0 0 6px;
}

.alert-subtitle {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.9rem;
  color: #6b7280;
  margin: 0;
}

.alert-stats {
  color: #0c1743;
  font-weight: 500;
}

.alert-loading,
.alert-error,
.alert-empty {
  text-align: center;
  padding: 48px 24px;
  font-family: "Fira Sans", sans-serif;
  font-size: 0.95rem;
  color: #6b7280;
}

.alert-error {
  color: #dc2626;
}

.alert-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.alert-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: box-shadow 0.2s, border-color 0.2s;

  &:hover {
    box-shadow: 0 2px 12px rgba(12, 23, 67, 0.08);
    border-color: #c7cad9;
  }

  &--paused {
    opacity: 0.7;
  }
}

.alert-card-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.alert-card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.alert-card-name {
  font-family: "Fira Sans", sans-serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #0c1743;
  margin: 0;
}

.alert-status-badge {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 3px 10px;
  border-radius: 12px;
  white-space: nowrap;
}

.badge-active {
  background: #dcfce7;
  color: #166534;
}

.badge-paused {
  background: #fef3c7;
  color: #92400e;
}

.alert-card-date {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.78rem;
  color: #9ca3af;
}

.alert-card-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-chip {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.75rem;
  background: #f0f2f8;
  color: #0c1743;
  padding: 4px 10px;
  border-radius: 14px;
  word-break: break-word;
}

.chip-label {
  font-weight: 600;
  margin-right: 2px;
}

.alert-card-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
  padding-top: 4px;
}

.btn-action {
  font-family: "Fira Sans", sans-serif;
  font-size: 0.78rem;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #fff;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;

  &:hover {
    background: #f3f4f6;
  }
}

.btn-toggle {
  color: #0c1743;

  &:hover {
    border-color: #0c1743;
  }
}

.btn-delete {
  color: #dc2626;

  &:hover {
    background: #fef2f2;
    border-color: #dc2626;
  }
}
</style>
