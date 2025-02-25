output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main_vpc.id
}

output "eks_cluster_name" {
  description = "EKS Cluster Name"
  value       = aws_eks_cluster.my_eks.name
}

output "ecr_repository_url" {
  description = "ECR Repository URL"
  value       = aws_ecr_repository.my_ecr.repository_url
}

output "s3_bucket_url" {
  value = "https://${aws_s3_bucket.my_s3_bucket.bucket}.s3.amazonaws.com"  # ✅ Corrected reference
}



output "cloudfront_url" {
  description = "CloudFront Distribution URL"
  value       = aws_cloudfront_distribution.my_distribution.domain_name
}
