import os
import uuid
from typing import Any, Union


from ..utils.s3 import (
    initiate_multipart_upload,
    complete_multipart_upload,
    abort_multipart_upload,
)


def handle_multipart_initiate(body) -> tuple[int, dict[str, str]]:
    content_type = body.get("contentType")

    if not content_type:
        return (400, {"error": "Missing contentType"})

    video_id = str(uuid.uuid4())
    s3_key = f"raw/{video_id}"

    result = initiate_multipart_upload(
        region=os.getenv("AWS_REGION", "ap-south-1"),
        bucket=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
        s3_key=s3_key,
        content_type=content_type,
    )

    if result is None:
        return (500, {"error": "Failed to initiate multipart upload"})

    return (200, {"uploadId": result, "s3Key": s3_key})


def handle_multipart_complete(body) -> tuple[int, Any]:
    return (200, "")


def handle_multipart_abort(body) -> tuple[int, dict[str, Union[bool, str]]]:
    s3_key = body.get("s3Key")
    upload_id = body.get("uploadId")

    if not s3_key or not upload_id:
        return (400, {"error": "Missing uploadId or s3Key"})

    success = abort_multipart_upload(
        region=os.getenv("AWS_REGION", "ap-south-1"),
        bucket=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
        s3_key=s3_key,
        upload_id=upload_id,
    )

    if not success:
        return (500, {"error": "Failed to abort multipart upload"})

    return (200, {"success": True, "uploadId": upload_id})
