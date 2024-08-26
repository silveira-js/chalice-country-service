terraform {
  backend "s3" {
    bucket = "terraform-chalice-state-bucket-2"
    key    = "country-data-service/terraform.tfstate"
    region = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt = true
  }
}
