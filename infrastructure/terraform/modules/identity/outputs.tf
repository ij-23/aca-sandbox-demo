output "id" {
  value       = azurerm_user_assigned_identity.this.id
  description = "Identity ARM ID."
}
output "client_id" {
  value       = azurerm_user_assigned_identity.this.client_id
  description = "Identity client ID."
}
output "principal_id" {
  value       = azurerm_user_assigned_identity.this.principal_id
  description = "Identity object ID."
}
