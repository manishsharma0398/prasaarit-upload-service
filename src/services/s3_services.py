import os
import uuid

from botocore.exceptions import ClientError
from fastapi import HTTPException

from src.api.models.multipart_upload import (
    MultiPartUploadAbortRequest,
    MultiPartUploadAbortResponse,
    MultiPartUploadCompleteRequest,
    MultiPartUploadCompleteResponse,
    MultiPartUploadInitiateRequest,
    MultiPartUploadInitiateResponse,
)
from src.api.models.s3_presigned_url import (
    GeneratePresignedUrlRequest,
    GeneratePresignedUrlResponse,
)
from src.utils.constants import URL_TYPE
from src.utils.logger import logger
from src.utils.s3 import (
    CompletedPartTypeDef,
    abort_multipart_upload,
    complete_multipart_upload,
    generate_presigned_url,
    initiate_multipart_upload,
)


def _extract_media_id(s3_key: str) -> str:
    """Safely extract the media UUID from a 'raw/<uuid>' s3Key."""
    parts = s3_key.split("raw/", 1)
    if len(parts) < 2 or not parts[1]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid s3Key format '{s3_key}'. Expected 'raw/<media-id>'.",
        )
    return parts[1]


def handle_generate_presigned_url(
    body: GeneratePresignedUrlRequest,
    url_type: URL_TYPE,
) -> GeneratePresignedUrlResponse:
    try:
        is_multipart = url_type == URL_TYPE.MULTIPART

        if is_multipart:
            if not body.uploadId:
                raise HTTPException(
                    status_code=400, detail="uploadId is required when type=multipart"
                )
            if body.partNumber is None:
                raise HTTPException(
                    status_code=400, detail="partNumber is required when type=multipart"
                )
            if not body.s3Key:
                raise HTTPException(
                    status_code=400, detail="s3Key is required when type=multipart"
                )
            s3_key = body.s3Key
            media_id = _extract_media_id(s3_key)
        else:
            media_id = str(uuid.uuid4())
            s3_key = f"raw/{media_id}"

        presigned_url, expires_in = generate_presigned_url(
            region=os.getenv("AWS_REGION", "ap-south-1"),
            bucket_name=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
            s3_key=s3_key,
            content_type=body.contentType,
            url_type=url_type,
            upload_id=body.uploadId,
            part_number=body.partNumber,
        )

        return GeneratePresignedUrlResponse(
            mediaId=media_id, expiresIn=expires_in, presignedUrl=presigned_url
        )
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate presigned URL")


def handle_multipart_initiate(
    body: MultiPartUploadInitiateRequest,
) -> MultiPartUploadInitiateResponse:
    try:
        media_id = str(uuid.uuid4())
        s3_key = f"raw/{media_id}"

        upload_id = initiate_multipart_upload(
            region=os.getenv("AWS_REGION", "ap-south-1"),
            bucket=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
            s3_key=s3_key,
            content_type=body.contentType,
        )

        return MultiPartUploadInitiateResponse(s3Key=s3_key, uploadId=upload_id)
    except ClientError as e:
        logger.error(f"Failed to initiate multipart upload: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to initiate multipart upload"
        )


def handle_multipart_complete(
    body: MultiPartUploadCompleteRequest,
) -> MultiPartUploadCompleteResponse:
    try:
        complete_multipart_upload(
            region=os.getenv("AWS_REGION", "ap-south-1"),
            bucket=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
            s3_key=body.s3Key,
            upload_id=body.uploadId,
            parts=[
                CompletedPartTypeDef(PartNumber=p.PartNumber, ETag=p.ETag)
                for p in body.parts
            ],
        )

        return MultiPartUploadCompleteResponse(success=True, uploadId=body.uploadId)
    except ClientError as e:
        logger.error(f"Failed to complete multipart upload: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to complete multipart upload"
        )


def handle_multipart_abort(
    body: MultiPartUploadAbortRequest,
) -> MultiPartUploadAbortResponse:
    try:
        abort_multipart_upload(
            region=os.getenv("AWS_REGION", "ap-south-1"),
            bucket=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
            s3_key=body.s3Key,
            upload_id=body.uploadId,
        )

        return MultiPartUploadAbortResponse(success=True, uploadId=body.uploadId)
    except ClientError as e:
        logger.error(f"Failed to abort multipart upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to abort multipart upload")
