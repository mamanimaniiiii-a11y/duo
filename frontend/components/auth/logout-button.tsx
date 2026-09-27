"use client";

import { useRouter } from "@/i18n/navigation";
import { clearTokens } from "@/lib/auth/client-storage";

type LogoutButtonProps = {
  label: string;
  className?: string;
};

export function LogoutButton({ label, className }: LogoutButtonProps) {
  const router = useRouter();

  function handleLogout() {
    clearTokens();
    router.push("/");
    router.refresh();
  }

  return (
    <button type="button" onClick={handleLogout} className={className}>
      {label}
    </button>
  );
}
