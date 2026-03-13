<script setup lang="ts">
import { computed, ref } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import type { ColDef, GridReadyEvent, GridApi } from "ag-grid-community";
import { icon as faIcon } from "@fortawesome/fontawesome-svg-core";
import { faThumbtack } from "@fortawesome/free-solid-svg-icons";
import type { Stock } from "../types/stock";

const props = defineProps<{
  stocks: Stock[];
  isLoading: boolean;
  error: string | null;
  pinnedCodes: Set<string>;
}>();

const emit = defineEmits<{
  "toggle-pin": [code: string];
}>();

const PAGE_SIZES = [10, 50, 100] as const;
const pageSize = ref<number>(50);
let gridApi: GridApi | null = null;

const pinSvg = faIcon(faThumbtack).html[0];

function onGridReady(params: GridReadyEvent): void {
  gridApi = params.api;
  params.api.sizeColumnsToFit();
}

function changePageSize(size: number): void {
  pageSize.value = size;
}

const pinnedRows = computed(() =>
  props.stocks.filter((s) => props.pinnedCodes.has(s.code))
);

const unpinnedRows = computed(() =>
  props.stocks.filter((s) => !props.pinnedCodes.has(s.code))
);

function formatMarketCap(value: number | null): string {
  if (value == null) return "\u2014";
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}T`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}B`;
  return `$${value.toFixed(0)}M`;
}

function formatPct(value: number | null): string {
  if (value == null) return "\u2014";
  return `${value >= 0 ? "+" : ""}${(value * 100).toFixed(1)}%`;
}

function formatNum(value: number | null, decimals = 1): string {
  if (value == null) return "\u2014";
  return value.toFixed(decimals);
}

const ELLIPSIS_STYLE: Record<string, string> = {
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap",
};

const TICKER_STYLE: Record<string, string> = {
  color: "#1a85a1",
  fontWeight: "600",
  fontFamily: "'Roboto Mono', monospace",
};

const columnDefs = computed<ColDef[]>(() => [
  {
    colId: "_pin",
    headerName: "",
    width: 40,
    maxWidth: 40,
    pinned: "left",
    sortable: false,
    resizable: false,
    suppressMovable: true,
    cellRenderer: (params: { data?: Stock }) => {
      const code = params.data?.code;
      const isPinned = code ? props.pinnedCodes.has(code) : false;
      return `<span class="pin-toggle${isPinned ? " is-pinned" : ""}">${pinSvg}</span>`;
    },
    onCellClicked: (event: { data?: Stock }) => {
      if (event.data?.code) emit("toggle-pin", event.data.code);
    },
  },
  {
    field: "code",
    headerName: "Ticker",
    width: 100,
    pinned: "left",
    cellStyle: TICKER_STYLE,
    sort: "asc",
  },
  {
    field: "name",
    headerName: "Name",
    flex: 2,
    minWidth: 180,
    tooltipField: "name",
    cellStyle: ELLIPSIS_STYLE,
  },
  { field: "country", headerName: "Country", width: 100 },
  {
    field: "industry",
    headerName: "Industry",
    width: 170,
    cellStyle: ELLIPSIS_STYLE,
  },
  { field: "currency", headerName: "Ccy", width: 65 },
  {
    field: "price",
    headerName: "Price",
    width: 100,
    type: "rightAligned",
    headerClass: "ag-right-aligned-header",
    cellClass: "text-monospace",
    valueFormatter: (p) => (p.value != null ? p.value.toFixed(2) : "\u2014"),
  },
  {
    field: "market_cap",
    headerName: "Mkt Cap",
    width: 110,
    type: "rightAligned",
    headerClass: "ag-right-aligned-header",
    cellClass: "text-monospace",
    valueFormatter: (p) => formatMarketCap(p.value),
  },
  {
    field: "pe_ratio",
    headerName: "P/E",
    width: 80,
    type: "rightAligned",
    headerClass: "ag-right-aligned-header",
    cellClass: "text-monospace",
    valueFormatter: (p) => formatNum(p.value),
  },
  {
    field: "pb_ratio",
    headerName: "P/B",
    width: 80,
    type: "rightAligned",
    headerClass: "ag-right-aligned-header",
    cellClass: "text-monospace",
    valueFormatter: (p) => formatNum(p.value),
  },
  {
    field: "dividend_yield",
    headerName: "Div Yld",
    width: 90,
    type: "rightAligned",
    headerClass: "ag-right-aligned-header",
    cellClass: "text-monospace",
    valueFormatter: (p) => (p.value != null ? `${p.value.toFixed(2)}%` : "\u2014"),
  },
  {
    field: "return_ytd",
    headerName: "YTD %",
    width: 95,
    type: "rightAligned",
    headerClass: "ag-right-aligned-header",
    cellClass: "text-monospace",
    valueFormatter: (p) => formatPct(p.value),
    cellClassRules: {
      "text-success": (p) => (p.value ?? 0) > 0,
      "text-danger": (p) => (p.value ?? 0) < 0,
    },
  },
  {
    field: "volatility_1y",
    headerName: "Vol 1Y",
    width: 90,
    type: "rightAligned",
    headerClass: "ag-right-aligned-header",
    cellClass: "text-monospace",
    valueFormatter: (p) => formatNum(p.value, 2),
  },
]);

