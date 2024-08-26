aws_region = "us-west-2"
vpc_cidr = "10.0.0.0/16"
redis_node_type = "cache.t3.micro"
redis_num_cache_nodes = 1
codebuild_compute_type = "BUILD_GENERAL1_MEDIUM"
codebuild_image = "aws/codebuild/standard:6.0"
github_repo = "silveira-js/test-chalice-app"
github_connection_arn = "arn:aws:codestar-connections:us-west-2:010438487093:connection/3546d68c-22b3-4b6b-8a59-e94087ea14b4"