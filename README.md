### Create vault

```shell
ansible-vault create --vault-id mikr.us.k122@prompt ./host_vars/mikr.us.k122.yml
```

### Edit vault

```shell
ansible-vault edit --vault-id mikr.us.k122@prompt ./host_vars/mikr.us.k122.yml
```

### Launch playbook

```shell
# locally
ansible-playbook ./01-access.yml \
  -l prd \
  --vault-id mikr.us.k122@prompt \
  --inventory ./inventory.yml
```

```shell
# remotely
ansible-playbook ./01-access.yml \
  -l prd \
  --vault-id mikr.us.k122@mikr.us.k122.vault_pass \
  --inventory ./inventory.yml
```

### Vault keys

* ansible_host
* ansible_port
* ansible_ssh_user
* ansible_ssh_pass
