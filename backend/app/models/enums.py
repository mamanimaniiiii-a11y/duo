import enum


class UserRole(str, enum.Enum):
    CLIENT = "client"
    MENTOR = "mentor"
    APPRENANT = "apprenant"
    ADMIN = "admin"


class Locale(str, enum.Enum):
    FR = "fr"
    EN = "en"
    AR = "ar"


class ProjectDescriptionFormat(str, enum.Enum):
    SHORT = "short"
    STANDARD = "standard"
    DETAILED = "detailed"
    CUSTOM = "custom"


class LearnerComplexityLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVISION = "revision"
    APPROVED = "approved"


class DeliverableStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    REVISION_REQUESTED = "revision_requested"
    APPROVED = "approved"


class ListingStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ReviewType(str, enum.Enum):
    CLIENT_TO_MENTOR = "client_to_mentor"
    MENTOR_TO_APPRENANT = "mentor_to_apprenant"
    APPRENANT_TO_MENTOR = "apprenant_to_mentor"


class PackPurchaseStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    PENDING_ADMIN = "pending_admin"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class BoostStatus(str, enum.Enum):
    INACTIVE = "inactive"
    PENDING_PAYMENT = "pending_payment"
    ACTIVE = "active"
    EXPIRED = "expired"


class SubscriptionStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    PENDING_ADMIN = "pending_admin"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    CLOSED = "closed"
