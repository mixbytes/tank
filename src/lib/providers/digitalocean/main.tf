variable "do_token" {}
variable "pub_key" {}
variable "pvt_key" {}
variable "ssh_fingerprint" {}
variable "bc_count_prod_instances" {}
variable "setup_id" {}
variable "blockchain_name" {}
variable "instance_type_count" {
  type = "map"
  default = {
    "boot" = "1"
    "producer" = "1"
    "fullnode" = "0"
    "monitoring" = "1"
  }
}

provider "digitalocean" {
  version = "~> 1.1"
  token = "${var.do_token}"
}

resource "digitalocean_droplet" "tank-boot" {
    image = "docker-18-04"
    name = "tank-${var.blockchain_name}-${var.setup_id}-boot"
    count = "${var.instance_type_count["boot"]}"
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
    image = "docker-18-04"
    name = "tank-${var.blockchain_name}-${var.setup_id}-producer-${count.index}"
    count = "${var.instance_type_count["producer"]}"
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

resource "digitalocean_droplet" "tank-fullnode" {
  image = "docker-18-04"
  name = "tank-${var.blockchain_name}-${var.setup_id}-fullnode-${count.index}"
  count = "${var.instance_type_count["fullnode"]}"
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
    image = "docker-18-04"
    name = "tank-${var.blockchain_name}-${var.setup_id}-monitoring"
    count = "${var.instance_type_count["monitoring"]}"
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
    value = "${digitalocean_droplet.tank-boot.*.ipv4_address}"
}

output "Producers nodes IP addresses" {
    value = "${digitalocean_droplet.tank-producer.*.ipv4_address}"
}

output "Full nodes IP addresses" {
  value = "${digitalocean_droplet.tank-fullnode.*.ipv4_address}"
}

output "Monitoring instance IP address" {
    value = "${digitalocean_droplet.tank-monitoring.*.ipv4_address}"
}

output "Blockchain name" {
    value = "${var.blockchain_name}"
}

output "Setup ID" {
    value = "${var.setup_id}"
}
