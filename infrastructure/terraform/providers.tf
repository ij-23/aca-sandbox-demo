terraform {
  required_version = ">= 1.11.0, < 2.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.81.0"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "~> 2.13.0"
    }
  }
}

provider "azurerm" {
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  # Planning must never register resource providers.
  resource_provider_registrations = "none"
  features {}
}

provider "azapi" {
  subscription_id            = var.subscription_id
  tenant_id                  = var.tenant_id
  skip_provider_registration = true
  disable_default_output     = true
  enable_preflight           = false
}
