output "app_name" {
  description = "Deployed application name"
  value       = kubernetes_deployment.telecom_bot.metadata[0].name
}

output "service_name" {
  description = "Kubernetes service name"
  value       = kubernetes_service.telecom_bot.metadata[0].name
}

output "node_port" {
  description = "NodePort to access the app"
  value       = var.node_port
}

output "access_url" {
  description = "Local URL to access the app"
  value       = "http://localhost:${var.node_port}"
}