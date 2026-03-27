from fastapi import APIRouter


from src.api.models.multipart_upload import (
    MultiPartUploadAbortResponse,
    MultiPartUploadCompleteResponse,
    MultiPartUploadInitiateResponse,
    MultiPartUploadAbortRequest,
    MultiPartUploadCompleteRequest,
    MultiPartUploadInitiateRequest,
)


from services.s3_services import (
    handle_multipart_initiate,
    handle_multipart_complete,
    handle_multipart_abort,
)

router = APIRouter()


@router.post(
    "/initiate-multipart-upload",
    response_model=MultiPartUploadInitiateResponse,
)
def initiate_multipart_upload(body: MultiPartUploadInitiateRequest):
    return handle_multipart_initiate(body)


@router.post(
    "/complete-multipart-upload", response_model=MultiPartUploadCompleteResponse
)
def complete_multipart_upload(body: MultiPartUploadCompleteRequest):
    return handle_multipart_complete(body)


@router.post("/abort-multipart-upload", response_model=MultiPartUploadAbortResponse)
def abort_multipart_upload(body: MultiPartUploadAbortRequest):
    return handle_multipart_abort(body)
