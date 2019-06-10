#!/usr/bin/env bash
sudo apt-get install -y wget unzip
export TER_VER="0.11.13"
wget https://releases.hashicorp.com/terraform/${VER}/terraform_${VER}_linux_amd64.zip
unzip terraform_${VER}_linux_amd64.zip
sudo mv terraform /usr/local/bin/
export terraform_inventory_ver="v0.8"
wget https://github.com/adammck/terraform-inventory/releases/download/${terraform_inventory_ver}/terraform-inventory_${terraform_inventory_ver}_linux_amd64.zip terraform-inventory.zip
unzip terraform-inventory_v0.8_linux_amd64.zip
sudo mv terraform-inventory /usr/local/bin/
