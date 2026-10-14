terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm" }
    azapi   = { source = "Azure/azapi" }
  }
}

# Stable contract. Do not insert undocumented rich-preview defaults here.
# Limits and persistent egress remain gated compatibility items.
resource "azapi_resource" "this" {
  type      = "Microsoft.App/sandboxGroups@2026-07-01"
  name      = var.name
  parent_id = var.resource_group_id
  location  = var.location
  tags      = var.tags
  body      = { properties = {} }
  # AzAPI 2.13.0 has no embedded schema for this documented ARM resource.
  # The body is deliberately the minimal published 2026-07-01 contract.
  # See docs/compatibility.md: terraform validate cannot prove service support.
  schema_validation_enabled = false
  response_export_values    = []
  # The preview identity PATCH is the sole owner of this property. Stable
  # creation must not remove the telemetry identity on subsequent full plans.
  lifecycle {
    ignore_changes = [identity]
  }
}
