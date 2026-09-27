from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import account, admin, ai, apprenant, auth, client, common, mentor, public, reviews

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API backend Duo — freelancing, mentorat et apprentissage (marché algérien)",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = settings.api_v1_prefix

app.include_router(auth.router, prefix=api_prefix)
app.include_router(account.router, prefix=api_prefix)
app.include_router(public.router, prefix=api_prefix)
app.include_router(client.router, prefix=api_prefix)
app.include_router(mentor.router, prefix=api_prefix)
app.include_router(apprenant.router, prefix=api_prefix)
app.include_router(admin.router, prefix=api_prefix)
app.include_router(reviews.router, prefix=api_prefix)
app.include_router(ai.router, prefix=api_prefix)
app.include_router(common.router, prefix=api_prefix)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "app": settings.app_name}
