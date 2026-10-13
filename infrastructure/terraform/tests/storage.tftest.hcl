mock_provider "azurerm" {}
mock_provider "azapi" {}

run "storage_security_contract" {
  command = plan
  module { source = "./modules/storage" }
  variables {
    name              = "stunittest123"
    resource_group_id = "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-test"
    location          = "eastus2"
    tags              = {}
    replication       = "LRS"
    retention_days    = 30
    workspace_id      = "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-test/providers/Microsoft.OperationalInsights/workspaces/log-test"
  }
  assert {
    condition = (
      azapi_resource.account.body.properties.allowSharedKeyAccess == false &&
      azapi_resource.account.body.properties.allowBlobPublicAccess == false &&
      azapi_resource.account.body.properties.supportsHttpsTrafficOnly == true &&
      azapi_resource.account.body.properties.minimumTlsVersion == "TLS1_2"
    )
    error_message = "Storage must require Entra/HTTPS and reject public blobs."
  }
  assert {
    condition     = alltrue([for c in azapi_resource.container : c.body.properties.publicAccess == "None"])
    error_message = "Every container must remain private."
  }
  assert {
    condition     = azapi_resource.retention.body.properties.policy.rules[0].definition.actions.baseBlob.delete.daysAfterModificationGreaterThan == 30
    error_message = "Lifecycle retention must cover reports/events/diffs/replay."
  }
}
