"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { ContentCard } from "@/components/ui/content-card";
import { FormField, formControlClass } from "@/components/ui/form-field";
import { createClientProject } from "@/lib/api/roles/client";
import { getClientAccessToken } from "@/lib/auth/client-storage";
import { getApiErrorMessage } from "@/lib/api/errors";
import type { Category } from "@/lib/types/category";

type ProjectCreateFormProps = {
  categories: Category[];
};

export function ProjectCreateForm({ categories }: ProjectCreateFormProps) {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState(categories[0]?.id ?? "");
  const [budgetDzd, setBudgetDzd] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const token = getClientAccessToken();
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const project = await createClientProject(token, {
        title: title.trim(),
        description: description.trim(),
        categoryId,
        budgetDzd: budgetDzd ? Number(budgetDzd) : undefined,
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

          <FormField
            label="Description"
            htmlFor="project-description"
            hint="Minimum 10 caractères — soyez précis sur les livrables attendus."
          >
            <textarea
              id="project-description"
              required
              minLength={10}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className={`${formControlClass} min-h-32 resize-y`}
              placeholder="Décrivez le contexte, les objectifs et les contraintes…"
            />
          </FormField>

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
