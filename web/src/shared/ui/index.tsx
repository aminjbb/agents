import { useId } from 'react';
import type { ComponentProps, ReactNode } from 'react';

type FieldProps = Omit<ComponentProps<'input'>, 'style'> & { label: string; error?: string; hint?: string };
export function Field({ label, error, hint, id, ...props }: FieldProps) {
  const generated = useId();
  const fieldId = id ?? generated;
  return <div className="field">
    <label htmlFor={fieldId}>{label}</label>
    <input {...props} id={fieldId} aria-invalid={!!error}
      aria-describedby={error || hint ? `${fieldId}-detail` : undefined} />
    {(error || hint) && <small id={`${fieldId}-detail`} className={error ? 'error-text' : 'muted'}>{error || hint}</small>}
  </div>;
}
export function ErrorNotice({ error, retry }: { error: Error | null; retry?: () => void }) {
  if (!error) return null;
  return <div className="error-notice" role="alert"><span>{error.message}</span>
    {retry && <button type="button" className="button secondary" onClick={retry}>تلاش دوباره</button>}
  </div>;
}
export function PanelHeading({ eyebrow, title, trailing }: { eyebrow: string; title: string; trailing?: ReactNode }) {
  return <div className="panel-heading"><div><span className="eyebrow">{eyebrow}</span><h2>{title}</h2></div>{trailing}</div>;
}
export function Evidence({ value, title }: { value: unknown; title: string }) {
  if (value == null) return null;
  return <details className="evidence"><summary>{title}</summary>
    <pre dir="auto">{typeof value === 'string' ? value : JSON.stringify(value, null, 2)}</pre>
  </details>;
}
