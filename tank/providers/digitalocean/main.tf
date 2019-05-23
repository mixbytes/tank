variable "token" {}
variable "pub_key" {}
variable "pvt_key" {}
variable "ssh_fingerprint" {}
variable "bc_count_prod_instances" {}
variable "setup_id" {}
variable "blockchain_name" {}

provider "digitalocean" {
  version = "~> 1.1"
  token = "${var.token}"
}

resource "digitalocean_droplet" "tank-boot" {
    image = "ubuntu-18-04-x64"
    name = "tank-${var.blockchain_name}-${var.setup_id}-boot"
    region = "fra1"
    size = "512mb"
    private_networking = true
    ssh_keys = [
      "${var.ssh_fingerprint}"
    ]
    connection {
      user = "root"
      type = "ssh"
      private_key = "${file(var.pvt_key)}"
      timeout = "10m"
  }
  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
    ]
  }
}

resource "digitalocean_droplet" "tank-producer" {
    image = "ubuntu-18-04-x64"
    name = "tank-${var.blockchain_name}-${var.setup_id}-producer-${count.index}"
    count = "${var.bc_count_prod_instances}"
    region = "fra1"
    size = "512mb"
    private_networking = true
    ssh_keys = [
      "${var.ssh_fingerprint}"
    ]
    connection {
      user = "root"
      type = "ssh"
      private_key = "${file(var.pvt_key)}"
      timeout = "10m"
  }
  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
    ]
  }
}

resource "digitalocean_droplet" "tank-monitoring" {
    image = "ubuntu-18-04-x64"
    name = "tank-${var.blockchain_name}-${var.setup_id}-monitoring"
    region = "fra1"
    size = "2gb"
    private_networking = true
    ssh_keys = [
      "${var.ssh_fingerprint}"
    ]
    connection {
      user = "root"
      type = "ssh"
      private_key = "${file(var.pvt_key)}"
      timeout = "10m"
  }
  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
    ]
  }
}

output "Boot node IP address" {
    value = "${digitalocean_droplet.tank-boot.ipv4_address}"
}

output "Producers nodes IP addresses" {
    value = "${digitalocean_droplet.tank-producer.*.ipv4_address}"
}

output "Monitoring instance IP address" {
    value = "${digitalocean_droplet.tank-monitoring.ipv4_address}"
}

output "Blockchain name" {
    value = "${var.blockchain_name}"
}

output "Setup ID" {
    value = "${var.setup_id}"
}
