terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm" }
  }
}

resource "azurerm_role_assignment" "image_pull" {
  scope                = var.registry_id
  role_definition_name = "AcrPull"
  principal_id         = var.app_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "sandbox" {
  scope                = var.sandbox_group_id
  role_definition_name = "Container Apps SandboxGroup Data Owner"
  principal_id         = var.app_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "telemetry" {
  scope                = var.application_insights_id
  role_definition_name = "Monitoring Metrics Publisher"
  principal_id         = var.app_principal_id
  principal_type       = "ServicePrincipal"
}
resource "azurerm_role_assignment" "blob" {
  for_each             = var.blob_container_ids
  scope                = each.value
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.app_principal_id
  principal_type       = "ServicePrincipal"
}
resource "azurerm_role_assignment" "operator" {
  for_each             = var.operators
  scope                = var.sandbox_group_id
  role_definition_name = "Container Apps SandboxGroup Data Owner"
  principal_id         = each.value.object_id
  principal_type       = each.value.principal_type
}
