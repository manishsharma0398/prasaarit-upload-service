from fastapi import APIRouter, Query

from src.api.models.s3_presigned_url import (
    GeneratePresignedUrlRequest,
    GeneratePresignedUrlResponse,
)
from src.services.s3_services import handle_generate_presigned_url
from src.utils.constants import URL_TYPE

router = APIRouter()


@router.post("/generate-presigned-url", response_model=GeneratePresignedUrlResponse)
def generate_presigned_url(
    body: GeneratePresignedUrlRequest,
    upload_type: URL_TYPE = Query(
        default=URL_TYPE.SINGLE,
        alias="type",
        description="Upload type: 'single' or 'multipart'. Defaults to 'single'.",
    ),
):
    return handle_generate_presigned_url(body, url_type=upload_type)
