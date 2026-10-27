import type { RunState } from '@/entities/workspace';
import { PanelHeading } from '@/shared/ui';

const names: Record<string, string> = {
  blocker_detected: 'مانع شناسایی شد', repair_queued: 'تسک تعمیر ساخته شد',
  repair_verifying: 'در حال تأیید رفع مانع', task_resuming: 'ادامهٔ تسک اصلی',
  recovery_stuck: 'بازیابی نیازمند پیگیری است', recovery_blocked: 'مانع رفع نشده است',
  repair_consumers_invalidated: 'بررسی مجدد کارهای متأثر از تعمیر',
  task_retry_scheduled: 'تلاش اصلاحی با راهکار مشخص زمان‌بندی شد',
  agent_started: 'شروع کار', agent_finished: 'پایان کار', planning_finished: 'برنامه آماده شد',
  execution_incomplete: 'اجرا نیاز به پیگیری دارد', run_started: 'جلسه آغاز شد',
};
export function Activity({ events }: { events: RunState['events'] }) {
  return <section className="panel activity">
    <PanelHeading eyebrow="LIVE / EVENT STREAM" title="رویدادهای تیم" trailing={<span className="tag">{events.length} رویداد</span>} />
    {!events.length ? <p className="empty">رویدادهای واقعی اجرا در این بخش نمایش داده می‌شوند.</p> :
      <ol className="event-list">{events.slice(-60).reverse().map((event) => <li key={event.sequence}>
        <span className="event-dot" aria-hidden="true" /><div><strong>{names[event.event] ?? event.event}</strong>
          <p><bdi>{[event.agent, event.operation, event.task_id, event.parent_id, event.repair_id].filter(Boolean).join(' · ')}</bdi></p>
          {event.reason && <p>{event.reason}</p>}</div>
        <time dateTime={event.at}>{new Date(event.at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })}</time>
      </li>)}</ol>}
  </section>;
}
