"use client";

import { FormField, formControlClass } from "@/components/ui/form-field";

type SkillsInputProps = {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  hint?: string;
  required?: boolean;
};

export function SkillsInput({
  id,
  label,
  value,
  onChange,
  hint = "Séparez les compétences par des virgules. Ex. React, Python, UI/UX",
  required = false,
}: SkillsInputProps) {
  return (
    <FormField label={label} htmlFor={id} hint={hint}>
      <input
        id={id}
        required={required}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={formControlClass}
        placeholder="React, Python, Figma"
      />
    </FormField>
  );
}
