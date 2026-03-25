resource "aws_apigatewayv2_api" "main" {
  name          = "prasaarit-upload-services-api"
  description   = ""
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["http://localhost:3000", "https://prasaarit.themanishsharma.in", "http://localhost:3000/upload"]
    allow_headers = ["content-type"]
    allow_methods = ["POST", "OPTIONS", "PUT"]
    max_age       = 300
  }

  tags = {}

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
  name          = "stg"
  description   = ""
  auto_deploy   = false
  deployment_id = aws_apigatewayv2_deployment.main.id
}


resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
