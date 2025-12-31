terraform {
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "2.15.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "6.12.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.9.1"
    }
  }
}

provider "confluent" {
  cloud_api_key    = var.confluent_cloud_api_key
  cloud_api_secret = var.confluent_cloud_api_secret

  kafka_id            = var.confluent_kafka_cluster_id
  kafka_api_key       = var.confluent_cluster_api_key
  kafka_api_secret    = var.confluent_cluster_api_secret
  kafka_rest_endpoint = var.confluent_kafka_rest_endpoint

  schema_registry_id            = var.confluent_schema_registry_id
  schema_registry_api_key       = var.schema_registry_api_key
  schema_registry_api_secret    = var.schema_registry_api_secret
  schema_registry_rest_endpoint = var.confluent_schema_registry_url
}

provider "google" {
  project     = var.gcp_project_id
  region      = var.gcp_region
  credentials = var.google_service_account_key
}

data "confluent_environment" "main" {
  id = var.confluent_environment_id
}

data "confluent_kafka_cluster" "main" {
  id = var.confluent_kafka_cluster_id
  environment {
    id = data.confluent_environment.main.id
  }
}

data "confluent_schema_registry_cluster" "main" {
  environment {
    id = data.confluent_environment.main.id
  }
}

data "confluent_flink_region" "main" {
  cloud  = "GCP"
  region = var.gcp_region
}



# Flink Compute Pool
resource "confluent_flink_compute_pool" "main" {
  display_name = "streamguard-flink"
  cloud        = "GCP"
  region       = var.gcp_region
  max_cfu      = 5
  environment {
    id = data.confluent_environment.main.id
  }
}




