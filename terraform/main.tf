terraform {
  backend "s3" {
    bucket = "insidertradingstatefile"
    key    = "firstproject/one"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"  # replace with your AWS region
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": "first"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_exec_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "ses_full_access_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}

resource "aws_lambda_function" "insidertradinglambda" {
  function_name = "insidertradinglambda"
  handler       = "lambda_function.handler"  # replace with your handler
  runtime       = "python3.8"  # replace with your runtime

  filename      = "lambda_function_payload.zip"
  source_code_hash = filebase64sha256("lambda_function_payload.zip")

  role          = aws_iam_role.lambda_exec_role.arn
}
