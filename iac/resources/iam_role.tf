resource "aws_iam_role" "main" {
  name = local.lambda_full_name

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Effect" : "Allow",
        "Sid" : ""
      }
    ]
  })
}

resource "aws_iam_policy" "cloudwatch" {
  name = "cloudwatch-policy-for-${local.lambda_full_name}"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : "logs:CreateLogGroup",
        "Resource" : aws_cloudwatch_log_group.main.arn
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : [
          aws_cloudwatch_log_group.main.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "main" {
  role       = aws_iam_role.main.name
  policy_arn = aws_iam_policy.cloudwatch.arn
}

resource "aws_iam_policy" "s3" {
  name = "s3-policy-for-${local.lambda_full_name}"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "BucketLevelAccess",
        "Effect" : "Allow",
        "Action" : [
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
        ],
        "Resource" : "arn:aws:s3:::prasaarit-stg-raw-uploads"
      },
      {
        "Sid" : "ObjectLevelAccess",
        "Effect" : "Allow",
        "Action" : [
          "s3:GetObject",
          "s3:PutObject",
          # "s3:CreateMultipartUpload",
          "s3:AbortMultipartUpload",
          "s3:ListMultipartUploadParts",
        ],
        "Resource" : "arn:aws:s3:::prasaarit-stg-raw-uploads/raw/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3" {
  role       = aws_iam_role.main.name
  policy_arn = aws_iam_policy.s3.arn
}
