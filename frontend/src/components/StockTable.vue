<script setup lang="ts">
import { computed, ref } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import type { ColDef, GridReadyEvent, GridApi } from "ag-grid-community";
import { icon as faIcon } from "@fortawesome/fontawesome-svg-core";
import { faThumbtack } from "@fortawesome/free-solid-svg-icons";
import type { Stock } from "../types/stock";
import StockDetailPanel from "./StockDetailPanel.vue";
import {
  TAB_COLUMNS,
  PINNED_COLUMNS,
  DISPLAY_TO_FIELD,
  TEXT_FILTER_COLUMNS,
  SET_FILTER_COLUMNS,
  NUMBER_FILTER_COLUMNS,
  PERCENT_DECIMAL_COLUMNS,
  PERCENT_DISPLAY_COLUMNS,
  LARGE_NUMBER_COLUMNS,
  RATIO_COLUMNS,
  COLOR_FORMATTED_COLUMNS,
  FLEX_COLUMNS,
} from "../constants/tableColumns";

const props = withDefaults(
  defineProps<{
    stocks: Stock[];
    viewMode?: string;
    isLoading: boolean;
    error: string | null;
    pinnedCodes: Set<string>;
  }>(),
  { viewMode: "" }
);

const emit = defineEmits<{
  "toggle-pin": [code: string];
}>();

const TAB_NAMES = Object.keys(TAB_COLUMNS) as string[];
const activeTab = ref<string>("Overview");

const ALL_COLUMN_NAMES = Object.keys(DISPLAY_TO_FIELD).filter(
  (n) => !["Code", "Name", "Ticker"].includes(n),
);

const showColumnPicker = ref(false);
const extraColumns = ref<string[]>([]);

function toggleColumn(name: string): void {
  const idx = extraColumns.value.indexOf(name);
  if (idx >= 0) {
    extraColumns.value = extraColumns.value.filter((_, i) => i !== idx);
  } else {
    extraColumns.value = [...extraColumns.value, name];
  }
}

function isColumnActive(name: string): boolean {
  const tabCols = TAB_COLUMNS[activeTab.value] ?? [];
  return tabCols.includes(name) || extraColumns.value.includes(name);
}

const PAGE_SIZES = [10, 50, 100] as const;
const pageSize = ref<number>(50);
let gridApi: GridApi | null = null;

const pinSvg = faIcon(faThumbtack).html[0];

function onGridReady(params: GridReadyEvent): void {
  gridApi = params.api;
  params.api.sizeColumnsToFit();
}

const pinnedRows = computed(() =>
  props.stocks.filter((s) => props.pinnedCodes.has(s.code)),
);

const unpinnedRows = computed(() =>
  props.stocks.filter((s) => !props.pinnedCodes.has(s.code)),
);

const ELLIPSIS_STYLE: Record<string, string> = {
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap",
};

const TICKER_STYLE: Record<string, string> = {
  color: "#1a85a1",
  fontWeight: "400",
  fontFamily: "'Roboto', sans-serif",
};

const DASH = "\u2014";

function formatPercentDecimal(value: number | null): string {
  if (value == null) return DASH;
  return `${value >= 0 ? "+" : ""}${(value * 100).toFixed(2)}%`;
}

function formatPercentDisplay(value: number | null): string {
  if (value == null) return DASH;
  return `${value.toFixed(2)}%`;
}

