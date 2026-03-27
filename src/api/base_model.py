from pydantic import BaseModel as _BaseModel, Field
from ulid import ULID
from utils.constants import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE


class BaseModel(_BaseModel):
    class Config:
        json_encoders = {ULID: str}


class CommonContentValidation(BaseModel):
    contentType: str = Field(description="MIME type of the file")

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()  # type: ignore
        yield cls.validate_content_type

    @classmethod
    def validate_content_type(cls, value):
        if value not in ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"Invalid contentType: {value}. Allowed: {ALLOWED_CONTENT_TYPES}"
            )
        return value


class CommonFileSizeValidation(BaseModel):
    fileSize: float = Field(
        description="Size of the file in bytes", ge=0, le=MAX_FILE_SIZE
    )
