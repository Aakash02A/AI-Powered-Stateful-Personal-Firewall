output "vpc_id" {
  value = module.vpc.vpc_id
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "rds_endpoint" {
  value = module.rds.db_instance_endpoint
}

output "redis_endpoint" {
  value = module.elasticache.primary_endpoint_address
}

output "opensearch_endpoint" {
  value = module.opensearch.domain_endpoint
}

output "kafka_bootstrap_brokers" {
  value = module.kafka.bootstrap_brokers
}
