resource "confluent_connector" "sink_playground_quarantine" {
  environment {
    id = data.confluent_environment.main.id
  }
  kafka_cluster {
    id = var.confluent_kafka_cluster_id
  }
  
  config_sensitive = {}

  config_nonsensitive = {
    "topics"                   = "fraud_quarantine_playground"
    "input.data.format"        = "AVRO"
    "connector.class"          = "BigQuerySink"
    "name"                     = "sink_playground_quarantine"
    "tasks.max"                = "1"
    "kafka.auth.mode"          = "KAFKA_API_KEY"
    "kafka.api.key"            = var.confluent_cluster_api_key
    "kafka.api.secret"         = var.confluent_cluster_api_secret
    "project"                  = var.gcp_project_id
    "datasets"                 = google_bigquery_dataset.streamguard_threats.dataset_id
    "keyfile"                  = base64decode(google_service_account_key.confluent_bq_sink_key.private_key)
    "auto.create.tables"       = "true"
    "sanitize.topics.name.format" = "false"
    # Mapping topic to table
    "bigquery.topics.fraud_quarantine_playground.table" = "quarantined_transactions"
  }
  
  depends_on = [
    confluent_kafka_topic.fraud_quarantine_playground,
    google_bigquery_dataset.streamguard_threats,
    google_project_iam_member.bq_data_editor,
    google_project_iam_member.bq_job_user
  ]
  
  lifecycle {
    prevent_destroy = false
  }
}
