resource "aws_sqs_queue" "data_fetch_queue" {
  name                      = "${var.project_name}-data-fetch-queue"
  delay_seconds             = 0
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 0
  visibility_timeout_seconds = 4*60
  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue" "data_fetch_dlq" {
  name = "${var.project_name}-data-fetch-dlq"
  
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.data_fetch_queue.arn]
  })
}

resource "aws_sqs_queue_redrive_policy" "data_fetch_queue" {
  queue_url = aws_sqs_queue.data_fetch_queue.id

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.data_fetch_dlq.arn
    maxReceiveCount     = 5
  })
}