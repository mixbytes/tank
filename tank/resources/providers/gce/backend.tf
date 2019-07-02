{% raw %}
variable "state_path" {}

terraform {
  backend "local" {}
}

data "terraform_remote_state" "state" {
  backend = "local"
  config {
    path = "${var.state_path}"
  }
}
{% endraw %}