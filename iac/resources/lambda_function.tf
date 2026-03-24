resource "aws_lambda_function" "prasaarit_upload_service" {
  function_name = "stg-prasaarit-upload-service-fn"
  role          = aws_iam_role.prasaarit_upload_service.arn

  filename         = "../../prasaarit_upload_service.zip"
  source_code_hash = filebase64sha256("../../prasaarit_upload_service.zip")
  handler          = "src.main.handler"
  runtime          = "python3.13"

  environment {
    variables = {
      ENV = "stg"
    }
  }

  tags = {
    Environment = "production"
    Application = "Prasaarit"
  }
}
