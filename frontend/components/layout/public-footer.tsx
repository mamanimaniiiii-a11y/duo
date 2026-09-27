import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";

export async function PublicFooter() {
  const t = await getTranslations();
  const year = new Date().getFullYear();

  return (
    <footer className="mt-auto bg-primary-800 text-white/80">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-8 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p className="text-sm">
          {t("footer.copyright", { year })}
        </p>

        <nav
          aria-label={t("footer.legalNav")}
          className="flex flex-wrap gap-4 text-sm"
        >
          <Link
            href="/legal"
            className="transition-colors hover:text-white"
          >
            {t("footer.legal")}
          </Link>
          <Link
            href="/legal"
            className="transition-colors hover:text-white"
          >
            {t("footer.privacy")}
          </Link>
        </nav>
      </div>
    </footer>
  );
}
