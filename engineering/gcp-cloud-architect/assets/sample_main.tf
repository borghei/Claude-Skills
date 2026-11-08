# Deliberately flawed Terraform for gcp_architecture_validator.py (exit 1).
resource "google_compute_instance" "bastion" {
  name         = "bastion"
  machine_type = "e2-small"
  zone         = "us-central1-a"
  boot_disk {
    initialize_params { image = "debian-cloud/debian-12" }
  }
  network_interface {
    network = "default"
    access_config {}
  }
}

resource "google_project_iam_member" "ci_editor" {
  project = "acme-prod"
  role    = "roles/editor"
  member  = "serviceAccount:ci@acme-prod.iam.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "public_assets" {
  bucket = "acme-assets"
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_service_account_key" "ci_key" {
  service_account_id = "ci@acme-prod.iam.gserviceaccount.com"
}
