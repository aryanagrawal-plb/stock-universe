<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted } from "vue";
import { useChat } from "../composables/useChat";
import { aiFiltersToChips } from "../composables/useStocks";
import type { UniverseFilters, FilterAction, ChatMessage } from "../types/stock";

const emit = defineEmits<{
  "apply-filters": [filters: UniverseFilters];
  "remove-filters": [filters: UniverseFilters];
  "clear-filters": [];
}>();

const { messages, isSending, sendMessage, confirmFilters, dismissFilters, clearMessages } =
  useChat((action: FilterAction, filters: UniverseFilters | null) => {
    if (action === "add" && filters) emit("apply-filters", filters);
    else if (action === "remove" && filters) emit("remove-filters", filters);
    else if (action === "clear") emit("clear-filters");
  });

const input = ref("");
const messagesEl = ref<HTMLElement | null>(null);

const lastPendingIndex = computed<number>(() => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].filterStatus === "pending") return i;
  }
  return -1;
});

const inputEmpty = computed(() => input.value.trim().length === 0);
const hasPendingSuggestion = computed(() => lastPendingIndex.value !== -1);
const showHighlight = computed(() => inputEmpty.value && hasPendingSuggestion.value);

async function handleSend(): Promise<void> {
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await sendMessage(text);
  await nextTick();
  scrollToBottom();
}

function scrollToBottom(): void {
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight;
  }
}

watch(() => messages.value.length, async () => {
  await nextTick();
  scrollToBottom();
});

watch(isSending, async () => {
  await nextTick();
  scrollToBottom();
});

onMounted(async () => {
  await nextTick();
  scrollToBottom();
});

function handleKeydown(e: KeyboardEvent): void {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (inputEmpty.value && hasPendingSuggestion.value) {
      handleConfirm(lastPendingIndex.value);
    } else {
      handleSend();
    }
    return;
  }
  if (e.key === "Escape" && inputEmpty.value && hasPendingSuggestion.value) {
    e.preventDefault();
    handleDismiss(lastPendingIndex.value);
  }
}

function handleConfirm(index: number): void {
  confirmFilters(index);
}

function handleDismiss(index: number): void {
  dismissFilters(index);
}

function handleClearChat(): void {
  clearMessages();
  emit("clear-filters");
}

function getFilterChips(msg: ChatMessage) {
  if (!msg.pendingFilters) return [];
  return aiFiltersToChips(msg.pendingFilters);
}

function actionLabel(msg: ChatMessage): string {
  if (msg.action === "remove") return "Remove";
  if (msg.action === "clear") return "Clear all";
  return "Add";
}
</script>

<template>
  <div class="pl-chat-panel">
    <div class="pl-chat-header">
      <span class="pl-chat-badge">AI</span>
      <span class="pl-chat-title">Assistant</span>
      <button
        v-if="messages.length > 0"
        class="pl-chat-clear-btn"
        title="Clear chat history"
        @click="handleClearChat"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
        </svg>
      </button>
    </div>

    <div ref="messagesEl" class="pl-chat-messages">
      <div v-if="messages.length === 0 && !isSending" class="pl-chat-empty">
        Ask the AI to filter stocks, e.g.<br />
        <em>"Show me US tech stocks under $50"</em>
      </div>
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="pl-chat-msg"
        :class="[msg.role, { 'pl-highlighted': showHighlight && i === lastPendingIndex }]"
      >
        <span class="pl-chat-msg-role">{{ msg.role === "user" ? "You" : "AI" }}</span>
        <span class="pl-chat-msg-text">{{ msg.content }}</span>

        <div v-if="msg.filterStatus && msg.pendingFilters && getFilterChips(msg).length > 0" class="pl-pending-chips">
          <span class="pl-pending-label" :class="{ 'pl-remove': msg.action === 'remove' }">
            {{ actionLabel(msg) }}:
          </span>
          <span
            v-for="(chip, ci) in getFilterChips(msg)"
            :key="ci"
            class="pl-preview-chip"
            :class="{ 'pl-chip-remove': msg.action === 'remove' }"
          >
            <span class="pl-preview-chip-cat">{{ chip.category }}:</span>
            {{ chip.value }}
          </span>
        </div>
        <div v-if="msg.filterStatus === 'pending' && msg.action === 'clear'" class="pl-pending-chips">
          <span class="pl-pending-label pl-remove">Clear all filters</span>
        </div>

        <div v-if="msg.filterStatus === 'pending'" class="pl-filter-actions">
          <button class="pl-btn-apply" @click="handleConfirm(i)">Apply</button>
          <button class="pl-btn-dismiss" @click="handleDismiss(i)">Dismiss</button>
        </div>
        <div v-else-if="msg.filterStatus === 'applied'" class="pl-filter-badge pl-badge-applied">
          Filters applied
        </div>
        <div v-else-if="msg.filterStatus === 'dismissed'" class="pl-filter-badge pl-badge-dismissed">
          Dismissed
        </div>
      </div>
      <div v-if="isSending" class="pl-chat-msg assistant">
        <span class="pl-chat-msg-role">AI</span>
        <span class="pl-chat-msg-text pl-typing">Thinking...</span>
      </div>
    </div>

    <div class="pl-chat-input-row">
      <input
        v-model="input"
        type="text"
        :placeholder="hasPendingSuggestion ? 'Enter to apply · Esc to dismiss' : 'Ask about stocks...'"
        class="pl-chat-input"
        @keydown="handleKeydown"
      />
      <button
        class="pl-chat-send"
        :disabled="isSending || !input.trim()"
        @click="handleSend"
      >
        Send
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.pl-chat-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background: #fff;
}

