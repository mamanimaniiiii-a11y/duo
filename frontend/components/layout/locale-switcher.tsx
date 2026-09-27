import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { routing, type AppLocale } from "@/i18n/routing";

type LocaleSwitcherProps = {
  currentLocale: string;
};

const LOCALE_LABELS: Record<AppLocale, string> = {
  fr: "FR",
  en: "EN",
  ar: "ع",
};

export async function LocaleSwitcher({ currentLocale }: LocaleSwitcherProps) {
  const t = await getTranslations("common");

  return (
    <nav
      aria-label={t("languageSwitcher")}
      className="flex items-center gap-1 rounded-md border border-border bg-surface-100 p-1"
    >
      {routing.locales.map((locale) => {
        const isActive = locale === currentLocale;

        return (
          <Link
            key={locale}
            href="/"
            locale={locale}
            className={[
              "min-w-9 rounded px-2 py-1 text-center text-sm font-medium transition-colors",
              isActive
                ? "bg-primary-600 text-white"
                : "text-text-muted hover:bg-surface-50 hover:text-text-primary",
            ].join(" ")}
            aria-current={isActive ? "page" : undefined}
          >
            {LOCALE_LABELS[locale]}
          </Link>
        );
      })}
    </nav>
  );
}
