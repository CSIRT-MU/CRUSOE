# Running (building) the project using Vagrant

## Prerequisites

### Vagrant

- To check your version, run `vagrant -v` in a terminal/console window.
- To get Vagrant, go to [vagrantup.com/downloads](https://www.vagrantup.com/downloads).

### Ansible

The Vagrant Ansible provisioner allows you to provision the guest using Ansible playbooks. To get Ansible, go to [https://docs.ansible.com/ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-the-control-machine)

## Ensure credentials are configured

Before building the image, make sure that neo4j credentials are set properly. See README.md for instructions on how to set credentials.

## Running vagrant virtual machine

Run `vagrant up` to start and provision virtual machine. Afterwards, GraphQL API should be available on `http://localhost:4001/graphql`.
