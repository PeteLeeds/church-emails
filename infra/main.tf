terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"
}

data "aws_ssm_parameter" "reviewer_email" {
  name = "/church-emails/reviewer-email"
}

data "aws_ssm_parameter" "church_id" {
  name = "/church-emails/church-id"
}

resource "aws_ssm_parameter" "test" {
  name  = "/church-emails/test"
  type  = "String"
  value = "${data.aws_ssm_parameter.church_id.value}"
}