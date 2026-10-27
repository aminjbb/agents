import { useMutation, useQueryClient } from '@tanstack/react-query';
import { z } from 'zod';
import { workspaceKeys } from '@/entities/workspace';
import { request } from '@/shared/api';

const connection = z.object({ configured: z.boolean(), model: z.string().nullable() });
const runId = z.object({ id: z.string() });
export function useConnection() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: { api_key: string; model?: string }) =>
      request('/connection', connection, { method: 'POST', body: JSON.stringify(input) }),
    onSuccess: () => client.invalidateQueries({ queryKey: workspaceKeys.bootstrap }),
    gcTime: 0,
  });
}
export function useDisconnect() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => request('/connection', connection, { method: 'DELETE', body: '{}' }),
    onSuccess: () => client.invalidateQueries({ queryKey: workspaceKeys.bootstrap }),
  });
}
export function useCreateRun() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: { text: string; project_root: string }) =>
      request('/runs', runId, { method: 'POST', body: JSON.stringify(input) }),
    onSuccess: () => client.invalidateQueries({ queryKey: workspaceKeys.bootstrap }),
  });
}
export function useResumeRun(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: { answers?: Record<string, string>; execute?: boolean; retry_tasks?: string[] }) =>
      request(`/runs/${encodeURIComponent(id)}/resume`, runId, { method: 'POST', body: JSON.stringify(input) }),
    onSuccess: async () => {
      await Promise.all([
        client.invalidateQueries({ queryKey: workspaceKeys.run(id) }),
        client.invalidateQueries({ queryKey: workspaceKeys.bootstrap }),
      ]);
    },
  });
}
