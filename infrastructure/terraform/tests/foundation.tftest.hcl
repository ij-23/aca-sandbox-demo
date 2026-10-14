# Offline configuration tests only. No Azure calls, no cloud success claims.
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

run "bootstrap_has_no_application" {
  command = plan
  assert {
    condition     = output.application_url == ""
    error_message = "Foundation must not deploy a host image or expose an application."
  }
  assert {
    condition     = toset(output.blob_container_names) == toset(["reports", "events", "diffs", "replay"])
    error_message = "All four private artifact containers must be present."
  }
}

run "reject_invalid_retention" {
  command = plan
  variables { report_retention_days = 0 }
  expect_failures = [var.report_retention_days]
}

run "reject_operator_without_object_uuid" {
  command = plan
  variables {
    sandbox_operators = { bad = { object_id = "not-an-object-id", principal_type = "User" } }
  }
  expect_failures = [var.sandbox_operators]
}

run "reject_invalid_prefix" {
  command = plan
  variables { name_prefix = "UPPERCASE" }
  expect_failures = [var.name_prefix]
}
