output "assignment_ids" {
  value       = concat([azurerm_role_assignment.image_pull.id, azurerm_role_assignment.sandbox.id, azurerm_role_assignment.telemetry.id], [for a in azurerm_role_assignment.blob : a.id], [for a in azurerm_role_assignment.operator : a.id])
  description = "Managed RBAC IDs."
}
