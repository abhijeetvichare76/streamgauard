resource "confluent_schema" "customer_bank_transfer" {
  schema_registry_cluster {
    id = data.confluent_schema_registry_cluster.main.id
  }
  rest_endpoint = data.confluent_schema_registry_cluster.main.rest_endpoint
  subject_name  = "customer_bank_transfers-value"
  format        = "AVRO"
  schema        = <<EOF
{
  "type": "record",
  "name": "CustomerBankTransfer",
  "namespace": "com.streamguard.banking",
  "doc": "Bank transfer with playground traceability",
  "fields": [
    {"name": "transaction_id", "type": "string"},
    {"name": "playground_run_id", "type": ["null", "string"], "default": null, "doc": "Unique ID per playground run for E2E tracing"},
    {"name": "sender_user_id", "type": "string"},
    {"name": "beneficiary_account_id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "currency", "type": "string", "default": "USD"},
    {"name": "session_id", "type": "string", "doc": "Links to BigQuery mobile_banking_sessions"},
    {"name": "first_transfer_to_beneficiary", "type": "boolean"},
    {"name": "transfer_count_last_hour", "type": "int"},
    {"name": "device_fingerprint", "type": ["null", "string"], "default": null},
    {"name": "ip_address", "type": ["null", "string"], "default": null},
    {"name": "geolocation_lat", "type": "double"},
    {"name": "geolocation_lon", "type": "double"},
    {"name": "event_time", "type": "long", "logicalType": "timestamp-millis"}
  ]
}
EOF
}

resource "confluent_schema" "fraud_investigation_alert" {
  schema_registry_cluster {
    id = data.confluent_schema_registry_cluster.main.id
  }
  rest_endpoint = data.confluent_schema_registry_cluster.main.rest_endpoint
  subject_name  = "fraud_investigation_queue-value"
  format        = "AVRO"
  schema        = <<EOF
{
  "type": "record",
  "name": "FraudInvestigationAlert",
  "namespace": "com.streamguard.fraud",
  "fields": [
    {"name": "alert_id", "type": "string"},
    {"name": "transaction_id", "type": "string"},
    {"name": "user_id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "beneficiary_account", "type": "string"},
    {"name": "investigation_type", "type": "string"},
    {"name": "suggested_quarantine_name", "type": "string"},
    {"name": "priority", "type": "string"},
    {"name": "event_time", "type": "long", "logicalType": "timestamp-millis"}
  ]
}
EOF
}

resource "confluent_schema" "fraud_quarantine_transaction" {
  schema_registry_cluster {
    id = data.confluent_schema_registry_cluster.main.id
  }
  rest_endpoint = data.confluent_schema_registry_cluster.main.rest_endpoint
  subject_name  = "fraud_quarantine_playground-value"
  format        = "AVRO"
  schema        = <<EOF
{
  "type": "record",
  "name": "CustomerBankTransfer",
  "namespace": "com.streamguard.banking",
  "doc": "Bank transfer with playground traceability",
  "fields": [
    {"name": "transaction_id", "type": "string"},
    {"name": "playground_run_id", "type": ["null", "string"], "default": null, "doc": "Unique ID per playground run for E2E tracing"},
    {"name": "sender_user_id", "type": "string"},
    {"name": "beneficiary_account_id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "currency", "type": "string", "default": "USD"},
    {"name": "session_id", "type": "string", "doc": "Links to BigQuery mobile_banking_sessions"},
    {"name": "first_transfer_to_beneficiary", "type": "boolean"},
    {"name": "transfer_count_last_hour", "type": "int"},
    {"name": "device_fingerprint", "type": ["null", "string"], "default": null},
    {"name": "ip_address", "type": ["null", "string"], "default": null},
    {"name": "geolocation_lat", "type": "double"},
    {"name": "geolocation_lon", "type": "double"},
    {"name": "event_time", "type": "long", "logicalType": "timestamp-millis"}
  ]
}
EOF
}
