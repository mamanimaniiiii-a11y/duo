import type { ReactNode } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { requireRole } from "@/lib/auth/server";

type MentorLayoutProps = {
  children: ReactNode;
  params: Promise<{ locale: string }>;
};

export default async function MentorLayout({
  children,
  params,
}: MentorLayoutProps) {
  const { locale } = await params;
  await requireRole(locale, "mentor");

  return (
    <AppShell role="mentor" locale={locale}>
      {children}
    </AppShell>
  );
}
