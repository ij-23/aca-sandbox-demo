locals {
  suffix = substr(sha256("${lower(var.subscription_id)}/${var.name_prefix}"), 0, 8)
  stem   = "${var.name_prefix}-${local.suffix}"
  tags   = merge(var.tags, { project = "aca-sandbox-demo", managed_by = "terraform" })
}
module "resource_group" {
  source   = "./modules/resource_group"
  name     = "rg-${local.stem}"
  location = var.region
  tags     = local.tags
}
module "identity" {
  source              = "./modules/identity"
  name                = "id-${local.stem}"
  resource_group_name = module.resource_group.name
  location            = var.region
  tags                = local.tags
}
module "registry" {
  source              = "./modules/registry"
  name                = "acr${var.name_prefix}${local.suffix}"
  resource_group_name = module.resource_group.name
  sku                 = var.acr_sku
  location            = var.region
  tags                = local.tags
}
module "monitoring" {
  source              = "./modules/monitoring"
  stem                = local.stem
  resource_group_name = module.resource_group.name
  resource_group_id   = module.resource_group.id
  retention_days      = var.log_retention_days
  daily_cap_gb        = var.telemetry_daily_cap_gb
  location            = var.region
  tags                = local.tags
}
module "storage" {
  source            = "./modules/storage"
  name              = "st${var.name_prefix}${local.suffix}"
  resource_group_id = module.resource_group.id
  replication       = var.storage_replication
  retention_days    = var.report_retention_days
  workspace_id      = module.monitoring.workspace_id
  location          = var.region
  tags              = local.tags
}
module "sandbox_group" {
  source            = "./modules/sandbox_group"
  name              = "sbg-${local.stem}"
  resource_group_id = module.resource_group.id
  location          = var.region
  tags              = local.tags
}
module "access" {
  source                  = "./modules/access"
  app_principal_id        = module.identity.principal_id
  registry_id             = module.registry.id
  sandbox_group_id        = module.sandbox_group.id
  blob_container_ids      = module.storage.container_ids
  application_insights_id = module.monitoring.application_insights_id
  operators               = var.sandbox_operators
}

module "application" {
  count               = var.application == null ? 0 : 1
  source              = "./modules/application"
  name                = "ca-${local.stem}"
  resource_group_name = module.resource_group.name
  environment_id      = module.monitoring.environment_id
  identity_id         = module.identity.id
  registry_server     = module.registry.login_server
  image               = var.application.image
  tags                = local.tags
  environment = {
    TENANT_ID                  = var.tenant_id
    API_CLIENT_ID              = var.application.api_client_id
    SPA_CLIENT_ID              = var.application.spa_client_id
    AUTHORIZED_USERS           = join(",", sort(tolist(var.application.authorized_users)))
    ALLOWED_REPOSITORIES       = join(",", sort(tolist(var.application.allowed_repositories)))
    STORAGE_ACCOUNT            = module.storage.name
    MANAGED_IDENTITY_CLIENT_ID = module.identity.client_id
    SUBSCRIPTION_ID            = var.subscription_id
    RESOURCE_GROUP             = module.resource_group.name
    SANDBOX_GROUP              = module.sandbox_group.name
    CREDENTIAL_CONNECTION_ID   = var.application.credential_connection_id
    REGION                     = var.region
    PUBLIC_ORIGIN              = var.application.public_origin
    PUBLICATION_OWNER          = var.application.publication_owner
    LIVE_EXECUTION_ENABLED     = tostring(var.application.live_execution_enabled)
    PUBLICATION_ENABLED        = tostring(var.application.publication_enabled)
  }
  depends_on = [module.access]
}
