export const CATEGORY_SLUGS = [
  "web",
  "design",
  "community",
  "writing",
  "marketing",
  "video",
  "accounting",
  "photography",
  "ecommerce",
] as const;

export type CategorySlug = (typeof CATEGORY_SLUGS)[number];
