# Hoth

This repository contains Ansible playbook to deploy a VM for personal use which
includes but not limited to self hosting various services. It's named after the
planet from Star Wars since most (if not all) of my devices are named after
Star Wars planets.

## Prerequisites

Custom `oci_image_unpack` Ansible module relies on the following components to
be available on the provisioner node:

 * skopeo
 * umoci
 * rsync

## Services

### [Ntfy]

ntfy lets you send push notifications to your phone or desktop via scripts from
any computer, using simple HTTP PUT or POST requests.

[Ntfy]: https://docs.ntfy.sh

### [Vaultwarden]

Alternative implementation of the Bitwarden server API written in Rust and
compatible with upstream [Bitwarden clients], perfect for self-hosted
deployment where running the official resource-heavy service might not be
ideal.

[Vaultwarden]: https://github.com/dani-garcia/vaultwarden
[Bitwarden clients]: https://bitwarden.com/#download

### [Wireguard]

Wireguard is an extremely simple yet fast and modern VPN that utilizes
state-of-the-art cryptography. It aims to be faster, simpler, leaner, and more
useful than IPsec, while avoiding the massive headache. It intends to be
considerably more performant than [OpenVPN].

[Wireguard]: https://www.wireguard.com/
[OpenVPN]: https://openvpn.net/

## Backups

A systemd timer archives `backup_targets`, compresses them with zstd, encrypts
them with [age], and uploads them to WebDAV with [rclone]. Restore an archive
with the private age identity:

```console
$ age --decrypt --identity backup-key.txt backup.tar.zst.age \
    | zstd --decompress \
    | tar --extract
```

[age]: https://age-encryption.org/
[rclone]: https://rclone.org/
