import { fetchApi } from "@/lib/api/client";
import { toMessage, toNotification } from "@/lib/api/mappers";
import type { Message } from "@/lib/types/message";
import type { Notification } from "@/lib/types/notification";

export async function getMessages(token: string): Promise<Message[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/messages", { token });
  return records.map(toMessage);
}

export async function sendMessage(
  token: string,
  recipientId: string,
  content: string,
  projectId?: string,
): Promise<void> {
  const params = new URLSearchParams({ recipient_id: recipientId, content });
  if (projectId) params.set("project_id", projectId);
  await fetchApi(`/messages?${params.toString()}`, {
    method: "POST",
    token,
  });
}

export async function getNotifications(token: string): Promise<Notification[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/notifications", {
    token,
  });
  return records.map(toNotification);
}

export async function markNotificationRead(
  token: string,
  notificationId: string,
): Promise<void> {
  await fetchApi(`/notifications/${notificationId}/read`, {
    method: "PATCH",
    token,
  });
}
