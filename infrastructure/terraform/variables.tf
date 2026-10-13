variable "subscription_id" {
  type        = string
  description = "Explicit target Azure subscription."
  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$", var.subscription_id))
    error_message = "Use a UUID."
  }
}
variable "tenant_id" {
  type        = string
  description = "Entra tenant containing the deployment subscription."
  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$", var.tenant_id))
    error_message = "Use a UUID."
  }
}
variable "region" {
  type        = string
  description = "Public-cloud region supporting both ACA and Sandboxes; verify availability before applying."
  validation {
    condition     = can(regex("^[a-z][a-z0-9]+$", var.region))
    error_message = "Use an Azure region identifier."
  }
}
variable "name_prefix" {
  type        = string
  description = "Short lowercase prefix for a new dedicated deployment."
  validation {
    condition     = can(regex("^[a-z][a-z0-9]{2,11}$", var.name_prefix))
    error_message = "Use 3-12 lowercase alphanumeric characters starting with a letter."
  }
}
variable "tags" {
  type        = map(string)
  description = "Additional non-secret resource tags."
  default     = {}
}
variable "acr_sku" {
  type        = string
  description = "Application registry SKU."
  default     = "Basic"
  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "Unsupported ACR SKU."
  }
}
variable "storage_replication" {
  type        = string
  description = "Standard StorageV2 replication."
  default     = "LRS"
  validation {
    condition     = contains(["LRS", "ZRS", "GRS", "RAGRS", "GZRS", "RAGZRS"], var.storage_replication)
    error_message = "Unsupported replication."
  }
}
variable "report_retention_days" {
  type        = number
  description = "Days after last modification before asynchronous blob lifecycle deletion."
  default     = 30
  validation {
    condition     = var.report_retention_days >= 1 && var.report_retention_days <= 365 && floor(var.report_retention_days) == var.report_retention_days
    error_message = "Use an integer from 1 to 365."
  }
}
variable "log_retention_days" {
  type        = number
  description = "Common Log Analytics and Application Insights retention in days."
  default     = 30
  validation {
    condition     = contains([30, 60, 90, 120, 180, 270, 365, 550, 730], var.log_retention_days)
    error_message = "Unsupported telemetry retention."
  }
}
variable "telemetry_daily_cap_gb" {
  type        = number
  description = "Daily ingestion cap; not a hard total spending limit."
  default     = 1
  validation {
    condition     = var.telemetry_daily_cap_gb > 0
    error_message = "Daily cap must be positive."
  }
}
variable "sandbox_operators" {
  type        = map(object({ object_id = string, principal_type = string }))
  description = "Explicit Entra object IDs for credential setup and smoke testing; not app-login authorization."
  default     = {}
  validation {
    condition     = alltrue([for p in values(var.sandbox_operators) : can(regex("^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$", p.object_id)) && contains(["User", "Group", "ServicePrincipal"], p.principal_type)])
    error_message = "Operators need object UUIDs and User, Group or ServicePrincipal type."
  }
}
