import { useQuery } from '@tanstack/react-query';
import { request } from '@/shared/api';
import { bootstrapSchema, runSchema } from './contracts';

export const workspaceKeys = {
  bootstrap: ['entities', 'workspace', 'local', 'bootstrap'] as const,
  run: (id: string | null) => ['entities', 'workspace', 'local', 'run', id] as const,
};
export function useBootstrap() {
  return useQuery({
    queryKey: workspaceKeys.bootstrap,
    queryFn: ({ signal }) => request('/bootstrap', bootstrapSchema, { signal }),
    refetchInterval: 5000,
    retry: 1,
  });
}
export function useRun(id: string | null) {
  return useQuery({
    queryKey: workspaceKeys.run(id),
    queryFn: ({ signal }) => request(`/runs/${encodeURIComponent(id ?? '')}`, runSchema, { signal }),
    enabled: id !== null,
    refetchInterval: (query) => query.state.data?.busy ? 1000 : false,
    retry: 1,
  });
}
