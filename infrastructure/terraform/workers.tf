variable "enable_public_workers" {
  type        = bool
  default     = false
  description = "Create an identity-free, credential-free group for public repository workers. Does not enable application execution."
}

# Separate group: existing coordinator group identity endpoints return HTTP 200.
# Never attach a provider connection, managed identity or direct ingestion identity.
resource "azapi_resource" "public_workers" {
  count                     = var.enable_public_workers ? 1 : 0
  type                      = "Microsoft.App/sandboxGroups@2026-07-01"
  name                      = "sbg-${local.stem}-workers"
  parent_id                 = module.resource_group.id
  location                  = var.region
  tags                      = local.tags
  body                      = { properties = {} }
  schema_validation_enabled = false
  response_export_values    = []
}

resource "azurerm_role_assignment" "public_worker_app" {
  count                = var.enable_public_workers ? 1 : 0
  scope                = azapi_resource.public_workers[0].id
  role_definition_name = "Container Apps SandboxGroup Data Owner"
  principal_id         = module.identity.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "public_worker_operator" {
  for_each             = var.enable_public_workers ? var.sandbox_operators : {}
  scope                = azapi_resource.public_workers[0].id
  role_definition_name = "Container Apps SandboxGroup Data Owner"
  principal_id         = each.value.object_id
  principal_type       = each.value.principal_type
}

output "worker_sandbox_group_name" {
  value       = var.enable_public_workers ? azapi_resource.public_workers[0].name : ""
  description = "Optional identity-free worker group; never configure provider credentials here."
}

variable "enable_public_coordinators" {
  type        = bool
  default     = false
  description = "Prepare a separate trusted coordinator group for a manually configured Copilot-only credential. Does not enable public execution."
}

module "public_coordinators" {
  count             = var.enable_public_coordinators ? 1 : 0
  source            = "./modules/sandbox_group"
  name              = "sbg-${local.stem}-analysis"
  resource_group_id = module.resource_group.id
  location          = var.region
  tags              = local.tags
}

resource "azapi_update_resource" "public_coordinator_telemetry" {
  count       = var.enable_public_coordinators ? 1 : 0
  type        = "Microsoft.App/sandboxGroups@2026-02-01-preview"
  resource_id = module.public_coordinators[0].id
  body = {
    identity = {
      type                   = "UserAssigned"
      userAssignedIdentities = { (module.sandbox_telemetry.identity_id) = {} }
    }
  }
}

resource "azurerm_role_assignment" "public_coordinator_app" {
  count                = var.enable_public_coordinators ? 1 : 0
  scope                = module.public_coordinators[0].id
  role_definition_name = "Container Apps SandboxGroup Data Owner"
  principal_id         = module.identity.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "public_coordinator_operator" {
  for_each             = var.enable_public_coordinators ? var.sandbox_operators : {}
  scope                = module.public_coordinators[0].id
  role_definition_name = "Container Apps SandboxGroup Data Owner"
  principal_id         = each.value.object_id
  principal_type       = each.value.principal_type
}

output "public_coordinator_group_name" {
  value       = var.enable_public_coordinators ? module.public_coordinators[0].name : ""
  description = "Trusted coordinator group; configure only Copilot Requests here, never GitHub publication permissions."
}
