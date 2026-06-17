<template>
  <div class="flex flex-col h-full">
    <!-- 顶部工具栏 -->
    <div class="flex items-center gap-2 mb-3 flex-shrink-0">
      <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 flex-1">RAGFlow 对话</h3>
      <span
        v-if="!isConfigured"
        class="text-xs text-amber-500 bg-amber-50 dark:bg-amber-900/30 px-2 py-0.5 rounded-full"
      >
        未配置
      </span>
      <button
        class="btn-ghost py-1 px-2 text-xs"
        title="新建会话"
        @click="handleNewSession"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        新建会话
      </button>
      <button
        v-if="isStreaming"
        class="btn-ghost py-1 px-2 text-xs text-red-500"
        @click="abort"
      >
        停止
      </button>
    </div>

    <!-- 消息列表 -->
    <div
      ref="messagesRef"
      class="flex-1 overflow-y-auto space-y-4 pr-1"
    >
      <!-- 空状态 -->
      <div
        v-if="!messages.length"
        class="flex flex-col items-center justify-center h-full text-gray-400 dark:text-gray-500 gap-2"
      >
        <svg class="w-12 h-12 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>
        <span class="text-sm">向 RAGFlow 发起对话</span>
        <span v-if="!isConfigured" class="text-xs text-amber-500">请先配置 RAGFLOW_API_URL 等环境变量</span>
      </div>

      <!-- 消息气泡 -->
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <!-- AI 消息 -->
        <div v-if="msg.role === 'assistant'" class="flex items-start gap-2 max-w-[85%]">
          <!-- 头像 -->
          <div class="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-0.5">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zm0 16a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
            </svg>
          </div>
          <div class="flex flex-col gap-1.5">
            <div
              class="card px-3.5 py-2.5 rounded-tl-none shadow-sm"
            >
              <!-- AI Loading 三点动效 -->
              <div v-if="msg.loading" class="flex gap-1 items-center py-1">
                <span v-for="i in 3" :key="i"
                  class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce"
                  :style="{ animationDelay: `${(i-1) * 0.15}s` }"
                />
              </div>
              <!-- Markdown 渲染内容 -->
              <div
                v-else
                class="prose-chat text-gray-800 dark:text-gray-200"
                v-html="renderMarkdown(msg.content)"
              />
            </div>
            <!-- TTS播放器（如果有音频） -->
            <AudioPlayer
              v-if="msg.audioSrc"
              :src="msg.audioSrc"
              :label="msg.audioLabel"
              class="max-w-sm"
            />
          </div>
        </div>

        <!-- 用户消息 -->
        <div v-else class="max-w-[75%]">
          <div class="bg-blue-600 text-white px-3.5 py-2.5 rounded-xl rounded-tr-none text-sm leading-relaxed shadow-sm">
            {{ msg.content }}
          </div>
        </div>
      </div>

      <!-- 底部占位 -->
      <div ref="bottomRef" />
    </div>

    <!-- 输入区域 -->
    <div class="flex-shrink-0 pt-3 border-t border-gray-200 dark:border-gray-700 mt-3">
      <!-- TTS选项 -->
      <div class="flex items-center gap-3 mb-2 text-xs">
        <label class="flex items-center gap-1.5 cursor-pointer select-none">
          <div
            class="w-8 h-4 rounded-full transition-colors relative"
            :class="ttsEnabled ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'"
            @click="ttsEnabled = !ttsEnabled"
          >
            <div
              class="absolute top-0.5 left-0.5 w-3 h-3 rounded-full bg-white shadow transition-transform"
              :class="ttsEnabled ? 'translate-x-4' : ''"
            />
          </div>
          <span class="text-gray-600 dark:text-gray-400">回复转语音</span>
        </label>
        <span v-if="ttsEnabled && ttsVoice" class="text-gray-400 truncate max-w-32">{{ ttsVoice }}</span>
        <span v-if="ttsEnabled" class="text-gray-400 dark:text-gray-500 font-mono">
          {{ ttsRate }} / {{ ttsVolume }} / {{ ttsPitch }}
        </span>
      </div>
      <!-- 输入框 + 发送 -->
      <div class="flex gap-2">
        <textarea
          v-model="inputText"
          class="input-base resize-none text-sm leading-relaxed flex-1"
          rows="2"
          placeholder="输入问题... (Enter 发送，Shift+Enter 换行)"
          :disabled="isStreaming || !isConfigured"
          @keydown.enter.exact.prevent="handleSend"
          @keydown.shift.enter.exact="() => {}"
        />
        <button
          class="btn-primary self-end px-3"
          :disabled="isStreaming || !inputText.trim() || !isConfigured"
          @click="handleSend"
          aria-label="发送消息"
        >
          <svg v-if="isStreaming" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, watch } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import { useToast } from 'vue-toastification'
import { useChat } from '../composables/useChat.js'
import AudioPlayer from './AudioPlayer.vue'

const props = defineProps({
  selectedVoice: { type: String, default: '' },
  isConfigured: { type: Boolean, default: false },
  ttsRate: { type: String, default: '+0%' },
  ttsVolume: { type: String, default: '+0%' },
  ttsPitch: { type: String, default: '+0Hz' },
})

const toast = useToast()
const messagesRef = ref(null)
const bottomRef = ref(null)
const inputText = ref('')
const ttsEnabled = ref(false)

const ttsVoice = computed(() => props.selectedVoice)

// 配置 marked + highlight.js
marked.setOptions({
  highlight(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  },
  langPrefix: 'hljs language-',
  breaks: true,
})

function renderMarkdown(text) {
  if (!text) return ''
  // 过滤 RAGFlow 引用标记，如 [ID:0]、[ID:1] 等
  const cleaned = text.replace(/\[ID:\d+\]/g, '')
  const raw = marked.parse(cleaned)
  return DOMPurify.sanitize(raw, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'code', 'pre', 'ul', 'ol', 'li',
      'h1', 'h2', 'h3', 'h4', 'blockquote', 'a', 'span', 'div'],
    ALLOWED_ATTR: ['class', 'href', 'target', 'rel'],
  })
}

const { messages, isStreaming, send, newSession, abort } = useChat()

function scrollToBottom() {
  nextTick(() => {
    bottomRef.value?.scrollIntoView({ behavior: 'smooth' })
  })
}

watch(messages, scrollToBottom, { deep: true })

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || isStreaming.value) return
  inputText.value = ''
  try {
    await send(text, ttsEnabled.value ? {
      voice: ttsVoice.value,
      rate: props.ttsRate,
      volume: props.ttsVolume,
      pitch: props.ttsPitch,
    } : null)
  } catch (e) {
    toast.error(e.message || '发送失败')
  }
}

function handleNewSession() {
  newSession()
  toast.info('已开启新会话')
}
</script>
