variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "eks_node_instance_types" {
  description = "Instance types for EKS nodes"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "eks_node_min_size" {
  type    = number
  default = 2
}

variable "eks_node_max_size" {
  type    = number
  default = 5
}

variable "eks_node_desired" {
  type    = number
  default = 3
}

variable "rds_instance_class" {
  type    = string
  default = "db.t3.medium"
}

variable "rds_storage_gb" {
  type    = number
  default = 20
}

variable "elasticache_node_type" {
  type    = string
  default = "cache.t3.micro"
}

variable "opensearch_instance_type" {
  type    = string
  default = "t3.medium.search"
}

variable "opensearch_ebs_size_gb" {
  type    = number
  default = 10
}

variable "kafka_instance_type" {
  type    = string
  default = "kafka.t3.small"
}