const defaultColDef: ColDef = {
  sortable: true,
  resizable: true,
  suppressMovable: true,
};
</script>

<template>
  <div class="stock-table-container">
    <div v-if="error" class="pl-error-msg">{{ error }}</div>

    <div class="pl-page-size-bar">
      <span class="pl-bar-label">Show</span>
      <button
        v-for="size in PAGE_SIZES"
        :key="size"
        class="pl-size-btn"
        :class="{ active: pageSize === size }"
        @click="changePageSize(size)"
      >
        {{ size }}
      </button>
    </div>

    <div class="grid-wrapper ag-theme-alpine">
      <AgGridVue
        style="width: 100%; height: 100%"
        :rowData="unpinnedRows"
        :pinnedTopRowData="pinnedRows"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :pagination="true"
        :paginationPageSize="pageSize"
        :suppressPaginationPanel="false"
        :animateRows="true"
        :suppressCellFocus="true"
        :overlayLoadingTemplate="'<span>Loading stocks...</span>'"
        :overlayNoRowsTemplate="'<span>No stocks match filters</span>'"
        @grid-ready="onGridReady"
      />
    </div>
  </div>
</template>

<style lang="scss">
.stock-table-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.pl-error-msg {
  padding: 8px 16px;
  color: #d9534f;
  font-size: 13px;
}

.pl-page-size-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 16px;
  border-bottom: 1px solid #d8dde2;
  flex-shrink: 0;
}

.pl-bar-label {
  font-size: 12px;
  color: #495057;
  margin-right: 4px;
}

.pl-size-btn {
  padding: 4px 10px;
  font-size: 12px;
  font-family: 'Fira Sans', sans-serif;
  color: #495057;
  background: transparent;
  border: 1px solid #d8dde2;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    border-color: #bbc1c7;
  }

  &.active {
    color: #fff;
    background: #1a85a1;
    border-color: #1a85a1;
  }
}

.stock-table-container .grid-wrapper {
  flex: 1;
  min-height: 400px;
  width: 100%;
}

.stock-table-container .ag-theme-alpine .text-success {
  color: #5cb85c !important;
}

.stock-table-container .ag-theme-alpine .text-danger {
  color: #d9534f !important;
}

/* Pin toggle icon */
.pin-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  cursor: pointer;
  color: #d8dde2;
  transition: color 0.15s;

  svg {
    width: 12px;
    height: 12px;
  }

  &:hover {
    color: #495057;
  }

  &.is-pinned {
    color: #1a85a1;

    &:hover {
      color: #167089;
    }
  }
}
</style>
