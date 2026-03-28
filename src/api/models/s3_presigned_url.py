from typing import Optional

from pydantic import Field

from src.api.base_model import (
    BaseModel,
    CommonContentValidation,
    CommonFileSizeValidation,
)


class GeneratePresignedUrlRequest(CommonContentValidation, CommonFileSizeValidation):
    s3Key: Optional[str] = Field(
        default=None, description="S3 object key. Required when type=multipart."
    )
    uploadId: Optional[str] = Field(
        default=None, description="Multipart upload ID. Required when type=multipart."
    )
    partNumber: Optional[int] = Field(
        default=None,
        ge=1,
        le=10000,
        description="Part number (1–10000). Required when type=multipart.",
    )


class GeneratePresignedUrlResponse(BaseModel):
    mediaId: str = Field(description="Media ID")
    presignedUrl: str = Field(description="Presigned S3 URL")
    expiresIn: int = Field(description="presigned link expiry time")
