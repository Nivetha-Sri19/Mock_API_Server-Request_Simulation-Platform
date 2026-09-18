from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class SuccessResponse(BaseSchema):
    success: bool = True
    message: str


class ErrorResponse(BaseSchema):
    success: bool = False
    message: str
    error_code: str
    details: object | None = None


class PaginationParams(BaseSchema):
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginationMeta(BaseSchema):
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseSchema):
    items: list
    pagination: PaginationMeta