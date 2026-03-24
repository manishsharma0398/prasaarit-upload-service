terraform {
  # Local state intentionally — this config bootstraps the remote state backend
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.37.0"
    }
  }

  required_version = "1.14.7"

  backend "s3" {
    bucket       = "prasaarit-tf-states"
    key          = "prasaarit-upload-service-bootstrap/terraform.tfstate" # IMPORTANT: Make sure the key is different!
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = "ap-south-1"
}
