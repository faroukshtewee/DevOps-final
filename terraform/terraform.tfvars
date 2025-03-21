aws_region       = "eu-central-1"
project_name     = "GymNest-project"
environment      = "dev"

# EKS Configuration
eks_cluster_name                = "my-cluster"
eks_cluster_version             = "1.28"
vpc_cidr                        = "10.0.0.0/16"
vpc_private_subnets             = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
vpc_public_subnets              = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
eks_node_group_instance_types   = ["t3.medium"]
eks_node_group_desired_capacity = 2
eks_node_group_min_size         = 1
eks_node_group_max_size         = 3

# ECR Configuration
ecr_repository_names = ["django-repository", "init-repository"]

# S3 and CloudFront Configuration
s3_bucket_name          = "gymnest2"
cloudfront_price_class  = "PriceClass_100"
cloudfront_allowed_methods = ["GET", "HEAD", "OPTIONS"]
cloudfront_cached_methods  = ["GET", "HEAD"]
cloudfront_default_ttl     = 3600
