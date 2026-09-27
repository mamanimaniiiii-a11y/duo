import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { CategoryGrid } from "@/components/home/category-grid";
import { HeroSection } from "@/components/home/hero-section";
import type { AppLocale } from "@/i18n/routing";
import { PublicPageLayout } from "@/components/layout/public-page-layout";

type HomePageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({
  params,
}: HomePageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "home" });

  return {
    title: t("metaTitle"),
    description: t("metaDescription"),
  };
}

export default async function HomePage({ params }: HomePageProps) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <PublicPageLayout locale={locale}>
      <HeroSection />
      <CategoryGrid locale={locale as AppLocale} />
    </PublicPageLayout>
  );
}
