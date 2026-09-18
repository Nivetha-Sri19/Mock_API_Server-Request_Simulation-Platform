from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.enums import PermissionType
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class APIPermission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "api_permissions"

    __table_args__ = (
        UniqueConstraint(
            "mock_api_id",
            "user_id",
            "permission",
            name="uq_api_permissions_api_user_permission",
        ),
        Index(
            "ix_api_permissions_mock_api_id",
            "mock_api_id",
        ),
        Index(
            "ix_api_permissions_user_id",
            "user_id",
        ),
    )

    mock_api_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "mock_apis.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    permission: Mapped[PermissionType] = mapped_column(
        String(30),
        nullable=False,
    )

    mock_api: Mapped["MockAPI"] = relationship(
        "MockAPI",
        back_populates="permissions",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="permissions",
    )