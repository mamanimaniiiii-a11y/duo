import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";

export async function HeroSection() {
  const t = await getTranslations("home");

  return (
    <section className="hero-zellige overflow-hidden border-b border-border">
      <div className="hero-enter relative mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-24">
        <div className="max-w-2xl">
          <h1 className="text-3xl font-semibold leading-tight text-text-primary sm:text-4xl sm:leading-tight">
            {t("hero.title")}
          </h1>
          <p className="mt-4 text-lg leading-relaxed text-text-muted">
            {t("hero.subtitle")}
          </p>
        </div>

        <div
          id="roles"
          className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap"
        >
          <Link
            href="/auth/inscription?role=client"
            className="inline-flex items-center justify-center rounded-lg bg-primary-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-800"
          >
            {t("roles.client")}
          </Link>
          <Link
            href="/auth/inscription?role=mentor"
            className="inline-flex items-center justify-center rounded-lg bg-primary-800 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-600"
          >
            {t("roles.mentor")}
          </Link>
          <Link
            href="/auth/inscription?role=apprenant"
            className="inline-flex items-center justify-center rounded-lg bg-primary-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-800"
          >
            {t("roles.apprenant")}
          </Link>
        </div>
      </div>
    </section>
  );
}
