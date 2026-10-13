terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm" }
  }
}

resource "azurerm_container_registry" "this" {
  name                   = var.name
  resource_group_name    = var.resource_group_name
  location               = var.location
  sku                    = var.sku
  admin_enabled          = false
  anonymous_pull_enabled = false
  role_assignment_mode   = "LegacyRegistryPermissions"
  tags                   = var.tags
}
