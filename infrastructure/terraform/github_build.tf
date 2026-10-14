variable "github_build_repository" {
  type        = string
  default     = null
  description = "Optional GitHub owner/repository whose main branch receives build-only AcrPush federation."
  validation {
    condition     = var.github_build_repository == null ? true : can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_build_repository))
    error_message = "Use an exact owner/repository, without URL, ref or wildcard."
  }
}

variable "github_build_subject" {
  type        = string
  default     = null
  description = "Optional exact OIDC subject observed in azure/login, including GitHub immutable IDs when enabled."
  validation {
    condition     = var.github_build_subject == null ? true : can(regex("^repo:[A-Za-z0-9_.@-]+/[A-Za-z0-9_.@-]+:ref:refs/heads/main$", var.github_build_subject))
    error_message = "Subject must identify one exact repository main branch, without wildcards."
  }
}

module "github_build" {
  count               = var.github_build_repository == null ? 0 : 1
  source              = "./modules/github_build"
  name                = "id-${local.stem}-github-build"
  resource_group_name = module.resource_group.name
  location            = var.region
  tags                = local.tags
  registry_id         = module.registry.id
  subject             = coalesce(var.github_build_subject, "repo:${coalesce(var.github_build_repository, "disabled/disabled")}:ref:refs/heads/main")
}

output "github_build_client_id" {
  value       = try(module.github_build[0].client_id, null)
  description = "Optional build-only OIDC client ID for GitHub Actions. Terraform state remains local."
}
