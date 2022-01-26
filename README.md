# vm.kalnytskyi.com

This repository contains Ansible playbook to deploy a VM for personal use which
includes but not limited to self hosting various services.

## Services

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
