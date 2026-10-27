import type { Run } from '@/entities/workspace';
import { Questions, RunActions } from '@/features/manage-work';
import { Evidence, ErrorNotice } from '@/shared/ui';
import { TaskBoard } from './TaskBoard';
import { Activity } from './Activity';
import './run.css';

const statuses: Record<string, string> = {
  intake: 'تک‌لید در حال بررسی است', planned: 'منتظر تأیید برنامه', needs_input: 'منتظر پاسخ شما',
  executing: 'تیم در حال اجراست', reviewing: 'در حال بازبینی', delivered: 'تحویل شد',
  blocked: 'نیازمند پیگیری', changes_required: 'نیازمند اصلاح',
};
export function RunWorkspace({ run, refresh }: { run: Run; refresh: () => void }) {
  const state = run.state;
  const error = run.error || state?.error;
  return <div className="stack run-workspace">
    <section className="panel run-brief">
      <div className="panel-heading"><span className="eyebrow">TECH LEAD / SESSION</span>
        <span className="tag" role="status">{run.busy ? 'در حال پردازش…' : statuses[state?.status ?? ''] ?? state?.status ?? 'در انتظار شروع'}</span></div>
      <h2>{state?.request.text ?? 'در حال دریافت اطلاعات جلسه…'}</h2>
      {state && <p className="project-path" dir="ltr">{state.request.project_root}</p>}
      <ErrorNotice error={error ? new Error(error) : null} retry={refresh} />
      {typeof state?.planning?.summary === 'string' && <p className="lead-summary" dir="auto">{state.planning.summary}</p>}
      {run.busy && <p className="muted" role="status">ارتباط برقرار است؛ وضعیت تیم هر ثانیه به‌روز می‌شود.</p>}
    </section>
    {!!state?.questions.length && <Questions key={`${run.id}:${state.questions.map((question) => question.id).join('|')}`}
      id={run.id} questions={state.questions} busy={run.busy} />}
    {state?.plan && <TaskBoard tasks={state.plan.tasks} />}
    {state && <RunActions run={run} />}
    {state && <section className="review-results"><Evidence value={state.audit} title="گزارش بازبین کیفیت" />
      <Evidence value={state.acceptance} title="جمع‌بندی و پذیرش تک‌لید" /></section>}
    <Activity events={state?.events ?? []} />
  </div>;
}
