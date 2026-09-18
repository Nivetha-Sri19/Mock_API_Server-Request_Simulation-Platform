from uuid import UUID

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.enums import HTTPMethod
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MockAPI(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "mock_apis"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "base_path",
            "http_method",
            name="uq_mock_apis_user_path_method",
        ),
        Index("ix_mock_apis_user_id", "user_id"),
        Index("ix_mock_apis_base_path", "base_path"),
        Index("ix_mock_apis_http_method", "http_method"),
        Index("ix_mock_apis_active", "is_active"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    base_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    http_method: Mapped[HTTPMethod] = mapped_column(
        Enum(HTTPMethod),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )

    is_private: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="mock_apis",
    )

    versions: Mapped[list["APIVersion"]] = relationship(
        "APIVersion",
        back_populates="mock_api",
        cascade="all, delete-orphan",
    )

    permissions: Mapped[list["APIPermission"]] = relationship(
        "APIPermission",
        back_populates="mock_api",
        cascade="all, delete-orphan",
    )