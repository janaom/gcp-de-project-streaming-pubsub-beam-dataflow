terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.19.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_storage_bucket" "streaming_project_bucket" {
  name     = var.bucket_name
  location = var.region
}

resource "google_storage_bucket_object" "conversations_json" {
  name   = "conversations.json"
  bucket = google_storage_bucket.streaming_project_bucket.name
  source = "/path-to-your-file/conversations.json"
}

resource "google_pubsub_topic" "topic" {
  name = var.topic_name
}

resource "google_pubsub_subscription" "subscription" {
  name  = var.subscription_name
  topic = google_pubsub_topic.topic.name
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = var.dataset_id
  friendly_name               = "dt_chat"
  location                    = "US"
  default_table_expiration_ms = null
}

resource "google_bigquery_table" "conversations" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = var.table_conversations_name

  schema = <<EOF
[
  {
    "name": "senderAppType",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "courierId",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "fromId",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "toId",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "chatStartedByMessage",
    "type": "BOOLEAN",
    "mode": "NULLABLE"
  },
  {
    "name": "orderId",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "orderStage",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "customerId",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "messageSentTime",
    "type": "TIMESTAMP",
    "mode": "NULLABLE"
  }
]
EOF
}

resource "google_bigquery_table" "orders" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = var.table_orders_name

  schema = <<EOF
[
  {
    "name": "cityCode",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "orderId",
    "type": "INTEGER",
    "mode": "NULLABLE"
  }
]
EOF
}
