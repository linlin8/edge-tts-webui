import { ref, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import client from '@/api/client'

export function useVoices() {
  const { data: voices, isLoading, error } = useQuery({
    queryKey: ['voices'],
    queryFn: () => client.get('/voices'),
    staleTime: 3600 * 1000, // 1小时客户端缓存
  })

  function filteredVoices(locale, gender, search) {
    const list = voices.value || []
    return list.filter((v) => {
      if (locale && v.Locale !== locale) return false
      if (gender && v.Gender !== gender) return false
      if (search) {
        const kw = search.toLowerCase()
        if (
          !v.ShortName.toLowerCase().includes(kw) &&
          !v.FriendlyName.toLowerCase().includes(kw) &&
          !v.Locale.toLowerCase().includes(kw)
        ) return false
      }
      return true
    })
  }

  const locales = computed(() => {
    const list = voices.value || []
    return [...new Set(list.map((v) => v.Locale))].sort()
  })

  return { voices, isLoading, error, filteredVoices, locales }
}
