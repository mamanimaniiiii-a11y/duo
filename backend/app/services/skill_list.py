def normalize_skill_list(
    skills: list[str],
    *,
    max_items: int = 20,
    max_item_length: int = 50,
) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for raw in skills:
        skill = raw.strip()
        if not skill:
            continue
        if len(skill) > max_item_length:
            raise ValueError(
                f"Chaque compétence doit faire au maximum {max_item_length} caractères"
            )
        key = skill.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(skill)
        if len(normalized) > max_items:
            raise ValueError(f"Maximum {max_items} compétences autorisées")

    return normalized
