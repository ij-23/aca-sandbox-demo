terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm" }
    azapi   = { source = "Azure/azapi" }
  }
}

# ARM avoids the shared keys exported by the AzureRM workspace resource.
resource "azapi_resource" "workspace" {
  type                      = "Microsoft.OperationalInsights/workspaces@2025-07-01"
  name                      = "log-${var.stem}"
  parent_id                 = var.resource_group_id
  location                  = var.location
  tags                      = var.tags
  schema_validation_enabled = true
  response_export_values    = []
  body = {
    properties = {
      sku              = { name = "PerGB2018" }
      retentionInDays  = var.retention_days
      features         = { disableLocalAuth = true }
      workspaceCapping = { dailyQuotaGb = var.daily_cap_gb }
    }
  }
}
resource "azurerm_application_insights" "this" {
  name                         = "appi-${var.stem}"
  resource_group_name          = var.resource_group_name
  location                     = var.location
  application_type             = "web"
  workspace_id                 = azapi_resource.workspace.id
  retention_in_days            = var.retention_days
  daily_data_cap_in_gb         = var.daily_cap_gb
  local_authentication_enabled = false
  ip_masking_enabled           = true
  tags                         = var.tags
}
resource "azurerm_container_app_environment" "this" {
  name                = "cae-${var.stem}"
  resource_group_name = var.resource_group_name
  location            = var.location
  logs_destination    = "azure-monitor"
  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
  tags = var.tags
}
resource "azurerm_monitor_diagnostic_setting" "environment" {
  name                           = "environment-logs"
  target_resource_id             = azurerm_container_app_environment.this.id
  log_analytics_workspace_id     = azapi_resource.workspace.id
  log_analytics_destination_type = "Dedicated"
  enabled_log { category = "ContainerAppConsoleLogs" }
  enabled_log { category = "ContainerAppSystemLogs" }
}
