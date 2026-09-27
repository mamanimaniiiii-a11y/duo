import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { LocaleSwitcher } from "./locale-switcher";

type PublicHeaderProps = {
  locale: string;
};

export async function PublicHeader({ locale }: PublicHeaderProps) {
  const t = await getTranslations();

  return (
    <header className="sticky top-0 z-50 border-b border-primary-600/20 bg-surface-50/95 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <Link
          href="/"
          className="text-xl font-semibold tracking-tight text-primary-600"
        >
          {t("common.appName")}
        </Link>

        <nav
          aria-label={t("nav.main")}
          className="hidden items-center gap-6 sm:flex"
        >
          <Link
            href="/mentors"
            className="text-sm font-medium text-text-muted transition-colors hover:text-primary-600"
          >
            {t("nav.mentors")}
          </Link>
          <Link
            href="/#categories"
            className="text-sm font-medium text-text-muted transition-colors hover:text-primary-600"
          >
            {t("nav.howItWorks")}
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <LocaleSwitcher currentLocale={locale} />
          <Link
            href="/auth/connexion"
            className="hidden text-sm font-medium text-text-muted transition-colors hover:text-primary-600 sm:inline-flex"
          >
            {t("common.login")}
          </Link>
          <Link
            href="/auth/inscription"
            className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-800"
          >
            {t("common.register")}
          </Link>
        </div>
      </div>
    </header>
  );
}
