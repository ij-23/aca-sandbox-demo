variable "stem" {
  type        = string
  description = "Project naming stem."
}
variable "resource_group_name" {
  type        = string
  description = "Existing project resource group name."
}
variable "workspace_id" {
  type        = string
  description = "Existing Log Analytics workspace ARM ID."
}
variable "location" {
  type        = string
  description = "Region shared by workspace, DCR and DCE."
}
variable "retention_days" {
  type        = number
  description = "Sandbox telemetry retention in days."
}
variable "tags" {
  type        = map(string)
  description = "Project resource tags."
}
