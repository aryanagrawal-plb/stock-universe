<script setup lang="ts">
import { ref, nextTick } from "vue";
import { useChat } from "../composables/useChat";

const { messages, isSending, sendMessage } = useChat();
const input = ref("");
const isOpen = ref(false);
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
  <Teleport to="body">
    <!-- Floating circle button -->
    <button v-show="!isOpen" class="fab" @click="isOpen = true" title="AI Assistant">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      </svg>
    </button>

    <!-- Chat panel -->
    <div v-show="isOpen" class="chat-window">
      <div class="chat-header">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
        </svg>
        <span class="chat-header-title">AI Assistant</span>
        <button class="chat-close" @click="isOpen = false" title="Close">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div ref="messagesEl" class="chat-messages">
        <div v-if="messages.length === 0" class="chat-empty">
          Ask the AI to help filter or analyze stocks.
        </div>
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="chat-msg"
          :class="msg.role"
        >
          <span class="chat-msg-role">{{ msg.role === "user" ? "You" : "AI" }}</span>
          <span class="chat-msg-text">{{ msg.content }}</span>
        </div>
        <div v-if="isSending" class="chat-msg assistant">
          <span class="chat-msg-role">AI</span>
          <span class="chat-msg-text typing">Thinking...</span>
        </div>
      </div>

      <div class="chat-input-row">
        <input
          v-model="input"
          type="text"
          placeholder="Ask about stocks..."
          class="chat-input"
          @keydown="handleKeydown"
        />
        <button class="chat-send" :disabled="isSending || !input.trim()" @click="handleSend">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(108, 92, 231, 0.4);
  transition: transform 0.2s, background 0.15s, box-shadow 0.2s;
  z-index: 1000;
}

.fab:hover {
  background: var(--color-primary-hover);
  transform: scale(1.08);
  box-shadow: 0 6px 28px rgba(108, 92, 231, 0.55);
}

.chat-window {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 380px;
  height: 480px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--color-primary);
  color: white;
  flex-shrink: 0;
}

.chat-header-title {
  font-size: 14px;
  font-weight: 600;
  flex: 1;
}

.chat-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.15s, background 0.15s;
}

.chat-close:hover {
  color: white;
  background: rgba(255, 255, 255, 0.15);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.chat-empty {
  color: var(--color-text-muted);
  font-size: 13px;
  text-align: center;
  padding: 60px 20px;
  line-height: 1.6;
}

.chat-msg {
  margin-bottom: 12px;
}

.chat-msg-role {
  display: block;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 3px;
  color: var(--color-text-muted);
}

.chat-msg.user .chat-msg-role {
  color: var(--color-primary);
}

.chat-msg.assistant .chat-msg-role {
  color: var(--color-accent);
}

.chat-msg-text {
  font-size: 13px;
  line-height: 1.5;
  display: block;
}

.typing {
  color: var(--color-text-muted);
  font-style: italic;
}

.chat-input-row {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}

.chat-input {
  flex: 1;
  padding: 8px 12px;
  font-size: 13px;
  font-family: var(--font-sans);
  color: var(--color-text);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  outline: none;
  transition: border-color 0.15s;
}

.chat-input:focus {
  border-color: var(--color-primary);
}

.chat-send {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-sans);
  color: white;
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}

.chat-send:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.chat-send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
