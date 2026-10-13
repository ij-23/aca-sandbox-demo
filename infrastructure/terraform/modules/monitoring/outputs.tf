output "workspace_id" {
  value       = azapi_resource.workspace.id
  description = "Workspace ID without shared keys."
}
output "environment_id" {
  value       = azurerm_container_app_environment.this.id
  description = "Container Apps Environment ID."
}
output "application_insights_id" {
  value       = azurerm_application_insights.this.id
  description = "Application Insights ID."
}
