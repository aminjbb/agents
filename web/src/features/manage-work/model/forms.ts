import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const meetingSchema = z.object({
  project_root: z.string().trim().min(1, 'مسیر پروژه را وارد کنید.'),
  text: z.string().trim().min(1, 'درخواست خود را بنویسید.'),
});
export function useMeetingForm(projectRoot: string) {
  return useForm<z.infer<typeof meetingSchema>>({
    resolver: zodResolver(meetingSchema),
    defaultValues: { project_root: projectRoot, text: '' },
  });
}
