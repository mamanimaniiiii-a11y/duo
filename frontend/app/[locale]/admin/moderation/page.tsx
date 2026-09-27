import { ShellPage } from "@/components/templates/shell-page";

type PageProps = { params: Promise<{ locale: string }> };

export default async function AdminModerationPage({ params }: PageProps) {
  await params;
  return <ShellPage namespace="adminPages.moderation" variant="dark" accent="accent" />;
}
