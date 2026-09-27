TASK_COUNT_RULE_DEFAULT = (
    "Propose entre 3 et 8 sous-tâches, ordonnées logiquement (sort_order croissant à partir de 0)."
)
TASK_COUNT_RULE_EXACT = (
    "Propose exactement {task_count} sous-tâches (ni plus ni moins), ordonnées logiquement "
    "(sort_order croissant de 0 à {last_sort_order})."
)

COMPLEXITY_GUIDANCE = {
    "beginner": (
        "Niveau DÉBUTANT : sous-tâches courtes, guidées, peu d'autonomie technique avancée, "
        "vocabulaire accessible, étapes très concrètes."
    ),
    "intermediate": (
        "Niveau INTERMÉDIAIRE : sous-tâches avec un peu d'autonomie, bonnes pratiques attendues, "
        "complexité modérée, critères d'acceptation plus exigeants."
    ),
    "advanced": (
        "Niveau AVANCÉ : sous-tâches plus autonomes et techniques, profondeur attendue plus élevée, "
        "toujours réalisables par un apprenant encadré (pas de tâches mentor-only)."
    ),
}

DESCRIPTION_FORMAT_LABELS = {
    "short": "Résumé court (environ 5 lignes)",
    "standard": "Description standard (environ 10 lignes)",
    "detailed": "Description détaillée (environ 1 page)",
    "custom": "Format personnalisé (texte libre)",
}

TASK_BREAKDOWN_SYSTEM_TEMPLATE = """Tu es l'assistant IA de 5ibra, une plateforme algérienne de freelancing et de mentorat par projets réels.

Ta mission : proposer un découpage du projet en sous-tâches destinées à des APPRENANTS, encadrés par un mentor qui validera le travail.

=== NIVEAU APPRENANTS ===
{complexity_guidance}

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
2. {task_count_rule}
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


def resolve_task_count_bounds(task_count: int | None) -> tuple[int, int]:
    if task_count is None:
        return 3, 8
    return task_count, task_count


def build_task_breakdown_json_schema(task_count: int | None = None) -> dict:
    min_items, max_items = resolve_task_count_bounds(task_count)
    return {
    "type": "object",
    "additionalProperties": False,
    "required": ["suggested_tasks"],
    "properties": {
        "suggested_tasks": {
            "type": "array",
            "minItems": min_items,
            "maxItems": max_items,
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


TASK_BREAKDOWN_JSON_SCHEMA = build_task_breakdown_json_schema()


def resolve_output_locale(locale: str | None) -> str:
    if locale in {"fr", "ar", "en"}:
        return locale
    return "fr"


def build_task_count_rule(task_count: int | None) -> str:
    if task_count is None:
        return TASK_COUNT_RULE_DEFAULT
    return TASK_COUNT_RULE_EXACT.format(
        task_count=task_count,
        last_sort_order=task_count - 1,
    )


def build_task_breakdown_system_prompt(
    locale: str | None,
    task_count: int | None = None,
    learner_complexity_level: str = "beginner",
) -> str:
    return TASK_BREAKDOWN_SYSTEM_TEMPLATE.format(
        locale=resolve_output_locale(locale),
        task_count_rule=build_task_count_rule(task_count),
        complexity_guidance=COMPLEXITY_GUIDANCE.get(
            learner_complexity_level,
            COMPLEXITY_GUIDANCE["beginner"],
        ),
    )


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
    task_count: int | None = None,
    description_format: str = "standard",
    learner_complexity_level: str = "beginner",
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
        f"Format de description choisi par le client : {DESCRIPTION_FORMAT_LABELS.get(description_format, description_format)}",
        f"Niveau de complexité souhaité pour les apprenants : {learner_complexity_level}",
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
    if task_count is not None:
        lines.append(
            f"Le mentor demande exactement {task_count} sous-tâches dans suggested_tasks."
        )
        lines.append("")
    lines.append("Produis le JSON selon le schéma.")
    return "\n".join(lines)


GAP_ANALYSIS_SYSTEM_TEMPLATE = """Tu es l'assistant IA de 5ibra, une plateforme algérienne de freelancing et de mentorat par projets réels.

