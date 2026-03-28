locals {
  api-gw_name      = var.aws_api_gw_name
  api-gw_full_name = "${var.aws_env}-${var.aws_api_gw_name}"
}

resource "aws_apigatewayv2_api" "main" {
  name          = local.api-gw_name
  description   = ""
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["http://localhost:3000", "https://prasaarit.themanishsharma.in"]
    allow_headers = ["content-type"]
    allow_methods = ["POST", "OPTIONS", "PUT"]
    max_age       = 300
  }

  tags = {
    Environment = "stg"
  }

  body = templatefile("${path.module}/../../api/openapi.yaml", {
    lambda_invoke_arn = aws_lambda_function.main.invoke_arn
  })
}

resource "aws_apigatewayv2_deployment" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  description = ""

  triggers = {
    redeployment = sha1(aws_apigatewayv2_api.main.body)
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_apigatewayv2_stage" "main" {
  api_id        = aws_apigatewayv2_api.main.id
  name          = var.aws_env
  description   = ""
  auto_deploy   = false
  deployment_id = aws_apigatewayv2_deployment.main.id

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api-gw_logs.arn

    # Full reference for all available HTTP API (v2) context variables:
    # https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-logging-variables.html
    # https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
    format = jsonencode({
      requestId               = "$context.requestId"               # Unique ID per request; use to correlate with Lambda logs
      requestTime             = "$context.requestTime"             # CLF-formatted timestamp of when the request was received
      httpMethod              = "$context.httpMethod"              # HTTP method e.g. GET, POST, PUT
      routeKey                = "$context.routeKey"                # Matched route key e.g. "POST /generate-presigned-url"
      status                  = "$context.status"                  # HTTP response status code returned to the client
      protocol                = "$context.protocol"                # Request protocol e.g. "HTTP/1.1"
      responseLength          = "$context.responseLength"          # Response payload size in bytes
      ip                      = "$context.identity.sourceIp"       # Source IP address of the caller
      userAgent               = "$context.identity.userAgent"      # User-Agent header sent by the client
      responseLatency         = "$context.responseLatency"         # Total latency (ms): request received → response sent to client (includes API GW overhead)
      integrationLatency      = "$context.integrationLatency"      # Time (ms) spent inside Lambda only; responseLatency - integrationLatency = API GW overhead
      integrationStatus       = "$context.integrationStatus"       # HTTP status code returned by the Lambda integration to API GW
      integrationErrorMessage = "$context.integrationErrorMessage" # Error message from the integration when the request fails (502/503/504)
    })
  }


}


resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
