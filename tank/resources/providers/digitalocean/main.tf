{% raw %}
# user-specific settings
variable "token" {}
variable "pvt_key" {}
variable "ssh_fingerprint" {}
variable "scripts_path" {}

# test case-specific settings
variable "blockchain_name" {}

# run-specific settings
variable "setup_id" {}

provider "digitalocean" {
  version = "~> 1.1"
  token = "${var.token}"
}
{% endraw %}


{% macro machine_type(type) -%}
  {% if type == 'micro' %}
  size = "512mb"
  {% elif type == 'small' %}
  size = "2gb"
  {% elif type == 'standard' %}
  size = "4gb"
  {% elif type == 'large' %}
  size = "8gb"
  {% elif type == 'xlarge' %}
  size = "16gb"
  {% elif type == 'xxlarge' %}
  size = "32gb"
  {% elif type == 'huge' %}
  size = "64gb"
  {% else %}
  unsupported instance type: {{ type }}
  {% endif %}
{%- endmacro %}


# Dynamic resources
{% for name, instance_configs in instances.items() %}
{% for cfg in instance_configs %}

resource "digitalocean_droplet" "tank-{{ name }}-{{ loop.index }}" {
    image = "ubuntu-18-04-x64"
    name = "tank-${var.blockchain_name}-${var.setup_id}-{{ name }}-{{ loop.index }}-${count.index}"
    count = "{{ cfg.count }}"
    {{ machine_type(cfg.type) }}
    region = "{{ cfg.region }}"

{% raw %}
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
  provisioner "file" {
    source      = "${var.scripts_path}/tank-packetloss"
    destination = "/usr/local/bin/tank-packetloss"
  }
  provisioner "remote-exec" {
    inline = [
      "chmod +x /usr/local/bin/tank-packetloss",
    {% endraw %}
      "/usr/local/bin/tank-packetloss add {{  cfg.packetloss }}",
    {% raw %}
    ]
  }
}
{% endraw %}

{% endfor %}
{% endfor %}
# End of dynamic resources


{% raw %}
resource "digitalocean_droplet" "tank-monitoring" {
    image = "ubuntu-18-04-x64"
    name = "tank-${var.blockchain_name}-${var.setup_id}-monitoring"
{% endraw %}
  {{ machine_type(monitoring_machine_type) }}
{% raw %}

    region = "fra1"
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
{% endraw %}


# Dynamic output
{% for name, instance_configs in instances.items() %}
{% for cfg in instance_configs %}

output "{{ name }}-{{ loop.index }} node IP addresses" {
    value = "${digitalocean_droplet.tank-{{ name }}-{{ loop.index }}.*.ipv4_address}"
}

{% endfor %}
{% endfor %}
# End of dynamic output


{% raw %}
output "Monitoring instance IP address" {
    value = "${digitalocean_droplet.tank-monitoring.ipv4_address}"
}

output "Blockchain name" {
    value = "${var.blockchain_name}"
}

output "Setup ID" {
    value = "${var.setup_id}"
}
{% endraw %}
