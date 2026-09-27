import type { ReactNode } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { requireRole } from "@/lib/auth/server";

type ClientLayoutProps = {
  children: ReactNode;
  params: Promise<{ locale: string }>;
};

export default async function ClientLayout({
  children,
  params,
}: ClientLayoutProps) {
  const { locale } = await params;
  await requireRole(locale, "client");

  return (
    <AppShell role="client" locale={locale}>
      {children}
    </AppShell>
  );
}
