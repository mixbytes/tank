{% raw %}
# user-specific settings
variable "pub_key" {
  description = "Path to file containing public key"
}
variable "pvt_key" {
  description = "Path to file containing private key"
}
variable "cred_path" {}
variable "project" {}

# test case-specific settings
variable "blockchain_name" {}

variable "region_zone" {
  default = "europe-west4-a"
}

variable "region" {
  default = "europe-west4"
}

# run-specific settings
variable "setup_id" {}


provider "google" {
  version = "~> 2.5"
  credentials = "${file("${var.cred_path}")}"
  project     = "${var.project}"
  region      = "${var.region}"
}


resource "google_compute_firewall" "default" {
  name    = "firewall"
  network = "default"

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
  }

  source_ranges = ["0.0.0.0/0"]
  source_tags = ["monitoring", "blockchain"]
}
{% endraw %}


{% macro machine_type(type) -%}
  {% if type == 'micro' %}
  machine_type = "f1-micro"
  {% elif type == 'small' %}
  machine_type = "g1-small"
  {% elif type == 'standard' %}
  machine_type = "n1-standard-1"
  {% elif type == 'large' %}
  machine_type = "n1-standard-2"
  {% elif type == 'xlarge' %}
  machine_type = "n1-standard-4"
  {% elif type == 'xxlarge' %}
  machine_type = "n1-standard-8"
  {% elif type == 'huge' %}
  machine_type = "n1-standard-16"
  {% else %}
  unsupported instance type: {{ type }}
  {% endif %}
{%- endmacro %}


# Dynamic resources
{% for name, instance_cfg in instances.items() %}
resource "google_compute_instance" "tank-{{ name }}" {
  name         = "tank-${var.blockchain_name}-${var.setup_id}-{{ name }}-${count.index}"
  count        = "{{ instance_cfg.count }}"
  {{ machine_type(instance_cfg.type) }}

{% raw %}
  zone         = "${var.region_zone}"
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
{% endraw %}
{% endfor %}
# End of dynamic resources


{% raw %}
resource "google_compute_instance" "monitoring" {
  name         = "tank-${var.blockchain_name}-${var.setup_id}-monitoring"
{% endraw %}
  {{ machine_type(monitoring_machine_type) }}
{% raw %}

  zone         = "${var.region_zone}"
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
{% endraw %}


# Dynamic output
{% for name, instance_cfg in instances.items() %}
output "{{ name }} nodes IP addresses" {
    value = "${google_compute_instance.tank-{{ name }}.*.network_interface.0.access_config.0.nat_ip}"
}
{% endfor %}
# End of dynamic output


{% raw %}
output "Monitoring instance IP address" {
    value = "${google_compute_instance.monitoring.network_interface.0.access_config.0.nat_ip}"
}

output "Blockchain name" {
    value = "${var.blockchain_name}"
}

output "Setup ID" {
    value = "${var.setup_id}"
}
{% endraw %}
