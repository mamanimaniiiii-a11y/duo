from uuid import UUID

from sqlalchemy.orm import Session

from app.models.support import Notification


def create_notification(
    db: Session,
    *,
    user_id: UUID,
    title: str,
    body: str,
    link: str | None = None,
    extra_data: dict | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        body=body,
        link=link,
        extra_data=extra_data or {},
    )
    db.add(notification)
    return notification
