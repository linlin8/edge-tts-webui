<template>
  <div class="flex flex-col gap-3 h-full">
    <!-- 搜索栏 -->
    <div class="flex gap-2">
      <div class="relative flex-1">
        <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="searchText"
          class="input-base pl-8"
          placeholder="搜索语音..."
          aria-label="搜索语音"
        />
      </div>
    </div>
    <!-- 过滤器 -->
    <div class="flex gap-2 flex-wrap">
      <select v-model="selectedLocale" class="input-base flex-1 min-w-24" aria-label="语言/地区">
        <option value="">全部语言</option>
        <option v-for="loc in locales" :key="loc" :value="loc">{{ loc }}</option>
      </select>
      <select v-model="selectedGender" class="input-base flex-1 min-w-24" aria-label="性别">
        <option value="">全部性别</option>
        <option value="Male">男声</option>
        <option value="Female">女声</option>
      </select>
    </div>
    <!-- 结果计数 -->
    <div class="text-xs text-gray-500 dark:text-gray-400 px-1">
      共 {{ filtered.length }} 个语音
      <span v-if="modelValue" class="ml-1 text-blue-500">（已选: {{ modelValue }}）</span>
    </div>
    <!-- 虚拟列表 -->
    <div class="flex-1 overflow-hidden border border-gray-200 dark:border-gray-700 rounded-lg">
      <RecycleScroller
        v-if="filtered.length > 0"
        class="h-full"
        :items="filtered"
        :item-size="52"
        key-field="ShortName"
        v-slot="{ item }"
      >
        <div
          class="flex items-center gap-3 px-3 py-2.5 cursor-pointer border-b border-gray-100 dark:border-gray-700/50
            hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors duration-100"
          :class="{
            'bg-blue-50 dark:bg-blue-900/30 border-l-2 border-l-blue-500': modelValue === item.ShortName
          }"
          role="option"
          :aria-selected="modelValue === item.ShortName"
          @click="selectVoice(item)"
          @dblclick="previewVoice(item)"
        >
          <!-- 选中标记 -->
          <div class="w-5 flex-shrink-0 flex items-center justify-center">
            <svg v-if="modelValue === item.ShortName" class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
          </div>
          <!-- 语音信息 -->
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">
              {{ item.FriendlyName || item.ShortName }}
            </div>
            <div class="text-xs text-gray-400 dark:text-gray-500 truncate">
              {{ item.ShortName }} · {{ item.Gender === 'Male' ? '男声' : '女声' }}
            </div>
          </div>
          <!-- 试听按钮（波形动效） -->
          <button
            class="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center
              hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            :aria-label="`试听 ${item.FriendlyName}`"
            :disabled="previewingVoice === item.ShortName"
            @click.stop="previewVoice(item)"
          >
            <!-- 播放波形动效 -->
            <template v-if="previewingVoice === item.ShortName">
              <span class="flex gap-0.5 items-end h-4">
                <span v-for="i in 3" :key="i"
                  class="w-0.5 bg-blue-500 rounded-sm animate-wave"
                  :style="{ animationDelay: `${(i-1) * 0.15}s` }"
                />
              </span>
            </template>
            <template v-else>
              <svg class="w-3.5 h-3.5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clip-rule="evenodd"/>
              </svg>
            </template>
          </button>
        </div>
      </RecycleScroller>
      <div v-else class="flex items-center justify-center h-full text-sm text-gray-400 dark:text-gray-500">
        未找到匹配的语音
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { useVoices } from '../composables/useVoices.js'
import { apiClient } from '../api/client.js'

const props = defineProps({
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const toast = useToast()
const { filteredVoices, locales } = useVoices()

const searchText = ref('')
const selectedLocale = ref('')
const selectedGender = ref('')
const previewingVoice = ref(null)

const filtered = computed(() =>
  filteredVoices(selectedLocale.value, selectedGender.value, searchText.value)
)

function selectVoice(item) {
  emit('update:modelValue', item.ShortName)
}

async function previewVoice(item) {
  if (previewingVoice.value === item.ShortName) return
  previewingVoice.value = item.ShortName
  try {
    const data = await apiClient.post('/tts/synthesize', {
      text: '你好，这是试听效果。',
      voice: item.ShortName,
      rate: '+0%',
      volume: '+0%',
      pitch: '+0Hz',
    })
    const audio = new Audio(data.audio_url)
    audio.onended = () => { previewingVoice.value = null }
    audio.onerror = () => { previewingVoice.value = null }
    audio.play()
  } catch {
    previewingVoice.value = null
    toast.error('试听失败')
  }
}
</script>

<style scoped>
@keyframes wave {
  0%, 100% { height: 6px; }
  50% { height: 14px; }
}
.animate-wave {
  animation: wave 0.7s ease-in-out infinite;
}
</style>
