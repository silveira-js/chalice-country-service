resource "aws_s3_bucket" "chalice_state_store" {
  bucket = "${var.project_name}-chalice-state-store"
}

resource "aws_s3_bucket_versioning" "chalice_state_store_versioning" {
  bucket = aws_s3_bucket.chalice_state_store.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "chalice_state_store_encryption" {
  bucket = aws_s3_bucket.chalice_state_store.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "chalice_state" {
  bucket = aws_s3_bucket.chalice_state_store.id
  key    = ".chalice/deployed/dev.json"
  source = "/dev/null"  // This creates an empty object
  
  // Uncomment the following line if you want to prevent accidental overwrite of existing state
  // force_destroy = false
}
