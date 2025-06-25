"""
ECDHE (Elliptic Curve Diffie-Hellman Ephemeral) Key Exchange for TLS

This script demonstrates:
1. Basic ECDHE key exchange between two parties
2. Integration with TLS using Python's ssl module
3. Creating a simple TLS server and client using ECDHE

ECDHE provides perfect forward secrecy, ensuring that session keys
will not be compromised even if the server's private key is compromised.
"""

import os
import socket
import ssl
import threading
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def demonstrate_basic_ecdhe():
    """
    Demonstrate a basic ECDHE key exchange between Alice and Bob.
    
    This shows the core concept of ECDHE without TLS integration.
    """
    print("\n=== Basic ECDHE Key Exchange ===")
    
    # Alice generates her key pair
    print("Alice generates her key pair...")
    alice_private_key = ec.generate_private_key(ec.SECP256R1())
    alice_public_key = alice_private_key.public_key()
    
    # Bob generates his key pair
    print("Bob generates his key pair...")
    bob_private_key = ec.generate_private_key(ec.SECP256R1())
    bob_public_key = bob_private_key.public_key()
    
    # Alice serializes her public key to send to Bob
    alice_public_bytes = alice_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print(f"Alice sends her public key to Bob ({len(alice_public_bytes)} bytes)")
    
    # Bob serializes his public key to send to Alice
    bob_public_bytes = bob_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print(f"Bob sends his public key to Alice ({len(bob_public_bytes)} bytes)")
    
    # Alice deserializes Bob's public key
    bob_public_key_received = serialization.load_pem_public_key(bob_public_bytes)
    
    # Bob deserializes Alice's public key
    alice_public_key_received = serialization.load_pem_public_key(alice_public_bytes)
    
    # Alice computes the shared key
    alice_shared_key = alice_private_key.exchange(ec.ECDH(), bob_public_key_received)
    
    # Bob computes the shared key
    bob_shared_key = bob_private_key.exchange(ec.ECDH(), alice_public_key_received)
    
    # Derive a symmetric key from the shared secret using HKDF
    alice_derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(alice_shared_key)
    
    bob_derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(bob_shared_key)
    
    # Verify that both parties derived the same key
    print(f"Alice's derived key: {alice_derived_key.hex()[:10]}...")
    print(f"Bob's derived key:   {bob_derived_key.hex()[:10]}...")
    
    if alice_derived_key == bob_derived_key:
        print("Success! Both parties derived the same key.")
    else:
        print("Error: The derived keys do not match.")
    
    return alice_derived_key


def create_self_signed_cert(cert_file, key_file):
    """
    Create a self-signed certificate for TLS demonstration.
    
    Args:
        cert_file: Output path for certificate
        key_file: Output path for private key
    """
    # Check if files already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Certificate and key files already exist at {cert_file} and {key_file}")
        return
    
    print(f"Generating self-signed certificate and key...")
    
    # Generate a private key
    private_key = ec.generate_private_key(ec.SECP256R1())
    
    # Write the private key to a file
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Use OpenSSL command-line to generate a self-signed certificate
    # This is simpler than using cryptography library for this purpose
    os.system(f'openssl req -new -x509 -key {key_file} -out {cert_file} -days 365 -subj "/CN=localhost" -addext "subjectAltName = DNS:localhost"')
    
    print(f"Certificate and key generated and saved to {cert_file} and {key_file}")


def run_tls_server(host, port, cert_file, key_file):
    """
    Run a simple TLS server that uses ECDHE for key exchange.
    
    Args:
        host: Server hostname
        port: Server port
        cert_file: Path to certificate file
        key_file: Path to private key file
    """
    # Create a context with modern TLS settings
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    
    # Load certificate and private key
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    
    # Set the ECDHE cipher suites as preferred
    context.set_ciphers('ECDHE:!COMPLEMENTOFDEFAULT')
    
    # Create a socket and wrap it with SSL/TLS
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(5)
        
        print(f"TLS Server listening on {host}:{port}")
        print("Cipher suites enabled:")
        for cipher in context.get_ciphers():
            if 'ECDHE' in cipher['name']:
                print(f"  - {cipher['name']}")
        
        # Accept a client connection
        client_sock, addr = sock.accept()
        with context.wrap_socket(client_sock, server_side=True) as ssock:
            print(f"Client connected from {addr}")
            print(f"TLS version: {ssock.version()}")
            print(f"Cipher used: {ssock.cipher()[0]}")
            
            # Receive data from client
            data = ssock.recv(1024)
            print(f"Received: {data.decode()}")
            
            # Send response
            ssock.send(b"Hello from TLS server using ECDHE!")


