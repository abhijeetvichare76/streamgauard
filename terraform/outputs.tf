output "bootstrap_servers" {
  value = data.confluent_kafka_cluster.main.bootstrap_endpoint
}

output "environment_id" {
  value = data.confluent_environment.main.id
}

output "kafka_cluster_id" {
  value = data.confluent_kafka_cluster.main.id
}

output "flink_compute_pool_id" {
  value = confluent_flink_compute_pool.main.id
}


