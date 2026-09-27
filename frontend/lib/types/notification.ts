export interface Notification {
  id: string;
  title: string;
  body: string;
  link?: string;
  isRead: boolean;
  createdAt: string;
}
