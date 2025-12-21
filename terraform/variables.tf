variable "confluent_cloud_api_key" {
  type      = string
  sensitive = true
}

variable "confluent_cloud_api_secret" {
  type      = string
  sensitive = true
}

variable "confluent_cluster_api_key" {
  type      = string
  sensitive = true
}

variable "confluent_cluster_api_secret" {
  type      = string
  sensitive = true
}

variable "confluent_environment_id" {
  type = string
}

variable "confluent_kafka_cluster_id" {
  type = string
}

variable "flink_api_key" {
  type      = string
  sensitive = true
}

variable "flink_api_secret" {
  type      = string
  sensitive = true
}

variable "gcp_project_id" {
  type = string
}

variable "gcp_region" {
  type    = string
  default = "us-east1"
}

variable "flink_rest_endpoint" {
  type = string
}

variable "google_service_account_key" {
  type      = string
  sensitive = true
}
