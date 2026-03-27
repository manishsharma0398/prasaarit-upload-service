from src.api.base_model import BaseModel, CommonContentValidation
from pydantic import Field
from typing import Any


class MultiPartUploadInitiateRequest(CommonContentValidation):
    pass


class MultiPartUploadInitiateResponse(BaseModel):
    uploadId: str = Field(description="Multipart upload ID")
    s3Key: str = Field(description="S3 object key")


class MultiPartUploadCompleteRequest(BaseModel):
    parts: list[Any] = Field()
    s3Key: str = Field(description="S3 object key")
    uploadId: str = Field(description="Multipart upload ID")


class MultiPartUploadCompleteResponse(BaseModel):
    uploadId: str = Field(description="Multipart upload ID")
    success: bool = Field(
        description="Whether the multipart upload was completed successfully"
    )


class MultiPartUploadAbortRequest(BaseModel):
    uploadId: str = Field(description="Multipart upload ID")
    s3Key: str = Field(description="S3 object key")


class MultiPartUploadAbortResponse(BaseModel):
    uploadId: str = Field(description="Multipart upload ID")
    success: bool = Field(
        description="Whether the multipart upload was aborted successfully"
    )
