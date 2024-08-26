resource "aws_codebuild_project" "build" {
  name         = "${var.project_name}-build"
  description  = "Builds the ${var.project_name} project"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = var.codebuild_compute_type
    image                       = var.codebuild_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = false

    environment_variable {
      name  = "REDIS_HOST"
      value = aws_elasticache_cluster.main.cache_nodes[0].address
    }
    environment_variable {
      name  = "REDIS_PORT"
      value = aws_elasticache_cluster.main.port
    }
    environment_variable {
      name  = "IAM_ROLE_ARN"
      value = aws_iam_role.chalice_role.arn
    }
    environment_variable {
      name  = "SQS_QUEUE_URL"
      value = aws_sqs_queue.data_fetch_queue.url
    }
    environment_variable {
      name  = "SUBNET_IDS"
      value = join(",", aws_subnet.private[*].id)
    }
    environment_variable {
      name  = "SECURITY_GROUP_ID"
      value = aws_security_group.chalice.id
    }
    environment_variable {
        name  = "CHALICE_STATE_BUCKET"
        value = aws_s3_bucket.chalice_state_store.id
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = file("./buildspec.yaml")
  }
}

resource "aws_codebuild_project" "test_project" {
  name          = "${var.project_name}-test-project"
  description   = "Runs tests for the ${var.project_name} project"
  service_role   = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = var.codebuild_compute_type
    image                       = var.codebuild_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = false
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = file("./test_buildspec.yaml")
  }
}

resource "aws_iam_role" "codebuild_role" {
  name = "${var.project_name}-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "codebuild_policy" {
  name = "${var.project_name}-codebuild-policy"
  role = aws_iam_role.codebuild_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Action = [
          "iam:AttachRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:DetachRolePolicy",
          "iam:CreateRole",
          "iam:PutRolePolicy",
          "iam:GetRole",
          "iam:PassRole"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Effect = "Allow"
        "Action": [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:ListBucket"
        ],
        "Resource": [
          "${aws_s3_bucket.chalice_state_store.arn}",
          "${aws_s3_bucket.chalice_state_store.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:*"
        ]
        Resource = [
          "arn:aws:lambda:us-west-2:010438487093:function:${var.project_name}-*",
          "*"
        ]
      },
      {
          Action = [
            "apigateway:*",
          ]
          Effect   = "Allow"
          Resource = "*"
        },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "codebuild_managed_policies" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AWSCodeBuildAdminAccess",
    "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess",
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
  ])

  role       = aws_iam_role.codebuild_role.name
  policy_arn = each.value
}