from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class APIVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "api_versions"

    __table_args__ = (
        UniqueConstraint(
            "mock_api_id",
            "version",
            name="uq_api_versions_mock_api_version",
        ),
        Index(
            "ix_api_versions_mock_api_id",
            "mock_api_id",
        ),
        Index(
            "ix_api_versions_active",
            "is_active",
        ),
    )

    mock_api_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "mock_apis.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )

    mock_api: Mapped["MockAPI"] = relationship(
        "MockAPI",
        back_populates="versions",
    )

    request_schema: Mapped["RequestSchema | None"] = relationship(
        "RequestSchema",
        back_populates="api_version",
        uselist=False,
        cascade="all, delete-orphan",
    )

    response_templates: Mapped[list["ResponseTemplate"]] = relationship(
        "ResponseTemplate",
        back_populates="api_version",
        cascade="all, delete-orphan",
    )

    request_logs: Mapped[list["RequestLog"]] = relationship(
        "RequestLog",
        back_populates="api_version",
        cascade="all, delete-orphan",
    )