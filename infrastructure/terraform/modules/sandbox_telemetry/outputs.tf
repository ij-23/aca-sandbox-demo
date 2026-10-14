output "identity_id" {
  value       = azurerm_user_assigned_identity.this.id
  description = "Ingestion-only UAMI to attach to Sandbox Group."
}
output "config" {
  description = "Non-secret official Sandbox telemetryConfig."
  value = {
    endpoints = [{
      kind               = "LogAnalytics"
      data               = ["ContainerStdoutStderr"]
      dceEndpoint        = azurerm_monitor_data_collection_endpoint.this.logs_ingestion_endpoint
      dcrImmutableId     = azurerm_monitor_data_collection_rule.this.immutable_id
      tableName          = local.stream
      dynamicJsonColumns = true
      auth = {
        kind     = "ManagedIdentity"
        identity = azurerm_user_assigned_identity.this.id
      }
    }]
  }
}
