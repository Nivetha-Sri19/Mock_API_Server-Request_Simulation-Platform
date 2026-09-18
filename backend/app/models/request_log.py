from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class RequestLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "request_logs"

    __table_args__ = (
        Index(
            "ix_request_logs_api_version_id",
            "api_version_id",
        ),
        Index(
            "ix_request_logs_timestamp",
            "timestamp",
        ),
        Index(
            "ix_request_logs_http_method",
            "http_method",
        ),
        Index(
            "ix_request_logs_response_status",
            "response_status",
        ),
        Index(
            "ix_request_logs_endpoint",
            "endpoint",
        ),
    )

    api_version_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "api_versions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    endpoint: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    http_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    request_parameters: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    request_headers: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    request_body: Mapped[dict | list | str | None] = mapped_column(
        JSON,
        nullable=True,
    )

    response_status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    response_time_ms: Mapped[float] = mapped_column(
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    api_version: Mapped["APIVersion"] = relationship(
        "APIVersion",
        back_populates="request_logs",
    )