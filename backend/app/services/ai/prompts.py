TASK_BREAKDOWN_SYSTEM_TEMPLATE = """Tu es l'assistant IA de 5ibra, une plateforme algérienne de freelancing et de mentorat par projets réels.

Ta mission : proposer un découpage du projet en sous-tâches destinées à des APPRENANTS (niveau débutant à intermédiaire), encadrés par un mentor qui validera le travail.

=== LANGUE DE SORTIE ===
Locale du mentor connecté : {locale}

Tu dois rédiger l'intégralité des champs texte de la réponse (title, description, acceptance_criteria) dans la langue correspondant à cette locale :
- "fr" → français
- "ar" → arabe (arabe standard moderne, naturel pour le web professionnel ; pas une traduction mot à mot depuis le français)
- "en" → anglais

Si la locale est absente, invalide ou non supportée, utilise le français.

Règles linguistiques :
- Ne mélange pas les langues dans une même réponse (sauf noms propres, acronymes techniques universels : API, HTML, GitHub, etc.).
- Si la description du projet est dans une autre langue que la locale demandée, comprends-la mais produis la sortie uniquement dans la locale du mentor.
- Pour "ar" : formulation directe et professionnelle, adaptée à un public algérien ; évite un arabe trop littéral ou administratif.

=== RÈGLES MÉTIER ===
1. Réponds UNIQUEMENT en JSON valide, conforme au schéma fourni. Aucun texte avant ou après le JSON.
2. Propose entre 3 et 8 sous-tâches, ordonnées logiquement (sort_order croissant à partir de 0).
3. Chaque sous-tâche doit être :
   - réalisable par un apprenant en 3 à 10 jours de travail ;
   - indépendante ou avec dépendances implicites via l'ordre (sort_order) ;
   - formulée avec un titre court (max 120 caractères) et une description actionnable ;
   - accompagnée de 2 à 5 critères d'acceptation mesurables et vérifiables (acceptance_criteria).
4. Ne crée PAS de tâches réservées au mentor seul. Exclusions obligatoires :
   - gestion client, facturation, paiement ;
   - prise de contact initiale avec le client ;
   - déploiement production critique ou mise en production finale ;
   - négociation commerciale, contrats, validation juridique.
   Le mentor garde la supervision, la relation client et la livraison finale.
5. Si le projet est trop vague, fais des hypothèses raisonnables et reste pragmatique pour le marché algérien (PME, freelances, étudiants).
6. due_date : optionnel. Si le projet a une deadline, répartis des dates intermédiaires cohérentes (format ISO 8601 UTC, ex. "2026-04-15T23:59:59Z"). Sinon null.
7. Ne duplique pas les livrables finaux du client : décompose le chemin pour les atteindre.
8. Ne duplique pas les tâches déjà existantes listées dans le message utilisateur.

Le JSON doit contenir exactement la clé "suggested_tasks" (tableau d'objets)."""


TASK_BREAKDOWN_JSON_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": ["suggested_tasks"],
    "properties": {
        "suggested_tasks": {
            "type": "array",
            "minItems": 3,
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["title", "description", "acceptance_criteria", "sort_order"],
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 120,
                    },
                    "description": {
                        "type": "string",
                        "minLength": 20,
                        "maxLength": 2000,
                    },
                    "acceptance_criteria": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 5,
                        "items": {
                            "type": "string",
                            "minLength": 10,
                            "maxLength": 300,
                        },
                    },
                    "due_date": {
                        "type": ["string", "null"],
                    },
                    "sort_order": {
                        "type": "integer",
                        "minimum": 0,
                    },
                },
            },
        },
    },
}


def resolve_output_locale(locale: str | None) -> str:
    if locale in {"fr", "ar", "en"}:
        return locale
    return "fr"


def build_task_breakdown_system_prompt(locale: str | None) -> str:
    return TASK_BREAKDOWN_SYSTEM_TEMPLATE.format(locale=resolve_output_locale(locale))


def build_task_breakdown_user_prompt(
    *,
    project_title: str,
    category_name: str,
    category_slug: str,
    project_description: str,
    budget_dzd: int | None,
    project_deadline: str | None,
    deliverables: list[dict],
    assigned_apprenants_count: int,
    existing_tasks: list[dict],
) -> str:
    lines = [
        "Découpe ce projet en sous-tâches pour apprenants.",
        "",
        "=== PROJET ===",
        f"Titre : {project_title}",
        f"Catégorie : {category_name} ({category_slug})",
        "Description :",
        project_description,
        "",
        f"Budget indicatif (DZD) : {budget_dzd if budget_dzd is not None else 'non précisé'}",
        f"Deadline projet : {project_deadline or 'non précisée'}",
        "",
        "=== LIVRABLES ATTENDUS (côté client) ===",
    ]

    if deliverables:
        for item in deliverables:
            lines.append(f"- {item['title']} (statut actuel : {item['status']})")
    else:
        lines.append("(Aucun livrable formalisé — propose un découpage cohérent avec la description.)")

    lines.extend(
        [
            "",
            "=== CONTEXTE MENTOR ===",
            f"Nombre d'apprenants déjà assignés sur ce projet : {assigned_apprenants_count}",
            "Tâches existantes (ne pas dupliquer) :",
        ]
    )

    if existing_tasks:
        for task in existing_tasks:
            lines.append(f"- [{task['sort_order']}] {task['title']}")
    else:
        lines.append("(Aucune tâche existante.)")

    lines.append("")
    lines.append("Produis le JSON selon le schéma.")
    return "\n".join(lines)
