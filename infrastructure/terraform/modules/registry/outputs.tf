output "id" {
  value       = azurerm_container_registry.this.id
  description = "Registry ARM ID."
}
output "login_server" {
  value       = azurerm_container_registry.this.login_server
  description = "Registry DNS name."
}
