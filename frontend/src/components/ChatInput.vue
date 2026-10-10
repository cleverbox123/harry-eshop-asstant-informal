<script setup>
import { ref } from 'vue'

const emit = defineEmits(['send'])
const text = ref('')
const props = defineProps({
  disabled: { type: Boolean, default: false },
})

function submit() {
  const value = text.value.trim()
  if (!value || props.disabled) return
  emit('send', value)
  text.value = ''
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    submit()
  }
}
</script>

<template>
  <div class="input-bar">
    <textarea
      v-model="text"
      class="input"
      rows="1"
      placeholder="输入消息，Enter 发送，Shift+Enter 换行"
      :disabled="disabled"
      @keydown="onKeydown"
    />
    <button class="send-btn" :disabled="disabled || !text.trim()" @click="submit">
      {{ disabled ? '处理中...' : '发送' }}
    </button>
  </div>
</template>

<style scoped>
.input-bar {
  display: flex;
  gap: 10px;
  padding: 14px 18px;
  background: #fff;
  border-top: 1px solid #e5e7eb;
}
.input {
  flex: 1;
  resize: none;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.5;
  max-height: 120px;
  transition: border-color 0.15s;
}
.input:focus {
  border-color: #3b82f6;
}
.input:disabled {
  background: #f9fafb;
  cursor: not-allowed;
}
.send-btn {
  padding: 0 22px;
  background: #3b82f6;
  color: #fff;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.15s;
}
.send-btn:hover:not(:disabled) {
  background: #2563eb;
}
.send-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>
