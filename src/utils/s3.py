import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from .logger import logger
from .constants import URL_TYPE, PRESIGNED_URL_EXPIRY
from typing import Optional, Union, TypedDict


class CompletedPartTypeDef(TypedDict):
    PartNumber: int
    ETag: str


def get_s3_client(region: str):
    return boto3.client(
        "s3",
        region_name=region,
        endpoint_url=f"https://s3.{region}.amazonaws.com",
        config=Config(signature_version="s3v4"),
    )


def initiate_multipart_upload(
    region: str,
    bucket: str,
    s3_key: str,
    content_type: str,
) -> Optional[str]:
    try:
        data = get_s3_client(region).create_multipart_upload(
            Bucket=bucket,
            Key=s3_key,
            ContentType=content_type,
        )
        return data["UploadId"]

    except ClientError as e:
        logger.error(f"Failed to initiate multipart upload: {e}")
        return None


def generate_presigned_url(
    region: str,
    bucket_name: str,
    s3_key: str,
    time_to_expire: int = PRESIGNED_URL_EXPIRY,
    content_type: Optional[str] = None,
    url_type: URL_TYPE = URL_TYPE.SINGLE,
    upload_id: Optional[str] = None,
    part_number: Optional[int] = -1,
) -> Optional[tuple[str, int]]:
    try:
        operation = ""
        Params: dict[str, Union[str, int]] = {
            "Bucket": bucket_name,
            "Key": s3_key,
        }

        if url_type == URL_TYPE.SINGLE:
            operation = "put_object"
            if content_type is not None:
                Params["ContentType"] = content_type

        elif url_type == URL_TYPE.MULTIPART:
            operation = "upload_part"

            if not upload_id:
                logger.error("upload_id is required for multipart uploads")
                return None

            if part_number is None or part_number <= 0:
                logger.error("part_number must be greater than 0")
                return None

            Params["UploadId"] = upload_id
            Params["PartNumber"] = part_number

        else:
            # Handle unexpected url_type
            logger.error(f"Invalid url_type: {url_type}")
            return None

        link = get_s3_client(region).generate_presigned_url(
            operation,
            Params=Params,
            ExpiresIn=time_to_expire,
        )
        return (link, time_to_expire)

    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        return None


def complete_multipart_upload(
    region: str,
    bucket: str,
    s3_key: str,
    upload_id: str,
    parts: list[CompletedPartTypeDef],
):
    try:
        return get_s3_client(region).complete_multipart_upload(
            Bucket=bucket,
            Key=s3_key,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},  # type: ignore
        )
    except ClientError as e:
        logger.error(f"Failed to complete multipart upload: {e}")
        return False


def abort_multipart_upload(
    region: str,
    bucket: str,
    s3_key: str,
    upload_id: str,
) -> bool:
    try:
        get_s3_client(region).abort_multipart_upload(
            Bucket=bucket,
            Key=s3_key,
            UploadId=upload_id,
        )
        return True

    except ClientError as e:
        logger.error(f"Failed to abort multipart upload: {e}")
        return False
