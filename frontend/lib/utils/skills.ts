export function parseSkillsInput(raw: string): string[] {
  return raw
    .split(",")
    .map((skill) => skill.trim())
    .filter(Boolean);
}
