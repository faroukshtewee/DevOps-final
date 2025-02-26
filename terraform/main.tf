# Declare the VPC
resource "aws_vpc" "main_vpc" {
  cidr_block = var.vpc_cidr_block
}



# Declare the S3 Bucket ACL
resource "aws_s3_bucket" "my_s3_bucket" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_ownership_controls" "ownership" {
  bucket = aws_s3_bucket.my_s3_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}


## Define the ACL separately
#resource "aws_s3_bucket_acl" "my_s3_bucket_acl" {
# bucket = aws_s3_bucket.my_s3_bucket.id
#  acl    = "private"
#
#}

# S3 Bucket Website Configuration
resource "aws_s3_bucket_website_configuration" "my_s3_website" {
  bucket = aws_s3_bucket.my_s3_bucket.id
  index_document {
    suffix = "index.html"
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "my_distribution" {
  enabled = true

  origin {
    domain_name = aws_s3_bucket.my_s3_bucket.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.my_s3_bucket.id}"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.my_s3_bucket.id}"
	forwarded_values {
    query_string = false
    cookies {
      forward = "none"
     }
    }
    viewer_protocol_policy = "redirect-to-https"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# IAM Policy for CloudFront to Access S3
resource "aws_iam_policy" "cloudfront_policy" {
  name        = "cloudfront_policy"
  description = "IAM policy for CloudFront to access S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "arn:aws:s3:::${aws_s3_bucket.my_s3_bucket.bucket}/*"
      }
    ]
  })
}
# EKS Cluster
resource "aws_eks_cluster" "my_eks" {
  name     = "my-eks-cluster"
  role_arn = aws_iam_role.eks_role.arn

  vpc_config {
    subnet_ids = [aws_subnet.public_subnet.id, aws_subnet.private_subnet.id]
  }
}

# ECR Repository
resource "aws_ecr_repository" "my_ecr_init" {
  name                 = "my-ecr-repo-init"
  image_tag_mutability = "MUTABLE"
}
# ECR Repository
resource "aws_ecr_repository" "my_ecr_django" {
  name                 = "my-ecr-repo-dj"
  image_tag_mutability = "MUTABLE"
}

# IAM Role for EKS
resource "aws_iam_role" "eks_role" {
  name = "eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "eks.amazonaws.com" }
    }]
  })
}
# Public Subnet
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = "eu-central-1a"
  map_public_ip_on_launch = true
}

# Private Subnet
resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = var.private_subnet_cidr
  availability_zone = "eu-central-1b"
}


