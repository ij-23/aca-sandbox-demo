terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm" }
  }
}
# The app validates delegated Entra JWTs itself. MSAL uses authorization code +
# PKCE; no EasyAuth implicit login/client secret or trusted proxy-header shortcut.
resource "azurerm_container_app" "this" {
  name                         = var.name
  resource_group_name          = var.resource_group_name
  container_app_environment_id = var.environment_id
  revision_mode                = "Single"
  tags                         = var.tags
  identity {
    type         = "UserAssigned"
    identity_ids = [var.identity_id]
  }
  registry {
    server   = var.registry_server
    identity = var.identity_id
  }
  ingress {
    external_enabled           = true
    target_port                = 8000
    transport                  = "http"
    allow_insecure_connections = false
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
  template {
    min_replicas                     = 1
    max_replicas                     = 1
    termination_grace_period_seconds = 120
    container {
      name   = "application"
      image  = var.image
      cpu    = var.cpu
      memory = var.memory
      dynamic "env" {
        for_each = var.environment
        content {
          name  = env.key
          value = env.value
        }
      }
      startup_probe {
        transport               = "HTTP"
        port                    = 8000
        path                    = "/api/healthz"
        interval_seconds        = 5
        timeout                 = 3
        failure_count_threshold = 30
      }
      liveness_probe {
        transport        = "HTTP"
        port             = 8000
        path             = "/api/healthz"
        interval_seconds = 30
        timeout          = 3
      }
      readiness_probe {
        transport               = "HTTP"
        port                    = 8000
        path                    = "/api/readyz"
        interval_seconds        = 10
        timeout                 = 5
        failure_count_threshold = 12
      }
    }
  }
}
