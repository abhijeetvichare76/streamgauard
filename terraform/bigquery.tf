# BigQuery Dataset
resource "google_bigquery_dataset" "streamguard_threats" {
  dataset_id                  = "streamguard_threats"
  friendly_name               = "StreamGuard Threats"
  description                 = "StreamGuard threat isolation and analysis"
  location                    = var.gcp_region
  default_table_expiration_ms = 3600000 # 1 hour
}

# Service Account for Confluent BigQuery Sink Connector
resource "google_service_account" "confluent_bq_sink" {
  account_id   = "confluent-bigquery-sink"
  display_name = "Confluent BigQuery Sink Connector"
}

# IAM Bindings
resource "google_project_iam_member" "bq_data_editor" {
  project = var.gcp_project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.confluent_bq_sink.email}"
}

resource "google_project_iam_member" "bq_job_user" {
  project = var.gcp_project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.confluent_bq_sink.email}"
}

# Create Key for the Service Account
resource "google_service_account_key" "confluent_bq_sink_key" {
  service_account_id = google_service_account.confluent_bq_sink.name
}

# Output the key (Sensitive)
output "confluent_bq_sink_key_json" {
  value     = base64decode(google_service_account_key.confluent_bq_sink_key.private_key)
  sensitive = true
}
