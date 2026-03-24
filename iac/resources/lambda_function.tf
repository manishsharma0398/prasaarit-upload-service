locals {
  lambda_full_name = "${var.aws_lambda_env}-${var.aws_lambda_name}"
}

resource "aws_cloudwatch_log_group" "main" {
  name              = "/aws/lambda/${local.lambda_full_name}"
  retention_in_days = 14

  tags = {
    Environment = "stg"
    Application = "Prasaarit"
  }
}

resource "aws_lambda_function" "main" {
  function_name    = local.lambda_full_name
  description      = var.aws_lambda_description
  role             = aws_iam_role.main.arn
  filename         = "../../prasaarit_upload_service.zip"
  source_code_hash = filebase64sha256("../../prasaarit_upload_service.zip")
  handler          = "src.main.handler"
  runtime          = "python3.13"
  architectures    = ["arm64"]
  depends_on       = [aws_cloudwatch_log_group.main]
  memory_size      = var.aws_lambda_memory_size
  timeout          = var.aws_lambda_timeout

  environment {
    variables = {
      ENV = "stg"
    }
  }

  tags = {
    Environment = "stg"
    Application = "Prasaarit"
  }
}
