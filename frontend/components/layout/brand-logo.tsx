import Image from "next/image";
import { Link } from "@/i18n/navigation";

type BrandLogoProps = {
  className?: string;
  priority?: boolean;
};

export function BrandLogo({ className = "", priority = false }: BrandLogoProps) {
  return (
    <Link
      href="/"
      className={`inline-flex items-center gap-2 ${className}`}
      aria-label="Duo Agency"
    >
      <Image
        src="/duo-logo.png"
        alt="Duo Agency"
        width={120}
        height={40}
        priority={priority}
        className="h-9 w-auto object-contain"
      />
    </Link>
  );
}
