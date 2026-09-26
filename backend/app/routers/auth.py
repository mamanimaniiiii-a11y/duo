from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.core.security import create_access_token, decode_token
from app.models.user import User
from app.schemas.auth import RefreshRequest, RegisterRequest, TokenResponse, UserPublic
from app.services.auth_service import authenticate_user, issue_tokens, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> User:
    """Inscription — page /auth (frontend)."""
    return register_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(
    db: DbSession,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    """Connexion — page /auth. Utilisez email comme username dans /docs."""
    user = authenticate_user(db, form_data.username, form_data.password)
    return issue_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: DbSession) -> TokenResponse:
    try:
        token_payload = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalide")

    if token_payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Type de token invalide")

    user_id = token_payload.get("sub")
    user = db.scalar(select(User).where(User.id == user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")

    return issue_tokens(user)


@router.get("/me", response_model=UserPublic)
def get_me(current_user: CurrentUser) -> User:
    """Utilisateur connecté — header, layouts."""
    return current_user
