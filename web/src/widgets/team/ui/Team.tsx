import type { Agent, RunState } from '@/entities/workspace';
import { PanelHeading } from '@/shared/ui';
import './team.css';

const roles: Record<string, string> = {
  architect: 'تک‌لید و معمار', 'ui-crafter': 'طراح رابط کاربری',
  'form-wizard': 'متخصص فرم', 'state-master': 'مدیریت داده',
  navigator: 'مسیریابی و دسترسی', auditor: 'بازبین کیفیت',
};
export function Team({ agents, state, busy = false }: { agents: Agent[]; state?: RunState | null; busy?: boolean }) {
  const active = new Map<string, number>();
  for (const event of state?.events ?? []) {
    if (!event.agent) continue;
    const owner = event.agent.replace('@', '');
    const count = active.get(owner) ?? 0;
    if (event.event === 'agent_started') active.set(owner, count + 1);
    if (event.event === 'agent_finished') active.set(owner, Math.max(0, count - 1));
  }
  return <section className="team-section" aria-label="اعضای تیم مهندسی">
    <PanelHeading eyebrow="YOUR ENGINEERING TEAM" title="تیم شما، آمادهٔ ساختن" trailing={<span className="tag">{agents.length} عضو</span>} />
    <div className="team-grid">{agents.map((agent) => {
      const id = agent.id.replace('@', '');
      const working = busy && (active.get(id) ?? 0) > 0;
      return <article className={`agent-card ${working ? 'working' : ''}`} key={agent.id}>
        <div className="agent-card-top"><span className={`avatar ${id}`} aria-hidden="true">{id.slice(0, 1).toUpperCase()}</span>
          <span className={`agent-status ${working ? 'active' : ''}`}>{working ? 'مشغول کار' : 'آماده'}</span></div>
        <h3>{roles[id] ?? agent.name}</h3><span className="agent-handle" dir="ltr">@{id}</span>
        <p>{agent.description}</p>
      </article>;
    })}</div>
  </section>;
}
