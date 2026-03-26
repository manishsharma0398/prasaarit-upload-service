import os
import uuid
from typing import Union


from ..utils.s3 import generate_presigned_url


def handle_generate_presigned_url(body) -> tuple[int, dict[str, Union[str, int]]]:
    content_type = body.get("contentType")

    if not content_type:
        return (400, {"error": "Missing contentType"})

    video_id = str(uuid.uuid4())
    s3_key = f"raw/{video_id}"

    result = generate_presigned_url(
        region=os.getenv("AWS_REGION", "ap-south-1"),
        bucket_name=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
        s3_key=s3_key,
        content_type=content_type,
    )

    if result is None:
        return (500, {"error": "Failed to generate presigned URL"})

    presigned_url, expires_in = result

    return (
        200,
        {
            "presignedUrl": presigned_url,
            "videoId": video_id,
            "expiresIn": expires_in,
        },
    )
