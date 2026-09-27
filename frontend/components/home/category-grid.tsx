import { getTranslations } from "next-intl/server";
import { getPublicCategories } from "@/lib/api/public";
import { ApiErrorBox } from "@/components/ui/api-state";
import type { AppLocale } from "@/i18n/routing";

const CATEGORY_ICONS: Record<string, string> = {
  "dev-web-mobile": "</>",
  "design-graphique": "◆",
  "community-management": "◎",
  "redaction-traduction": "¶",
  "marketing-digital": "▲",
  video: "▶",
  comptabilite: "═",
  photographie: "◉",
  ecommerce: "▣",
};

type CategoryGridProps = {
  locale: AppLocale;
};

export async function CategoryGrid({ locale }: CategoryGridProps) {
  const t = await getTranslations();

  try {
    const categories = (await getPublicCategories())
      .filter((category) => category.isActive)
      .sort((a, b) => a.sortOrder - b.sortOrder);

    return (
      <section
        id="categories"
        className="bg-primary-600 px-4 py-16 sm:px-6 sm:py-20"
      >
        <div className="mx-auto max-w-6xl">
          <div className="max-w-xl">
            <h2 className="text-2xl font-semibold text-white">
              {t("home.categories.title")}
            </h2>
            <p className="mt-2 text-white/80">{t("home.categories.subtitle")}</p>
          </div>

          <ul className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {categories.map((category) => (
              <li key={category.id}>
                <article
                  className="flex h-full items-start gap-4 rounded-lg border border-white/10 bg-surface-100 p-5 transition-colors hover:border-white/30"
                >
                  <span
                    aria-hidden="true"
                    className="flex size-10 shrink-0 items-center justify-center rounded-md bg-primary-600/10 text-sm font-semibold text-primary-600"
                  >
                    {CATEGORY_ICONS[category.slug] ?? "•"}
                  </span>
                  <h3 className="text-base font-medium leading-snug text-text-primary">
                    {category.name[locale]}
                  </h3>
                </article>
              </li>
            ))}
          </ul>
        </div>
      </section>
    );
  } catch (error) {
    return (
      <section className="bg-primary-600 px-4 py-16 sm:px-6">
        <div className="mx-auto max-w-6xl">
          <ApiErrorBox error={error} title="Impossible de charger les catégories" />
        </div>
      </section>
    );
  }
}
