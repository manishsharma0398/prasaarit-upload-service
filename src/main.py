from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext

from .utils.logger import logger

from .utils.s3 import (
    abort_multipart_upload,
    complete_multipart_upload,
    generate_presigned_url,
    initiate_multipart_upload,
)


def handler(event: APIGatewayProxyEventV2, context: LambdaContext):
    logger.info("Incoming event", extra={"event": event})
    route = event.path
    if route:
        pass
