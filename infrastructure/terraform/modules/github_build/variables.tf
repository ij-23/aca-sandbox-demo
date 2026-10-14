variable "name" {
  type        = string
  description = "Build-only managed identity name."
}
variable "resource_group_name" {
  type        = string
  description = "Existing project resource group."
}
variable "location" {
  type        = string
  description = "Azure region for the build identity."
}
variable "tags" {
  type        = map(string)
  description = "Project resource tags."
}
variable "registry_id" {
  type        = string
  description = "Exact project registry ARM scope for AcrPush."
}
variable "subject" {
  type        = string
  description = "Exact verified GitHub OIDC subject for this repository's main branch."
}
