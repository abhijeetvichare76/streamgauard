# Topics definition
resource "confluent_kafka_topic" "customer_bank_transfers" {
  kafka_cluster {
    id = var.confluent_kafka_cluster_id
  }
  topic_name       = "customer_bank_transfers"
  partitions_count = 3
  rest_endpoint    = data.confluent_kafka_cluster.main.rest_endpoint
  lifecycle {
    prevent_destroy = false
  }
}

resource "confluent_kafka_topic" "fraud_investigation_queue" {
  kafka_cluster {
    id = var.confluent_kafka_cluster_id
  }
  topic_name       = "fraud_investigation_queue"
  partitions_count = 3
  rest_endpoint    = data.confluent_kafka_cluster.main.rest_endpoint
  lifecycle {
    prevent_destroy = false
  }
}

resource "confluent_kafka_topic" "fraud_quarantine_playground" {
  kafka_cluster {
    id = var.confluent_kafka_cluster_id
  }
  topic_name       = "fraud_quarantine_playground"
  partitions_count = 3
  rest_endpoint    = data.confluent_kafka_cluster.main.rest_endpoint
  lifecycle {
    prevent_destroy = false
  }
}
