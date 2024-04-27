variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
  default     = "project-id"
}

variable "region" {
  description = "The region for the resources"
  type        = string
  default     = "your-region"
}

variable "zone" {
  description = "The zone for the resources"
  type        = string
  default     = "your-zone"
}

variable "bucket_name" {
  description = "The name of the GCS bucket"
  type        = string
  default     = "your-bucket"
}

variable "topic_name" {
  description = "The name of the Pub/Sub topic"
  type        = string
  default     = "your-topic-name"
}

variable "subscription_name" {
  description = "The name of the Pub/Sub subscription"
  type        = string
  default     = "your-subscription-name"
}

variable "dataset_id" {
  description = "The ID of the BigQuery dataset"
  type        = string
  default     = "your-dataset-name"
}

variable "table_conversations_name" {
  description = "The name of the BigQuery conversations table"
  type        = string
  default     = "conversations"
}

variable "table_orders_name" {
  description = "The name of the BigQuery orders table"
  type        = string
  default     = "orders"
}
