resource "digitalocean_droplet" "test-cyberos-boot" {
    image = "ubuntu-18-04-x64"
    name = "test-${var.setup_id}-cyberos-boot"
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

resource "digitalocean_droplet" "test-cyberos-producer" {
    image = "ubuntu-18-04-x64"
    name = "test-${var.setup_id}-cyberos-producer-${count.index}"
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

resource "digitalocean_droplet" "test-cyberos-monitoring" {
    image = "ubuntu-18-04-x64"
    name = "test-${var.setup_id}-cyberos-monitoring"
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

output "boot_ip" {
    value = "${digitalocean_droplet.test-cyberos-boot.ipv4_address}"
}

output "producer_ip" {
    value = "${digitalocean_droplet.test-cyberos-producer.*.ipv4_address}"
}

output "monitoring_ip" {
    value = "${digitalocean_droplet.test-cyberos-monitoring.ipv4_address}"
}

output "setup_id" {
    value = "${var.setup_id}"
}
