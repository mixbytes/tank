variable "bc_count_prod_instances" {}
variable "setup_id" {}
variable "blockchain_name" {}
variable "public_key_path" {
  description = "Path to file containing public key"
  default = "~/.ssh/id_rsa.pub"
}
variable "region_zone" {
  default = "europe-west4-a"
}

provider "google" {
  credentials = "${file("/Users/alevkin/noble-district-237215-c0550dc8ff33.json")}"
  project     = "noble-district-237215"
  region      = "europe-west4"
}

resource "google_compute_instance" "tank-boot" {
  name         = "tank-${var.blockchain_name}-${var.setup_id}-boot"
  machine_type = "f1-micro" 
  zone         = "${var.region_zone}"
  tags         = ["web"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-minimal-1804-lts"
    }
  }

  // Local SSD disk
  //scratch_disk {
  //}

  network_interface {
    network = "default"

    access_config {
      // Ephemeral IP
    }
  }

  metadata {
    ssh-keys = "root:${file("${var.public_key_path}")}"
  }

  metadata_startup_script = "echo hi > /test.txt"

}