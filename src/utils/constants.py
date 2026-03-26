from enum import Enum


class URL_TYPE(Enum):
    SINGLE = "single"
    MULTIPART = "multipart"


MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
PRESIGNED_URL_EXPIRY = 15 * 60  # 15 minutes
ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
}
