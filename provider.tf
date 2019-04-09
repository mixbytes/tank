variable "do_token" {}
variable "pub_key" {}
variable "pvt_key" {}
variable "ssh_fingerprint" {}
variable "bc_count_prod_instances" {}
variable "setup_id" {}

provider "digitalocean" {
  token = "${var.do_token}"
}
