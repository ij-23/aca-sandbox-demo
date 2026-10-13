variable "name" {
  type        = string
  description = "Globally unique account name."
}
variable "resource_group_id" {
  type        = string
  description = "Parent resource group."
}
variable "replication" {
  type        = string
  description = "Standard replication."
}
variable "retention_days" {
  type        = number
  description = "Blob expiry days since modification."
}
variable "workspace_id" {
  type        = string
  description = "Diagnostic destination."
}
variable "location" {
  type        = string
  description = "Azure region."
}
variable "tags" {
  type        = map(string)
  description = "Resource tags."
}
