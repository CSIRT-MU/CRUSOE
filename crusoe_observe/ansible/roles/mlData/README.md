# Ansible role - Machine Learning Data #

## Role Description ##
This role serves for automatic download of machine learning data used in crusoe enviroment.

## How to use ##
Move the role into the `/path/to/ansible/roles` folder, so that path `/path/to/ansible/roles/mlData` exists.

### Using the role in a playbook ###

If you want to use role in a playbook, then add following lines to the play:

```
  roles:
    - mlData
```

so that beginning of your playbook (or one of the plays if you use multiple) looks like this:

```
- hosts: all
  vars:
    ml_data_path: /usr/share/crusoe/ # Where to store ML data
    ml_model_path: /var/tmp/crusoe/ # Where to store ML models
  roles:
    - mlData
```

This will ensure that mlData will be installed before running the tasks in the play(book).

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
    ml_data_path: /usr/share/crusoe/ # Where to store ML data
    ml_model_path: /var/tmp/crusoe/ # Where to store ML models
  roles:
    - mlData
```

This will ensure that after vagrant builds enviroment, mlData will be already installed.
