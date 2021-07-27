# Running (building) the project using Vagrant

## Prerequisites

### Vagrant

- To check your version, run `vagrant -v` in a terminal/console window.
- To get Vagrant, go to [vagrantup.com/downloads](https://www.vagrantup.com/downloads).

### Ansible

The Vagrant Ansible provisioner allows you to provision the guest using Ansible playbooks. To get Ansible, go to [https://docs.ansible.com/ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-the-control-machine)

## Ensure API endpoints are set correctly

Before running `vagrant up`, make sure that file `ansible/playbook.yml` contains proper API urls.

## Running vagrant virtual machine

Run `vagrant up` to start and provision virtual machine. Afterwards, application should be available on `http://localhost:4200/`.
