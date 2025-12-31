variable "confluent_cloud_api_key" {
  description = "Confluent Cloud API Key (also used as Flink API Key)"
  type        = string
  sensitive   = true
}

variable "confluent_cloud_api_secret" {
  description = "Confluent Cloud API Secret"
  type        = string
  sensitive   = true
}

variable "confluent_flink_api_key" {
  description = "Flink API Key"
  type        = string
  sensitive   = true
}

variable "confluent_flink_api_secret" {
  description = "Flink API Secret"
  type        = string
  sensitive   = true
}

variable "confluent_kafka_cluster_id" {
  description = "ID of the Kafka Cluster"
  type        = string
}

variable "confluent_cluster_api_key" {
  description = "Kafka Cluster API Key"
  type        = string
  sensitive   = true
}

variable "confluent_cluster_api_secret" {
  description = "Kafka Cluster API Secret"
  type        = string
  sensitive   = true
}

variable "schema_registry_api_key" {
  description = "Schema Registry API Key"
  type        = string
  sensitive   = true
}

variable "schema_registry_api_secret" {
  description = "Schema Registry API Secret"
  type        = string
  sensitive   = true
}


variable "confluent_schema_registry_id" {
  description = "Schema Registry Cluster ID"
  type        = string
}

variable "confluent_schema_registry_url" {
  description = "Schema Registry REST Endpoint URL"
  type        = string
}

variable "confluent_kafka_rest_endpoint" {
  description = "Kafka REST Endpoint URL"
  type        = string
}

variable "confluent_organization_id" {
  description = "Confluent Organization ID"
  type        = string
}

variable "confluent_environment_id" {
  description = "Confluent Environment ID"
  type        = string
}





variable "gcp_project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "gcp_region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-east1"
}

variable "google_service_account_key" {
  description = "Google Service Account JSON Key (Minified)"
  type        = string
  sensitive   = true
}
