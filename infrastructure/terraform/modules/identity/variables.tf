variable "name" {
  type        = string
  description = "Host identity name."
}
variable "resource_group_name" {
  type        = string
  description = "Resource group."
}
variable "location" {
  type        = string
  description = "Azure region."
}
variable "tags" {
  type        = map(string)
  description = "Resource tags."
}
