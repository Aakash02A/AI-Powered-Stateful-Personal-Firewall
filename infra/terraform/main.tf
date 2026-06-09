# ============================================================
# SentinelX AI-SOC — Terraform Root Module
# Environment: ${var.environment}
# ============================================================

terraform {
  required_version = ">= 1.8"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }
  }

  backend "s3" {
    # Configure in environments/dev/backend.hcl or environments/prod/backend.hcl
    # bucket = "sentinelx-terraform-state"
    # key    = "sentinelx/terraform.tfstate"
    # region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "SentinelX"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ── Networking ───────────────────────────────────────────────
module "vpc" {
  source = "./modules/vpc"

  environment         = var.environment
  cidr_block          = var.vpc_cidr
  availability_zones  = var.availability_zones
  private_subnet_cidrs = var.private_subnet_cidrs
  public_subnet_cidrs  = var.public_subnet_cidrs
}

# ── EKS Cluster ──────────────────────────────────────────────
module "eks" {
  source = "./modules/eks"

  environment    = var.environment
  cluster_name   = "sentinelx-${var.environment}"
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  node_instance_types = var.eks_node_instance_types
  node_min_size  = var.eks_node_min_size
  node_max_size  = var.eks_node_max_size
  node_desired   = var.eks_node_desired
}

# ── RDS MySQL ────────────────────────────────────────────────
module "rds" {
  source = "./modules/rds"

  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnet_ids
  db_name             = "sentinelx"
  db_username         = "sentinelx"
  instance_class      = var.rds_instance_class
  allocated_storage   = var.rds_storage_gb
  engine_version      = "8.0"
  multi_az            = var.environment == "prod"
}

# ── ElastiCache Redis ─────────────────────────────────────────
module "elasticache" {
  source = "./modules/elasticache"

  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  node_type      = var.elasticache_node_type
  num_cache_nodes = var.environment == "prod" ? 3 : 1
}

# ── OpenSearch ────────────────────────────────────────────────
module "opensearch" {
  source = "./modules/opensearch"

  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  instance_type     = var.opensearch_instance_type
  instance_count    = var.environment == "prod" ? 3 : 1
  ebs_volume_size   = var.opensearch_ebs_size_gb
}

# ── MSK (Kafka) ───────────────────────────────────────────────
module "kafka" {
  source = "./modules/kafka"

  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  broker_count   = var.environment == "prod" ? 3 : 1
  instance_type  = var.kafka_instance_type
}
