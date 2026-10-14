terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm" }
    azapi   = { source = "Azure/azapi" }
  }
}

locals {
  stream = "Custom-AcademoSandboxLogs_CL"
  fields = ["source", "run_id", "sandbox_id", "role", "event_type", "step_id", "msg"]
}

# Separate from the host identity: ingestion only, no Blob/Sandbox management.
resource "azurerm_user_assigned_identity" "this" {
  name                = "id-${var.stem}-telemetry"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags
}
resource "azurerm_monitor_data_collection_endpoint" "this" {
  name                          = "dce-${var.stem}"
  resource_group_name           = var.resource_group_name
  location                      = var.location
  public_network_access_enabled = true
  tags                          = var.tags
}

# AzureRM table resource cannot author custom columns in the pinned schema.
resource "azapi_resource" "table" {
  type                   = "Microsoft.OperationalInsights/workspaces/tables@2022-10-01"
  name                   = "AcademoSandboxLogs_CL"
  parent_id              = var.workspace_id
  response_export_values = []
  body = {
    properties = {
      plan            = "Analytics"
      retentionInDays = var.retention_days
      schema = {
        name = "AcademoSandboxLogs_CL"
        columns = concat(
          [{ name = "TimeGenerated", type = "datetime", description = "Ingestion timestamp" }],
          [for field in local.fields : { name = field, type = "string", description = "Sanitized workflow ${field}" }]
        )
      }
    }
  }
}
resource "azurerm_monitor_data_collection_rule" "this" {
  name                        = "dcr-${var.stem}-sandboxes"
  resource_group_name         = var.resource_group_name
  location                    = var.location
  data_collection_endpoint_id = azurerm_monitor_data_collection_endpoint.this.id
  tags                        = var.tags
  destinations {
    log_analytics {
      name                  = "existing-workspace"
      workspace_resource_id = var.workspace_id
    }
  }
  stream_declaration {
    stream_name = local.stream
    dynamic "column" {
      for_each = local.fields
      content {
        name = column.value
        type = "string"
      }
    }
  }
  data_flow {
    streams       = [local.stream]
    destinations  = ["existing-workspace"]
    output_stream = local.stream
    transform_kql = "source | where source == 'academo' | extend TimeGenerated = now() | project TimeGenerated, source, run_id, sandbox_id, role, event_type, step_id, msg"
  }
  depends_on = [azapi_resource.table]
}
resource "azurerm_role_assignment" "ingestion" {
  scope                = azurerm_monitor_data_collection_rule.this.id
  role_definition_name = "Monitoring Metrics Publisher"
  principal_id         = azurerm_user_assigned_identity.this.principal_id
  principal_type       = "ServicePrincipal"
}

# Verified LogErrors category exposes pipeline failures without exporting payloads.
resource "azurerm_monitor_diagnostic_setting" "ingestion" {
  name                       = "sandbox-ingestion-errors"
  target_resource_id         = azurerm_monitor_data_collection_rule.this.id
  log_analytics_workspace_id = var.workspace_id
  enabled_log {
    category = "LogErrors"
  }
}
