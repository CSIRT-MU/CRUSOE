# Ansible role - Neo4j - graph database version 3.4.7 #

## Role Description ##
This role serves for automatic installation of neo4j 3.4.7 on debian-based systems.


## How to use ##

Move the role into the `/path/to/ansible/roles` folder, so that path `/path/to/ansible/roles/neo4j` exists.

### Using the role in a playbook ###

If you want to use role in a playbook, then add following lines to the play:

```
  roles:
    - neo4j
```

so that beginning of your playbook (or one of the plays if you use multiple) looks like this:

```
- hosts: all
  roles:
    - neo4j
```

This will ensure that neo4j 3.4.7 will be installed before running the tasks in the play(book).

## Using the role with vagrant ##

If you want to use role in a vagrant enviroment, then your Vagrantfile should contain path to playbook:

```
config.vm.define "name_of_vm" do |name_of_vm|
        name_of_vm.vm.provision "ansible" do |ansible|
	    # where is the playbook located
            ansible.playbook = "path/to/playbook/playbook.yml"
        end
    end
```

While you playbook looks like this:

```
- hosts: all
  roles:
    - neo4j
```

This will ensure that after vagrant builds enviroment, neo4j 3.4.7 will already be installed.
