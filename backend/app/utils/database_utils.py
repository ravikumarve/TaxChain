"""
Database utilities for handling SQLite vs PostgreSQL differences
"""

from sqlalchemy import Column, String
from app.config import settings
import uuid


def uuid_column():
    """Create appropriate UUID column based on database type"""
    if "sqlite" in settings.DATABASE_URL:
        return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        from sqlalchemy.dialects.postgresql import UUID

        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def uuid_foreign_key(column_name):
    """Create appropriate foreign key column based on database type"""
    from sqlalchemy import ForeignKey

    if "sqlite" in settings.DATABASE_URL:
        return Column(String(36), ForeignKey(column_name), nullable=False)
    else:
        from sqlalchemy.dialects.postgresql import UUID

        return Column(UUID(as_uuid=True), ForeignKey(column_name), nullable=False)


def jsonb_column():
    """Create appropriate JSONB column based on database type"""
    if "sqlite" in settings.DATABASE_URL:
        from sqlalchemy import JSON

        return Column(JSON)
    else:
        from sqlalchemy.dialects.postgresql import JSONB

        return Column(JSONB)
