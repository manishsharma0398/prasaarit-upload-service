import json
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext

from .utils.logger import logger

from .controllers.generate_presigned_url import handle_generate_presigned_url
from .controllers.multi_part_upload import (
    handle_multipart_abort,
    handle_multipart_complete,
    handle_multipart_initiate,
)


def build_response(status_code: int, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
}


def validate_request(body):
    """
    Validate incoming request body.
    Returns (is_valid, error_message)
    """
    if not body:
        return False, "Body is empty"

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


ROUTES = {
    "POST /generate-presigned-url": "generate_presigned_url",
    "POST /initiate-multipart-upload": "multipart_initiate",
    "POST /complete-multipart-upload": "multipart_complete",
    "POST /abort-multipart-upload": "multipart_abort",
}


def handler(event: APIGatewayProxyEventV2, context: LambdaContext):
    logger.info("Incoming event", extra={"event": json.dumps(event)})

    try:
        route_key = str(event.get("route_key", ""))

        action = ROUTES.get(route_key)

        if action is None:
            return build_response(404, {"error": f"Route not found: {route_key}"})

        raw_body = event.get("body") or "{}"
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

        if body is None:
            body = {}

        result = validate_request(body)
        if result is None:
            return build_response(500, {"error": "validate_request returned None"})

        is_valid, error = result
        if not is_valid:
            return build_response(400, {"error": error})

        content_type = body.get("contentType")

        status = 0
        res = {}

        if action == "generate_presigned_url":
            status, res = handle_generate_presigned_url(event, context)
        if action == "multipart_initiate":
            status, res = handle_multipart_initiate(event, context)
        if action == "multipart_complete":
            status, res = handle_multipart_complete(event, context)
        if action == "multipart_abort":
            status, res = handle_multipart_abort(event, context)

        return build_response(status, res)

    except json.JSONDecodeError:
        return build_response(400, {"error": "Invalid JSON body"})

    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        return build_response(500, {"error": "Server configuration error"})

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return build_response(500, {"error": "Internal server error"})
