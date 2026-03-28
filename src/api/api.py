from fastapi import APIRouter

from src.api.endpoints import multipart_uploads, s3_presigned_url

router = APIRouter()

router.include_router(s3_presigned_url.router)
router.include_router(multipart_uploads.router)
