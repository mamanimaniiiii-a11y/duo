import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { AuthForm } from "@/components/auth/auth-form";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import type { AppLocale } from "@/i18n/routing";
import type { UserRole } from "@/lib/types/common";

type PageProps = {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ role?: string }>;
};

const ROLES: UserRole[] = ["client", "mentor", "apprenant"];

function parseRole(value?: string): UserRole {
  if (value && ROLES.includes(value as UserRole)) {
    return value as UserRole;
  }
  return "client";
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "auth" });
  return { title: t("registerMetaTitle") };
}

export default async function RegisterPage({ params, searchParams }: PageProps) {
  const { locale } = await params;
  const { role } = await searchParams;
  setRequestLocale(locale);

  return (
    <PublicPageLayout locale={locale}>
      <AuthForm
        locale={locale as AppLocale}
        mode="register"
        defaultRole={parseRole(role)}
      />
    </PublicPageLayout>
  );
}
