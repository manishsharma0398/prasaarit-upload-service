from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext
from typing import Any


from ..utils.s3 import generate_presigned_url


def handle_generate_presigned_url(
    event: APIGatewayProxyEventV2, context: LambdaContext
) -> tuple[int, Any]:
    return (200, "")