Ta mission : analyser le profil et l'historique d'un APPRENANT, identifier ses lacunes de compétences (skill gap), recommander des projets existants quand le catalogue le permet, et proposer des idées de projets fictifs quand le catalogue est insuffisant.

=== RÔLE ET LIMITES ===
- Tu RECOMMANDES uniquement. Tu n'assignes jamais un projet, une mission ou une annonce à l'apprenant.
- L'apprenant choisit lui-même de postuler ou de demander une mission (action volontaire).
- Ne suggère jamais que 5ibra ou le système fera l'assignation, la création de projet ou la publication d'annonce à sa place.
- Tu peux inventer des IDÉES DE PROJETS uniquement dans le champ suggested_project_ideas (titres et descriptions fictifs). Tu n'inventes jamais de mission passée, d'évaluation, d'UUID de projet existant, ni d'annonce réelle.
- suggested_project_ideas est purement informatif : aucune entrée de ce champ ne doit être interprétée comme un projet ou une annonce créée sur la plateforme.

=== LANGUE DE SORTIE (PRIORITÉ ABSOLUE) ===
Locale de l'apprenant connecté : {locale}

Tu dois rédiger l'intégralité des champs texte de la réponse (skill_gap, explanation, title, description, target_skills) UNIQUEMENT dans la langue correspondant à cette locale :
- "fr" → français intégral
- "ar" → arabe intégral (arabe standard moderne, naturel pour le web professionnel ; pas une traduction mot à mot depuis le français)
- "en" → anglais intégral

Si la locale est absente, invalide ou non supportée, utilise le français.

Contrainte stricte (même si career_goal, declared_skills, missions ou le catalogue sont rédigés dans une autre langue) :
- locale "en" → aucune phrase en français ni en arabe dans skill_gap, explanation, title, description (acronymes techniques autorisés : API, HTML, Git, Docker, etc.).
- locale "ar" → aucune phrase en français ni en anglais dans les champs texte (acronymes techniques autorisés).
- locale "fr" → aucune phrase en anglais ni en arabe dans les champs texte (acronymes techniques autorisés).

