import type { Run } from '@/entities/workspace';
import { ErrorNotice } from '@/shared/ui';
import { useResumeRun } from '../api/mutations';

export function RunActions({ run }: { run: Run }) {
  const mutation = useResumeRun(run.id);
  const state = run.state;
  const retries = state?.plan?.tasks.filter((task) => ['blocked', 'failed', 'changes_required', 'running', 'review', 'ready'].includes(task.status)).map((task) => task.id) ?? [];
  const planned = state?.status === 'planned';
  const interrupted = !run.busy && ['intake', 'executing', 'reviewing'].includes(state?.status ?? '');
  const recoverable = (interrupted || ['blocked', 'changes_required'].includes(state?.status ?? '')) && !state?.questions.length;
  if (!planned && !recoverable) return null;
  return <div className="approval">
    <div><strong>{planned ? 'برنامه آمادهٔ تأیید است' : 'اجرا به بررسی شما نیاز دارد'}</strong>
      <p className="muted">{planned ? 'مسئولیت‌ها و محدودهٔ تغییر فایل‌ها را بررسی کنید؛ با تأیید شما تیم روی پروژه کار می‌کند.' : 'شواهد و تغییرات احتمالی را بررسی کنید و سپس ادامه دهید.'}</p>
      {interrupted && <p className="muted">جلسه در اجرای قبلی قطع شده است. پیش از ادامه، تغییر فایل‌ها و قفل‌های باقی‌مانده را بررسی کنید. ادامه فقط با اقدام شما انجام می‌شود.</p>}</div>
    <ErrorNotice error={mutation.error} />
    <button type="button" className="button primary" disabled={run.busy || mutation.isPending}
      onClick={() => mutation.mutate({ execute: !!state?.plan, ...(retries.length ? { retry_tasks: retries } : {}) })}>
      {mutation.isPending ? 'در حال ادامه…' : planned ? 'تأیید برنامه و شروع اجرا ←' : state?.plan ? 'ادامه / تلاش مجدد' : 'ادامهٔ جلسه و برنامه‌ریزی'}</button>
  </div>;
}
