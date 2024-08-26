resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"
}
