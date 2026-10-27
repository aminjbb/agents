import { ErrorNotice, Field, PanelHeading } from '@/shared/ui';
import { useCreateRun } from '../api/mutations';
import { useMeetingForm } from '../model/forms';

type Props = { projectRoot: string; configured: boolean; onCreated: (id: string) => void };
export function Meeting({ projectRoot, configured, onCreated }: Props) {
  const form = useMeetingForm(projectRoot);
  const mutation = useCreateRun();
  const submit = form.handleSubmit(async (values) => {
    try {
      const { id } = await mutation.mutateAsync(values);
      onCreated(id);
    } catch { /* Query owns and displays the recoverable failure. */ }
  });
  const errors = form.formState.errors;
  return <section className="panel meeting">
    <PanelHeading eyebrow="01 / BRIEFING" title="جلسه با تک‌لید" trailing={<span className="tag">@architect</span>} />
    <div className="lead-message"><span className="avatar architect" aria-hidden="true">A</span>
      <div><strong>از ایده تا برنامهٔ اجرایی</strong><p>بگو چه می‌خواهی بسازیم. تک‌لید نیاز را روشن می‌کند و مسئولیت هر عضو تیم را مشخص می‌کند.</p></div>
    </div>
    <form onSubmit={submit} className="stack" noValidate>
      <Field label="مسیر کامل پروژهٔ مقصد" dir="ltr" {...form.register('project_root')}
        error={errors.project_root?.message} disabled={mutation.isPending} />
      <div className="field"><label htmlFor="request">چه چیزی می‌خواهی توسعه بدهیم؟</label>
        <textarea id="request" {...form.register('text')} rows={6} disabled={mutation.isPending}
          placeholder="هدف، رفتار مورد انتظار و محدودیت‌ها را توضیح بده…"
          aria-invalid={!!errors.text} aria-describedby={errors.text ? 'request-error' : undefined} />
        {errors.text && <small className="error-text" id="request-error">{errors.text.message}</small>}
      </div>
      <ErrorNotice error={mutation.error} />
      <div className="form-footer"><span className="muted">اجرای تسک‌ها پس از تأیید برنامه آغاز می‌شود.</span>
        <button type="submit" className="button primary" disabled={!configured || mutation.isPending}>
          {mutation.isPending ? 'در حال ایجاد جلسه…' : 'شروع جلسه ←'}</button></div>
      {!configured && <p className="muted">برای شروع، ابتدا اتصال Codex را بررسی کنید.</p>}
    </form>
  </section>;
}
