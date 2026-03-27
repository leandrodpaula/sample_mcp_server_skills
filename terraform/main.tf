# Habilitando a API do Cloud Run
resource "google_project_service" "cloud_run" {
  project = var.project_id
  service = "run.googleapis.com"

  disable_on_destroy = false
}

# Deploy do serviço no Cloud Run
resource "google_cloud_run_v2_service" "default" {
  name     = "${var.service_name}-cloud-run-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"
  project  = var.project_id

  template {
    max_instance_request_concurrency = 50
    service_account                  = google_service_account.component_sa.email
    execution_environment            = "EXECUTION_ENVIRONMENT_GEN2"

    volumes {
      name = "gcs-fuse-data"
      gcs {
        bucket    = google_storage_bucket.app_data.name
        read_only = false
      }
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${data.google_artifact_registry_repository.registry.repository_id}/${var.service_name}:${var.image_tag}"

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "SERVER_PORT"
        value = "8000"
      }

      env {
        name  = "MCP_TRANSPORT"
        value = "http"
      }

      env {
        name  = "PATH_SKILLS"
        value = "/app/data/skills"
      }

      env {
        name  = "PATH_DOCS"
        value = "/app/data/docs"
      }

      ports {
        container_port = 8000
      }

      resources {
        cpu_idle          = true
        startup_cpu_boost = true
        limits = {
          cpu    = "1"
          memory = "1024Mi" # Memory increased to accommodate gcs fuse
        }
      }

      volume_mounts {
        name       = "gcs-fuse-data"
        mount_path = "/app/data"
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
  }

  depends_on = [google_project_service.cloud_run]
}

resource "google_cloud_run_v2_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.default.location
  name     = google_cloud_run_v2_service.default.name
  project  = google_cloud_run_v2_service.default.project
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.component_sa.email}"
}

# Permissao publica
resource "google_cloud_run_v2_service_iam_member" "public" {
  location = google_cloud_run_v2_service.default.location
  name     = google_cloud_run_v2_service.default.name
  project  = google_cloud_run_v2_service.default.project
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_url" {
  value       = google_cloud_run_v2_service.default.uri
  description = "A URL pública do MCP Server"
}
