resource "aws_dynamodb_table" "country_data" {
  name           = "${var.project_name}-country-data"

  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  hash_key       = "country"

  attribute {
    name = "country"
    type = "S"
  }
}

resource "aws_dynamodb_table" "operation_status" {
  name           = "${var.project_name}-operation-status"

  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  hash_key       = "country"
  range_key      = "timestamp"

  attribute {
    name = "country"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }
}