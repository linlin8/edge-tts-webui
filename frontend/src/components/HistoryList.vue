<template>
  <div ref="el" class="flex flex-col h-full">
    <!-- 工具栏 -->
    <div class="flex items-center gap-2 mb-3 flex-shrink-0 flex-wrap">
      <!-- 搜索 -->
      <div class="relative flex-1 min-w-40">
        <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="searchKeyword"
          class="input-base pl-8 py-1.5 text-xs"
          placeholder="搜索历史..."
          aria-label="搜索历史记录"
          @keydown.enter="handleSearch"
        />
      </div>
      <!-- 排序 -->
      <select v-model="orderBy" class="input-base py-1.5 text-xs w-auto" aria-label="排序字段">
        <option value="created_at">按时间</option>
        <option value="file_size">按大小</option>
      </select>
      <button class="btn-ghost py-1.5 px-2 text-xs" @click="toggleOrder" :title="orderDir === 'desc' ? '从新到旧' : '从旧到新'">
        <svg class="w-3.5 h-3.5" :class="{'rotate-180': orderDir === 'asc'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>
      <!-- 批量操作 -->
      <template v-if="selected.size > 0">
        <span class="text-xs text-gray-500 dark:text-gray-400">已选 {{ selected.size }}</span>
        <button class="btn-danger py-1.5 px-2 text-xs" @click="confirmBatchDelete">
          删除所选
        </button>
        <button class="btn-ghost py-1.5 px-2 text-xs" @click="selected.clear()">
          取消选择
        </button>
      </template>
      <!-- 全选/全删 -->
      <button class="btn-ghost py-1.5 px-2 text-xs" @click="toggleSelectAll" :aria-label="allSelected ? '取消全选' : '全选'">
        {{ allSelected ? '取消全选' : '全选' }}
      </button>
      <button class="btn-ghost py-1.5 px-2 text-xs text-red-500 hover:text-red-600" @click="showDeleteAll = true">
        清空
      </button>
    </div>

    <!-- 历史列表 -->
    <div class="flex-1 overflow-y-auto space-y-2 pr-0.5">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="flex justify-center py-8">
        <svg class="w-6 h-6 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
      </div>
      <!-- 空状态 -->
      <div v-else-if="!items.length" class="flex flex-col items-center justify-center py-12 text-gray-400 dark:text-gray-500">
        <svg class="w-10 h-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
        </svg>
        <span class="text-sm">暂无历史记录</span>
      </div>
      <!-- 历史条目 -->
      <div
        v-for="item in items"
        :key="item.id"
        class="card p-3 group cursor-pointer select-none transition-all duration-150"
        :class="{
          'ring-2 ring-blue-400 ring-offset-1 dark:ring-offset-gray-900': selected.has(item.id),
          'hover:shadow-md': !selected.has(item.id)
        }"
        @click="toggleSelect(item.id)"
      >
        <div class="flex items-start gap-2.5">
          <!-- Checkbox -->
          <div class="mt-0.5 flex-shrink-0">
            <div
              class="w-4 h-4 rounded border-2 flex items-center justify-center transition-colors"
              :class="selected.has(item.id)
                ? 'bg-blue-500 border-blue-500'
                : 'border-gray-300 dark:border-gray-600 group-hover:border-blue-400'"
            >
              <svg v-if="selected.has(item.id)" class="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>
          <!-- 内容 -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-2 mb-1">
              <span class="text-xs font-medium text-gray-700 dark:text-gray-300 truncate">
                {{ item.voice }}
              </span>
              <div class="flex items-center gap-2 flex-shrink-0">
                <span class="text-xs text-gray-400 dark:text-gray-500" :title="formatAbsTime(item.created_at)">
                  {{ formatRelTime(item.created_at) }}
                </span>
                <span v-if="item.file_size" class="text-xs text-gray-400 dark:text-gray-500">
                  {{ formatSize(item.file_size) }}
                </span>
              </div>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 leading-snug mb-2">
              {{ item.text_preview || item.text }}
            </p>
            <!-- 内联播放器（展开） -->
            <AudioPlayer
              v-if="item.audio_available && expandedId === item.id"
              :src="item.audio_url"
              :label="item.voice"
              class="mt-1"
              @click.stop
            />
            <!-- 操作栏 -->
            <div class="flex items-center gap-1 mt-1" @click.stop>
              <button
                v-if="item.audio_available"
                class="btn-ghost py-0.5 px-2 text-xs"
                @click="toggleExpand(item.id)"
              >
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
                </svg>
                {{ expandedId === item.id ? '收起' : '播放' }}
              </button>
              <span v-else class="text-xs text-gray-400 italic">音频已清理</span>
              <button
                class="btn-ghost py-0.5 px-2 text-xs text-red-400 hover:text-red-600 ml-auto"
                @click.stop="confirmDelete(item.id)"
                aria-label="删除此条记录"
              >
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 pt-3 flex-shrink-0">
      <button class="btn-ghost py-1 px-2 text-xs" :disabled="page === 1" @click="page--">上一页</button>
      <span class="text-xs text-gray-500 dark:text-gray-400">{{ page }} / {{ totalPages }}</span>
      <button class="btn-ghost py-1 px-2 text-xs" :disabled="page === totalPages" @click="page++">下一页</button>
    </div>

    <!-- 确认对话框 -->
    <ConfirmDialog
      v-model="showDeleteSingle"
      title="删除记录"
      message="确认删除这条历史记录？"
      type="danger"
      @confirm="doDeleteSingle"
    />
    <ConfirmDialog
      v-model="showDeleteBatch"
      title="批量删除"
      :message="`确认删除选中的 ${selected.size} 条记录？`"
      type="danger"
      @confirm="doBatchDelete"
    />
    <ConfirmDialog
      v-model="showDeleteAll"
      title="清空历史"
      message="确认清空所有历史记录？此操作不可撤销。"
      type="danger"
      @confirm="doDeleteAll"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useToast } from 'vue-toastification'
