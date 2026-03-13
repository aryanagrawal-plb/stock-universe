<script setup lang="ts">
import { ref, nextTick } from "vue";
import { useChat } from "../composables/useChat";

const { messages, isSending, sendMessage } = useChat();
const input = ref("");
const messagesEl = ref<HTMLElement | null>(null);

async function handleSend(): Promise<void> {
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await sendMessage(text);
  await nextTick();
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight;
  }
}

function handleKeydown(e: KeyboardEvent): void {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}
</script>

<template>
  <div class="ai-chat-panel">
    <div class="ai-header">
      <span class="ai-label">AI</span>
      <span class="ai-header-title">Assistant</span>
    </div>

    <div ref="messagesEl" class="ai-messages">
      <div v-if="messages.length === 0 && !isSending" class="ai-empty">
        Ask the AI to help filter or analyze stocks.
      </div>
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="ai-msg"
        :class="msg.role"
      >
        <span class="ai-msg-role">{{ msg.role === "user" ? "You" : "AI" }}</span>
        <span class="ai-msg-text">{{ msg.content }}</span>
      </div>
      <div v-if="isSending" class="ai-msg assistant">
        <span class="ai-msg-role">AI</span>
        <span class="ai-msg-text typing">Thinking...</span>
      </div>
    </div>

    <div class="ai-input-row">
      <input
        v-model="input"
        type="text"
        placeholder="Ask about stocks..."
        class="ai-input"
        @keydown="handleKeydown"
      />
      <button
        class="ai-send"
        :disabled="isSending || !input.trim()"
        @click="handleSend"
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
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.ai-chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.ai-label {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: white;
  background: var(--color-primary);
  border-radius: 4px;
}

.ai-header-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}

.ai-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
}

.ai-empty {
  color: var(--color-text-muted);
  font-size: 13px;
  text-align: center;
  padding: 40px 12px;
  line-height: 1.6;
}

.ai-msg {
  margin-bottom: 10px;
}

.ai-msg-role {
  display: block;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
  color: var(--color-text-muted);
}

.ai-msg.user .ai-msg-role {
  color: var(--color-primary);
}

.ai-msg.assistant .ai-msg-role {
  color: var(--color-accent);
}

.ai-msg-text {
  font-size: 13px;
  line-height: 1.5;
  display: block;
  word-break: break-word;
}

.typing {
  color: var(--color-text-muted);
  font-style: italic;
}

.ai-input-row {
  display: flex;
  gap: 8px;
  padding: 10px 14px;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}

.ai-input {
  flex: 1;
  min-width: 0;
  padding: 7px 10px;
  font-size: 13px;
  font-family: var(--font-sans);
  color: var(--color-text);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  outline: none;
  transition: border-color 0.15s;
}

.ai-input:focus {
  border-color: var(--color-primary);
}

.ai-send {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: background 0.15s;
}

.ai-send:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.ai-send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
