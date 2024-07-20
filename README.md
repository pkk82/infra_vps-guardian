# VPS Guardian

Ansible orchestrating my VPS.

## Vault

### Create vaults

```shell
ansible-vault create --vault-id mikr.us.k122@prompt ./host_vars/mikr.us.k122.yml
ansible-vault create --vault-id all@prompt ./group_vars/all.yml
```

### Edit vault

```shell
ansible-vault edit --vault-id mikr.us.k122@prompt ./host_vars/mikr.us.k122.yml
ansible-vault edit --vault-id all@prompt ./group_vars/all.yml
```

### Vault keys

#### Host
* ansible_host
* ansible_port
* ansible_ssh_user
* ansible_ssh_pass
* certificate_subject
* certificate_email
* ip
* domain

#### Group

* root_ca_crt_path
* root_ca_crt_content
* root_ca_key_content
* root_ca_key_passphrase
* pg_version

## Playbooks

### Launch playbook

```shell
# locally
ansible-playbook ./01-access.yml \
  -l prd \
  --vault-id mikr.us.k122@.mikr.us.k122.vault_pass \
  --vault-id all@.all.vault_pass \
  --inventory ./inventory.yml
```

```shell
# locally via act (installed as gh extension)
# gh extension install https://github.com/nektos/gh-act
gh act \
  -P ubuntu-latest=-self-hosted \ 
  -W .github/workflows/access.yml \
  -s VAULT_PASS_ALL \
  -s VAULT_PASS_MIKR_US_K122
```



```shell
# remotely
ansible-playbook ./01-access.yml \
  -l prd \
  --vault-id mikr.us.k122@.mikr.us.k122.vault_pass \
  --vault-id all@.all.vault_pass \
  --inventory ./inventory.yml
```

## CI

Define secrets for the repository in GitHub for vaults:

* `VAULT_PASS_ALL`
* `VAULT_PASS_MIKR_US_K122`

[Creating secrets for a repository](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository)
