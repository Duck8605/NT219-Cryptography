# ECDHE for TLS - Usage Guide

This guide explains how to use the ECDHE (Elliptic Curve Diffie-Hellman Ephemeral) for TLS example script.

## Prerequisites

- Python 3.6+
- cryptography library
- OpenSSL (for certificate generation)

## Installation

1. Install the required package:

```bash
pip install cryptography
```

2. Save the provided `ecdhe_tls.py` script to your project directory.

## Usage

### Running the Example

The script demonstrates ECDHE key exchange and its integration with TLS:

1. Run the script:

```bash
python ecdhe_tls.py
```

This will:
- Demonstrate a basic ECDHE key exchange between two parties
- Create a self-signed certificate for TLS
- Run a TLS server that uses ECDHE for key exchange
- Connect a TLS client to the server
- Explain how ECDHE works in TLS

### Understanding the Output

The script output is divided into three sections:

1. **Basic ECDHE Key Exchange**: Shows the core concept of ECDHE without TLS integration
2. **TLS with ECDHE Key Exchange**: Demonstrates a practical implementation of ECDHE in TLS
3. **How ECDHE Works in TLS**: Explains the TLS handshake process with ECDHE

### Using the Functions in Your Own Code

#### Basic ECDHE Key Exchange

```python
from ecdhe_tls import demonstrate_basic_ecdhe

# Perform a basic ECDHE key exchange
shared_key = demonstrate_basic_ecdhe()
```

#### TLS Server with ECDHE

```python
from ecdhe_tls import create_self_signed_cert, run_tls_server

# Create a self-signed certificate
cert_file = "server.crt"
key_file = "server.key"
create_self_signed_cert(cert_file, key_file)

# Run a TLS server with ECDHE
host = "0.0.0.0"  # Listen on all interfaces
port = 8443
run_tls_server(host, port, cert_file, key_file)
```

#### TLS Client

```python
from ecdhe_tls import run_tls_client

# Connect to a TLS server
host = "example.com"  # Server hostname
port = 8443
run_tls_client(host, port)
```

## Function Reference

### ECDHE Key Exchange

- `demonstrate_basic_ecdhe()`: Demonstrate a basic ECDHE key exchange between two parties

### TLS with ECDHE

- `create_self_signed_cert(cert_file, key_file)`: Create a self-signed certificate for TLS
- `run_tls_server(host, port, cert_file, key_file)`: Run a TLS server with ECDHE
- `run_tls_client(host, port)`: Connect to a TLS server
- `demonstrate_tls_with_ecdhe()`: Demonstrate TLS with ECDHE by running a server and client

### Explanation

- `explain_ecdhe_in_tls()`: Explain how ECDHE is used in TLS

## Security Considerations

### Perfect Forward Secrecy

ECDHE provides perfect forward secrecy, which means that even if the server's long-term private key is compromised, past session keys cannot be recovered. This is because the ephemeral keys used for the key exchange are discarded after the session.

### Key Size

The example uses the SECP256R1 curve, which provides 128 bits of security. For higher security, you can use larger curves like SECP384R1 or SECP521R1.

### Certificate Validation

In a production environment, clients should validate the server's certificate against a trusted certificate authority (CA). The example uses a self-signed certificate for simplicity.

### Cipher Suites

The example prioritizes ECDHE cipher suites. In a production environment, you should carefully select the cipher suites based on your security requirements.

## Integration with Web Applications

To use ECDHE in a web application:

1. Configure your web server (e.g., Nginx, Apache) to use TLS with ECDHE cipher suites
2. Ensure your server's private key is kept secure
3. Use a valid certificate from a trusted CA
4. Configure the server to prioritize ECDHE cipher suites

## Common Issues and Troubleshooting

- **Connection failures**: Ensure the server is running and accessible
- **Certificate errors**: Verify that the certificate is valid and trusted
- **Cipher suite negotiation failures**: Check that both client and server support compatible cipher suites
- **Performance issues**: ECDHE is computationally intensive; consider using hardware acceleration if available

## Further Reading

- [TLS 1.3 Specification (RFC 8446)](https://tools.ietf.org/html/rfc8446)
- [Elliptic Curve Cryptography (RFC 6090)](https://tools.ietf.org/html/rfc6090)
- [ECDHE_RSA Key Exchange Algorithm (RFC 4492)](https://tools.ietf.org/html/rfc4492)
