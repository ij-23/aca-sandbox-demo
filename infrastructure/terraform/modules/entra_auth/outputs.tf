output "api_client_id" {
  value       = azuread_application.api.client_id
  description = "API audience client ID."
}
output "spa_client_id" {
  value       = azuread_application.spa.client_id
  description = "Dashboard PKCE client ID."
}
