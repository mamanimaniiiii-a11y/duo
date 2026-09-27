"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { getMe, login, register } from "@/lib/api/auth";
import { getApiErrorMessage } from "@/lib/api/errors";
import { setTokens } from "@/lib/auth/client-storage";
import { getPostAuthPath } from "@/lib/auth/paths";
import type { Locale, UserRole } from "@/lib/types/common";

const ROLES: UserRole[] = ["client", "mentor", "apprenant"];

type AuthFormProps = {
  locale: Locale;
  mode: "login" | "register";
  defaultRole?: UserRole;
};

export function AuthForm({ locale, mode, defaultRole = "client" }: AuthFormProps) {
  const t = useTranslations("auth");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [role, setRole] = useState<UserRole>(defaultRole);
  const [skillsInput, setSkillsInput] = useState("");
  const [careerGoal, setCareerGoal] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function parseSkills(raw: string): string[] {
    return raw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const normalizedEmail = email.trim().toLowerCase();

    try {
      if (mode === "login") {
        const tokens = await login(normalizedEmail, password);
        setTokens(tokens.accessToken, tokens.refreshToken);
        const user = await getMe(tokens.accessToken);
        window.location.assign(
          `/${locale}${getPostAuthPath(user.role, user.onboardingCompleted)}`,
        );
        return;
      }

      const user = await register({
        email: normalizedEmail,
        password,
        displayName: displayName.trim(),
        role,
        locale,
        skills: role === "apprenant" ? parseSkills(skillsInput) : undefined,
        careerGoal: role === "apprenant" ? careerGoal.trim() : undefined,
      });

      const tokens = await login(normalizedEmail, password);
      setTokens(tokens.accessToken, tokens.refreshToken);
      window.location.assign(
        `/${locale}${getPostAuthPath(user.role, user.onboardingCompleted)}`,
      );
    } catch (err) {
      setError(getApiErrorMessage(err, mode));
    } finally {
      setLoading(false);
    }
  }

  const tabClass = (active: boolean) =>
    active
      ? "rounded-lg bg-white px-4 py-2 text-sm font-medium text-primary-600"
      : "rounded-lg bg-white/15 px-4 py-2 text-sm font-medium text-white hover:bg-white/25";

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col lg:flex-row">
      <div className="hero-zellige relative flex flex-1 flex-col justify-center px-8 py-12 lg:px-12">
        <div className="relative z-10 max-w-md">
          <h1 className="text-3xl font-semibold text-text-primary">
            {mode === "login" ? t("loginHeading") : t("registerHeading")}
          </h1>
          <p className="mt-4 text-lg text-text-muted">
            {mode === "login" ? t("loginSubtitle") : t("registerSubtitle")}
          </p>
        </div>
      </div>

      <div className="flex flex-1 flex-col justify-center bg-primary-600 px-8 py-12 lg:px-12">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8 flex gap-2">
            <Link href="/auth/connexion" className={tabClass(mode === "login")}>
              {t("loginTitle")}
            </Link>
            <Link href="/auth/inscription" className={tabClass(mode === "register")}>
              {t("registerTitle")}
            </Link>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit} noValidate>
            {mode === "register" && (
              <div>
                <label
                  htmlFor="displayName"
                  className="mb-1.5 block text-sm font-medium text-white"
                >
                  {t("displayName")}
                </label>
                <input
                  id="displayName"
                  type="text"
                  required
                  minLength={2}
                  maxLength={120}
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2.5 text-white outline-none focus:border-white/40"
                />
              </div>
            )}

            <div>
              <label
                htmlFor="email"
                className="mb-1.5 block text-sm font-medium text-white"
              >
                {t("email")}
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2.5 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                placeholder="vous@exemple.dz"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="mb-1.5 block text-sm font-medium text-white"
              >
                {t("password")}
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2.5 text-white outline-none focus:border-white/40"
              />
            </div>

            {mode === "register" && (
              <fieldset>
                <legend className="mb-2 text-sm font-medium text-white">
                  {t("role")}
                </legend>
                <div className="flex flex-wrap gap-2">
                  {ROLES.map((item) => (
                    <button
                      key={item}
                      type="button"
                      onClick={() => setRole(item)}
                      className={`rounded-lg px-3 py-1.5 text-xs font-medium capitalize ${
                        role === item
                          ? "bg-white text-primary-600"
                          : "bg-white/15 text-white"
                      }`}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </fieldset>
            )}

            {mode === "register" && role === "mentor" && (
              <p className="text-sm text-white/80">{t("mentorOnboardingHint")}</p>
            )}

            {mode === "register" && role === "apprenant" && (
              <>
                <div>
                  <label
                    htmlFor="skills"
                    className="mb-1.5 block text-sm font-medium text-white"
                  >
                    {t("skills")}
                  </label>
                  <input
                    id="skills"
                    type="text"
                    value={skillsInput}
                    onChange={(e) => setSkillsInput(e.target.value)}
                    placeholder={t("skillsPlaceholder")}
                    className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2.5 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                  />
                </div>
                <div>
                  <label
                    htmlFor="careerGoal"
                    className="mb-1.5 block text-sm font-medium text-white"
                  >
                    {t("careerGoal")}
                  </label>
                  <textarea
                    id="careerGoal"
                    rows={2}
                    value={careerGoal}
                    onChange={(e) => setCareerGoal(e.target.value)}
                    className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2.5 text-white outline-none focus:border-white/40"
                  />
                </div>
              </>
            )}

            {error && (
              <p
                role="alert"
                className="rounded-lg bg-red-500/20 px-3 py-2 text-sm text-white"
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-white px-4 py-3 text-sm font-semibold text-primary-600 transition-colors hover:bg-surface-50 disabled:opacity-60"
            >
              {loading ? "…" : mode === "login" ? t("loginTitle") : t("registerTitle")}
            </button>
          </form>

          <p className="mt-4 text-sm text-white/80">
            {mode === "login" ? (
              <>
                {t("noAccount")}{" "}
                <Link href="/auth/inscription" className="font-medium text-white hover:underline">
                  {t("registerTitle")}
                </Link>
              </>
            ) : (
              <>
                {t("hasAccount")}{" "}
                <Link href="/auth/connexion" className="font-medium text-white hover:underline">
                  {t("loginTitle")}
                </Link>
              </>
            )}
          </p>

          {mode === "login" && (
            <Link
              href="/auth/mot-de-passe"
              className="mt-2 inline-block text-sm text-white/80 hover:text-white"
            >
              {t("forgotPassword")}
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
