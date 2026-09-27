import type { ReactNode } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { requireRole } from "@/lib/auth/server";

type ApprenantLayoutProps = {
  children: ReactNode;
  params: Promise<{ locale: string }>;
};

export default async function ApprenantLayout({
  children,
  params,
}: ApprenantLayoutProps) {
  const { locale } = await params;
  await requireRole(locale, "apprenant");

  return (
    <AppShell role="apprenant" locale={locale}>
      {children}
    </AppShell>
  );
}
