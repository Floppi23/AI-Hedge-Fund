"""Portable column types that work on both SQLite and PostgreSQL."""

import uuid

from sqlalchemy import String, TypeDecorator, types


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type when available, otherwise stores as String(36).
    """

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(uuid.UUID(value))
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value


# JSON type works on both SQLite (stored as TEXT) and PostgreSQL (native JSONB)
PortableJSON = types.JSON
