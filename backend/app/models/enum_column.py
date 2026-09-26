"""Helper SQLAlchemy : persiste les .value des enums Python, pas les noms de membres."""

import enum
from typing import TypeVar

from sqlalchemy import Enum

E = TypeVar("E", bound=enum.Enum)


def pg_enum(enum_class: type[E], name: str, **kwargs) -> Enum:
    """
    PostgreSQL native enum attend des valeurs en minuscules (ex. "admin").
    Par défaut SQLAlchemy 2.x envoie le nom du membre (ex. "ADMIN") — ce helper
    force l'utilisation des .value définis dans app/models/enums.py.
    """
    return Enum(
        enum_class,
        name=name,
        values_callable=lambda members: [member.value for member in members],
        **kwargs,
    )
