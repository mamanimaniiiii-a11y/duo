import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { ListingApplyForm } from "@/components/annonces/listing-apply-form";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { Link } from "@/i18n/navigation";
import { getPublicListing } from "@/lib/api/public";
import { getOptionalAuth } from "@/lib/auth/server";

type AnnoncePageProps = {
  params: Promise<{ locale: string; id: string }>;
};

export async function generateMetadata({ params }: AnnoncePageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "annonce" });
  return { title: t("metaTitle") };
}

export default async function AnnoncePage({ params }: AnnoncePageProps) {
  const { locale, id } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("annonce");

  try {
    const [listing, session] = await Promise.all([
      getPublicListing(id),
      getOptionalAuth(),
    ]);

    const isApprenant = session?.user.role === "apprenant";

    return (
      <PublicPageLayout locale={locale}>
        <PageHeader title={listing.title} variant="primary" />
        <div className="mx-auto max-w-3xl space-y-6 px-4 pb-16 sm:px-6">
          <ContentCard accent="primary" className="shadow-sm">
            <p className="text-sm leading-relaxed text-text-muted">{listing.description}</p>
          </ContentCard>
          <ContentCard accent="primary" className="shadow-sm">
            <h2 className="font-semibold text-primary-600">{t("requiredSkills")}</h2>
            <p className="mt-2 text-sm text-text-muted">
              {listing.requiredSkills.length > 0
                ? listing.requiredSkills.join(", ")
                : "—"}
            </p>
          </ContentCard>
          <p className="text-sm text-text-muted">
            {listing.applicationsCount} candidature(s) · statut {listing.status}
          </p>

          {isApprenant ? (
            <ContentCard accent="highlight" className="shadow-sm">
              <h2 className="mb-3 font-semibold text-text-primary">Postuler à cette annonce</h2>
              <ListingApplyForm listingId={listing.id} />
            </ContentCard>
          ) : (
            <Link
              href="/auth/inscription?role=apprenant"
              className="inline-flex rounded-lg bg-highlight-500 px-6 py-3 text-sm font-medium text-white hover:opacity-90"
            >
              {t("apply")}
            </Link>
          )}
        </div>
      </PublicPageLayout>
    );
  } catch (error) {
    return (
      <PublicPageLayout locale={locale}>
        <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
          <ApiErrorBox error={error} />
        </div>
      </PublicPageLayout>
    );
  }
}
