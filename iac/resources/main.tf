terraform {
  backend "s3" {
    bucket       = "prasaarit-tf-states"
    key          = "prasaarit-upload-service/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.37.0"
    }
  }

  required_version = "1.14.7"
}


provider "aws" {
  region = "ap-south-1"
}
