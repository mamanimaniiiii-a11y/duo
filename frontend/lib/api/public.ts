import { fetchApi } from "@/lib/api/client";
import {
  toAnnonce,
  toApprenantSummary,
  toCategory,
  toMentorSummary,
} from "@/lib/api/mappers";
import type { Annonce } from "@/lib/types/annonce";
import type { Category } from "@/lib/types/category";
import type { ApprenantSummary, MentorSummary } from "@/lib/types/user";

export async function getPublicCategories(): Promise<Category[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/public/categories");
  return records.map(toCategory);
}

export async function getPublicMentors(): Promise<MentorSummary[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/public/mentors");
  return records.map(toMentorSummary);
}

export async function getPublicMentor(mentorId: string): Promise<MentorSummary> {
  const record = await fetchApi<Record<string, unknown>>(
    `/public/mentors/${mentorId}`,
  );
  return toMentorSummary(record);
}

export async function getPublicApprenant(
  apprenantId: string,
): Promise<ApprenantSummary> {
  const record = await fetchApi<Record<string, unknown>>(
    `/public/apprenants/${apprenantId}`,
  );
  return toApprenantSummary(record);
}

export async function getPublicListing(listingId: string): Promise<Annonce> {
  const record = await fetchApi<Record<string, unknown>>(
    `/public/listings/${listingId}`,
  );
  return toAnnonce(record);
}
