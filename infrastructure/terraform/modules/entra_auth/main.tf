terraform {
  required_providers {
    azuread = { source = "hashicorp/azuread" }
  }
}
data "azuread_client_config" "current" {}
locals {
  scope_id = uuidv5("dns", "${var.name}.access_as_user")
}
resource "azuread_application" "api" {
  display_name     = "${var.name}-api"
  sign_in_audience = "AzureADMyOrg"
  owners           = [data.azuread_client_config.current.object_id]
  api {
    requested_access_token_version = 2
    oauth2_permission_scope {
      id                         = local.scope_id
      enabled                    = true
      type                       = "User"
      value                      = "access_as_user"
      admin_consent_display_name = "Use the Academo demo"
      admin_consent_description  = "Run the isolated trusted-fixture demo as the signed-in user."
      user_consent_display_name  = "Use the Academo demo"
      user_consent_description   = "Run the isolated trusted-fixture demo as you."
    }
  }
  lifecycle {
    ignore_changes = [identifier_uris]
  }
}
resource "azuread_application_identifier_uri" "api" {
  application_id = azuread_application.api.id
  identifier_uri = "api://${azuread_application.api.client_id}"
}
resource "azuread_service_principal" "api" {
  client_id = azuread_application.api.client_id
  owners    = [data.azuread_client_config.current.object_id]
}
resource "azuread_application" "spa" {
  display_name     = "${var.name}-dashboard"
  sign_in_audience = "AzureADMyOrg"
  owners           = [data.azuread_client_config.current.object_id]
  single_page_application {
    redirect_uris = ["${var.public_origin}/"]
  }
  required_resource_access {
    resource_app_id = azuread_application.api.client_id
    resource_access {
      id   = local.scope_id
      type = "Scope"
    }
  }
}
resource "azuread_service_principal" "spa" {
  client_id = azuread_application.spa.client_id
  owners    = [data.azuread_client_config.current.object_id]
}
