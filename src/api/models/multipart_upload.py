from pydantic import Field

from src.api.base_model import (
    BaseModel,
    CommonContentValidation,
    CommonFileSizeValidation,
)


class CompletedPart(BaseModel):
    PartNumber: int = Field(ge=1, le=10000, description="Part number (1–10000)")
    ETag: str = Field(description="ETag returned by S3 in the PUT response header")


class MultiPartUploadInitiateRequest(CommonContentValidation, CommonFileSizeValidation):
    pass


class MultiPartUploadInitiateResponse(BaseModel):
    uploadId: str = Field(description="Multipart upload ID")
    s3Key: str = Field(description="S3 object key")


class MultiPartUploadCompleteRequest(BaseModel):
    parts: list[CompletedPart] = Field(
        description="List of completed parts with PartNumber and ETag"
    )
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
