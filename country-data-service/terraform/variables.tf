variable "project_name" {
  description = "The name of the project"
  default     = "country-data-service"
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
