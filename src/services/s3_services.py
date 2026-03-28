import os
import uuid
from botocore.exceptions import ClientError
from fastapi import HTTPException
from src.utils.logger import logger


from src.utils.s3 import (
    initiate_multipart_upload,
    complete_multipart_upload,
    abort_multipart_upload,
    generate_presigned_url,
)

from src.api.models.s3_presigned_url import (
    GeneratePresignedUrlRequest,
    GeneratePresignedUrlResponse,
)
from src.api.models.multipart_upload import (
    MultiPartUploadInitiateRequest,
    MultiPartUploadInitiateResponse,
    MultiPartUploadCompleteRequest,
    MultiPartUploadCompleteResponse,
    MultiPartUploadAbortRequest,
    MultiPartUploadAbortResponse,
)


def handle_generate_presigned_url(
    body: GeneratePresignedUrlRequest,
) -> GeneratePresignedUrlResponse:
    try:
        media_id = str(uuid.uuid4())
        s3_key = f"raw/{media_id}"

        presigned_url, expires_in = generate_presigned_url(
            region=os.getenv("AWS_REGION", "ap-south-1"),
            bucket_name=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
            s3_key=s3_key,
            content_type=body.contentType,
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

        # TODO:
        # if not parts or not isinstance(parts, list):
        #     return (400, {"error": "Missing or invalid parts array"})
        complete_multipart_upload(
            region=os.getenv("AWS_REGION", "ap-south-1"),
            bucket=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
            s3_key=body.s3Key,
            upload_id=body.uploadId,
            parts=body.parts,
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