function formatLargeNumber(value: number | null): string {
  if (value == null) return DASH;
  return value.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatRatio(value: number | null): string {
  if (value == null) return DASH;
  return value.toFixed(2);
}

function stripSurroundingQuotes(s: string): string {
  const trimmed = s.trim();
  if (trimmed.length >= 2 && trimmed.startsWith('"') && trimmed.endsWith('"')) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function formatText(value: string | number | null | undefined): string {
  if (value == null || value === undefined) return DASH;
  if (typeof value === "string") {
    const stripped = stripSurroundingQuotes(value);
    if (stripped === "") return DASH;
    return stripped;
  }
  return String(value);
}

function buildColDef(displayName: string): ColDef {
  const field = DISPLAY_TO_FIELD[displayName];
  if (!field)
    return {
      field: displayName.toLowerCase().replace(/\s/g, "_"),
      headerName: displayName,
    };

  const isText =
    TEXT_FILTER_COLUMNS.has(displayName) || SET_FILTER_COLUMNS.has(displayName);
  const isPctDecimal = PERCENT_DECIMAL_COLUMNS.has(displayName);
  const isPctDisplay = PERCENT_DISPLAY_COLUMNS.has(displayName);
  const isLarge = LARGE_NUMBER_COLUMNS.has(displayName);
  const isRatio = RATIO_COLUMNS.has(displayName);
  const hasColor = COLOR_FORMATTED_COLUMNS.has(displayName);
  const isFlex = FLEX_COLUMNS.has(displayName);

  let valueFormatter: (params: { value: unknown }) => string;
  if (isPctDecimal) {
    valueFormatter = (p) => formatPercentDecimal(p.value as number | null);
  } else if (isPctDisplay) {
    valueFormatter = (p) => formatPercentDisplay(p.value as number | null);
  } else if (isLarge) {
    valueFormatter = (p) => formatLargeNumber(p.value as number | null);
  } else if (isRatio) {
    valueFormatter = (p) => formatRatio(p.value as number | null);
  } else {
    valueFormatter = (p) =>
      formatText(p.value as string | number | null | undefined);
  }

  const colDef: ColDef = {
    field,
    headerName: displayName,
    valueFormatter,
    cellClass: "text-monospace",
    tooltipField: field,
  };

  colDef.cellStyle = { textAlign: "left" };

  if (isFlex) {
    colDef.flex = 1;
    colDef.minWidth = 150;
  } else {
    colDef.width = 150;
    colDef.minWidth = 120;
  }

  if (
    TEXT_FILTER_COLUMNS.has(displayName) ||
    SET_FILTER_COLUMNS.has(displayName)
  ) {
    colDef.filter = "agTextColumnFilter";
  } else if (NUMBER_FILTER_COLUMNS.has(displayName)) {
    colDef.filter = "agNumberColumnFilter";
  }

  if (hasColor) {
    colDef.cellClassRules = {
      "text-danger": (p) => (p.value ?? 0) < 0,
    };
  }

  if (displayName === "Name") {
    colDef.cellStyle = { ...ELLIPSIS_STYLE, textAlign: "left" };
  } else if (displayName === "Code" || displayName === "Ticker") {
    colDef.cellStyle = { ...TICKER_STYLE, textAlign: "left" };
  }

  return colDef;
}

const columnDefs = computed<ColDef[]>(() => {
  const defs: ColDef[] = [
    {
      colId: "_expand",
      headerName: "",
      width: 36,
      maxWidth: 36,
      pinned: "left",
      sortable: false,
      resizable: false,
      suppressMovable: true,
      cellRenderer: "agGroupCellRenderer",
    },
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
  ];

  const tabCols = TAB_COLUMNS[activeTab.value] ?? [];
  const seen = new Set<string>(PINNED_COLUMNS);

  for (const displayName of PINNED_COLUMNS) {
    defs.push({
      ...buildColDef(displayName),
      pinned: "left",
      sort: displayName === "Code" ? "asc" : undefined,
    });
  }

  for (const displayName of tabCols) {
    if (seen.has(displayName)) continue;
    seen.add(displayName);
    defs.push(buildColDef(displayName));
  }

  for (const displayName of extraColumns.value) {
    if (seen.has(displayName)) continue;
    seen.add(displayName);
    defs.push(buildColDef(displayName));
  }

  return defs;
});

const defaultColDef: ColDef = {
  sortable: true,
  resizable: true,
  suppressMovable: true,
};

const popupParent = typeof document !== "undefined" ? document.body : undefined;
</script>

<template>
  <div class="stock-table-container">
    <div v-if="error" class="pl-error-msg">{{ error }}</div>

    <div class="pl-tab-bar">
      <button
        v-for="tab in TAB_NAMES"
        :key="tab"
        class="pl-tab-btn"
        :class="{ active: activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ tab }}
      </button>
      <div class="pl-col-picker-wrap">
        <button
          class="pl-col-picker-btn"
          :class="{ active: showColumnPicker }"
          title="Add/remove columns"
          @click="showColumnPicker = !showColumnPicker"
        >
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
            <rect x="3" y="3" width="7" height="7" />
            <rect x="14" y="3" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" />
            <rect x="14" y="14" width="7" height="7" />
          </svg>
          <span>Columns</span>
          <svg
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline
              :points="showColumnPicker ? '18 15 12 9 6 15' : '6 9 12 15 18 9'"
            />
          </svg>
        </button>
        <div v-if="showColumnPicker" class="pl-col-picker-panel shadow">
          <div class="pl-col-picker-scroll">
            <label
              v-for="col in ALL_COLUMN_NAMES"
              :key="col"
              class="pl-col-option"
              :class="{ checked: isColumnActive(col) }"
            >
              <input
                type="checkbox"
                :checked="isColumnActive(col)"
                @change="toggleColumn(col)"
              />
              <span>{{ col }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <div class="grid-wrapper ag-theme-alpine">
      <AgGridVue
        style="width: 100%; height: 100%"
        :rowHeight="40"
        :rowData="unpinnedRows"
        :pinnedTopRowData="pinnedRows"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :masterDetail="true"
        :detailCellRenderer="StockDetailPanel"
        :detailRowHeight="280"
        :pagination="true"
        :paginationPageSize="pageSize"
        :suppressPaginationPanel="false"
        :animateRows="true"
        :suppressCellFocus="true"
        :popupParent="popupParent"
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

.pl-tab-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 0 10px 0;
  border-bottom: 1px solid #d8dde2;
  flex-shrink: 0;
}

.pl-tab-btn {
  padding: 6px 14px;
  font-size: 13px;
  font-family: "Fira Sans", sans-serif;
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

.pl-col-picker-wrap {
  position: relative;
  margin-left: auto;
}

.pl-col-picker-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 500;
  font-family: "Fira Sans", sans-serif;
  color: #495057;
  background: transparent;
  border: 1px solid #d8dde2;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;

  &:hover,
  &.active {
    border-color: #1a85a1;
    color: #1a85a1;
  }
}

.pl-col-picker-panel {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  width: 240px;
  background: #fff;
  border: 1px solid #d8dde2;
  border-radius: 6px;
  z-index: 300;
  padding: 6px 0;
}

.pl-col-picker-scroll {
  max-height: 320px;
  overflow-y: auto;
  padding: 0 4px;
}

.pl-col-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px;
  font-size: 12px;
  font-family: "Fira Sans", sans-serif;
  color: #495057;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.1s;

  &:hover {
    background: #f1f3f5;
  }

  &.checked {
    color: #1a85a1;
    font-weight: 500;
  }

  input[type="checkbox"] {
    accent-color: #1a85a1;
    width: 14px;
    height: 14px;
    cursor: pointer;
  }

  span {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
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
  font-family: "Fira Sans", sans-serif;
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
  min-height: 0;
  width: 100%;
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
