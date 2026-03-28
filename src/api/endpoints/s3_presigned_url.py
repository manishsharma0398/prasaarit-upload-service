from fastapi import APIRouter
from src.api.models.s3_presigned_url import (
    GeneratePresignedUrlResponse,
    GeneratePresignedUrlRequest,
)


from src.services.s3_services import handle_generate_presigned_url

router = APIRouter()


@router.post("/generate-presigned-url", response_model=GeneratePresignedUrlResponse)
def generate_presigned_url(body: GeneratePresignedUrlRequest):
    return handle_generate_presigned_url(body)
