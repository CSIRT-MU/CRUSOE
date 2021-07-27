# Ansible role - Python packages #

## Role Description ##
This role serves for automatic installation of python tools used in crusoe enviroment on debian-based systems.


## How to use ##

Move the role into the `/path/to/ansible/roles` folder, so that path `/path/to/ansible/roles/crusoeComponents` exists.

### Using the role in a playbook ###

If you want to use role in a playbook, then add following lines to the play:

```
  vars:
    key_path: git/private/key/path # Key without passphrase
  roles:
    - crusoeComponents
```

so that beginning of your playbook (or one of the plays if you use multiple) looks like this:

```
- hosts: all
  vars:
    key_path: git/private/key/path # Key without passphrase
  roles:
    - crusoeComponents
```

This will ensure that python tools will be installed before running the tasks in the play(book).

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
  vars:
    key_path: git/private/key/path # Key without passphrase
  roles:
    - crusoeComponents
```

This will ensure that after vagrant builds enviroment, python tools will be already installed.
