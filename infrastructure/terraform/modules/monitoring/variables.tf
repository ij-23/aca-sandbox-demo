variable "stem" {
  type        = string
  description = "Name stem."
}
variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}
variable "resource_group_id" {
  type        = string
  description = "Resource group ID."
}
variable "retention_days" {
  type        = number
  description = "Telemetry retention."
}
variable "daily_cap_gb" {
  type        = number
  description = "Daily ingestion cap."
}
variable "location" {
  type        = string
  description = "Azure region."
}
variable "tags" {
  type        = map(string)
  description = "Resource tags."
}
