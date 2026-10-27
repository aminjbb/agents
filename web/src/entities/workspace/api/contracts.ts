import { z } from 'zod';

export const connectionSchema = z.object({ configured: z.boolean(), model: z.string().nullable() });
export const agentSchema = z.object({
  id: z.string(), name: z.string(), description: z.string(), version: z.string().optional(),
});
const historySchema = z.object({
  id: z.string(), status: z.string(), text: z.string(),
  project_root: z.string(), updated_at: z.string().nullable(),
});
export const bootstrapSchema = z.object({
  agents: z.array(agentSchema), connection: connectionSchema,
  runs: z.array(historySchema), project_root: z.string(),
});
const taskSchema = z.object({
  id: z.string(), owner: z.string(), objective: z.string(),
  deliverable: z.string().optional(), depends_on: z.array(z.string()).default([]),
  write_scope: z.array(z.string()).default([]), acceptance_criteria: z.array(z.string()).default([]),
  status: z.string().default('pending'), result: z.unknown().optional(), review: z.unknown().optional(),
  feedback: z.string().optional(), error: z.string().nullable().optional(), recovery_error: z.string().optional(),
  active_repair: z.string().nullable().optional(),
  recovery: z.object({ parent_id: z.string() }).optional(),
  blockers: z.array(z.object({
    id: z.string(), category: z.string(), summary: z.string(), status: z.string(),
    repair_id: z.string().optional(),
  })).optional(),
});
const questionSchema = z.object({
  id: z.string(), question: z.string(), options: z.array(z.string()).optional(),
});
const eventSchema = z.object({
  sequence: z.number(), at: z.string(), event: z.string(),
  agent: z.string().optional(), operation: z.string().optional(),
  task_id: z.string().nullable().optional(), reason: z.string().optional(),
  parent_id: z.string().optional(), repair_id: z.string().optional(),
});
export const stateSchema = z.object({
  request: z.object({ text: z.string(), project_root: z.string(), mode: z.string().optional() }),
  planning: z.record(z.string(), z.unknown()).optional(),
  plan: z.object({ tasks: z.array(taskSchema) }).passthrough().nullable().optional(),
  questions: z.array(questionSchema).default([]), events: z.array(eventSchema).default([]),
  status: z.string(), error: z.string().nullable().optional(),
  audit: z.unknown().optional(), acceptance: z.unknown().optional(),
}).passthrough();
export const runSchema = z.object({
  id: z.string(), busy: z.boolean(), error: z.string().nullable().optional(),
  state: stateSchema.nullable(),
});
export const runIdSchema = z.object({ id: z.string() });
export type Bootstrap = z.infer<typeof bootstrapSchema>;
export type Agent = z.infer<typeof agentSchema>;
export type Run = z.infer<typeof runSchema>;
export type RunState = z.infer<typeof stateSchema>;
export type Task = z.infer<typeof taskSchema>;
