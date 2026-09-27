"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { applyToListing } from "@/lib/api/roles/apprenant";
import { getApiErrorMessage } from "@/lib/api/errors";
import { getClientAccessToken } from "@/lib/auth/client-storage";

type ListingApplyFormProps = {
  listingId: string;
};

export function ListingApplyForm({ listingId }: ListingApplyFormProps) {
  const router = useRouter();
  const [coverLetter, setCoverLetter] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

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
      await applyToListing(token, listingId, coverLetter.trim());
      setSuccess(true);
      router.push("/apprenant/activite");
    } catch (err) {
      setError(getApiErrorMessage(err, "register"));
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <p className="rounded-lg bg-green-50 px-4 py-3 text-sm text-green-800">
        Candidature envoyée. Suivez son statut dans votre activité.
      </p>
    );
  }

  return (
    <form className="space-y-3" onSubmit={handleSubmit}>
      <label htmlFor="coverLetter" className="block text-sm font-medium text-text-primary">
        Lettre de motivation
      </label>
      <textarea
        id="coverLetter"
        rows={4}
        required
        minLength={20}
        value={coverLetter}
        onChange={(e) => setCoverLetter(e.target.value)}
        className="w-full rounded-lg border border-border bg-white px-4 py-2.5 text-sm outline-none focus:border-highlight-500"
      />
      {error && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}
      <button
        type="submit"
        disabled={loading}
        className="inline-flex rounded-lg bg-highlight-500 px-6 py-3 text-sm font-medium text-white disabled:opacity-60"
      >
        {loading ? "…" : "Postuler"}
      </button>
    </form>
  );
}
