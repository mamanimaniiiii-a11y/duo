from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.models.enums import UserRole
from app.models.profile import ApprenantProfile, ClientProfile, MentorProfile
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse


def register_user(db: Session, payload: RegisterRequest) -> User:
    if payload.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="L'inscription admin n'est pas autorisée via l'API publique",
        )

    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cet email",
        )

    user = User(
        email=payload.email.lower(),
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        display_name=payload.display_name,
        locale=payload.locale,
        onboarding_completed=False,
    )
    db.add(user)
    db.flush()

    if payload.role == UserRole.CLIENT:
        db.add(ClientProfile(user_id=user.id))
    elif payload.role == UserRole.MENTOR:
        db.add(MentorProfile(user_id=user.id))
    elif payload.role == UserRole.APPRENANT:
        db.add(
            ApprenantProfile(
                user_id=user.id,
                skills=payload.skills,
                career_goal=payload.career_goal,
            )
        )

    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé",
        )
    return user


def issue_tokens(user: User) -> TokenResponse:
    claims = {"role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(str(user.id), claims),
        refresh_token=create_refresh_token(str(user.id)),
    )
