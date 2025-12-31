# BigQuery Dataset
resource "google_bigquery_dataset" "streamguard_threats" {
  dataset_id                  = "streamguard_threats"
  friendly_name               = "StreamGuard Threats"
  description                 = "StreamGuard threat isolation and analysis"
  location                    = var.gcp_region
  # No expiration - tables persist for judges to test
}

# Service Account for Confluent BigQuery Sink Connector
resource "google_service_account" "confluent_bq_sink" {
  account_id   = "confluent-bq-sink-aegis"
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

resource "google_bigquery_table" "customer_profiles" {
  dataset_id          = google_bigquery_dataset.streamguard_threats.dataset_id
  table_id            = "customer_profiles"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "user_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "age_group",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "account_tenure_days",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "avg_transfer_amount",
    "type": "FLOAT",
    "mode": "NULLABLE"
  },
  {
    "name": "behavioral_segment",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "created_at",
    "type": "TIMESTAMP",
    "mode": "NULLABLE"
  }
]
EOF
}

resource "google_bigquery_table" "beneficiary_graph" {
  dataset_id          = google_bigquery_dataset.streamguard_threats.dataset_id
  table_id            = "beneficiary_graph"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "account_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "risk_score",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "account_age_hours",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "linked_to_flagged_device",
    "type": "BOOLEAN",
    "mode": "NULLABLE"
  },
  {
    "name": "created_at",
    "type": "TIMESTAMP",
    "mode": "NULLABLE"
  }
]
EOF
}

resource "google_bigquery_table" "mobile_banking_sessions" {
  dataset_id          = google_bigquery_dataset.streamguard_threats.dataset_id
  table_id            = "mobile_banking_sessions"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "session_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "user_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "transaction_id",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "event_type",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "is_call_active",
    "type": "BOOLEAN",
    "mode": "NULLABLE"
  },
  {
    "name": "typing_cadence_score",
    "type": "FLOAT",
    "mode": "NULLABLE"
  },
  {
    "name": "session_duration_seconds",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "battery_level",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "app_version",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "os_version",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "is_rooted_jailbroken",
    "type": "BOOLEAN",
    "mode": "NULLABLE"
  },
  {
    "name": "geolocation_lat",
    "type": "FLOAT",
    "mode": "NULLABLE"
  },
  {
    "name": "geolocation_lon",
    "type": "FLOAT",
    "mode": "NULLABLE"
  },
  {
    "name": "geolocation_accuracy_meters",
    "type": "FLOAT",
    "mode": "NULLABLE"
  },
  {
    "name": "time_of_day_hour",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "event_time",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  }
]
EOF
}
