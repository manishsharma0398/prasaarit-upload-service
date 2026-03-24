from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext
from typing import Any


from ..utils.s3 import (
    initiate_multipart_upload,
    complete_multipart_upload,
    abort_multipart_upload,
)


def handle_multipart_initiate(
    event: APIGatewayProxyEventV2, context: LambdaContext
) -> tuple[int, Any]:
    return (200, "")


def handle_multipart_complete(
    event: APIGatewayProxyEventV2, context: LambdaContext
) -> tuple[int, Any]:
    return (200, "")


def handle_multipart_abort(
    event: APIGatewayProxyEventV2, context: LambdaContext
) -> tuple[int, Any]:
    return (200, "")
