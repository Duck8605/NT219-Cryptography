# OpenVPN Server Setup Guide

This comprehensive guide will walk you through setting up an OpenVPN server with strong cryptographic security, including installation, configuration, certificate management, client setup, and security best practices.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Certificate Authority Setup](#certificate-authority-setup)
4. [Server Configuration](#server-configuration)
5. [Client Configuration](#client-configuration)
6. [Security Hardening](#security-hardening)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Topics](#advanced-topics)

## Prerequisites

Before starting, ensure you have:

- A server running Ubuntu 20.04 LTS or newer
- Root or sudo access
- A static IP address (recommended)
- Basic knowledge of Linux command line
- Ports 1194 UDP/TCP open in your firewall

## Installation

### Step 1: Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install OpenVPN and Easy-RSA

```bash
sudo apt install openvpn easy-rsa -y
```

### Step 3: Set Up the PKI Directory

```bash
mkdir -p ~/openvpn-ca
cp -r /usr/share/easy-rsa/* ~/openvpn-ca/
cd ~/openvpn-ca
```

## Certificate Authority Setup

### Step 1: Configure the CA Variables

Create a file named `vars` in the `~/openvpn-ca` directory:

```bash
cat > ~/openvpn-ca/vars << EOF
set_var EASYRSA_REQ_COUNTRY    "US"
set_var EASYRSA_REQ_PROVINCE   "California"
set_var EASYRSA_REQ_CITY       "San Francisco"
set_var EASYRSA_REQ_ORG        "Example Organization"
set_var EASYRSA_REQ_EMAIL      "admin@example.com"
set_var EASYRSA_REQ_OU         "IT Department"
set_var EASYRSA_KEY_SIZE       2048
set_var EASYRSA_ALGO           rsa
set_var EASYRSA_CA_EXPIRE      3650
set_var EASYRSA_CERT_EXPIRE    825
set_var EASYRSA_CRL_DAYS       180
EOF
```

### Step 2: Initialize the PKI

```bash
cd ~/openvpn-ca
./easyrsa init-pki
```

### Step 3: Build the Certificate Authority

```bash
./easyrsa build-ca
```

When prompted, enter a secure passphrase for your CA key and a Common Name for your CA (e.g., "Example-CA").

### Step 4: Generate Server Certificate and Key

```bash
./easyrsa gen-req server nopass
```

When prompted, enter a Common Name for your server (e.g., "vpn-server").

### Step 5: Sign the Server Certificate

```bash
./easyrsa sign-req server server
```

When prompted, confirm by typing "yes" and enter your CA passphrase.

### Step 6: Generate Diffie-Hellman Parameters

```bash
./easyrsa gen-dh
```

This may take several minutes to complete.

### Step 7: Generate TLS Authentication Key

```bash
openvpn --genkey --secret ~/openvpn-ca/pki/ta.key
```

## Server Configuration

### Step 1: Copy the Required Files to OpenVPN Directory

```bash
sudo cp ~/openvpn-ca/pki/ca.crt /etc/openvpn/
sudo cp ~/openvpn-ca/pki/issued/server.crt /etc/openvpn/
sudo cp ~/openvpn-ca/pki/private/server.key /etc/openvpn/
sudo cp ~/openvpn-ca/pki/dh.pem /etc/openvpn/
sudo cp ~/openvpn-ca/pki/ta.key /etc/openvpn/
```

### Step 2: Create Server Configuration File

```bash
sudo cp /usr/share/doc/openvpn/examples/sample-config-files/server.conf /etc/openvpn/
sudo nano /etc/openvpn/server.conf
```

Edit the configuration file with the following settings:

```
port 1194
proto udp
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh.pem
topology subnet
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist /var/log/openvpn/ipp.txt
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"
keepalive 10 120
tls-auth ta.key 0
cipher AES-256-GCM
auth SHA256
compress lz4-v2
push "compress lz4-v2"
user nobody
group nogroup
persist-key
persist-tun
status /var/log/openvpn/status.log
verb 3
explicit-exit-notify 1
```

### Step 3: Enable IP Forwarding

```bash
sudo nano /etc/sysctl.conf
```

Uncomment or add the following line:

```
net.ipv4.ip_forward=1
```

Apply the changes:

```bash
sudo sysctl -p
```

### Step 4: Configure Firewall Rules

For UFW:

```bash
sudo ufw allow 1194/udp
sudo ufw allow OpenSSH
sudo ufw disable
sudo ufw enable
```

Configure NAT forwarding:

```bash
sudo nano /etc/ufw/before.rules
```

Add the following lines before the `*filter` line:

```
# NAT table rules
*nat
:POSTROUTING ACCEPT [0:0]
# Allow traffic from OpenVPN client to eth0 (change eth0 to your network interface)
-A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE
COMMIT
```

### Step 5: Start and Enable OpenVPN Service

```bash
sudo mkdir -p /var/log/openvpn
sudo systemctl start openvpn@server
sudo systemctl enable openvpn@server
```

## Client Configuration

### Step 1: Generate Client Certificate and Key

For each client, run:

```bash
cd ~/openvpn-ca
./easyrsa gen-req client1 nopass
./easyrsa sign-req client client1
```

### Step 2: Create Client Configuration Directory

```bash
mkdir -p ~/client-configs/files
chmod 700 ~/client-configs/files
```

### Step 3: Create Base Client Configuration

```bash
cp /usr/share/doc/openvpn/examples/sample-config-files/client.conf ~/client-configs/base.conf
```

Edit the base configuration:

```bash
nano ~/client-configs/base.conf
```

Modify it to look like this:

```
client
dev tun
proto udp
remote your_server_ip 1194
resolv-retry infinite
nobind
user nobody
group nogroup
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-GCM
auth SHA256
key-direction 1
compress lz4-v2
verb 3
```

### Step 4: Create a Script to Generate Client Configurations

```bash
nano ~/client-configs/make_config.sh
```

Add the following content:

```bash
#!/bin/bash

# First argument: Client name

KEY_DIR=~/openvpn-ca/pki
OUTPUT_DIR=~/client-configs/files
BASE_CONFIG=~/client-configs/base.conf

cat ${BASE_CONFIG} \
    <(echo -e '<ca>') \
    ${KEY_DIR}/ca.crt \
    <(echo -e '</ca>\n<cert>') \
    ${KEY_DIR}/issued/${1}.crt \
    <(echo -e '</cert>\n<key>') \
    ${KEY_DIR}/private/${1}.key \
    <(echo -e '</key>\n<tls-auth>') \
    ${KEY_DIR}/ta.key \
    <(echo -e '</tls-auth>') \
    > ${OUTPUT_DIR}/${1}.ovpn
```

Make the script executable:

```bash
chmod 700 ~/client-configs/make_config.sh
```

### Step 5: Generate Client Configuration

```bash
cd ~/client-configs
./make_config.sh client1
```

The client configuration file will be saved to `~/client-configs/files/client1.ovpn`.

## Security Hardening

### Use Strong Encryption

The configuration above already uses strong encryption (AES-256-GCM), but you can further enhance security:

1. **Use Elliptic Curve Cryptography**:
   
   When generating keys with Easy-RSA, modify your vars file:
   
   ```
   set_var EASYRSA_ALGO ec
   set_var EASYRSA_CURVE secp384r1
   ```

2. **Implement Perfect Forward Secrecy**:
   
   Add to server.conf:
   
   ```
   tls-cipher TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384
   ```

### Implement Two-Factor Authentication

1. Install the required packages:

   ```bash
   sudo apt install libpam-google-authenticator -y
   ```

2. Configure PAM for OpenVPN:

   ```bash
   sudo nano /etc/pam.d/openvpn
   ```

   Add:

   ```
   auth required pam_google_authenticator.so
   ```

3. Modify server.conf:

   ```
   plugin /usr/lib/x86_64-linux-gnu/openvpn/plugins/openvpn-plugin-auth-pam.so openvpn
   ```

4. Set up Google Authenticator for each user:

   ```bash
   google-authenticator
   ```

### Restrict User Access

Create a dedicated user for OpenVPN:

```bash
sudo adduser --system --shell /usr/sbin/nologin --no-create-home openvpn
```

Update server.conf:

```
user openvpn
group nogroup
```

### Regular Certificate Revocation

1. Create a Certificate Revocation List:

   ```bash
   cd ~/openvpn-ca
   ./easyrsa gen-crl
   sudo cp pki/crl.pem /etc/openvpn/
   ```

2. Add to server.conf:

   ```
   crl-verify /etc/openvpn/crl.pem
   ```

3. To revoke a client certificate:

   ```bash
   cd ~/openvpn-ca
   ./easyrsa revoke client1
   ./easyrsa gen-crl
   sudo cp pki/crl.pem /etc/openvpn/
   sudo systemctl restart openvpn@server
   ```

## Troubleshooting

### Check OpenVPN Status

```bash
sudo systemctl status openvpn@server
```

### View OpenVPN Logs

```bash
sudo tail -f /var/log/openvpn/status.log
sudo journalctl -u openvpn@server
```

### Connection Issues

1. **Firewall Problems**:
   
   Verify firewall settings:
   
   ```bash
   sudo ufw status
   ```

2. **Port Accessibility**:
   
   Test if the port is open:
   
   ```bash
   nc -vz your_server_ip 1194
   ```

3. **Certificate Issues**:
   
   Check certificate validity:
   
   ```bash
   openssl verify -CAfile ~/openvpn-ca/pki/ca.crt ~/openvpn-ca/pki/issued/server.crt
   ```

## Advanced Topics

### Configure Split Tunneling

To route only specific traffic through the VPN:

1. Remove the redirect-gateway directive from server.conf:
   
   ```
   # push "redirect-gateway def1 bypass-dhcp"
   ```

2. Add specific routes:
   
   ```
   push "route 192.168.1.0 255.255.255.0"
   ```

### Set Up a Kill Switch on Clients

Add to client configuration:

```
script-security 2
up /etc/openvpn/up.sh
down /etc/openvpn/down.sh
```

Create up.sh:

```bash
#!/bin/bash
iptables -F
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -P FORWARD DROP
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -i tun+ -j ACCEPT
iptables -A OUTPUT -o tun+ -j ACCEPT
iptables -A OUTPUT -o eth0 -p udp --dport 1194 -j ACCEPT
```

Create down.sh:

```bash
#!/bin/bash
iptables -F
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT
```

### Set Up Multiple VPN Servers

1. Create additional server configurations:
   
   ```bash
   sudo cp /etc/openvpn/server.conf /etc/openvpn/server2.conf
   ```

2. Edit the new configuration with different port and subnet:
   
   ```
   port 1195
   server 10.9.0.0 255.255.255.0
   ```

3. Start the new instance:
   
   ```bash
   sudo systemctl start openvpn@server2
   sudo systemctl enable openvpn@server2
   ```

---

This guide provides a comprehensive approach to setting up an OpenVPN server with strong cryptographic security. By following these steps, you'll have a secure VPN solution that protects your network communications with modern encryption standards.
