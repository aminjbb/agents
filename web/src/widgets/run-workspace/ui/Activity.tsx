import type { RunState } from '@/entities/workspace';
import { PanelHeading } from '@/shared/ui';

const names: Record<string, string> = {
  agent_started: 'شروع کار', agent_finished: 'پایان کار', planning_finished: 'برنامه آماده شد',
  execution_incomplete: 'اجرا نیاز به پیگیری دارد', run_started: 'جلسه آغاز شد',
};
export function Activity({ events }: { events: RunState['events'] }) {
  return <section className="panel activity">
    <PanelHeading eyebrow="LIVE / EVENT STREAM" title="رویدادهای تیم" trailing={<span className="tag">{events.length} رویداد</span>} />
    {!events.length ? <p className="empty">رویدادهای واقعی اجرا در این بخش نمایش داده می‌شوند.</p> :
      <ol className="event-list">{events.slice(-60).reverse().map((event) => <li key={event.sequence}>
        <span className="event-dot" aria-hidden="true" /><div><strong>{names[event.event] ?? event.event}</strong>
          <p><bdi>{[event.agent, event.operation, event.task_id].filter(Boolean).join(' · ')}</bdi></p>
          {event.reason && <p>{event.reason}</p>}</div>
        <time dateTime={event.at}>{new Date(event.at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })}</time>
      </li>)}</ol>}
  </section>;
}
