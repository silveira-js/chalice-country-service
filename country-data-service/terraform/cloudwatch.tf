resource "aws_cloudwatch_log_group" "codebuild_logs" {
  name              = "/aws/codebuild/${aws_codebuild_project.build.name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "codepipeline_logs" {
  name              = "/aws/codepipeline/${aws_codepipeline.pipeline.name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_metric_alarm" "chalice_errors" {
  alarm_name          = "${var.project_name}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "This metric monitors Chalice lambda errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = "${var.project_name}-dev"
  }
}

resource "aws_cloudwatch_metric_alarm" "chalice_duration" {
  alarm_name          = "${var.project_name}-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Average"
  threshold           = "5000"  # 5 seconds
  alarm_description   = "This metric monitors Chalice lambda duration"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = "${var.project_name}-dev"
  }
}

resource "aws_cloudwatch_metric_alarm" "codebuild_failed_builds" {
  alarm_name          = "${var.project_name}-codebuild-failed-builds"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FailedBuilds"
  namespace           = "AWS/CodeBuild"
  period              = "300"  # 5 minutes
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "This metric monitors CodeBuild failed builds"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ProjectName = aws_codebuild_project.build.name
  }
}

resource "aws_cloudwatch_metric_alarm" "codepipeline_failed_executions" {
  alarm_name          = "${var.project_name}-codepipeline-failed-executions"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FailedPipeline"
  namespace           = "AWS/CodePipeline"
  period              = "300"  # 5 minutes
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "This metric monitors CodePipeline failed executions"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    PipelineName = aws_codepipeline.pipeline.name
  }
}
