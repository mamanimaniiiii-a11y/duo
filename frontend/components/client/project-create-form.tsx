"use client";

import { useMemo, useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { ContentCard } from "@/components/ui/content-card";
import { FormField, formControlClass } from "@/components/ui/form-field";
import { SkillsInput } from "@/components/ui/skills-input";
import { createClientProject } from "@/lib/api/roles/client";
import { getClientAccessToken } from "@/lib/auth/client-storage";
import { getApiErrorMessage } from "@/lib/api/errors";
import { parseSkillsInput } from "@/lib/utils/skills";
import type { Category } from "@/lib/types/category";
import type {
  LearnerComplexityLevel,
  ProjectDescriptionFormat,
} from "@/lib/types/common";

type ProjectCreateFormProps = {
  categories: Category[];
};

const DESCRIPTION_FORMAT_OPTIONS: {
  value: ProjectDescriptionFormat;
  label: string;
  rows: number;
  placeholder: string;
  hint: string;
}[] = [
  {
    value: "short",
    label: "Résumé court (5 lignes)",
    rows: 5,
    placeholder: "Contexte, objectif principal, livrable clé, contrainte, délai souhaité…",
    hint: "Environ 5 lignes. Idéal pour un besoin simple et ciblé.",
  },
  {
    value: "standard",
    label: "Description standard (10 lignes)",
    rows: 8,
    placeholder: "Contexte, objectifs, livrables attendus, contraintes techniques, public visé…",
    hint: "Environ 10 lignes. Le format le plus courant.",
  },
  {
    value: "detailed",
    label: "Description détaillée (1 page)",
    rows: 14,
    placeholder:
      "Contexte métier, objectifs détaillés, périmètre, livrables, critères de qualité, contraintes, planning…",
    hint: "Description complète (~1 page) pour cadrer finement le projet.",
  },
  {
    value: "custom",
    label: "Personnalisé (texte libre)",
    rows: 10,
    placeholder: "Rédigez librement la description du projet…",
    hint: "Longueur libre selon votre besoin.",
  },
];

const COMPLEXITY_OPTIONS: { value: LearnerComplexityLevel; label: string }[] = [
  { value: "beginner", label: "Débutant" },
  { value: "intermediate", label: "Intermédiaire" },
  { value: "advanced", label: "Avancé" },
];

export function ProjectCreateForm({ categories }: ProjectCreateFormProps) {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [descriptionFormat, setDescriptionFormat] =
    useState<ProjectDescriptionFormat>("standard");
  const [description, setDescription] = useState("");
  const [learnerComplexityLevel, setLearnerComplexityLevel] =
    useState<LearnerComplexityLevel>("beginner");
  const [categoryId, setCategoryId] = useState(categories[0]?.id ?? "");
  const [budgetDzd, setBudgetDzd] = useState("");
  const [requiredSkillsInput, setRequiredSkillsInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const formatConfig = useMemo(
    () =>
      DESCRIPTION_FORMAT_OPTIONS.find((option) => option.value === descriptionFormat) ??
      DESCRIPTION_FORMAT_OPTIONS[1],
    [descriptionFormat],
  );

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const token = getClientAccessToken();
    if (!token) return;
    const requiredSkills = parseSkillsInput(requiredSkillsInput);
    if (requiredSkills.length === 0) {
      setError("Ajoutez au moins une compétence requise pour le mentor.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const project = await createClientProject(token, {
        title: title.trim(),
        description: description.trim(),
        descriptionFormat,
        learnerComplexityLevel,
        categoryId,
        budgetDzd: budgetDzd ? Number(budgetDzd) : undefined,
        requiredSkills,
      });
      router.push(`/client/projets/${project.id}`);
      router.refresh();
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-2xl min-w-0">
      <ContentCard accent="primary" className="shadow-md">
        <div className="mb-6 border-b border-border pb-4">
          <h2 className="text-lg font-semibold text-text-primary">Nouveau projet</h2>
          <p className="mt-1 text-sm text-text-muted">
            Décrivez votre besoin. Le mentor pourra prendre en charge le projet une fois publié.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <FormField label="Titre du projet" htmlFor="project-title">
            <input
              id="project-title"
              required
              minLength={3}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className={formControlClass}
              placeholder="Ex. Refonte site vitrine"
            />
          </FormField>

          <fieldset className="space-y-3 rounded-lg border border-border bg-surface-50 p-4">
            <legend className="px-1 text-sm font-semibold text-text-primary">
              Description du projet
            </legend>

            <FormField label="Format de description" htmlFor="project-description-format">
              <select
                id="project-description-format"
                value={descriptionFormat}
                onChange={(e) =>
                  setDescriptionFormat(e.target.value as ProjectDescriptionFormat)
                }
                className={formControlClass}
              >
                {DESCRIPTION_FORMAT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>

            <FormField
              label="Description"
              htmlFor="project-description"
              hint={formatConfig.hint}
            >
              <textarea
                id="project-description"
                required
                minLength={10}
                rows={formatConfig.rows}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className={`${formControlClass} resize-y`}
                placeholder={formatConfig.placeholder}
              />
            </FormField>

            <FormField
              label="Niveau de complexité souhaité pour les apprenants"
              htmlFor="project-complexity"
            >
              <select
                id="project-complexity"
                value={learnerComplexityLevel}
                onChange={(e) =>
                  setLearnerComplexityLevel(e.target.value as LearnerComplexityLevel)
                }
                className={formControlClass}
              >
                {COMPLEXITY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>
          </fieldset>

          <SkillsInput
            id="project-required-skills"
            label="Compétences requises du mentor"
            value={requiredSkillsInput}
            onChange={setRequiredSkillsInput}
            hint="Utilisées pour matcher le mentor le plus adapté (score + compétences)."
            required
          />

          <FormField label="Catégorie" htmlFor="project-category">
            <select
              id="project-category"
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              className={formControlClass}
            >
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name.fr}
                </option>
              ))}
            </select>
          </FormField>

          <FormField label="Budget (DZD)" htmlFor="project-budget" hint="Optionnel">
            <input
              id="project-budget"
              type="number"
              min={0}
              value={budgetDzd}
              onChange={(e) => setBudgetDzd(e.target.value)}
              className={formControlClass}
              placeholder="50000"
            />
          </FormField>

          {error && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}

          <div className="flex flex-wrap gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-800 disabled:opacity-60"
            >
              {loading ? "Création…" : "Créer le projet"}
            </button>
          </div>
        </form>
      </ContentCard>
    </div>
  );
}
