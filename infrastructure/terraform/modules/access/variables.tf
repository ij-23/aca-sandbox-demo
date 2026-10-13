variable "app_principal_id" {
  type        = string
  description = "Host UAMI object ID; never attach to untrusted sandboxes."
}
variable "registry_id" {
  type        = string
  description = "Registry scope."
}
variable "sandbox_group_id" {
  type        = string
  description = "Sandbox Group scope."
}
variable "blob_container_ids" {
  type        = map(string)
  description = "Container scopes."
}
variable "application_insights_id" {
  type        = string
  description = "Telemetry scope."
}
variable "operators" {
  type        = map(object({ object_id = string, principal_type = string }))
  description = "Explicit operator object IDs."
}
