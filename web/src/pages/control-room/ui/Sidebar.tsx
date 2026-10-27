import type { Bootstrap } from '@/entities/workspace';

type Props = { runs: Bootstrap['runs']; selected: string | null; select: (id: string | null) => void };
export function Sidebar({ runs, selected, select }: Props) {
  return <aside className="sidebar">
    <a className="brand" href="#main"><span className="brand-symbol" aria-hidden="true">F<span>↗</span></span>
      <div><strong>FAgent</strong><span>ENGINEERING WORKSPACE</span></div></a>
    <div className="sidebar-section"><span className="eyebrow">فضای کار شما</span>
      <button type="button" className={`new-session ${selected === null ? 'selected' : ''}`} onClick={() => select(null)}>
        <span aria-hidden="true">＋</span> جلسهٔ جدید</button></div>
    <nav className="history" aria-label="تاریخچه جلسات"><div className="history-heading"><span>جلسه‌های اخیر</span><span>{runs.length}</span></div>
      {!runs.length && <p className="muted">اولین جلسهٔ تیم را شروع کنید.</p>}
      {runs.map((run) => <button type="button" className={`history-item ${selected === run.id ? 'selected' : ''}`}
        key={run.id} onClick={() => select(run.id)} aria-current={selected === run.id ? 'page' : undefined}>
        <span>{run.text}</span><small><bdi>{run.status}</bdi> · {run.updated_at ? new Date(run.updated_at).toLocaleDateString('fa-IR') : 'بدون زمان ثبت‌شده'}</small>
      </button>)}
    </nav>
    <div className="sidebar-footer"><span className="connection-dot connected" />
      <div><strong>محیط توسعهٔ محلی</strong><small>از جلسه تا تحویل، کنار تیم</small></div></div>
  </aside>;
}
