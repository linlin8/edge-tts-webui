<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="`dialog-title-${uid}`"
      @keydown.esc="$emit('update:modelValue', false)"
    >
      <!-- 遮罩 -->
      <div
        class="absolute inset-0 bg-black/50 backdrop-blur-sm"
        @click="$emit('update:modelValue', false)"
      />
      <!-- 对话框 -->
      <div
        class="card relative z-10 w-full max-w-sm p-6 shadow-xl"
        @click.stop
      >
        <div class="flex items-start gap-3 mb-4">
          <div
            class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
            :class="iconClass"
          >
            <svg v-if="type === 'danger'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <h3
              :id="`dialog-title-${uid}`"
              class="font-semibold text-gray-900 dark:text-gray-100"
            >{{ title }}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ message }}</p>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <button
            class="btn-secondary"
            @click="$emit('update:modelValue', false)"
          >
            {{ cancelText }}
          </button>
          <button
            :class="type === 'danger' ? 'btn-danger' : 'btn-primary'"
            @click="handleConfirm"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '确定要执行此操作吗？' },
  confirmText: { type: String, default: '确认' },
  cancelText: { type: String, default: '取消' },
  type: { type: String, default: 'info', validator: v => ['info', 'danger'].includes(v) },
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const uid = Math.random().toString(36).slice(2)

const iconClass = computed(() => ({
  'bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-400': props.type === 'danger',
  'bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-blue-400': props.type === 'info',
}))

function handleConfirm() {
  emit('confirm')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-active .card,
.modal-leave-active .card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.modal-enter-from .card,
.modal-leave-to .card {
  transform: scale(0.95) translateY(-8px);
  opacity: 0;
}
</style>
