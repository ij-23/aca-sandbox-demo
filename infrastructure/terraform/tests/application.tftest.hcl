# Offline provider doubles; this is not deployment validation.
mock_provider "azurerm" {}
mock_provider "azapi" {}
mock_provider "azuread" {}
variables {
  entra_public_origin = null
  application         = null
  subscription_id     = "11111111-1111-1111-1111-111111111111"
  tenant_id           = "22222222-2222-2222-2222-222222222222"
  region              = "eastus2"
  name_prefix         = "unittest"
}
run "application_requires_authorized_users" {
  command = plan
  variables {
    application = {
      image                    = "example.azurecr.io/app@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      api_client_id            = "33333333-3333-3333-3333-333333333333"
      spa_client_id            = "44444444-4444-4444-4444-444444444444"
      authorized_users         = []
      allowed_repositories     = ["https://github.com/example/fixture"]
      credential_connection_id = "55555555-5555-5555-5555-555555555555"
      publication_owner        = "example"
      public_origin            = "https://example.azurecontainerapps.io"
    }
  }
  expect_failures = [var.application]
}
