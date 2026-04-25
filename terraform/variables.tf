variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "telecom-bot"
}

variable "app_image" {
  description = "Docker image to deploy"
  type        = string
  default     = "integrated-telecom-bot:latest"
}

variable "app_port" {
  description = "Port the app runs on"
  type        = number
  default     = 8501
}

variable "node_port" {
  description = "Kubernetes NodePort"
  type        = number
  default     = 30001
}

variable "replicas" {
  description = "Number of pod replicas"
  type        = number
  default     = 1
}