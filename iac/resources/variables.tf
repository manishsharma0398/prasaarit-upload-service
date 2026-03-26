variable "aws_lambda_name" {
  type        = string
  description = "Lambda function name"
}
variable "aws_api_gw_name" {
  type        = string
  description = "Api gateway name"
}

variable "aws_lambda_description" {
  type        = string
  description = "Lambda function description"
}

variable "aws_env" {
  type        = string
  description = "AWS environment"
}

variable "aws_lambda_memory_size" {
  description = "Lambda function memory size"
  type        = number
  default     = 128
}

variable "aws_lambda_timeout" {
  description = "Amount of time Lambda function has to run"
  type        = number
  default     = 3
}

variable "aws_raw_bucket_name" {
  description = "s3 bucket where uploads are kept"
  type        = string
}
