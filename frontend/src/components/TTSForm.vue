<template>
  <div class="flex flex-col gap-4 h-full">
    <!-- 文本输入区 -->
    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-gray-600 dark:text-gray-400">合成文本</label>
      <textarea
        ref="textareaRef"
        v-model="form.text"
        class="input-base resize-none leading-relaxed"
        :class="{ 'border-red-400 focus:ring-red-400': textError }"
        rows="5"
        maxlength="5000"
        placeholder="请输入要合成的文字（最多5000字）..."
        aria-label="合成文本"
        @keydown.ctrl.enter.prevent="handleSubmit"
      />
      <div class="flex justify-between items-center">
        <span v-if="textError" class="text-xs text-red-500">{{ textError }}</span>
        <span v-else class="text-xs text-gray-400">Ctrl+Enter 快速合成</span>
        <span class="text-xs text-gray-400 ml-auto">{{ form.text.length }}/5000</span>
      </div>
    </div>

    <!-- 参数调节 -->
    <div class="grid grid-cols-3 gap-3">
      <!-- 语速 -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-medium text-gray-600 dark:text-gray-400">
          语速 <span class="font-mono text-blue-500">{{ rateDisplay }}</span>
        </label>
        <input
          v-model.number="rateVal"
          type="range"
          min="-50"
          max="100"
          step="5"
          class="slider"
          aria-label="语速调节"
        />
        <div class="flex justify-between text-xs text-gray-400">
          <span>-50%</span><span>+100%</span>
        </div>
      </div>
      <!-- 音量 -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-medium text-gray-600 dark:text-gray-400">
          音量 <span class="font-mono text-blue-500">{{ volumeDisplay }}</span>
        </label>
        <input
          v-model.number="volumeVal"
          type="range"
          min="-50"
          max="100"
          step="5"
          class="slider"
          aria-label="音量调节"
        />
        <div class="flex justify-between text-xs text-gray-400">
          <span>-50%</span><span>+100%</span>
        </div>
      </div>
      <!-- 音调 -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-medium text-gray-600 dark:text-gray-400">
          音调 <span class="font-mono text-blue-500">{{ pitchDisplay }}</span>
        </label>
        <input
          v-model.number="pitchVal"
          type="range"
          min="-50"
          max="50"
          step="5"
          class="slider"
          aria-label="音调调节"
        />
        <div class="flex justify-between text-xs text-gray-400">
          <span>-50Hz</span><span>+50Hz</span>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex gap-2 pt-1">
      <button
        class="btn-primary flex-1"
        :disabled="isLoading || !selectedVoice"
        @click="handleSubmit"
        aria-label="合成语音"
      >
        <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
        </svg>
        {{ isLoading ? '合成中...' : '合成语音' }}
      </button>
      <button
        class="btn-secondary"
        :disabled="isLoading || !selectedVoice"
        @click="handleStream"
        aria-label="流式播放"
        title="流式播放（边合成边播放）"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        流式
      </button>
      <button class="btn-ghost" @click="resetForm" title="重置参数">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
      </button>
    </div>

    <!-- 合成结果播放器 -->
    <AudioPlayer
      v-if="resultAudio"
      :src="resultAudio"
      :label="resultLabel"
      class="mt-1"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { apiClient } from '../api/client.js'
import AudioPlayer from './AudioPlayer.vue'

const props = defineProps({
  selectedVoice: { type: String, default: '' },
})

const emit = defineEmits(['update:params'])

const toast = useToast()
const isLoading = ref(false)
const resultAudio = ref(null)
const resultLabel = ref('')

// 滑块数值（纯数字，直接 v-model.number 绑定）
const rateVal = ref(0)
const volumeVal = ref(0)
const pitchVal = ref(0)

// 显示用的格式化字符串
const rateDisplay = computed(() => formatRate(rateVal.value))
const volumeDisplay = computed(() => formatVolume(volumeVal.value))
const pitchDisplay = computed(() => formatPitch(pitchVal.value))

// 滑块变化时通知父组件
watch([rateVal, volumeVal, pitchVal], () => {
  emit('update:params', {
    rate: formatRate(rateVal.value),
    volume: formatVolume(volumeVal.value),
    pitch: formatPitch(pitchVal.value),
  })
}, { immediate: true })

const form = ref({
  text: '',
})

const textError = computed(() => {
  if (form.value.text.length > 5000) return '文字超出5000字限制'
  return ''
})

function formatRate(val) {
  const n = parseInt(val)
  return n >= 0 ? `+${n}%` : `${n}%`
}
function formatVolume(val) {
  const n = parseInt(val)
  return n >= 0 ? `+${n}%` : `${n}%`
}
function formatPitch(val) {
  const n = parseInt(val)
  return n >= 0 ? `+${n}Hz` : `${n}Hz`
}

function resetForm() {
  rateVal.value = 0
  volumeVal.value = 0
  pitchVal.value = 0
}

async function handleSubmit() {
  if (!form.value.text.trim()) {
    toast.warning('请输入合成文字')
    return
  }
  if (!props.selectedVoice) {
    toast.warning('请先选择语音')
    return
  }
  if (textError.value) return

  isLoading.value = true
  resultAudio.value = null
  try {
    const data = await apiClient.post('/tts/synthesize', {
      text: form.value.text,
      voice: props.selectedVoice,
      rate: formatRate(rateVal.value),
      volume: formatVolume(volumeVal.value),
      pitch: formatPitch(pitchVal.value),
    })
    resultAudio.value = data.audio_url
    resultLabel.value = data.audio_url.split('/').pop()
    toast.success('合成成功')
  } catch (e) {
    toast.error(e.message || '合成失败')
  } finally {
    isLoading.value = false
  }
}

async function handleStream() {
  if (!form.value.text.trim()) {
    toast.warning('请输入合成文字')
    return
  }
  if (!props.selectedVoice) {
    toast.warning('请先选择语音')
    return
  }
  try {
    const { token } = await apiClient.post('/tts/stream-token', {
      text: form.value.text,
      voice: props.selectedVoice,
      rate: formatRate(rateVal.value),
      volume: formatVolume(volumeVal.value),
      pitch: formatPitch(pitchVal.value),
    })
    const audio = new Audio(`/api/v1/tts/stream/${token}`)
    audio.onerror = () => toast.error('流式播放失败，请重试')
    audio.play()
    toast.success('开始流式播放')
  } catch (e) {
    toast.error(e.message || '流式播放失败')
  }
}
</script>

<style scoped>
.slider {
  @apply w-full h-1.5 rounded-full appearance-none cursor-pointer
    bg-gray-200 dark:bg-gray-600 accent-blue-500;
}
</style>
