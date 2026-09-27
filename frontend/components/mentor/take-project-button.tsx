"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { takeMentorProject } from "@/lib/api/roles/mentor";
import { getClientAccessToken } from "@/lib/auth/client-storage";
import { ApiError } from "@/lib/api/client";

type TakeProjectButtonProps = {
  projectId: string;
};

export function TakeProjectButton({ projectId }: TakeProjectButtonProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    const token = getClientAccessToken();
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      await takeMentorProject(token, projectId);
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Échec de la prise en charge");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button
        type="button"
        onClick={handleClick}
        disabled={loading}
        className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-800 disabled:opacity-60"
      >
        {loading ? "…" : "Prendre en charge"}
      </button>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}
