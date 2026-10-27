import { useForm } from 'react-hook-form';
import type { RunState } from '@/entities/workspace';
import { ErrorNotice, PanelHeading } from '@/shared/ui';
import { useResumeRun } from '../api/mutations';

export function Questions({ id, questions, busy }: { id: string; questions: RunState['questions']; busy: boolean }) {
  const mutation = useResumeRun(id);
  const form = useForm<{ answers: { value: string }[] }>({
    defaultValues: { answers: questions.map(() => ({ value: '' })) },
  });
  const submit = form.handleSubmit(async (values) => {
    const answers = Object.fromEntries(questions.map((question, index) => [question.id, values.answers[index].value.trim()]));
    try {
      await mutation.mutateAsync({ answers });
    } catch { /* Query owns and displays the recoverable failure. */ }
  });
  return <section className="panel"><PanelHeading eyebrow="TECH LEAD / CLARIFICATION" title="چند سؤال پیش از ادامه" />
    <form onSubmit={submit} className="stack">
      {questions.map((question, index) => {
        const field = `answer-${index}`;
        const registration = form.register(`answers.${index}.value`, {
          validate: (value) => value.trim().length > 0 || 'پاسخ این سؤال لازم است.',
        });
        const error = form.formState.errors.answers?.[index]?.value?.message;
        return <div className="field" key={question.id}>
          <label htmlFor={field}>{question.question}</label>
          {question.options?.length ? <select id={field} {...registration} disabled={busy || mutation.isPending}
            aria-invalid={!!error} aria-describedby={error ? `${field}-error` : undefined}>
            <option value="">انتخاب کنید</option>{question.options.map((option) => <option key={option}>{option}</option>)}
          </select> : <textarea id={field} rows={3} {...registration} disabled={busy || mutation.isPending}
            aria-invalid={!!error} aria-describedby={error ? `${field}-error` : undefined} />}
          {error && <small id={`${field}-error`} className="error-text">{error}</small>}
        </div>;
      })}
      <ErrorNotice error={mutation.error} />
      <button className="button primary" type="submit" disabled={busy || mutation.isPending}>
        {mutation.isPending ? 'در حال ارسال…' : 'ارسال پاسخ به تک‌لید'}</button>
    </form>
  </section>;
}
