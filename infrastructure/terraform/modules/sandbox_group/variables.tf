variable "name" {
  type        = string
  description = "Sandbox Group name."
}
variable "resource_group_id" {
  type        = string
  description = "Parent resource group."
}
variable "location" {
  type        = string
  description = "Azure region."
}
variable "tags" {
  type        = map(string)
  description = "Resource tags."
}
