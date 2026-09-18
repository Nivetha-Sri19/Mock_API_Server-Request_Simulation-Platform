"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", mysql.CHAR(36), primary_key=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("role", sa.Enum("user", "admin", name="userrole"), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    op.create_table(
        "mock_apis",
        sa.Column("id", mysql.CHAR(36), primary_key=True, nullable=False),
        sa.Column("user_id", mysql.CHAR(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("base_path", sa.String(500), nullable=False),
        sa.Column("http_method", sa.Enum("GET","POST","PUT","PATCH","DELETE","HEAD","OPTIONS", name="httpmethod"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "base_path", "http_method", name="uq_mock_apis_user_path_method"),
    )
    for name, col in [
        ("ix_mock_apis_user_id","user_id"),("ix_mock_apis_base_path","base_path"),
        ("ix_mock_apis_http_method","http_method"),("ix_mock_apis_active","is_active")
    ]: op.create_index(name, "mock_apis", [col])

    op.create_table(
        "api_versions",
        sa.Column("id", mysql.CHAR(36), primary_key=True, nullable=False),
        sa.Column("mock_api_id", mysql.CHAR(36), sa.ForeignKey("mock_apis.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("mock_api_id","version",name="uq_api_versions_mock_api_version"),
    )
    op.create_index("ix_api_versions_mock_api_id","api_versions",["mock_api_id"])
    op.create_index("ix_api_versions_active","api_versions",["is_active"])

    op.create_table(
        "request_schemas",
        sa.Column("id", mysql.CHAR(36), primary_key=True, nullable=False),
        sa.Column("api_version_id", mysql.CHAR(36), sa.ForeignKey("api_versions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("query_parameters", sa.JSON(), nullable=True),
        sa.Column("path_parameters", sa.JSON(), nullable=True),
        sa.Column("headers", sa.JSON(), nullable=True),
        sa.Column("body_schema", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_request_schemas_api_version_id","request_schemas",["api_version_id"])

    op.create_table(
        "response_templates",
        sa.Column("id", mysql.CHAR(36), primary_key=True, nullable=False),
        sa.Column("api_version_id", mysql.CHAR(36), sa.ForeignKey("api_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario", sa.String(50), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("headers", sa.JSON(), nullable=True),
        sa.Column("body", sa.JSON(), nullable=True),
        sa.Column("delay_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("api_version_id","scenario",name="uq_response_templates_api_version_scenario"),
    )
    op.create_index("ix_response_templates_api_version_id","response_templates",["api_version_id"])
    op.create_index("ix_response_templates_scenario","response_templates",["scenario"])

    op.create_table(
        "request_logs",
        sa.Column("id", mysql.CHAR(36), primary_key=True, nullable=False),
        sa.Column("api_version_id", mysql.CHAR(36), sa.ForeignKey("api_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("endpoint", sa.String(500), nullable=False),
        sa.Column("http_method", sa.String(20), nullable=False),
        sa.Column("request_parameters", sa.JSON(), nullable=True),
        sa.Column("request_headers", sa.JSON(), nullable=True),
        sa.Column("request_body", sa.JSON(), nullable=True),
        sa.Column("response_status", sa.Integer(), nullable=False),
        sa.Column("response_time_ms", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )
    for name,col in [
        ("ix_request_logs_api_version_id","api_version_id"),("ix_request_logs_timestamp","timestamp"),
        ("ix_request_logs_http_method","http_method"),("ix_request_logs_response_status","response_status"),
        ("ix_request_logs_endpoint","endpoint")
    ]: op.create_index(name,"request_logs",[col])

    op.create_table(
        "api_permissions",
        sa.Column("id", mysql.CHAR(36), primary_key=True, nullable=False),
        sa.Column("mock_api_id", mysql.CHAR(36), sa.ForeignKey("mock_apis.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", mysql.CHAR(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("mock_api_id","user_id","permission",name="uq_api_permissions_api_user_permission"),
    )
    op.create_index("ix_api_permissions_mock_api_id","api_permissions",["mock_api_id"])
    op.create_index("ix_api_permissions_user_id","api_permissions",["user_id"])


def downgrade() -> None:
    for name in ["ix_api_permissions_user_id","ix_api_permissions_mock_api_id"]:
        op.drop_index(name, table_name="api_permissions")
    op.drop_table("api_permissions")

    for name in ["ix_request_logs_endpoint","ix_request_logs_response_status","ix_request_logs_http_method","ix_request_logs_timestamp","ix_request_logs_api_version_id"]:
        op.drop_index(name, table_name="request_logs")
    op.drop_table("request_logs")

    for name in ["ix_response_templates_scenario","ix_response_templates_api_version_id"]:
        op.drop_index(name, table_name="response_templates")
    op.drop_table("response_templates")

    op.drop_index("ix_request_schemas_api_version_id", table_name="request_schemas")
    op.drop_table("request_schemas")

    for name in ["ix_api_versions_active","ix_api_versions_mock_api_id"]:
        op.drop_index(name, table_name="api_versions")
    op.drop_table("api_versions")

    for name in ["ix_mock_apis_active","ix_mock_apis_http_method","ix_mock_apis_base_path","ix_mock_apis_user_id"]:
        op.drop_index(name, table_name="mock_apis")
    op.drop_table("mock_apis")

    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
