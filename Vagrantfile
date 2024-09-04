# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # the main virtual machine
  config.vm.define "crusoe", primary: true do |alpha|
    alpha.vm.box = "debian/buster64"
    alpha.vm.box_check_update = true
    alpha.vm.provider "virtualbox" do |v|
      v.memory = 4096
      v.cpus = 2
    end

    alpha.vm.hostname = "crusoe"
    alpha.vm.network "private_network", ip: "172.18.1.10"
    alpha.vm.boot_timeout = 400

    alpha.vm.provision "ansible" do |ansible|
     ansible.verbose = "v"
     ansible.playbook = "crusoe_observe/ansible/playbook.yml"
     ansible.limit = "crusoe"
     ansible.extra_vars = 'crusoe_observe/extra-vars.yml'
    end

    alpha.vm.provision "ansible" do |ansible|
     ansible.verbose = "v"
     ansible.playbook = "crusoe_orient/ansible/playbook.yml"
     ansible.limit = "crusoe"
     ansible.extra_vars = 'crusoe_orient/extra-vars.yml'
    end

    alpha.vm.provision "ansible" do |ansible|
     ansible.verbose = "v"
     ansible.playbook = "graphql-api/ansible/playbook.yml"
     ansible.limit = "crusoe"
     ansible.extra_vars = 'graphql-api/extra-vars.yml'
    end

     alpha.vm.provision "ansible" do |ansible|
       ansible.verbose = "v"
       ansible.playbook = "crusoe_decide/ansible/playbook.yml"
       ansible.limit = "crusoe"
     end

    alpha.vm.provision "ansible" do |ansible|
     ansible.verbose = "v"
     ansible.playbook = "crusoe_act/ansible/ansible/playbook.yml"
     ansible.limit = "crusoe"
     ansible.extra_vars = 'crusoe_act/extra-vars.yml'
    end

    alpha.vm.provision "ansible" do |ansible|
     ansible.verbose = "v"
     ansible.playbook = "recommender_system/ansible/playbook.yml"
     ansible.limit = "crusoe"
     ansible.extra_vars = 'recommender_system/extra-vars.yml'
    end


    alpha.vm.network "forwarded_port", guest: 80, host: 80
    alpha.vm.network "forwarded_port", guest: 4001, host: 4001
    alpha.vm.network "forwarded_port", guest: 4200, host: 4200
    alpha.vm.network "forwarded_port", guest: 5555, host: 5555
    alpha.vm.network "forwarded_port", guest: 7474, host: 7474
    alpha.vm.network "forwarded_port", guest: 7687, host: 7687
    alpha.vm.network "forwarded_port", guest: 16005, host: 16005
  end
end
