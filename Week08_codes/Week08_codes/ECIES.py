import random
import base64
import hashlib
from tinyec import registry
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Define a manual list of available curves based on tinyec's documentation.
AVAILABLE_CURVES = [
    "secp192r1",
    "secp224r1",
    "secp256r1",     # Default option (index 3)
    "secp384r1",
    "secp521r1",
    "brainpoolP160r1",
    "brainpoolP192r1",
    "brainpoolP224r1",
    "brainpoolP256r1",
    "brainpoolP320r1",
    "brainpoolP384r1",
    "brainpoolP512r1"
]

def generate_keys():
    """
    Generate ECC key pair by letting the user select a curve.
    The private key is a random scalar, and the public key is computed by multiplying the generator point with the private key.
    """
    print("Available curves:")
    for i, curve_name in enumerate(AVAILABLE_CURVES, start=1):
        print(f"{i}. {curve_name}")
    
    # Prompt user to select a curve by number (default to 3 for secp256r1)
    choice = input("Select a curve by number (default 3 for secp256r1): ").strip() or "3"
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(AVAILABLE_CURVES):
            raise ValueError("Invalid selection")
        selected_curve_name = AVAILABLE_CURVES[idx]
    except Exception as e:
        print(f"Error selecting curve: {e}. Defaulting to secp256r1.")
        selected_curve_name = "secp256r1"
    
    curve = registry.get_curve(selected_curve_name)
    
    # Private key: random integer in the proper range.
    
    # sua key tu 1028 tro len 
    priv_key = random.randrange(1, curve.field.n)
    # Public key: scalar multiplication of generator point.
    pub_key = priv_key * curve.g
    
    print("\nGenerated ECC Keys:")
    print(f"Curve: {curve.name}")
    print(f"Private Key (d): {priv_key}")
    print(f"Public Key (Q): ({pub_key.x}, {pub_key.y})")
    
    return priv_key, pub_key, curve

def encrypt(plain_text, pub_key, curve, output_format="base64"):
    """
    Encrypts a message using an ECIES-like scheme.
    1. Choose an ephemeral key and compute the ephemeral public key.
    2. Derive a shared secret from which a symmetric key is obtained.
    3. Use AES in EAX mode to encrypt the message.
    4. Package the ephemeral public key (its x and y), AES nonce,
       authentication tag, and ciphertext.
    """
    # Generate ephemeral key and corresponding public key.
    ephemeral_key = random.randrange(1, curve.field.n)
    R = ephemeral_key * curve.g  # ephemeral public key
    
    # Compute the shared secret point: (ephemeral_key * recipient_public_key)
    shared_point = ephemeral_key * pub_key
    # Use the x-coordinate's byte representation length computed from the prime p's bit-length.
    coord_size = (curve.field.p.bit_length() + 7) // 8
    # Derive a symmetric key using SHA-256 on the x-coordinate bytes.
    shared_key = hashlib.sha256(int.to_bytes(shared_point.x, coord_size, 'big')).digest()
    
    # Set up AES in EAX mode for authenticated encryption.
    cipher = AES.new(shared_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode())
    
    # Prepare byte representation. For the curves in our list, coordinates use a size computed by coord_size.
    R_bytes = int.to_bytes(R.x, coord_size, 'big') + int.to_bytes(R.y, coord_size, 'big')
    # Pack nonce, tag, and ciphertext.
    payload = R_bytes + cipher.nonce + tag + ciphertext
    
    if output_format == "base64":
        encoded_payload = base64.b64encode(payload).decode()
    else:
        encoded_payload = payload.hex()
    
    print(f"\nCiphertext ({output_format}): {encoded_payload}")
    return encoded_payload

def decrypt(encoded_payload, priv_key, curve, input_format="base64"):
    """
    Decrypts an ECIES-like encrypted message.
    1. Extract the ephemeral public key (R) along with the nonce, tag, and ciphertext.
    2. Recompute the shared secret with the ephemeral public key.
    3. Derive the symmetric key and decrypt the AES ciphertext.
    """
    if input_format == "base64":
        payload = base64.b64decode(encoded_payload)
    else:
        payload = bytes.fromhex(encoded_payload)
    
    coord_size = (curve.field.p.bit_length() + 7) // 8
    # Extract ephemeral public key coordinates.
    R_x = int.from_bytes(payload[:coord_size], 'big')
    R_y = int.from_bytes(payload[coord_size:2*coord_size], 'big')
    # Recreate the ephemeral public key point.
    from tinyec.ec import Point
    R = Point(curve, R_x, R_y)
    
    # Next, extract nonce, tag, and ciphertext.
    nonce_size = 16  # AES nonce size for EAX mode (typically 16 bytes)
    tag_size = 16    # AES tag size (typically 16 bytes)
    offset = 2 * coord_size
    nonce = payload[offset: offset + nonce_size]
    tag = payload[offset + nonce_size: offset + nonce_size + tag_size]
    ciphertext = payload[offset + nonce_size + tag_size:]
    
    # Recompute the shared secret using the ephemeral public key and receiver's private key.
    shared_point = priv_key * R
    shared_key = hashlib.sha256(int.to_bytes(shared_point.x, coord_size, 'big')).digest()
    
    # Decrypt ciphertext using AES in EAX mode.
    cipher = AES.new(shared_key, AES.MODE_EAX, nonce=nonce)
    decrypted_text = cipher.decrypt_and_verify(ciphertext, tag).decode()
    
    print(f"\nDecrypted Message: {decrypted_text}")
    return decrypted_text

def main():
    priv_key = None
    pub_key = None
    curve = None

    while True:
        print("\nECC Encryption (ECIES-like) Implementation")
        print("1. Generate ECC Key Pair")
        print("2. Encrypt a Message")
        print("3. Decrypt a Cipher")
        print("4. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            priv_key, pub_key, curve = generate_keys()

        elif choice == "2":
            message = input("Enter message to encrypt: ")
            # Option to use an existing public key or input manually.
            use_existing = input("Use previously generated keys? (y/n): ").strip().lower()
            if use_existing == "y" and pub_key and curve:
                target_pub_key = pub_key
                target_curve = curve
            else:
                # For manual input, user must provide curve details and public key coordinates.
                curve_name = input("Enter curve name (e.g., secp256r1): ").strip() or "secp256r1"
                target_curve = registry.get_curve(curve_name)
                x_val = int(input("Enter public key X coordinate: ").strip())
                y_val = int(input("Enter public key Y coordinate: ").strip())
                from tinyec.ec import Point
                target_pub_key = Point(target_curve, x_val, y_val)
            output_format = input("Output format (base64/hex, default=base64): ").strip().lower() or "base64"
            encrypt(message, target_pub_key, target_curve, output_format)

        elif choice == "3":
            encoded_payload = input("Enter cipher text: ").strip()
            use_existing = input("Use previously generated keys? (y/n): ").strip().lower()
            if use_existing == "y" and priv_key and curve:
                target_priv_key = priv_key
                target_curve = curve
            else:
                # Manual input for private key and curve.
                target_priv_key = int(input("Enter private key (d): ").strip())
                curve_name = input("Enter curve name (e.g., secp256r1): ").strip() or "secp256r1"
                target_curve = registry.get_curve(curve_name)
            input_format = input("Cipher format (base64/hex, default=base64): ").strip().lower() or "base64"
            decrypt(encoded_payload, target_priv_key, target_curve, input_format)

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
