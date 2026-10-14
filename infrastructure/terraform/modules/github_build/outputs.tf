output "client_id" {
  value       = azurerm_user_assigned_identity.this.client_id
  description = "Non-secret GitHub OIDC build identity client ID."
}
