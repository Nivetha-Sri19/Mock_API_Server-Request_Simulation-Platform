from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.enums import ResponseScenario
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ResponseTemplate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "response_templates"

    __table_args__ = (
        UniqueConstraint(
            "api_version_id",
            "scenario",
            name="uq_response_templates_api_version_scenario",
        ),
        Index(
            "ix_response_templates_api_version_id",
            "api_version_id",
        ),
        Index(
            "ix_response_templates_scenario",
            "scenario",
        ),
    )

    api_version_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "api_versions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    scenario: Mapped[ResponseScenario] = mapped_column(
        String(50),
        nullable=False,
    )

    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    headers: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    body: Mapped[dict | list | str | None] = mapped_column(
        JSON,
        nullable=True,
    )

    delay_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    api_version: Mapped["APIVersion"] = relationship(
        "APIVersion",
        back_populates="response_templates",
    )