#!/bin/bash

# Function to check if a command is available on the system
check_command() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Ansible is installed
if ! check_command "ansible"; then
    echo "Ansible is not installed. Checkout \"https://docs.ansible.com/ansible/latest/installation_guide/index.html\""
    exit 1
fi

# Check if Vagrant is installed
if ! check_command "vagrant"; then
    echo "Vagrant is not installed. Checkout \"https://developer.hashicorp.com/vagrant/docs/installation\""
    exit 1
fi

# Check if Virtulbox is installed
if ! check_command "virtualbox"; then
    echo "Virtualbox is not installed. Checkout \"https://www.virtualbox.org/wiki/Downloads\""
    exit 1
fi

vagrantfile="Vagrantfile"

# Check if master Vagrantfile exist in current workdir
if [ -f $vagrantfile ]; then
    # Run vagrant
    vagrant up
else
    echo "$vagrantfile does not exist! For successful installation you should not delete or modify provided $vagrantfile." 1>&2
    exit 1
fi