import { useHistory } from '../composables/useHistory.js'
import AudioPlayer from './AudioPlayer.vue'
import ConfirmDialog from './ConfirmDialog.vue'

const toast = useToast()

const page = ref(1)
const orderBy = ref('created_at')
const orderDir = ref('desc')
const searchKeyword = ref('')
const expandedId = ref(null)
const selected = ref(new Set())
const showDeleteSingle = ref(false)
const showDeleteBatch = ref(false)
const showDeleteAll = ref(false)
const deleteTargetId = ref(null)

const { historyData, isLoading, refetch, deleteMutation, deleteAllMutation, batchDeleteMutation } = useHistory({
  page, pageSize: ref(20), search: searchKeyword, orderBy, orderDir,
})

const items = computed(() => historyData.value?.items || [])
const totalPages = computed(() => historyData.value?.total_pages || 1)
const allSelected = computed(() =>
  items.value.length > 0 && items.value.every(i => selected.value.has(i.id))
)

watch(page, () => { selected.value.clear() })

// 切换到当前 Tab 时自动刷新
const el = ref(null)
let observer = null

function setupVisibilityRefetch(element) {
  if (!element || !window.IntersectionObserver) return
  observer?.disconnect()
  observer = new IntersectionObserver(
    ([entry]) => { if (entry.isIntersecting) refetch() },
    { threshold: 0.01 }
  )
  observer.observe(element)
}

onMounted(() => setupVisibilityRefetch(el.value))
onBeforeUnmount(() => observer?.disconnect())

function toggleOrder() {
  orderDir.value = orderDir.value === 'desc' ? 'asc' : 'desc'
}

function handleSearch() {
  page.value = 1
}

function toggleSelect(id) {
  const s = new Set(selected.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  selected.value = s
}

function toggleSelectAll() {
  if (allSelected.value) {
    selected.value = new Set()
  } else {
    selected.value = new Set(items.value.map(i => i.id))
  }
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function formatRelTime(iso) {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m}分钟前`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}小时前`
  const d = Math.floor(h / 24)
  if (d < 7) return `${d}天前`
  return new Date(iso).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function formatAbsTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN')
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / 1024 / 1024).toFixed(1)}MB`
}

function confirmDelete(id) {
  deleteTargetId.value = id
  showDeleteSingle.value = true
}

async function doDeleteSingle() {
  try {
    await deleteMutation.mutateAsync(deleteTargetId.value)
    toast.success('删除成功')
  } catch {
    toast.error('删除失败')
  }
}

function confirmBatchDelete() {
  showDeleteBatch.value = true
}

async function doBatchDelete() {
  try {
    await batchDeleteMutation.mutateAsync([...selected.value])
    selected.value = new Set()
    toast.success('批量删除成功')
  } catch {
    toast.error('批量删除失败')
  }
}

async function doDeleteAll() {
  try {
    await deleteAllMutation.mutateAsync()
    selected.value = new Set()
    toast.success('已清空历史')
  } catch {
    toast.error('清空失败')
  }
}
</script>
