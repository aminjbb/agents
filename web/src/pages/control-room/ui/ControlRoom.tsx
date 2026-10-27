import { useState } from 'react';
import { useBootstrap, useRun } from '@/entities/workspace';
import { Connection, Meeting } from '@/features/manage-work';
import { Team } from '@/widgets/team';
import { RunWorkspace } from '@/widgets/run-workspace';
import { ErrorNotice } from '@/shared/ui';
import { Sidebar } from './Sidebar';
import './shell.css';

export function ControlRoom() {
  const [selected, select] = useState<string | null>(null);
  const bootstrap = useBootstrap();
  const run = useRun(selected);
  const data = bootstrap.data;
  return <div className="workspace">
    <a className="skip-link" href="#main">رفتن به محتوای اصلی</a>
    <Sidebar runs={data?.runs ?? []} selected={selected} select={select} />
    <main id="main" className="main-content">
      <header className="topbar"><span>فضای کار <span className="slash">/</span> اتاق فرمان</span>
        <span className="workspace-label"><span className="connection-dot" /> LOCAL WORKSPACE</span></header>
      <div className="page-content">
        <div className="welcome"><div><span className="eyebrow">BUILD WITH YOUR AGENTS</span>
          <h1>ایدهٔ تو. تخصص تیم.</h1><p>با تک‌لید گفتگو کن، مسیر را مشخص کن و ساختن را به تیم بسپار.</p></div>
          <span className="version-badge">FA / 01</span></div>
        <ErrorNotice error={bootstrap.error} retry={() => void bootstrap.refetch()} />
        {bootstrap.isPending && <div className="panel empty" role="status">در حال اتصال به فضای کار…</div>}
        {data && <>
          <Team agents={data.agents} state={selected ? run.data?.state : null} busy={run.data?.busy} />
          <div className="work-area"><div className="primary-column">
            {selected === null ? <Meeting projectRoot={data.project_root} configured={data.connection.configured} onCreated={select} /> : <>
              <ErrorNotice error={run.error} retry={() => void run.refetch()} />
              {run.isPending && <div className="panel empty" role="status">در حال دریافت جلسه…</div>}
              {run.data && <RunWorkspace run={run.data} refresh={() => void run.refetch()} />}
            </>}
          </div><aside className="context-column" aria-label="اتصال و راهنمای کار">
            <Connection configured={data.connection.configured} model={data.connection.model} />
            <section className="workflow-guide"><span className="eyebrow">HOW YOUR TEAM WORKS</span>
              <h2>هر ایده، یک مسیر روشن</h2><ol>
                <li><span>01</span><div><strong>گفتگو با تک‌لید</strong><p>نیاز و محدودیت‌ها روشن می‌شوند.</p></div></li>
                <li><span>02</span><div><strong>برنامه و تأیید شما</strong><p>تسک‌ها، مسئول‌ها و وابستگی‌ها مشخص می‌شوند.</p></div></li>
                <li><span>03</span><div><strong>اجرا و بازبینی</strong><p>تیم اجرا می‌کند و کیفیت بررسی می‌شود.</p></div></li>
              </ol>
            </section>
          </aside></div>
        </>}
        <footer className="page-footer">FAgent — تیم مهندسی در فضای کار شما <span>PLAN · BUILD · REVIEW</span></footer>
      </div>
    </main>
  </div>;
}
