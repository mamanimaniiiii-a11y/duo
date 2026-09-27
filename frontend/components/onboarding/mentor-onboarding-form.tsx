"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { completeOnboarding, updateMentorProfile } from "@/lib/api/account";
import { getApiErrorMessage } from "@/lib/api/errors";
import { getClientAccessToken } from "@/lib/auth/client-storage";
import type { Category } from "@/lib/types/category";
import type { Locale } from "@/lib/types/common";

type MentorOnboardingFormProps = {
  locale: Locale;
  categories: Category[];
  initialBio: string;
  initialCategoryIds: string[];
};

export function MentorOnboardingForm({
  locale,
  categories,
  initialBio,
  initialCategoryIds,
}: MentorOnboardingFormProps) {
  const router = useRouter();
  const [bio, setBio] = useState(initialBio);
  const [selectedIds, setSelectedIds] = useState<string[]>(initialCategoryIds);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function toggleCategory(id: string) {
    setSelectedIds((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id],
    );
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const token = getClientAccessToken();
    if (!token) {
      router.push("/auth/connexion");
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await updateMentorProfile(token, {
        bio: bio.trim(),
        serviceCategoryIds: selectedIds,
      });
      await completeOnboarding(token);
      router.push("/mentor/dashboard");
    } catch (err) {
      setError(getApiErrorMessage(err, "register"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div>
        <label htmlFor="bio" className="mb-1.5 block text-sm font-medium text-text-primary">
          Bio professionnelle
        </label>
        <textarea
          id="bio"
          rows={4}
          required
          minLength={10}
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          className="w-full rounded-lg border border-border bg-white px-4 py-2.5 text-sm outline-none focus:border-primary-600"
        />
      </div>

      <fieldset>
        <legend className="mb-2 text-sm font-medium text-text-primary">
          Domaines d&apos;expertise
        </legend>
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => {
            const active = selectedIds.includes(category.id);
            return (
              <button
                key={category.id}
                type="button"
                onClick={() => toggleCategory(category.id)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium ${
                  active
                    ? "bg-primary-600 text-white"
                    : "border border-border bg-white text-text-muted"
                }`}
              >
                {category.name[locale]}
              </button>
            );
          })}
        </div>
      </fieldset>

      {error && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-800 disabled:opacity-60"
      >
        {loading ? "…" : "Terminer l'onboarding"}
      </button>
    </form>
  );
}
