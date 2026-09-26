from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import CurrentUser, DbSession
from app.models.support import Message, Notification
from app.schemas.common import MessageResponse

router = APIRouter(tags=["Common"])


@router.get("/messages")
def list_messages(db: DbSession, current_user: CurrentUser) -> list[dict]:
    """Page /messages."""
    messages = db.scalars(
        select(Message)
        .where(
            (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
        )
        .order_by(Message.created_at.desc())
    ).all()
    return [
        {
            "id": str(m.id),
            "sender_id": str(m.sender_id),
            "recipient_id": str(m.recipient_id),
            "content": m.content,
            "is_read": m.is_read,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    recipient_id: UUID,
    content: str,
    db: DbSession,
    current_user: CurrentUser,
    project_id: UUID | None = None,
) -> MessageResponse:
    message = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        project_id=project_id,
        content=content,
    )
    db.add(message)
    db.commit()
    return MessageResponse(message="Message envoyé")


@router.get("/notifications")
def list_notifications(db: DbSession, current_user: CurrentUser) -> list[dict]:
    """Page /notifications."""
    notifications = db.scalars(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    ).all()
    return [
        {
            "id": str(n.id),
            "title": n.title,
            "body": n.body,
            "link": n.link,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]


@router.patch("/notifications/{notification_id}/read", response_model=MessageResponse)
def mark_notification_read(
    notification_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> MessageResponse:
    notification = db.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification introuvable")
    notification.is_read = True
    db.commit()
    return MessageResponse(message="Notification marquée comme lue")


@router.get("/notifications/unread-count")
def unread_notifications_count(db: DbSession, current_user: CurrentUser) -> dict:
    count = db.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        )
    ) or 0
    return {"count": count}
