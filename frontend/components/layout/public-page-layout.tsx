import type { ReactNode } from "react";
import { PublicFooter } from "./public-footer";
import { PublicHeader } from "./public-header";

type PublicPageLayoutProps = {
  locale: string;
  children: ReactNode;
};

export async function PublicPageLayout({
  locale,
  children,
}: PublicPageLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col bg-surface-50">
      <PublicHeader locale={locale} />
      <main className="flex-1">{children}</main>
      <PublicFooter />
    </div>
  );
}
