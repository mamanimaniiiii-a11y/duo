import { fetchApi } from "@/lib/api/client";
import {
  toAnnonce,
  toApplication,
  toApprenantMission,
  toDashboardStats,
  toMentorPack,
  toPackPurchase,
  toScoreBreakdown,
} from "@/lib/api/mappers";
import type { Annonce } from "@/lib/types/annonce";
import type { Application } from "@/lib/types/application";
import type { DashboardStats } from "@/lib/types/dashboard";
import type { MentorPack, PackPurchase } from "@/lib/types/pack";
import type { ApprenantMissionDetail } from "@/lib/types/project";
import type { ScoreBreakdown } from "@/lib/types/review";

export async function getApprenantDashboard(token: string): Promise<DashboardStats> {
  const record = await fetchApi<Record<string, unknown>>("/apprenant/dashboard", {
    token,
  });
  return toDashboardStats(record);
}

export async function getApprenantListings(token: string): Promise<Annonce[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/apprenant/decouvrir/listings",
    { token },
  );
  return records.map(toAnnonce);
}

export async function getApprenantApplications(token: string): Promise<Application[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/apprenant/activite/applications",
    { token },
  );
  return records.map(toApplication);
}

export async function applyToListing(
  token: string,
  listingId: string,
  coverLetter: string,
): Promise<Application> {
  const record = await fetchApi<Record<string, unknown>>(
    `/apprenant/applications?listing_id=${listingId}`,
    {
      method: "POST",
      token,
      body: { cover_letter: coverLetter },
    },
  );
  return toApplication(record);
}

export async function getApprenantMissions(
  token: string,
): Promise<ApprenantMissionDetail[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/apprenant/missions", {
    token,
  });
  return records.map(toApprenantMission);
}

export async function getApprenantMission(
  token: string,
  taskId: string,
): Promise<ApprenantMissionDetail> {
  const record = await fetchApi<Record<string, unknown>>(
    `/apprenant/missions/${taskId}`,
    { token },
  );
  return toApprenantMission(record);
}

export async function getApprenantPacks(token: string): Promise<MentorPack[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/apprenant/packs", {
    token,
  });
  return records.map(toMentorPack);
}

export async function getApprenantPack(
  token: string,
  packId: string,
): Promise<MentorPack> {
  const record = await fetchApi<Record<string, unknown>>(
    `/apprenant/packs/${packId}`,
    { token },
  );
  return toMentorPack(record);
}

export async function getApprenantPackPurchases(
  token: string,
): Promise<PackPurchase[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/apprenant/packs/purchases",
    { token },
  );
  return records.map(toPackPurchase);
}

export async function getApprenantProgression(
  token: string,
): Promise<ScoreBreakdown> {
  const record = await fetchApi<Record<string, unknown>>("/apprenant/progression", {
    token,
  });
  return toScoreBreakdown(record);
}
