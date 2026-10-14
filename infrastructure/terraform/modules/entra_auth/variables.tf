variable "name" {
  type        = string
  description = "Project-specific Entra application naming stem."
}
variable "public_origin" {
  type        = string
  description = "Exact HTTPS dashboard origin used for PKCE redirect."
  validation {
    condition     = can(regex("^https://[a-z0-9.-]+$", var.public_origin))
    error_message = "Use an exact HTTPS origin without path or query."
  }
}
