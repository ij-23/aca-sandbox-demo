output "id" {
  value       = azapi_resource.account.id
  description = "Storage ARM ID."
}
output "name" {
  value       = azapi_resource.account.name
  description = "Storage name."
}
output "container_ids" {
  value       = { for name, container in azapi_resource.container : name => container.id }
  description = "Container-scoped RBAC IDs."
}
