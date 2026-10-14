output "application_url" {
  value       = var.application == null ? "" : module.application[0].url
  description = "Empty during foundation bootstrap; HTTPS URL after approved application deployment."
}
output "subscription_id" {
  value       = var.subscription_id
  description = "Explicit subscription."
}
output "tenant_id" {
  value       = var.tenant_id
  description = "Explicit tenant."
}
output "resource_group_name" {
  value       = module.resource_group.name
  description = "Dedicated resource group."
}
output "region" {
  value       = var.region
  description = "Deployment region."
}
output "sandbox_group_name" {
  value       = module.sandbox_group.name
  description = "Group requiring manual Copilot credentials."
}
output "sandbox_group_id" {
  value       = module.sandbox_group.id
  description = "Sandbox data-plane RBAC scope."
}
output "acr_login_server" {
  value       = module.registry.login_server
  description = "Application-image registry."
}
output "managed_identity_client_id" {
  value       = module.identity.client_id
  description = "Future host UAMI client ID."
}
output "managed_identity_id" {
  value       = module.identity.id
  description = "Future host UAMI ARM ID."
}
output "storage_account_name" {
  value       = module.storage.name
  description = "Private artifacts storage account."
}
output "blob_container_names" {
  value       = keys(module.storage.container_ids)
  description = "Private artifact containers."
}
output "container_app_environment_id" {
  value       = module.monitoring.environment_id
  description = "Future host environment."
}
output "application_insights_id" {
  value       = module.monitoring.application_insights_id
  description = "Entra-only telemetry component."
}
output "manual_setup" {
  value       = { portal = "https://sandboxes.azure.com", group = module.sandbox_group.name, action = "Sandbox Groups > this group > Security > Credentials > GitHub Copilot > Set Token. Follow README.md; never put the token in Terraform." }
  description = "Manual credential setup instructions; no tokens."
}
