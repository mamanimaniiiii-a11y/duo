"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { assignClientProjectMentor } from "@/lib/api/roles/client";
import { getApiErrorMessage } from "@/lib/api/errors";
import { getClientAccessToken } from "@/lib/auth/client-storage";
import { MatchScoreBadge } from "@/components/ui/match-score-badge";
import type { MentorProjectMatch } from "@/lib/types/project";

type AssignMentorButtonProps = {
  projectId: string;
  match: MentorProjectMatch;
};

export function AssignMentorButton({ projectId, match }: AssignMentorButtonProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAssign() {
    const token = getClientAccessToken();
    if (!token) return;

    setLoading(true);
    setError(null);
    try {
      await assignClientProjectMentor(token, projectId, match.mentor.id);
      router.refresh();
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <div className="flex flex-wrap items-center gap-2">
        <MatchScoreBadge score={match.matchScore} size="sm" />
        <button
          type="button"
          disabled={loading}
          onClick={handleAssign}
          className="rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-primary-800 disabled:opacity-60"
        >
          {loading ? "…" : "Choisir ce mentor"}
        </button>
      </div>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
