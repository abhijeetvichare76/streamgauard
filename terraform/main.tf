terraform {
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "2.15.0"
    }
  }
}

provider "confluent" {
  cloud_api_key    = var.confluent_cloud_api_key
  cloud_api_secret = var.confluent_cloud_api_secret
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

data "confluent_flink_region" "main" {
  cloud  = "GCP"
  region = var.gcp_region
}

# Flink Service Account
resource "confluent_service_account" "flink" {
  display_name = "flink-service-account"
  description  = "Service account for Flink statements"
}

resource "confluent_role_binding" "flink_admin" {
  principal   = "User:u-k8ok5r6"
  role_name   = "FlinkAdmin"
  crn_pattern = data.confluent_environment.main.resource_name
}

resource "confluent_role_binding" "flink_kafka_admin" {
  principal   = "User:u-k8ok5r6"
  role_name   = "CloudClusterAdmin"
  crn_pattern = data.confluent_kafka_cluster.main.rbac_crn
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

# Kafka Topics
resource "confluent_kafka_topic" "raw_transactions" {
  kafka_cluster {
    id = data.confluent_kafka_cluster.main.id
  }
  topic_name       = "raw_transactions"
  partitions_count = 3
  rest_endpoint    = data.confluent_kafka_cluster.main.rest_endpoint
  credentials {
    key    = var.confluent_cluster_api_key
    secret = var.confluent_cluster_api_secret
  }
}

resource "confluent_kafka_topic" "clean_transactions" {
  kafka_cluster {
    id = data.confluent_kafka_cluster.main.id
  }
  topic_name       = "clean_transactions"
  partitions_count = 3
  rest_endpoint    = data.confluent_kafka_cluster.main.rest_endpoint
  credentials {
    key    = var.confluent_cluster_api_key
    secret = var.confluent_cluster_api_secret
  }
}

resource "confluent_kafka_topic" "quarantine_transactions" {
  kafka_cluster {
    id = data.confluent_kafka_cluster.main.id
  }
  topic_name       = "quarantine_transactions"
  partitions_count = 3
  rest_endpoint    = data.confluent_kafka_cluster.main.rest_endpoint
  credentials {
    key    = var.confluent_cluster_api_key
    secret = var.confluent_cluster_api_secret
  }
}

# Flink AI Connection
resource "confluent_flink_statement" "googleai_connection" {
  statement = "CREATE CONNECTION `${data.confluent_environment.main.id}`.`${data.confluent_kafka_cluster.main.id}`.googleai_connection_v4 WITH ('type' = 'vertexai', 'endpoint' = 'https://${var.gcp_region}-aiplatform.googleapis.com/v1/projects/${var.gcp_project_id}/locations/${var.gcp_region}/publishers/google/models/gemini-2.0-flash-001:generateContent', 'service-key' = '${var.google_service_account_key}');"

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

  depends_on = [confluent_role_binding.flink_admin, confluent_role_binding.flink_kafka_admin]

  lifecycle {
    ignore_changes = [statement]
  }
}

# Flink AI Model
resource "confluent_flink_statement" "streamguard_validator" {
  statement = "CREATE MODEL `${data.confluent_environment.main.id}`.`${data.confluent_kafka_cluster.main.id}`.streamguard_validator_v4 INPUT (input STRING) OUTPUT (output_json STRING) WITH('provider' = 'vertexai', 'vertexai.connection' = 'googleai_connection_v4', 'vertexai.system_prompt' = 'You are a data validator. Return ONLY a single line of valid JSON with no markdown formatting, no code fences, no backticks. Format: {\"valid\": boolean, \"reason\": \"string\", \"confidence\": number}', 'task' = 'text_generation');"

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

  depends_on = [confluent_flink_statement.googleai_connection]

  lifecycle {
    ignore_changes = [statement]
  }
}

# Flink Table Definitions
# COMMENTED OUT - Confluent Cloud Flink auto-infers tables from Kafka topics
# resource "confluent_flink_statement" "table_raw_transactions" {
#   statement = <<EOT
#     CREATE TABLE IF NOT EXISTS raw_transactions (
#       payload STRING
#     );
#   EOT
# 
#   properties = {
#     "sql.current-catalog"  = data.confluent_environment.main.id
#     "sql.current-database" = data.confluent_kafka_cluster.main.id
#   }
# 
#   rest_endpoint = var.flink_rest_endpoint
# 
#   compute_pool {
#     id = confluent_flink_compute_pool.main.id
#   }
# 
#   principal {
#     id = "u-k8ok5r6"
#   }
# 
#   organization {
#     id = "15ba519e-1d72-4d31-a99b-9ad8162935db"
#   }
# 
#   credentials {
#     key    = var.flink_api_key
#     secret = var.flink_api_secret
#   }
# 
#   environment {
#     id = data.confluent_environment.main.id
#   }
# 
#   depends_on = [
#     confluent_kafka_topic.raw_transactions,
#     confluent_role_binding.flink_admin,
#     confluent_role_binding.flink_kafka_admin
#   ]
# }
# 
# resource "confluent_flink_statement" "table_clean_transactions" {
#   statement = <<EOT
#     CREATE TABLE IF NOT EXISTS clean_transactions (
#       payload STRING
#     );
#   EOT
# 
#   properties = {
#     "sql.current-catalog"  = data.confluent_environment.main.id
#     "sql.current-database" = data.confluent_kafka_cluster.main.id
#   }
# 
#   rest_endpoint = var.flink_rest_endpoint
# 
#   compute_pool {
#     id = confluent_flink_compute_pool.main.id
#   }
# 
#   principal {
#     id = "u-k8ok5r6"
#   }
# 
#   organization {
#     id = "15ba519e-1d72-4d31-a99b-9ad8162935db"
#   }
# 
#   credentials {
#     key    = var.flink_api_key
#     secret = var.flink_api_secret
#   }
# 
#   environment {
#     id = data.confluent_environment.main.id
#   }
# 
#   depends_on = [
#     confluent_kafka_topic.clean_transactions,
#     confluent_role_binding.flink_admin,
#     confluent_role_binding.flink_kafka_admin
#   ]
# }
# 
# resource "confluent_flink_statement" "table_quarantine_transactions" {
#   statement = <<EOT
#     CREATE TABLE IF NOT EXISTS quarantine_transactions (
#       payload STRING
#     );
#   EOT
# 
#   properties = {
#     "sql.current-catalog"  = data.confluent_environment.main.id
#     "sql.current-database" = data.confluent_kafka_cluster.main.id
#   }
# 
#   rest_endpoint = var.flink_rest_endpoint
# 
#   compute_pool {
#     id = confluent_flink_compute_pool.main.id
#   }
# 
#   principal {
#     id = "u-k8ok5r6"
#   }
# 
#   organization {
#     id = "15ba519e-1d72-4d31-a99b-9ad8162935db"
#   }
# 
#   credentials {
#     key    = var.flink_api_key
#     secret = var.flink_api_secret
#   }
# 
#   environment {
#     id = data.confluent_environment.main.id
#   }
# 
#   depends_on = [
#     confluent_kafka_topic.quarantine_transactions,
#     confluent_role_binding.flink_admin,
#     confluent_role_binding.flink_kafka_admin
#   ]
# }

# Flink AI Routing Logic
resource "confluent_flink_statement" "streamguard_router" {
  statement = <<EOT
    EXECUTE STATEMENT SET BEGIN
      -- Route valid transactions
      INSERT INTO clean_transactions
      SELECT 
        r.transaction_id,
        r.product_name,
        r.price,
        r.quantity,
        r.customer_id,
        r.`timestamp`
      FROM raw_transactions r,
      LATERAL TABLE(ML_PREDICT('streamguard_validator_v4', 
        CONCAT('Validate transaction: product=', r.product_name, 
               ' price=$', CAST(r.price AS STRING), 
               ' qty=', CAST(r.quantity AS STRING))
      )) AS ai(output_json)
      WHERE JSON_VALUE(ai.output_json, '$.valid') = 'true';
      
      -- Route invalid transactions with AI reasoning
      INSERT INTO quarantine_transactions
      SELECT 
        r.transaction_id,
        r.product_name,
        r.price,
        r.quantity,
        r.customer_id,
        r.`timestamp`,
        JSON_VALUE(ai.output_json, '$.reason') AS ai_reason,
        CAST(JSON_VALUE(ai.output_json, '$.confidence') AS DOUBLE) AS ai_confidence
      FROM raw_transactions r,
      LATERAL TABLE(ML_PREDICT('streamguard_validator_v4', 
        CONCAT('Validate transaction: product=', r.product_name, 
               ' price=$', CAST(r.price AS STRING), 
               ' qty=', CAST(r.quantity AS STRING))
      )) AS ai(output_json)
      WHERE JSON_VALUE(ai.output_json, '$.valid') = 'false';
    END;
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
    confluent_flink_statement.streamguard_validator
  ]
}


