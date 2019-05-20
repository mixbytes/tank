variable "bc_count_prod_instances" {}
variable "setup_id" {}
variable "blockchain_name" {}
variable "pub_key" {
  description = "Path to file containing public key"
  default = "~/.ssh/id_rsa.pub"
}
variable "pvt_key" {
  description = "Path to file containing private key"
  default = "~/.ssh/id_rsa"
}
variable "gce_cred_path" {
  default = "~/.ssh/gce.json"
}
variable "gce_project" {}
variable "gce_region_zone" {
  default = "europe-west4-a"
}

variable "gce_region" {
  default = "europe-west4"
}

variable "gce_machine_type" {
  default = "f1-micro"
}

provider "google" {
  version = "~> 2.5"
  credentials = "${file("${var.gce_cred_path}")}"
  project     = "${var.gce_project}"
  region      = "${var.gce_region}"
}

resource "google_compute_instance" "tank-boot" {
  name         = "tank-${var.blockchain_name}-${var.setup_id}-boot"
  machine_type = "${var.gce_machine_type}"
  zone         = "${var.gce_region_zone}"
  tags         = ["blockchain"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-minimal-1804-lts"
    }
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral IP
    }
  }

  metadata {
    ssh-keys = "root:${file("${var.pub_key}")}"
  }

  //metadata_startup_script = "echo hi > /root/hello.txt"
  provisioner "remote-exec" {
    connection {
        user = "root"
        type = "ssh"
        private_key = "${file(var.pvt_key)}"
        timeout = "10m"
    }
    inline = [
      "export PATH=$PATH:/usr/bin",
    ]
  }
}

resource "google_compute_instance" "tank-producer" {
  name         = "tank-${var.blockchain_name}-${var.setup_id}-producer-${count.index}"
  machine_type = "${var.gce_machine_type}"
  zone         = "${var.gce_region_zone}"
  tags         = ["blockchain"]
  count        = "${var.bc_count_prod_instances}"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-minimal-1804-lts"
    }
  }

  network_interface {
    network = "default"

    access_config {
      nat_ip = ""
      // Ephemeral IP
    }
  }

  metadata {
    ssh-keys = "root:${file("${var.pub_key}")}"
  }

  //metadata_startup_script = "echo hi > /root/hello.txt"

  provisioner "remote-exec" {
    connection {
        user = "root"
        type = "ssh"
        private_key = "${file(var.pvt_key)}"
        timeout = "10m"
    }
    inline = [
      "export PATH=$PATH:/usr/bin",
    ]
  }
}

resource "google_compute_firewall" "default" {
  name    = "monitoring-firewall"
  network = "default"

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["9090", "3000", "80"]
  }

  source_ranges = ["0.0.0.0/0"]
  source_tags = ["monitoring", "blockchain"]
}

resource "google_compute_instance" "monitoring" {
  name         = "tank-${var.blockchain_name}-${var.setup_id}-monitoring"
  machine_type = "${var.gce_machine_type}"
  zone         = "${var.gce_region_zone}"
  tags         = ["monitoring"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-minimal-1804-lts"
    }
  }

  network_interface {
    network = "default"

    access_config {
      nat_ip = ""
      //nat_ip = "${google_compute_instance.monitoring.network_interface.0.access_config.0.nat_ip}"
    }
  }

  metadata {
    ssh-keys = "root:${file("${var.pub_key}")}"
  }

  //metadata_startup_script = "echo hi > /root/hello.txt"

  provisioner "remote-exec" {
    connection {
        user = "root"
        type = "ssh"
        private_key = "${file(var.pvt_key)}"
        timeout = "10m"
    }
    inline = [
      "export PATH=$PATH:/usr/bin",
    ]
  }
}

output "Boot node IP address" {
    value = "${google_compute_instance.tank-boot.network_interface.0.access_config.0.nat_ip}"
}

output "Producers nodes IP addresses" {
    value = "${google_compute_instance.tank-producer.*.network_interface.0.access_config.0.nat_ip}"
}

output "Monitoring instance IP address" {
    value = "${google_compute_instance.monitoring.network_interface.0.access_config.0.nat_ip}"
}

output "Blockchain name" {
    value = "${var.blockchain_name}"
}

output "Setup ID" {
    value = "${var.setup_id}"
}
