import os
import uuid
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext
from typing import Any


from ..utils.s3 import generate_presigned_url


def handle_generate_presigned_url(
    event: APIGatewayProxyEventV2, context: LambdaContext
) -> tuple[int, Any]:
    video_id = str(uuid.uuid4())
    s3_key = f"raw/{video_id}"
    link = generate_presigned_url(
        region=os.getenv("AWS_REGION", "ap-south-1"),
        bucket_name=os.getenv("RAW_BUCKET_NAME", "prasaarit-stg-raw-uploads"),
        s3_key=s3_key,
        content_type=event.get("body")["contentType"],
        time_to_expire=30,
    )
    print("s3 link:", link)
    return (200, link)
