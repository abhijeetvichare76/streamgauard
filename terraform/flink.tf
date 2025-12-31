resource "confluent_flink_statement" "fraud_investigation_trigger" {
  environment {
    id = data.confluent_environment.main.id
  }
  compute_pool {
    id = resource.confluent_flink_compute_pool.main.id
  }

  
  rest_endpoint = data.confluent_flink_region.main.rest_endpoint

  organization {
    id = var.confluent_organization_id
  }

  credentials {
    key    = var.confluent_flink_api_key
    secret = var.confluent_flink_api_secret
  }

  principal {
    id = "u-k8ok5r6"
  }

  statement = <<EOT
    INSERT INTO fraud_investigation_queue
    SELECT
      CAST(NULL AS BYTES) AS key,
      transaction_id AS alert_id,
      transaction_id,
      sender_user_id AS user_id,
      amount,
      beneficiary_account_id AS beneficiary_account,
      'high_value_transaction' AS investigation_type,
      'fraud-quarantine-' || sender_user_id AS suggested_quarantine_name,
      'HIGH' AS priority,
      event_time
    FROM customer_bank_transfers
    WHERE amount > 1000.00;
  EOT
  
  properties = {
    "sql.current-catalog"  = data.confluent_environment.main.display_name
    "sql.current-database" = data.confluent_kafka_cluster.main.display_name
  }
  
  depends_on = [
    confluent_kafka_topic.customer_bank_transfers,
    confluent_kafka_topic.fraud_investigation_queue,
    confluent_schema.customer_bank_transfer,
    confluent_schema.fraud_investigation_alert
  ]
}

resource "confluent_flink_statement" "route_playground_quarantine" {
  environment {
    id = data.confluent_environment.main.id
  }
  compute_pool {
    id = resource.confluent_flink_compute_pool.main.id
  }

  
  rest_endpoint = data.confluent_flink_region.main.rest_endpoint

  organization {
    id = var.confluent_organization_id
  }

  credentials {
    key    = var.confluent_flink_api_key
    secret = var.confluent_flink_api_secret
  }

  principal {
    id = "u-k8ok5r6"
  }

  statement = <<EOT
    INSERT INTO fraud_quarantine_playground
    SELECT *
    FROM customer_bank_transfers
    WHERE sender_user_id LIKE 'pg_%';
  EOT
  
  properties = {
    "sql.current-catalog"  = data.confluent_environment.main.display_name
    "sql.current-database" = data.confluent_kafka_cluster.main.display_name
  }
  
  depends_on = [
    confluent_kafka_topic.customer_bank_transfers,
    confluent_kafka_topic.fraud_quarantine_playground,
    confluent_schema.customer_bank_transfer,
    confluent_schema.fraud_quarantine_transaction
  ]
}
