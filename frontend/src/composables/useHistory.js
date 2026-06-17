import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import client from '@/api/client'

export function useHistory({ page, pageSize, search, orderBy, orderDir } = {}) {
  const queryClient = useQueryClient()

  const { data: historyData, isLoading, refetch } = useQuery({
    queryKey: ['history', page, pageSize, search, orderBy, orderDir],
    queryFn: () =>
      client.get('/history', {
        params: {
          page: page?.value ?? 1,
          page_size: pageSize?.value ?? 20,
          search: search?.value || undefined,
          order_by: orderBy?.value ?? 'created_at',
          order_dir: orderDir?.value ?? 'desc',
        },
      }),
    keepPreviousData: true,
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => client.delete(`/history/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['history'] }),
  })

  const deleteAllMutation = useMutation({
    mutationFn: () => client.delete('/history/all'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['history'] }),
  })

  const batchDeleteMutation = useMutation({
    mutationFn: (ids) => client.post('/history/batch-delete', { ids }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['history'] }),
  })

  return {
    historyData,
    isLoading,
    refetch,
    deleteMutation,
    deleteAllMutation,
    batchDeleteMutation,
  }
}
