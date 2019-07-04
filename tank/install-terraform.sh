#!/usr/bin/env bash

set -eu


if ! which wget >/dev/null; then
    sudo apt-get install -y wget
fi

if ! which unzip >/dev/null; then
    sudo apt-get install -y unzip
fi

if [[ ! -x /usr/local/bin/terraform ]]; then
    TER_VER="0.11.13"
    wget https://releases.hashicorp.com/terraform/${TER_VER}/terraform_${TER_VER}_linux_amd64.zip
    unzip terraform_${TER_VER}_linux_amd64.zip
    rm terraform_${TER_VER}_linux_amd64.zip
    sudo mv terraform /usr/local/bin/
fi

if [[ ! -x /usr/local/bin/terraform-inventory ]]; then
    terraform_inventory_ver="v0.8"
    wget https://github.com/adammck/terraform-inventory/releases/download/${terraform_inventory_ver}/terraform-inventory_${terraform_inventory_ver}_linux_amd64.zip
    unzip terraform-inventory_${terraform_inventory_ver}_linux_amd64.zip
    rm terraform-inventory_${terraform_inventory_ver}_linux_amd64.zip
    sudo mv terraform-inventory /usr/local/bin/
fi
