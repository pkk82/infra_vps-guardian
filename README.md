### Create vault

```shell
ansible-vault create ./host_vars/mikr.us.k122.yml
```

### Edit vault

```shell
ansible-vault edit ./host_vars/mikr.us.k122.yml
```

### Launch playbook

```shell
# locally
ansible-playbook 01-access.yml \
  -l prd \
  --vault-id @prompt \
  --inventory inventory.yml
```

### Vault keys

* ansible_host
* ansible_port
* ansible_ssh_user
* ansible_ssh_pass
