variable "name" {
  type        = string
  description = "Container App name."
}
variable "resource_group_name" {
  type        = string
  description = "Existing foundation resource group."
}
variable "environment_id" {
  type        = string
  description = "Foundation Managed Environment ARM ID."
}
variable "identity_id" {
  type        = string
  description = "Foundation UAMI ARM ID for host and ACR pull."
}
variable "registry_server" {
  type        = string
  description = "Application ACR login server."
}
variable "image" {
  type        = string
  description = "Already-pushed application image pinned to its registry digest."
  validation {
    condition     = can(regex("^[a-z0-9.]+/[a-z0-9/_-]+@sha256:[a-f0-9]{64}$", var.image))
    error_message = "Use an existing registry image digest, never latest or a placeholder."
  }
}
variable "cpu" {
  type        = number
  description = "Application Consumption vCPU."
  default     = 0.5
  validation {
    condition     = contains([0.25, 0.5, 0.75, 1], var.cpu)
    error_message = "Use a supported MVP CPU size."
  }
}
variable "memory" {
  type        = string
  description = "Memory matching the Consumption CPU tier."
  default     = "1Gi"
}
variable "environment" {
  type        = map(string)
  description = "Non-secret runtime configuration; never provider tokens."
  validation {
    condition     = alltrue([for k in keys(var.environment) : !can(regex("(?i)token|password|secret|key", k))])
    error_message = "Credential values are forbidden in app environment configuration."
  }
}
variable "tags" {
  type        = map(string)
  description = "Consistent deployment tags."
}
