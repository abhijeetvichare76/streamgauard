# AI Validation Results Topic (Simple Kafka Topic)
# Flink will auto-infer the table schema from Schema Registry
resource "confluent_kafka_topic" "ai_validation_results" {
  kafka_cluster {
    id = data.confluent_kafka_cluster.main.id
  }
  topic_name       = "ai_validation_results"
  partitions_count = 3
  rest_endpoint    = data.confluent_kafka_cluster.main.rest_endpoint
  credentials {
    key    = var.confluent_cluster_api_key
    secret = var.confluent_cluster_api_secret
  }
}

# AI Validation Router - Single INSERT to ai_validation_results
resource "confluent_flink_statement" "ai_validation_router" {
  statement = <<EOT
    INSERT INTO ai_validation_results
    SELECT
      CAST(NULL AS BYTES) AS key,
      r.transaction_id,
      r.product_name,
      r.price,
      r.quantity,
      r.customer_id,
      r.event_time,
      JSON_VALUE(ai.output_json, '$.valid') AS ai_valid,
      JSON_VALUE(ai.output_json, '$.reason') AS ai_reason,
      CAST(JSON_VALUE(ai.output_json, '$.confidence') AS DOUBLE) AS ai_confidence
    FROM raw_transactions r,
    LATERAL TABLE(ML_PREDICT('streamguard_validator_v4',
      CONCAT('Validate: ', r.product_name, ' $', CAST(r.price AS STRING), ' qty=', CAST(r.quantity AS STRING))
    )) AS ai(output_json);
  EOT

  properties = {
    "sql.current-catalog"  = data.confluent_environment.main.id
    "sql.current-database" = data.confluent_kafka_cluster.main.id
  }

  rest_endpoint = var.flink_rest_endpoint

  compute_pool {
    id = confluent_flink_compute_pool.main.id
  }

  principal {
    id = "u-k8ok5r6"
  }

  organization {
    id = "15ba519e-1d72-4d31-a99b-9ad8162935db"
  }

  credentials {
    key    = var.flink_api_key
    secret = var.flink_api_secret
  }

  environment {
    id = data.confluent_environment.main.id
  }

  depends_on = [
    confluent_kafka_topic.ai_validation_results,
    confluent_flink_statement.streamguard_validator,
    confluent_role_binding.flink_admin,
    confluent_role_binding.flink_kafka_admin
  ]
}