Règles linguistiques :
- Ne mélange pas les langues dans une même réponse (sauf noms propres, acronymes techniques universels).
- Comprends les entrées dans toute langue, mais produis la sortie exclusivement dans la locale demandée.
- Pour "ar" : formulation directe et professionnelle, adaptée à un public algérien.
- Le bloc suggested_project_ideas obéit aux mêmes règles de langue que skill_gap et explanation (pas d'exception).

=== RÈGLES MÉTIER ===
1. Réponds UNIQUEMENT en JSON valide, conforme au schéma fourni. Aucun texte avant ou après le JSON.
2. skill_gap : synthèse claire et actionnable des compétences manquantes ou à renforcer (2 à 6 axes). Mentionne les écarts entre compétences déclarées, objectif de carrière et pratique observée (missions, avis).
3. recommended_project_ids :
   - Contient UNIQUEMENT des UUID de projets listés dans la section « CATALOGUE D'OPPORTUNITÉS » du message utilisateur.
   - Recommande 0 à 5 projets, par pertinence décroissante (les plus alignés avec career_goal et skill_gap en premier).
   - N'invente JAMAIS d'UUID. Si le catalogue est vide ou aucun projet n'est pertinent, renvoie un tableau vide [].
4. explanation : texte pédagogique (3 à 8 phrases) qui :
   - résume le raisonnement ;
   - indique pourquoi chaque projet recommandé est pertinent (ou pourquoi aucun n'est proposé) ;
   - si suggested_project_ideas est non vide, précise que ce sont des idées à titre indicatif, pas des offres existantes sur 5ibra ;
   - propose des prochaines étapes concrètes (postuler à une annonce, renforcer une compétence, compléter le profil, chercher un projet similaire à une idée proposée).
5. Adapte ton analyse au niveau réel de l'apprenant sur la plateforme (débutant sur 5ibra vs profil déjà actif).

=== IDÉES DE PROJETS FICTIFS (suggested_project_ideas) ===
Règle d'activation (exclusive) :
- Si recommended_project_ids contient au moins un UUID → suggested_project_ideas DOIT être [].
- Si recommended_project_ids est [] (catalogue vide ou aucune opportunité pertinente) → propose 1 à 3 idées dans suggested_project_ideas (0 autorisé seulement si skill_gap et explanation restent utiles sans idée concrète ; en pratique, privilégie 2 ou 3 idées quand le catalogue est vide).

Chaque idée doit (title, description et libellés dans target_skills rédigés dans la locale de sortie) :
- être un projet réaliste pour le marché algérien (PME locales, freelances, étudiants, startups, associations, e-commerce local, services publics numériques, etc.) ;
- combler une lacune identifiée dans skill_gap et rapprocher career_goal ;
- inclure des target_skills alignées sur les compétences déclarées + celles à acquérir (mélange raisonnable, pas uniquement du déjà maîtrisé) ;
- rester réalisable par un apprenant encadré (complexité modérée, livrable concret en quelques semaines) ;
- ne pas dupliquer mot pour mot un projet du catalogue.

Interdictions pour suggested_project_ideas :
- aucun UUID, aucun project_id, aucune référence à une annonce existante ;
- aucune formulation du type « ce projet a été créé », « vous êtes inscrit », « postulez maintenant sur cette offre » ;
- pas de promesse de paiement, de contrat ou d'assignation automatique.

=== HISTORIQUE PAUVRE OU VIDE (COLD START) ===
Si le message utilisateur indique history_richness = "empty" ou "sparse" :
- Dis-le explicitement dans explanation, dans la langue de sortie (l'apprenant débute ou a peu de missions terminées).
- Base l'analyse principalement sur career_goal et declared_skills.
- Propose des recommandations d'entrée de gamme : compétences fondamentales à acquérir, premiers types de projets à viser.
- Si le catalogue contient des opportunités, recommande celles dont le niveau (learner_complexity_level) et les compétences requises sont accessibles pour un profil débutant.
- Si le catalogue est vide, appuie-toi sur suggested_project_ideas pour donner des pistes concrètes d'entrée de gamme.
- Ne renvoie JAMAIS skill_gap ou explanation vides. Même sans historique ni catalogue, fournis un conseil utile et encourageant.

=== INTERPRÉTATION DES MISSIONS ===
- outcome "succeeded" (tâche approuvée) : compétence démontrée.
- outcome "needs_rework" (révision demandée) : lacune probable à adresser.
- outcome "pending_review" : travail soumis, pas encore validé.
- outcome "in_progress" : mission en cours, pas concluante pour l'évaluation.

=== AVIS MENTOR (mentor_to_apprenant) ===
- rating 1-2 + commentaire : signal fort de lacune sur le projet concerné.
- rating 4-5 : compétence validée ; ne pas recommander de « rattraper » ce qui est déjà bien noté sauf si career_goal l'exige.

Le JSON doit contenir exactement les clés : skill_gap, recommended_project_ids, explanation, suggested_project_ideas."""


GAP_ANALYSIS_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "skill_gap",
        "recommended_project_ids",
        "explanation",
        "suggested_project_ideas",
    ],
    "properties": {
        "skill_gap": {
            "type": "string",
            "minLength": 20,
            "maxLength": 2000,
        },
        "recommended_project_ids": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "string",
                "minLength": 36,
                "maxLength": 36,
            },
        },
        "explanation": {
            "type": "string",
            "minLength": 80,
            "maxLength": 3000,
        },
        "suggested_project_ideas": {
            "type": "array",
            "maxItems": 3,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["title", "description", "target_skills"],
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 5,
                        "maxLength": 120,
                    },
                    "description": {
                        "type": "string",
                        "minLength": 40,
                        "maxLength": 600,
                    },
                    "target_skills": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 6,
                        "items": {
                            "type": "string",
                            "minLength": 2,
                            "maxLength": 40,
                        },
                    },
                },
            },
        },
    },
}


def build_gap_analysis_system_prompt(locale: str | None) -> str:
    return GAP_ANALYSIS_SYSTEM_TEMPLATE.format(locale=resolve_output_locale(locale))


def build_gap_analysis_user_prompt(
    *,
    locale: str,
    display_name: str,
    career_goal: str,
    declared_skills: list[str],
    history_richness: str,
    missions: list[dict],
    reviews: list[dict],
    touched_categories: list[str],
    opportunities: list[dict],
) -> str:
    output_language = resolve_output_locale(locale)
    lines = [
        "Analyse les lacunes de compétences et recommande des projets pour cet apprenant.",
        "",
        "=== PROFIL ===",
        f"Nom : {display_name}",
        f"Objectif de carrière : {career_goal or '(non renseigné)'}",
        f"Compétences déclarées : {', '.join(declared_skills) if declared_skills else '(aucune)'}",
        f"Richesse de l'historique : {history_richness}",
        f"catalogue_insuffisant : {'true' if not opportunities else 'false'}",
        f"output_language : {output_language}",
        "Rédige skill_gap, explanation, title, description et target_skills exclusivement dans output_language.",
        "",
        "=== MISSIONS (tâches assignées) ===",
    ]

    if missions:
        for mission in missions:
            skills = ", ".join(mission.get("required_skills") or []) or "—"
            lines.append(
                f"- {mission['task_title']} | statut={mission['task_status']} | "
                f"outcome={mission['outcome']} | projet={mission['project_title']} "
                f"({mission['project_status']}) | catégorie={mission['category_name']} | "
                f"compétences projet : {skills}"
            )
    else:
        lines.append("(Aucune mission pour le moment.)")

    lines.extend(["", "=== AVIS REÇUS (mentor → apprenant) ==="])
    if reviews:
        for review in reviews:
            lines.append(
                f"- note {review['rating']}/5 | projet={review.get('project_id') or '—'} | "
                f"commentaire : {review.get('comment') or '(aucun)'}"
            )
    else:
        lines.append("(Aucun avis reçu pour le moment.)")

    lines.extend(["", "=== CATÉGORIES DÉJÀ TOUCHÉES ==="])
    if touched_categories:
        for category in touched_categories:
            lines.append(f"- {category}")
    else:
        lines.append("(Aucune)")

    lines.extend(
        [
            "",
            "=== CATALOGUE D'OPPORTUNITÉS "
            "(seuls project_id ci-dessous sont autorisés dans recommended_project_ids) ===",
        ]
    )
    if opportunities:
        for item in opportunities:
            project_skills = ", ".join(item.get("project_required_skills") or []) or "—"
            listing_skills = ", ".join(item.get("listing_required_skills") or []) or "—"
            lines.append(f"- project_id: {item['project_id']}")
            lines.append(f"  Titre projet : {item['project_title']}")
            lines.append(f"  Catégorie : {item['category_name']}")
            lines.append(f"  Niveau apprenant : {item['learner_complexity_level']}")
            lines.append(f"  Compétences projet : {project_skills}")
            lines.append(f"  Annonce : {item['listing_title']}")
            lines.append(f"  Compétences annonce : {listing_skills}")
    else:
        lines.append("(Catalogue vide — aucune annonce ouverte liée à un projet.)")

    lines.extend(
        [
            "",
            "Si catalogue_insuffisant = true et recommended_project_ids = [], "
            "génère 1 à 3 idées dans suggested_project_ideas.",
            "Sinon, suggested_project_ideas = [].",
            "",
            "Produis le JSON selon le schéma.",
        ]
    )
    return "\n".join(lines)
