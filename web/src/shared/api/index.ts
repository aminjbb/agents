import { z } from 'zod';

export async function request<T>(path: string, schema: z.ZodType<T>, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', 'X-FAgent-Client': 'web', ...init.headers },
  });
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const error = z.object({ error: z.string() }).safeParse(data);
    throw new Error(error.success ? error.data.error : `خطای ارتباط با سرور (${response.status})`);
  }
  const parsed = schema.safeParse(data);
  if (!parsed.success) throw new Error('پاسخ سرور با ساختار مورد انتظار سازگار نیست.');
  return parsed.data;
}
