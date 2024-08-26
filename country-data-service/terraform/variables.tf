variable "project_name" {
  description = "The name of the project"
  default     = "country-data-service"
}

variable "github_repo" {
  description = "The GitHub repository for the project"
  default     = "silveira-js/test-chalice-app"
}

variable "github_branch" {
  description = "The GitHub branch to use for deployments"
  default     = "main"
}

variable "aws_region" {
  description = "The AWS region to deploy resources"
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "redis_node_type" {
  description = "The node type for the ElastiCache Redis cluster"
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "The number of cache nodes for the ElastiCache Redis cluster"
  default     = 1
}

variable "codebuild_compute_type" {
  description = "The compute type for CodeBuild project"
  default     = "BUILD_GENERAL1_MEDIUM"
}

variable "codebuild_image" {
  description = "The Docker image to use for the CodeBuild project"
  default     = "aws/codebuild/standard:6.0"
}

variable "github_connection_arn" {
  description = "The ARN of the GitHub connection for CodePipeline"
  type        = "string"
}