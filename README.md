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
* origin_crt_path
* origin_crt_content
* origin_key_content

#### Group

* root_ca_crt_path
* root_ca_crt_content
* root_ca_key_content
* root_ca_key_passphrase
* pg_version
* pg_port
* pg_hba_path
* pg_conf_path
* pg_backup_output_dir
* pg_home_dir
* dropbox_pg_backuper_app_key
* dropbox_pg_backuper_app_secret
* dropbox_pg_backuper_refresh_token
* docker_registry_url
* docker_registry_username
* docker_registry_password

and PostgreSQL user passwords

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

## Dropbox

In order to access Dropbox, you need to create an app in the [Dropbox App Console](https://www.dropbox.com/developers/apps).


To generate offline refresh token 

1. Visit [OAuth2 Auth Endpoint](https://www.dropbox.com/oauth2/authorize?client_id=YOUR_APP_KEY&response_type=code&token_access_type=offline)
and replace `YOUR_APP_KEY` with the app key from the app settings.
2. Execute the following command in the terminal (replace `YOUR_APP_KEY` and `ACCESS_CODE_FROM_STEP_1` with the app key and access code obtained in the previous step)
    ```shell
    curl -u YOUR_APP_KEY -d "code=ACCESS_CODE_FROM_STEP_1&grant_type=authorization_code" https://api.dropbox.com/oauth2/token
    ```
   The command will ask for the app secret from the app settings.


In order to revoke refresh token execute the following commands in the terminal
1. Obtain access token (replace `YOUR_APP_KEY` and `REFRESH_TOKEN` with the app key and refresh token that should be revoked).
   ```shell
    curl -u YOUR_APP_KEY -d "grant_type=refresh_token&refresh_token=REFRESH_TOKEN" https://api.dropbox.com/oauth2/token
   ```
   The command will ask for the app secret from the app settings.

2. Revoke refresh token (replace `ACCESS_TOKEN` with the access token obtained in the previous step).
   ```shell
   curl -X POST https://api.dropboxapi.com/2/auth/token/revoke --header "Authorization: Bearer ACCESS_TOKEN"
   ```