.pl-chat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid #d8dde2;
  flex-shrink: 0;
}

.pl-chat-badge {
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #fff;
  background: #0c1743;
  border-radius: 4px;
}

.pl-chat-title {
  font-size: 13px;
  font-weight: 600;
  color: #495057;
  flex: 1;
}

.pl-chat-clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #bbc1c7;
  cursor: pointer;
  transition: color 0.15s, background 0.15s;

  &:hover {
    color: #e74c3c;
    background: rgba(231, 76, 60, 0.08);
  }
}

.pl-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
}

.pl-chat-empty {
  color: #bbc1c7;
  font-size: 13px;
  text-align: center;
  padding: 40px 12px;
  line-height: 1.6;

  em {
    color: #1a85a1;
    font-style: italic;
  }
}

.pl-chat-msg {
  margin-bottom: 12px;
  padding: 8px 10px;
  border-radius: 6px;
  transition: background 0.2s, box-shadow 0.2s;

  &.pl-highlighted {
    background: rgba(39, 174, 96, 0.06);
    box-shadow: inset 0 0 0 1px rgba(39, 174, 96, 0.25);
  }
}

.pl-chat-msg-role {
  display: block;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 3px;
  color: #bbc1c7;
}

.pl-chat-msg.user .pl-chat-msg-role {
  color: #1a85a1;
}

.pl-chat-msg.assistant .pl-chat-msg-role {
  color: #0c1743;
}

.pl-chat-msg-text {
  font-size: 14px;
  line-height: 1.55;
  display: block;
  word-break: break-word;
  color: #4b4b4b;
  white-space: pre-line;
}

.pl-typing {
  color: #bbc1c7;
  font-style: italic;
}

.pl-pending-chips {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
}

.pl-pending-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: #27ae60;
  margin-right: 2px;

  &.pl-remove {
    color: #e67e22;
  }
}

.pl-preview-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  color: #1a85a1;
  background: rgba(26, 133, 161, 0.08);
  border: 1px solid rgba(26, 133, 161, 0.18);
  border-radius: 99px;
  white-space: nowrap;

  &.pl-chip-remove {
    color: #e67e22;
    background: rgba(230, 126, 34, 0.08);
    border-color: rgba(230, 126, 34, 0.18);
    text-decoration: line-through;
  }
}

.pl-preview-chip-cat {
  color: #bbc1c7;
  font-weight: 500;
}

.pl-filter-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.pl-btn-apply {
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 600;
  font-family: 'Fira Sans', sans-serif;
  color: #fff;
  background: #27ae60;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: #219a52;
  }
}

.pl-btn-dismiss {
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 600;
  font-family: 'Fira Sans', sans-serif;
  color: #6c757d;
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: #e0e0e0;
  }
}

.pl-filter-badge {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 10px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  border-radius: 3px;
}

.pl-badge-applied {
  color: #27ae60;
  background: rgba(39, 174, 96, 0.1);
}

.pl-badge-dismissed {
  color: #95a5a6;
  background: rgba(149, 165, 166, 0.1);
}

.pl-chat-input-row {
  display: flex;
  gap: 8px;
  padding: 10px 16px;
  border-top: 1px solid #d8dde2;
  flex-shrink: 0;
}

.pl-chat-input {
  flex: 1;
  min-width: 0;
  padding: 7px 10px;
  font-size: 13px;
  font-family: 'Fira Sans', sans-serif;
  color: #4b4b4b;
  background: #f5f7fa;
  border: 1px solid #d8dde2;
  border-radius: 0.25rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;

  &::placeholder {
    color: #bbc1c7;
  }

  &:focus {
    border-color: #1a85a1;
    box-shadow: 0 0 0 3px rgba(26, 133, 161, 0.15);
  }
}

.pl-chat-send {
  flex-shrink: 0;
  padding: 0 14px;
  font-size: 12px;
  font-weight: 600;
  font-family: 'Fira Sans', sans-serif;
  color: #fff;
  background: #1a85a1;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.15s;

  &:hover:not(:disabled) {
    background: #167089;
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}
</style>
