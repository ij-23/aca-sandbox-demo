terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm" }
    azapi   = { source = "Azure/azapi" }
  }
}

locals { containers = toset(["reports", "events", "diffs", "replay"]) }
# ARM never invokes listKeys; private containers are also ARM-managed.
resource "azapi_resource" "account" {
  type                      = "Microsoft.Storage/storageAccounts@2025-06-01"
  name                      = var.name
  parent_id                 = var.resource_group_id
  location                  = var.location
  tags                      = var.tags
  schema_validation_enabled = true
  response_export_values    = []
  body = {
    kind = "StorageV2"
    sku  = { name = "Standard_${var.replication}" }
    properties = {
      accessTier                   = "Hot"
      supportsHttpsTrafficOnly     = true
      minimumTlsVersion            = "TLS1_2"
      allowBlobPublicAccess        = false
      allowSharedKeyAccess         = false
      defaultToOAuthAuthentication = true
      publicNetworkAccess          = "Enabled"
    }
  }
}
resource "azapi_resource" "container" {
  for_each                  = local.containers
  type                      = "Microsoft.Storage/storageAccounts/blobServices/containers@2025-06-01"
  name                      = each.key
  parent_id                 = "${azapi_resource.account.id}/blobServices/default"
  schema_validation_enabled = true
  response_export_values    = []
  body                      = { properties = { publicAccess = "None" } }
}
resource "azapi_resource" "retention" {
  type                      = "Microsoft.Storage/storageAccounts/managementPolicies@2025-06-01"
  name                      = "default"
  parent_id                 = azapi_resource.account.id
  schema_validation_enabled = true
  response_export_values    = []
  body = {
    properties = {
      policy = {
        rules = [{
          name    = "expire-demo-artifacts"
          enabled = true
          type    = "Lifecycle"
          definition = {
            filters = {
              blobTypes   = ["blockBlob", "appendBlob"]
              prefixMatch = [for name in sort(tolist(local.containers)) : "${name}/"]
            }
            actions = { baseBlob = { delete = { daysAfterModificationGreaterThan = var.retention_days } } }
          }
        }]
      }
    }
  }
}
resource "azurerm_monitor_diagnostic_setting" "blob" {
  name                           = "blob-audit"
  target_resource_id             = "${azapi_resource.account.id}/blobServices/default"
  log_analytics_workspace_id     = var.workspace_id
  log_analytics_destination_type = "Dedicated"
  enabled_log { category = "StorageRead" }
  enabled_log { category = "StorageWrite" }
  enabled_log { category = "StorageDelete" }
}
