"""Normalise les URLs PostgreSQL (Supabase / Prisma) pour psycopg2."""

from sqlalchemy.engine.url import make_url


def normalize_database_url(url: str) -> str:
    """
    - Force le driver psycopg2 (postgresql+psycopg2://)
    - Retire ?pgbouncer=true (option Prisma, invalide pour psycopg2)
    """
    sqlalchemy_url = make_url(url)

    if sqlalchemy_url.drivername in ("postgresql", "postgres"):
        sqlalchemy_url = sqlalchemy_url.set(drivername="postgresql+psycopg2")

    if "pgbouncer" in sqlalchemy_url.query:
        sqlalchemy_url = sqlalchemy_url.difference_update_query(["pgbouncer"])

    return sqlalchemy_url.render_as_string(hide_password=False)
