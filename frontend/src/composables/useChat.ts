import { ref, watch } from "vue";
import type {
  ChatMessage,
  UniverseFilters,
  FilterAction,
} from "../types/stock";

const STORAGE_KEY = "stock-universe-chat";

export type OnFilterAction = (
  action: FilterAction,
  filters: UniverseFilters | null
) => void;

function loadMessages(): ChatMessage[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as ChatMessage[];
  } catch {
    return [];
  }
}

function persistMessages(msgs: ChatMessage[]): void {
  try {
    const serialisable = msgs.map((m) => ({
      role: m.role,
      content: m.content,
      pendingFilters: m.pendingFilters ?? null,
      action: m.action ?? "none",
      filterStatus: m.filterStatus ?? undefined,
    }));
    localStorage.setItem(STORAGE_KEY, JSON.stringify(serialisable));
  } catch {
    /* quota exceeded – silently ignore */
  }
}

export function useChat(onFilterAction?: OnFilterAction) {
  const messages = ref<ChatMessage[]>(loadMessages());
  const isSending = ref(false);

  watch(messages, (val) => persistMessages(val), { deep: true });

  async function sendMessage(content: string): Promise<void> {
    if (!content.trim()) return;

    messages.value.push({ role: "user", content });
    isSending.value = true;

    try {
      const history = messages.value.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      const action: FilterAction = data.action ?? "none";
      const filters: UniverseFilters | null = data.filters ?? null;
      const hasFilterChange =
        action === "clear" || ((action === "set" || action === "add" || action === "remove") && filters !== null);

      const msg: ChatMessage = {
        role: "assistant",
        content: data.reply,
      };

      if (hasFilterChange) {
        msg.pendingFilters = filters;
        msg.action = action;
        msg.filterStatus = "pending";
      }

      messages.value.push(msg);
    } catch {
      messages.value.push({
        role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
      });
    } finally {
      isSending.value = false;
    }
  }

  function confirmFilters(index: number): void {
    const msg = messages.value[index];
    if (!msg || msg.filterStatus !== "pending") return;

    msg.filterStatus = "applied";
    messages.value = [...messages.value];

    if (onFilterAction) {
      onFilterAction(msg.action ?? "none", msg.pendingFilters ?? null);
    }
  }

  function dismissFilters(index: number): void {
    const msg = messages.value[index];
    if (!msg || msg.filterStatus !== "pending") return;

    msg.filterStatus = "dismissed";
    messages.value = [...messages.value];
  }

  function clearMessages(): void {
    messages.value = [];
    localStorage.removeItem(STORAGE_KEY);
  }

  return {
    messages,
    isSending,
    sendMessage,
    confirmFilters,
    dismissFilters,
    clearMessages,
  };
}
