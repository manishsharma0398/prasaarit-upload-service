import json
import logging
import os
import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
}

MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
PRESIGNED_URL_EXPIRY = 900  # 15 minutes


def get_s3_client():
    region = os.environ.get("AWS_REGION", "ap-south-1")
    return boto3.client(
        "s3",
        region_name=region,
        endpoint_url=f"https://s3.{region}.amazonaws.com",
        config=Config(signature_version="s3v4"),
    )


def generate_presigned_upload_url(bucket_name, s3_key, content_type):
    """
    Generate a presigned PUT URL for direct S3 upload.
    Returns presigned URL string or None on error.
    """
    s3_client = get_s3_client()
    try:
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name,
                "Key": s3_key,
                "ContentType": content_type,
            },
            ExpiresIn=PRESIGNED_URL_EXPIRY,
        )
        return presigned_url
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        return None


def validate_request(body):
    """
    Validate incoming request body.
    Returns (is_valid, error_message)
    """
    content_type = body.get("contentType", "")
    file_size = body.get("fileSize", 0)

    if not content_type:
        return False, "contentType is required"

    if content_type not in ALLOWED_CONTENT_TYPES:
        return False, f"Invalid content type: {content_type}"

    if not isinstance(file_size, (int, float)) or file_size <= 0:
        return False, "fileSize must be a positive number"

    if file_size > MAX_FILE_SIZE:
        return False, "File too large. Maximum allowed size is 5GB"

    return True, None


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Parse body
        raw_body = event.get("body", "{}")
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

        # Validate
        is_valid, error = validate_request(body)
        if not is_valid:
            return build_response(400, {"error": error})

        content_type = body["contentType"]

        # Generate unique video ID and S3 key
        video_id = str(uuid.uuid4())
        s3_key = f"raw/{video_id}/original"

        # Generate presigned URL
        bucket_name = os.environ["RAW_BUCKET_NAME"]
        presigned_url = generate_presigned_upload_url(bucket_name, s3_key, content_type)

        if not presigned_url:
            return build_response(500, {"error": "Failed to generate upload URL"})

        logger.info(f"Generated presigned URL for video_id: {video_id}")

        return build_response(
            200,
            {
                "presignedUrl": presigned_url,
                "videoId": video_id,
                "key": s3_key,
                "expiresIn": PRESIGNED_URL_EXPIRY,
            },
        )

    except json.JSONDecodeError:
        return build_response(400, {"error": "Invalid JSON body"})

    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        return build_response(500, {"error": "Server configuration error"})

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return build_response(500, {"error": "Internal server error"})
