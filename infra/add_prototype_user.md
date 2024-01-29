# Access to SOLR prototype
There's an ubuntu 22.04 instance running in Azure that we intend to use for prototyping the server-side component of Loombreaker

This doc outlines basic access & user configuration for that instance.

## Connect to host
`ssh -i ~/path_to_your_private_key.pem <username>@20.84.107.89`

## Add user to host w/ SSH access
Pre-req: you have the SSH public key for the user.
```
sudo useradd -m -d /home/username -s /bin/bash username
passwd username #use any password; password login is disabled in SSH settings for this host
mkdir /home/username/.ssh
vim /home/username/.ssh/authorized_keys
  # paste the user's pubkey
chown -R username:username /home/username/.ssh
chmod 700 /home/username/.ssh
chmod 600 /home/username/.ssh/authorized_keys

# optionally, add user to sudoers:
sudo usermod -a -G sudo username
```

