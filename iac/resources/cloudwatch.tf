resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${local.lambda_full_name}"
  retention_in_days = 14

  tags = {
    Environment = var.aws_env
    Application = "Prasaarit"
  }
}

resource "aws_cloudwatch_log_group" "api-gw_logs" {
  name              = "/aws/api-gw/${local.api-gw_full_name}"
  retention_in_days = 14

  tags = {
    Environment = var.aws_env
    Application = "Prasaarit"
  }
}
