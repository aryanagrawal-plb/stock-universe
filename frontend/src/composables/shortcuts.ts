/**
 * Central shortcut map and handler. All keyboard and command-bar input
 * resolves to a command and calls the same pipeline the AI chatbot uses
 * (applyAiFilters / clearAllFilters / setUniverseViewMode).
 */

import type { UniverseFilters } from "../types/stock";

export type ShortcutCommandType =
  | "reset"
  | "filters"
  | "view"
  | "focusChat"
  | "clearChat"
  | "help";

export interface ShortcutCommand {
  type: ShortcutCommandType;
  filters?: UniverseFilters;
  viewMode?: string;
}

export interface ShortcutCommandContext {
  clearAllFilters: () => void;
  applyAiFilters: (f: UniverseFilters) => void;
  setUniverseViewMode: (mode: string) => void;
  focusChat: () => void;
  clearChat: () => void;
  openHelp: () => void;
}

/** 2–3 letter codes (command bar) and single keys → command */
const SHORTCUT_MAP: Record<string, ShortcutCommand> = {
  // Command bar codes
  PF: { type: "view", viewMode: "portfolio" },
  DV: { type: "view", viewMode: "diversifiers" },
  HF: { type: "view", viewMode: "hedge" },
  SH: { type: "view", viewMode: "sharpe" },
  DD: { type: "view", viewMode: "drawdown" },
  VL: { type: "view", viewMode: "volatility" },
  MV: { type: "view", viewMode: "movers" },
  SC: { type: "view", viewMode: "screener" },
  LI: { type: "view", viewMode: "liquidity" },
  R: { type: "reset" },
  "/": { type: "focusChat" },
  "?": { type: "help" },
  // Single-key aliases (only when focus not in input)
  E: { type: "clearChat" },
  "1": { type: "view", viewMode: "sharpe" },
  "2": { type: "view", viewMode: "drawdown" },
  "3": { type: "view", viewMode: "volatility" },
  "4": { type: "view", viewMode: "diversifiers" },
  "5": { type: "view", viewMode: "movers" },
  H: { type: "filters", filters: { industries: ["Healthcare"] } },
  C: { type: "filters", filters: { industries: ["Consumer Discretionary"] } },
  I: { type: "filters", filters: { industries: ["Industrials"] } },
};

export function getShortcutCommand(code: string): ShortcutCommand | null {
  const normalized = String(code).trim().toUpperCase();
  if (!normalized) return null;
  return SHORTCUT_MAP[normalized] ?? null;
}

export function executeShortcutCommand(
  command: ShortcutCommand,
  ctx: ShortcutCommandContext
): void {
  switch (command.type) {
    case "reset":
      ctx.clearAllFilters();
      break;
    case "filters":
      if (command.filters) ctx.applyAiFilters(command.filters);
      break;
    case "view":
      if (command.viewMode) ctx.setUniverseViewMode(command.viewMode);
      break;
    case "focusChat":
      ctx.focusChat();
      break;
    case "clearChat":
      ctx.clearChat();
      break;
    case "help":
      ctx.openHelp();
      break;
    default:
      break;
  }
}

/** Plain-language list for PM shortcut help overlay */
export const SHORTCUT_HELP_ENTRIES: { keys: string; label: string; section: string }[] = [
  { keys: "?", label: "Open this shortcut help", section: "General" },
  { keys: "/", label: "Focus chat / command", section: "General" },
  { keys: "E", label: "Clear chat history", section: "General" },
  { keys: "R", label: "Reset universe (clear all filters)", section: "General" },
  { keys: "H", label: "Industry: Healthcare", section: "Industry quick" },
  { keys: "C", label: "Industry: Consumer Cyclicals", section: "Industry quick" },
  { keys: "I", label: "Industry: Industrials", section: "Industry quick" },
  { keys: "PF", label: "Portfolio overlay", section: "Portfolio & risk" },
  { keys: "DV / 4", label: "Diversifiers vs my book", section: "Portfolio & risk" },
  { keys: "HF", label: "Hedge Finder", section: "Portfolio & risk" },
  { keys: "SH / 1", label: "Sharpe view", section: "Portfolio & risk" },
  { keys: "DD / 2", label: "Drawdown view", section: "Portfolio & risk" },
  { keys: "VL / 3", label: "Volatility view", section: "Portfolio & risk" },
  { keys: "MV / 5", label: "Recent movers", section: "Universe & flow" },
  { keys: "LI", label: "Liquidity focus", section: "Universe & flow" },
  { keys: "SC", label: "Open screener", section: "Universe & flow" },
];
