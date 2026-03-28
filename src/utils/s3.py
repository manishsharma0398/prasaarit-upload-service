from typing import Optional, TypedDict, Union

import boto3
from botocore.config import Config

from src.utils.constants import PRESIGNED_URL_EXPIRY, URL_TYPE


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
) -> str:
    data = get_s3_client(region).create_multipart_upload(
        Bucket=bucket,
        Key=s3_key,
        ContentType=content_type,
    )
    return data["UploadId"]


def generate_presigned_url(
    region: str,
    bucket_name: str,
    s3_key: str,
    time_to_expire: int = PRESIGNED_URL_EXPIRY,
    content_type: Optional[str] = None,
    url_type: URL_TYPE = URL_TYPE.SINGLE,
    upload_id: Optional[str] = None,
    part_number: Optional[int] = None,
) -> tuple[str, int]:
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
            raise ValueError("upload_id is required for multipart uploads")

        if part_number is None or part_number <= 0:
            raise ValueError("part_number must be greater than 0")

        Params["UploadId"] = upload_id
        Params["PartNumber"] = part_number

    else:
        raise ValueError(f"Invalid url_type: {url_type}")

    link = get_s3_client(region).generate_presigned_url(
        operation,
        Params=Params,
        ExpiresIn=time_to_expire,
    )
    return (link, time_to_expire)


def complete_multipart_upload(
    region: str,
    bucket: str,
    s3_key: str,
    upload_id: str,
    parts: list[CompletedPartTypeDef],
) -> dict:
    return get_s3_client(region).complete_multipart_upload(
        Bucket=bucket,
        Key=s3_key,
        UploadId=upload_id,
        MultipartUpload={"Parts": parts},  # type: ignore
    )


def abort_multipart_upload(
    region: str,
    bucket: str,
    s3_key: str,
    upload_id: str,
) -> None:
    get_s3_client(region).abort_multipart_upload(
        Bucket=bucket,
        Key=s3_key,
        UploadId=upload_id,
    )
