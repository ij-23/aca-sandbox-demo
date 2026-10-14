variable "github_build_repository" {
  type        = string
  default     = null
  description = "Optional GitHub owner/repository whose main branch receives build-only AcrPush federation."
  validation {
    condition     = var.github_build_repository == null ? true : can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_build_repository))
    error_message = "Use an exact owner/repository, without URL, ref or wildcard."
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
  repository          = var.github_build_repository
}

output "github_build_client_id" {
  value       = try(module.github_build[0].client_id, null)
  description = "Optional build-only OIDC client ID for GitHub Actions. Terraform state remains local."
}
