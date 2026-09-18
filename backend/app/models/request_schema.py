from uuid import UUID

from sqlalchemy import ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RequestSchema(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "request_schemas"

    __table_args__ = (
        Index("ix_request_schemas_api_version_id", "api_version_id"),
    )

    api_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("api_versions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    query_parameters: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    path_parameters: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    headers: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    body_schema: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    api_version = relationship(
        "APIVersion",
        back_populates="request_schema",
    )