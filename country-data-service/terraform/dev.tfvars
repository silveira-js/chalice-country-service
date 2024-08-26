aws_region = "us-west-2"
vpc_cidr = "10.0.0.0/16"
redis_node_type = "cache.t3.micro"
redis_num_cache_nodes = 1
codebuild_compute_type = "BUILD_GENERAL1_MEDIUM"
codebuild_image = "aws/codebuild/standard:6.0"
github_repo = "silveira-js/test-chalice-app"
github_connection_arn = "arn:aws:codeconnections:us-west-2:010438487093:connection/257a3c51-8bfa-4d13-bda7-0071eff3d09b"