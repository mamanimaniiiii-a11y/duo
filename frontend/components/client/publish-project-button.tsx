"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { publishClientProject } from "@/lib/api/roles/client";
import { getApiErrorMessage } from "@/lib/api/errors";
import { getClientAccessToken } from "@/lib/auth/client-storage";

type PublishProjectButtonProps = {
  projectId: string;
};

export function PublishProjectButton({ projectId }: PublishProjectButtonProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [published, setPublished] = useState(false);

  async function handleClick() {
    const token = getClientAccessToken();
    if (!token) return;

    setLoading(true);
    setError(null);
    try {
      await publishClientProject(token, projectId);
      setPublished(true);
      router.refresh();
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  if (published) {
    return (
      <p className="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-800">
        Projet publié. Les mentors peuvent maintenant le voir dans « Projets disponibles ».
      </p>
    );
  }

  return (
    <div>
      <button
        type="button"
        onClick={handleClick}
        disabled={loading}
        className="rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-800 disabled:opacity-60"
      >
        {loading ? "Publication…" : "Publier le projet"}
      </button>
      <p className="mt-2 text-xs text-text-muted">
        Rend le projet visible aux mentors pour prise en charge.
      </p>
      {error && (
        <p role="alert" className="mt-2 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
