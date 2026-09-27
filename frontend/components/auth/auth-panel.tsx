import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";

export async function AuthPanel() {
  const t = await getTranslations("auth");

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col lg:flex-row">
      <div className="hero-zellige relative flex flex-1 flex-col justify-center px-8 py-12 lg:px-12">
        <div className="relative z-10 max-w-md">
          <h1 className="text-3xl font-semibold text-text-primary">
            {t("panelTitle")}
          </h1>
          <p className="mt-4 text-lg text-text-muted">{t("panelSubtitle")}</p>
        </div>
      </div>

      <div className="flex flex-1 flex-col justify-center bg-primary-600 px-8 py-12 lg:px-12">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8 flex gap-2">
            <span className="rounded-lg bg-white px-4 py-2 text-sm font-medium text-primary-600">
              {t("loginTitle")}
            </span>
            <span className="rounded-lg bg-white/15 px-4 py-2 text-sm font-medium text-white">
              {t("registerTitle")}
            </span>
          </div>

          <form className="space-y-4" action="#" method="post">
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
                name="email"
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
                name="password"
                className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2.5 text-white outline-none focus:border-white/40"
              />
            </div>
            <fieldset>
              <legend className="mb-2 text-sm font-medium text-white">
                {t("role")}
              </legend>
              <div className="flex flex-wrap gap-2">
                <span className="rounded-lg bg-primary-800 px-3 py-1.5 text-xs font-medium text-white">
                  Client
                </span>
                <span className="rounded-lg bg-white/15 px-3 py-1.5 text-xs font-medium text-white">
                  Mentor
                </span>
                <span className="rounded-lg bg-highlight-500 px-3 py-1.5 text-xs font-medium text-white">
                  Apprenant
                </span>
              </div>
            </fieldset>
            <button
              type="button"
              className="w-full rounded-lg bg-white px-4 py-3 text-sm font-semibold text-primary-600 transition-colors hover:bg-surface-50"
            >
              {t("loginTitle")}
            </button>
          </form>

          <Link
            href="/auth/mot-de-passe"
            className="mt-4 inline-block text-sm text-white/80 hover:text-white"
          >
            {t("forgotPassword")}
          </Link>
        </div>
      </div>
    </div>
  );
}
