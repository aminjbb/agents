import type { Task } from '@/entities/workspace';
import { Evidence, PanelHeading } from '@/shared/ui';

const taskStatus: Record<string, string> = {
  pending: 'در صف', running: 'در حال اجرا', done: 'انجام‌شده',
  blocked: 'متوقف', failed: 'ناموفق', changes_required: 'نیازمند اصلاح',
};
export function TaskBoard({ tasks }: { tasks: Task[] }) {
  const done = tasks.filter((task) => task.status === 'done').length;
  return <section className="panel">
    <PanelHeading eyebrow="02 / DELIVERY PLAN" title="تقسیم کار تیم" trailing={<span className="tag">{done} / {tasks.length} کامل</span>} />
    {!tasks.length && <p className="empty">هنوز تسکی تعریف نشده است.</p>}
    <div className="task-grid">{tasks.map((task) => <article className="task-card" key={task.id}>
      <div className="task-meta"><code>{task.id}</code><span className="tag" data-status={task.status}>{taskStatus[task.status] ?? task.status}</span></div>
      <h3>{task.objective}</h3><span className="agent-handle" dir="ltr">{task.owner}</span>
      {task.deliverable && <p>{task.deliverable}</p>}
      <div className="task-dependencies"><span className="muted">وابستگی:</span> {task.depends_on.length ? task.depends_on.join('، ') : 'مستقل'}</div>
      <details><summary>محدوده و معیار تحویل</summary>
        <ul>{task.acceptance_criteria.map((criterion) => <li key={criterion}>{criterion}</li>)}</ul>
        {task.write_scope.map((path) => <code className="scope-path" dir="ltr" key={path}>{path}</code>)}
      </details>
      <Evidence value={task.result} title="خروجی و شواهد اجرا" />
      <Evidence value={task.review} title="نتیجهٔ بازبینی" />
    </article>)}</div>
  </section>;
}
