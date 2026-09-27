import type { DeliverableStatus } from "./common";

export interface Deliverable {
  id: string;
  projectId: string;
  title: string;
  status: DeliverableStatus;
  fileIds: string[];
  submittedAt?: string;
  approvedAt?: string;
}
