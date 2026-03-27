from fastapi import FastAPI
from src.api.api import router
import json
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2

from .utils.logger import logger
from .utils.constants import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE

from services.s3_services import handle_generate_presigned_url
from src.services.s3_services import (
    handle_multipart_abort,
    handle_multipart_complete,
    handle_multipart_initiate,
)

from typing import Optional


def build_response(status_code: int, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


ROUTES = {
    "POST /generate-presigned-url": "generate_presigned_url",
    "POST /initiate-multipart-upload": "multipart_initiate",
    "POST /complete-multipart-upload": "multipart_complete",
    "POST /abort-multipart-upload": "multipart_abort",
}


def validate_request(body, action) -> tuple[bool, Optional[str]]:
    """
    Validate incoming request body.
    Returns (is_valid, error_message)
    """
    if not body:
        return False, "Body is empty"

    content_type = body.get("contentType", "")
    file_size = body.get("fileSize", 0)

    if action in ["generate_presigned_url", "multipart_initiate"]:
        if not content_type:
            return False, "contentType is required"

        if content_type not in ALLOWED_CONTENT_TYPES:
            return False, f"Invalid content type: {content_type}"

        if not isinstance(file_size, (int, float)) or file_size <= 0:
            return False, "fileSize must be a positive number"

        if file_size > MAX_FILE_SIZE:
            return False, "File too large. Maximum allowed size is 5GB"

    return True, None


def handler(event: APIGatewayProxyEventV2):
    logger.info("Incoming event", extra={"event": json.dumps(event)})

    try:
        route_key = str(event.get("routeKey", ""))

        action = ROUTES.get(route_key)

        if action is None:
            return build_response(404, {"error": f"Route not found: {route_key}"})

        raw_body = event.get("body") or "{}"
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

        if body is None:
            body = {}

        result = validate_request(body, action)
        if result is None:
            return build_response(500, {"error": "validate_request returned None"})

        is_valid, error = result
        if not is_valid:
            return build_response(400, {"error": error})

        status = 0
        res = {}

        if action == "generate_presigned_url":
            status, res = handle_generate_presigned_url(body)
        elif action == "multipart_initiate":
            status, res = handle_multipart_initiate(body)
        elif action == "multipart_complete":
            status, res = handle_multipart_complete(body)
        elif action == "multipart_abort":
            status, res = handle_multipart_abort(body)
        else:
            # This shouldn't happen since we check ROUTES.get() above
            return build_response(500, {"error": f"Unknown action: {action}"})

        return build_response(status, res)

    except json.JSONDecodeError:
        return build_response(400, {"error": "Invalid JSON body"})

    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        return build_response(500, {"error": "Server configuration error"})

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return build_response(500, {"error": "Internal server error"})


def create_fast_api_app() -> FastAPI:
    logger.debug("Initializing FastAPI application")
    app = FastAPI()

    app.include_router(router)

    return app


# print(
#     handler(
#         event={
#             "version": "2.0",
#             "routeKey": "POST /abort-multipart-upload",
#             "rawPath": "/stg/generate-presigned-url",
#             "rawQueryString": "",
#             "headers": {
#                 "accept": "*/*",
#                 "accept-encoding": "br, gzip, deflate",
#                 "accept-language": "*",
#                 "cache-control": "no-cache",
#                 "content-length": "47",
#                 "content-type": "application/json",
#                 "host": "y87ayje7id.execute-api.ap-south-1.amazonaws.com",
#                 "pragma": "no-cache",
#                 "sec-fetch-mode": "cors",
#                 "user-agent": "node",
#                 "x-amzn-trace-id": "Root=1-69b79cc7-6aa485e52f33a2b23aed2f50",
#                 "x-forwarded-for": "49.37.55.192",
#                 "x-forwarded-port": "443",
#                 "x-forwarded-proto": "https",
#             },
#             "requestContext": {
#                 "accountId": "221723377310",
#                 "apiId": "y87ayje7id",
#                 "domainName": "y87ayje7id.execute-api.ap-south-1.amazonaws.com",
#                 "domainPrefix": "y87ayje7id",
#                 "http": {
#                     "method": "POST",
#                     "path": "/stg/generate-presigned-url",
#                     "protocol": "HTTP/1.1",
#                     "sourceIp": "49.37.55.192",
#                     "userAgent": "node",
#                 },
#                 "requestId": "aTVvPju0hcwEPqg=",
#                 "routeKey": "POST /generate-presigned-url",
#                 "stage": "stg",
#                 "time": "16/Mar/2026:06:01:43 +0000",
#                 "timeEpoch": 1773640903579,
#             },
#             "body": '{"contentType":"video/mp4","fileSize":24377474,"s3Key":"raw/a14a931b-2ab0-4c5b-97a8-08ae60c3a204","uploadId":"XZ6dlqvlZ1TqQCskwAYyhsTg_3I_8UhiXzpD8Cp4hYP.jz_GGFvWB2V2K7nsU_GF1gHJkG991gGHZ7KEez20lVHp0IFBx1d1Bh8xzvbzUGNWdjxYnghkNcps8XeC5hTR"}',
#             "isBase64Encoded": False,
#         },  # type: ignore
#         context={},  # type: ignore
#     )
# )
