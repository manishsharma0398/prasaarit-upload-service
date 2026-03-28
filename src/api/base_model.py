from pydantic import BaseModel as _BaseModel
from pydantic import Field, field_validator
from ulid import ULID

from src.utils.constants import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE


class BaseModel(_BaseModel):
    class Config:
        json_encoders = {ULID: str}


class CommonContentValidation(BaseModel):
    contentType: str = Field(description="MIME type of the file")

    @field_validator("contentType")
    @classmethod
    def validate_content_type(cls, value: str) -> str:
        if value not in ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"Invalid contentType: {value}. Allowed: {ALLOWED_CONTENT_TYPES}"
            )
        return value


class CommonFileSizeValidation(BaseModel):
    fileSize: float = Field(
        description="Size of the file in bytes", ge=0, le=MAX_FILE_SIZE
    )