def run_tls_client(host, port):
    """
    Run a simple TLS client that connects to the server.
    
    Args:
        host: Server hostname
        port: Server port
    """
    # Create a context with modern TLS settings
    context = ssl.create_default_context()
    
    # Set the ECDHE cipher suites as preferred
    context.set_ciphers('ECDHE:!COMPLEMENTOFDEFAULT')
    
    # Create a socket and wrap it with SSL/TLS
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            # Connect to the server
            ssock.connect((host, port))
            
            print(f"Connected to {host}:{port}")
            print(f"TLS version: {ssock.version()}")
            print(f"Cipher used: {ssock.cipher()[0]}")
            
            # Send data to server
            ssock.send(b"Hello from TLS client!")
            
            # Receive response
            data = ssock.recv(1024)
            print(f"Received: {data.decode()}")


def demonstrate_tls_with_ecdhe():
    """
    Demonstrate TLS with ECDHE by running a server and client.
    """
    print("\n=== TLS with ECDHE Key Exchange ===")
    
    # Create certificate and key for TLS
    cert_file = "server.crt"
    key_file = "server.key"
    create_self_signed_cert(cert_file, key_file)
    
    # Set up server parameters
    host = "localhost"
    port = 8443
    
    # Start the server in a separate thread
    server_thread = threading.Thread(
        target=run_tls_server,
        args=(host, port, cert_file, key_file)
    )
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server time to start
    time.sleep(1)
    
    # Run the client
    try:
        run_tls_client(host, port)
    except Exception as e:
        print(f"Client error: {e}")
    
    # Wait for the server to finish
    server_thread.join(timeout=5)


def explain_ecdhe_in_tls():
    """
    Explain how ECDHE is used in TLS.
    """
    print("\n=== How ECDHE Works in TLS ===")
    print("""
ECDHE (Elliptic Curve Diffie-Hellman Ephemeral) in TLS works as follows:

1. TLS Handshake Initiation:
   - Client sends ClientHello with supported cipher suites (including ECDHE)
   - Server responds with ServerHello selecting an ECDHE cipher suite

2. Key Exchange:
   - Server generates an ephemeral ECDH key pair
   - Server sends its ephemeral public key in the ServerKeyExchange message
   - Server signs this message with its long-term private key
   - Client verifies the signature using the server's certificate
   - Client generates its own ephemeral ECDH key pair
   - Client sends its ephemeral public key to the server

3. Shared Secret Derivation:
   - Both parties compute the same shared secret using their private key
     and the other party's public key
   - This shared secret is used to derive the session keys

4. Session Key Generation:
   - Both parties derive the same session keys from the shared secret
   - These keys are used for encrypting and authenticating the data

5. Secure Communication:
   - Data is encrypted and authenticated using the derived session keys

Key Security Properties:
- Perfect Forward Secrecy: Even if the server's long-term private key is
  compromised later, past session keys cannot be recovered because the
  ephemeral keys are discarded after the session
- Authentication: The server's identity is verified using its certificate
- Confidentiality: The data is encrypted using strong symmetric encryption
- Integrity: The data is authenticated to prevent tampering
    """)


def main():
    """
    Main function to demonstrate ECDHE and its use in TLS.
    """
    print("ECDHE Key Exchange for TLS")
    print("==========================")
    
    # Demonstrate basic ECDHE key exchange
    demonstrate_basic_ecdhe()
    
    # Demonstrate TLS with ECDHE
    demonstrate_tls_with_ecdhe()
    
    # Explain how ECDHE works in TLS
    explain_ecdhe_in_tls()


if __name__ == "__main__":
    main()
