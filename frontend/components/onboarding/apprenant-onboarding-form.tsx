"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import {
  completeOnboarding,
  updateApprenantProfile,
} from "@/lib/api/account";
import { getApiErrorMessage } from "@/lib/api/errors";
import { getClientAccessToken } from "@/lib/auth/client-storage";

type ApprenantOnboardingFormProps = {
  initialSkills: string[];
  initialCareerGoal: string;
};

function parseSkills(raw: string): string[] {
  return raw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

export function ApprenantOnboardingForm({
  initialSkills,
  initialCareerGoal,
}: ApprenantOnboardingFormProps) {
  const router = useRouter();
  const [skillsInput, setSkillsInput] = useState(initialSkills.join(", "));
  const [careerGoal, setCareerGoal] = useState(initialCareerGoal);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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
      await updateApprenantProfile(token, {
        skills: parseSkills(skillsInput),
        careerGoal: careerGoal.trim(),
      });
      await completeOnboarding(token);
      router.push("/apprenant/dashboard");
    } catch (err) {
      setError(getApiErrorMessage(err, "register"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div>
        <label htmlFor="skills" className="mb-1.5 block text-sm font-medium text-text-primary">
          Compétences
        </label>
        <input
          id="skills"
          type="text"
          value={skillsInput}
          onChange={(e) => setSkillsInput(e.target.value)}
          placeholder="Python, React, SQL"
          className="w-full rounded-lg border border-border bg-white px-4 py-2.5 text-sm outline-none focus:border-primary-600"
        />
        <p className="mt-1 text-xs text-text-muted">Séparez les compétences par des virgules.</p>
      </div>

      <div>
        <label htmlFor="careerGoal" className="mb-1.5 block text-sm font-medium text-text-primary">
          Objectif de carrière
        </label>
        <textarea
          id="careerGoal"
          rows={3}
          value={careerGoal}
          onChange={(e) => setCareerGoal(e.target.value)}
          className="w-full rounded-lg border border-border bg-white px-4 py-2.5 text-sm outline-none focus:border-primary-600"
        />
      </div>

      {error && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-highlight-500 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
      >
        {loading ? "…" : "Terminer l'onboarding"}
      </button>
    </form>
  );
}
