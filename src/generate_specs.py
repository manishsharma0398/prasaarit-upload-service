import pathlib

import yaml
from fastapi.openapi.utils import get_openapi

from .app import create_fast_api_app

# ====== CONFIGURATION ======
_X_AMAZON_APIGATEWAY_INTEGRATION = "x-amazon-apigateway-integration"


# ====== INTEGRATION GENERATORS ======
def get_lambda_integration(description: str = ""):
    return {
        "type": "AWS_PROXY",
        "httpMethod": "POST",
        "uri": "${lambda_invoke_arn}",
        "payloadFormatVersion": "2.0",
        "description": description,
        "passthroughBehavior": "WHEN_NO_MATCH",
        "timeoutInMillis": 15000,
    }


def write_spec(spec: dict, folder: str):
    pathlib.Path(folder).mkdir(exist_ok=True, parents=True)
    with open(f"{folder}/openapi.yaml", "w") as f:
        yaml.dump(spec, f, sort_keys=False)


def generate_api_spec():
    app = create_fast_api_app()

    spec = get_openapi(
        title="prasaarit-upload-services-api",
        version=app.version,
        openapi_version="3.0.3",  # API Gateway v2 only supports OpenAPI 3.0.x
        description=app.description,
        routes=app.routes,
    )

    for path_key, path_value in spec["paths"].items():
        for method_key in path_value:
            openapi_method = path_value[method_key]
            summary = openapi_method.get("summary", "")

            selected_integration = get_lambda_integration(summary)

            # Merge with any existing integration values like cacheKeyParameters
            existing = openapi_method.get(_X_AMAZON_APIGATEWAY_INTEGRATION, {})
            path_value[method_key][_X_AMAZON_APIGATEWAY_INTEGRATION] = {
                **selected_integration,
                **existing,
            }

    write_spec(spec, "./api")


# Run the generator
generate_api_spec()
