variable "name" {
  type        = string
  description = "Globally unique registry name."
}
variable "resource_group_name" {
  type        = string
  description = "Resource group."
}
variable "sku" {
  type        = string
  description = "Registry SKU."
}
variable "location" {
  type        = string
  description = "Azure region."
}
variable "tags" {
  type        = map(string)
  description = "Resource tags."
}
