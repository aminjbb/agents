import { useForm } from 'react-hook-form';
import { ErrorNotice, Field } from '@/shared/ui';
import { useConnection, useDisconnect } from '../api/mutations';

export function Connection({ configured, model }: { configured: boolean; model: string | null }) {
  const connect = useConnection();
  const disconnect = useDisconnect();
  const form = useForm({ defaultValues: { api_key: '', model: model ?? '' } });
  const busy = connect.isPending || disconnect.isPending;
  const submit = form.handleSubmit(async (values) => {
    form.clearErrors('root');
    try {
      await connect.mutateAsync({ api_key: values.api_key.trim(), model: values.model.trim() || undefined });
    } catch (error) {
      form.setError('root', { message: error instanceof Error ? error.message : 'اتصال برقرار نشد.' });
    }
    finally {
      form.resetField('api_key');
      connect.reset();
    }
  });
  return <details className="connection-panel" open={!configured}>
    <summary><span className={`connection-dot ${configured ? 'connected' : ''}`} />
      {configured ? 'Codex متصل است' : 'اتصال به Codex'}<span className="muted">تنظیمات</span>
    </summary>
    <form onSubmit={submit} className="stack">
      <p className="muted">کلید فقط در حافظهٔ سرور محلی نگهداری می‌شود. برای استفاده از ورود فعلی Codex، کلید را خالی بگذارید.</p>
      <Field label="API Key (اختیاری)" type="password" autoComplete="off" dir="ltr"
        {...form.register('api_key')} disabled={busy} placeholder="sk-…" />
      <Field label="مدل (اختیاری)" dir="ltr" {...form.register('model')} disabled={busy} placeholder="پیش‌فرض Codex" />
      {form.formState.errors.root?.message && <p role="alert" className="error-text">{form.formState.errors.root.message}</p>}
      <ErrorNotice error={disconnect.error} />
      <div className="actions"><button className="button primary" type="submit" disabled={busy}>
        {connect.isPending ? 'در حال بررسی اتصال…' : 'بررسی و اتصال'}</button>
        {configured && <button className="button secondary" type="button" disabled={busy}
          onClick={() => disconnect.mutate()}>قطع اتصال</button>}</div>
    </form>
  </details>;
}
