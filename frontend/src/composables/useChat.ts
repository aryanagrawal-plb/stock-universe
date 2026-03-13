import { ref } from "vue";
import type { ChatMessage } from "../types/stock";

export function useChat() {
  const messages = ref<ChatMessage[]>([]);
  const isSending = ref(false);

  async function sendMessage(content: string): Promise<void> {
    if (!content.trim()) return;

    messages.value.push({ role: "user", content });
    isSending.value = true;

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      messages.value.push({ role: "assistant", content: data.reply });
    } catch {
      messages.value.push({
        role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
      });
    } finally {
      isSending.value = false;
    }
  }

  function clearMessages(): void {
    messages.value = [];
  }

  return { messages, isSending, sendMessage, clearMessages };
}
