import type { ReactNode } from "react";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { LogoutButton } from "@/components/auth/logout-button";
import {
  ROLE_NAV,
  ROLE_SHELL_STYLES,
} from "@/lib/navigation/role-nav";
import type { UserRole } from "@/lib/types";

type AppShellProps = {
  role: UserRole;
  locale: string;
  children: ReactNode;
};

export async function AppShell({ role, children }: AppShellProps) {
  const t = await getTranslations();
  const nav = ROLE_NAV[role];
  const styles = ROLE_SHELL_STYLES[role];

  return (
    <div className="flex min-h-screen w-full">
      <aside
        className={`hidden w-60 shrink-0 flex-col ${styles.sidebar} text-white lg:flex lg:min-h-screen`}
      >
        <div className="flex h-16 shrink-0 items-center border-b border-white/10 px-5">
          <Link href="/" className="text-lg font-semibold text-white">
            {t("common.appName")}
          </Link>
        </div>
        <nav
          aria-label={t("nav.sidebar")}
          className="flex flex-1 flex-col gap-1 p-3"
        >
          <span
            className={`mb-2 rounded-md px-3 py-1.5 text-xs font-medium uppercase tracking-wide text-white/70 ${styles.badge}`}
          >
            {t(`roles.${role}`)}
          </span>
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-lg px-3 py-2 text-sm font-medium text-white/90 transition-colors hover:bg-white/10"
            >
              {t(item.labelKey)}
            </Link>
          ))}
        </nav>
        <div className="border-t border-white/10 p-3">
          <LogoutButton
            label={t("common.logout")}
            className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-white/90 transition-colors hover:bg-white/10"
          />
        </div>
      </aside>

      <div className="flex min-h-screen min-w-0 flex-1 flex-col bg-surface-50">
        <header
          className={`flex h-14 shrink-0 items-center justify-between border-b border-border px-4 lg:hidden ${styles.sidebar}`}
        >
          <Link href="/" className="font-semibold text-white">
            {t("common.appName")}
          </Link>
          <div className="flex items-center gap-3">
            <span className="text-xs font-medium text-white/80">
              {t(`roles.${role}`)}
            </span>
            <LogoutButton
              label={t("common.logout")}
              className="rounded-lg border border-white/20 px-2.5 py-1 text-xs font-medium text-white transition-colors hover:bg-white/10"
            />
          </div>
        </header>
        <div className="flex-1 overflow-x-hidden p-4 sm:p-6 lg:p-8">{children}</div>
      </div>
    </div>
  );
}
