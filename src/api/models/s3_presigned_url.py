from src.api.base_model import (
    BaseModel,
    CommonContentValidation,
    CommonFileSizeValidation,
)
from pydantic import Field


class GeneratePresignedUrlRequest(CommonContentValidation, CommonFileSizeValidation):
    pass


class GeneratePresignedUrlResponse(BaseModel):
    mediaId: str = Field(description="Media ID")
    presignedUrl: str = Field(description="Presigned S3 URL")
    expiresIn: int = Field(description="presigned link expiry time")
