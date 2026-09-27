import type { ReactNode } from "react";

type FormFieldProps = {
  label: string;
  htmlFor?: string;
  hint?: string;
  children: ReactNode;
};

export function FormField({ label, htmlFor, hint, children }: FormFieldProps) {
  return (
    <div className="w-full min-w-0">
      <label
        htmlFor={htmlFor}
        className="mb-1.5 block text-sm font-medium text-text-primary"
      >
        {label}
      </label>
      {children}
      {hint && <p className="mt-1.5 text-xs text-text-muted">{hint}</p>}
    </div>
  );
}

export const formControlClass =
  "box-border w-full min-w-0 rounded-lg border border-border bg-surface-100 px-4 py-2.5 text-text-primary outline-none transition-colors focus:border-primary-600 focus:ring-2 focus:ring-primary-600/15";
