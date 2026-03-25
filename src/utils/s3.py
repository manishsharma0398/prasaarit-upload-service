import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from .logger import logger
from .constants import URL_TYPE
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
):
    try:
        return get_s3_client(region).create_multipart_upload(
            Bucket=bucket,
            Key=s3_key,
            ContentType=content_type,
        )
    except ClientError as e:
        logger.error(f"Failed to initiate multipart upload: {e}")
        return None


def generate_presigned_url(
    region: str,
    bucket_name: str,
    s3_key: str,
    content_type: str,
    time_to_expire: int,
    url_type: URL_TYPE = URL_TYPE.SINGLE,
    upload_id: Optional[str] = None,
    part_number: Optional[int] = -1,
):
    try:
        Params: dict[str, Union[str, int]] = {
            "Bucket": bucket_name,
            "Key": s3_key,
            "ContentType": content_type,
        }

        if url_type == URL_TYPE.MULTIPART:
            if not upload_id:
                return "required"

            if part_number is None or part_number <= 0:
                return "required"

            Params["UploadId"] = upload_id
            Params["PartNumber"] = part_number

        return get_s3_client(region).generate_presigned_url(
            "upload_part",
            Params=Params,
            ExpiresIn=time_to_expire,
        )
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
):
    try:
        return get_s3_client(region).abort_multipart_upload(
            Bucket=bucket,
            Key=s3_key,
            UploadId=upload_id,
        )
    except ClientError as e:
        logger.error(f"Failed to abort multipart upload: {e}")
        return False
