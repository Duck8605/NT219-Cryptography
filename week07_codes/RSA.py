import random
import base64
from sympy import isprime, mod_inverse

def generate_large_prime(bits=512):
    """Generate a large random prime number of specified bit size."""
    while True:
        num = random.getrandbits(bits)
        if isprime(num):
            return num

def generate_keys(bits=1024):
    """Generate RSA public and private keys with large primes."""
    p = generate_large_prime(bits // 2)
    q = generate_large_prime(bits // 2)

    while p == q:
        q = generate_large_prime(bits // 2)

    n = p * q
    phi_n = (p - 1) * (q - 1)

    e = 65537  # Common choice for efficiency
    d = mod_inverse(e, phi_n)  # Compute modular inverse of e

    print("\nGenerated Keys:")
    print(f"Prime number (p): {p}")
    print(f"Prime number (q): {q}")
    print(f"Modulus (n): {n}")
    print(f"Public Exponent (e): {e}")
    print(f"Private Exponent (d): {d}")
    print("\nCheck phi(n), e.d=1 mod phi(n)?")
    return e, n, d

def input_aes_key_and_encrypt(e, n, output_format="base64"):
    """Cho người dùng nhập AES key (hex hoặc text), rồi mã hóa bằng RSA"""
    key_type = input("Nhập kiểu AES key (1: text thường, 2: hex): ").strip()
    
    if key_type == "1":
        plain = input("Nhập AES key (chuỗi text): ").strip()
        aes_key_bytes = plain.encode()
    elif key_type == "2":
        hex_str = input("Nhập AES key (hex): ").strip()
        aes_key_bytes = bytes.fromhex(hex_str)
    else:
        print("Không hợp lệ.")
        return

    # Mã hóa AES key
    encrypted = encrypt_bytes(aes_key_bytes, e, n, output_format)
    print(f"\n🔐 AES key đã mã hóa ({output_format}):\n{encrypted}")
    
def encrypt(plain_text, e, n, output_format="base64"):
    """Encrypts message and returns Base64 or Hex-encoded cipher."""
    numeric_text = [ord(char) for char in plain_text]
    cipher_text = [pow(num, e, n) for num in numeric_text]
    
    cipher_bytes = b"".join(num.to_bytes((n.bit_length() + 7) // 8, 'big') for num in cipher_text)
    
    if output_format == "base64":
        encoded_cipher = base64.b64encode(cipher_bytes).decode()
    else:
        encoded_cipher = cipher_bytes.hex()
    
    print(f"\nCipher ({output_format}): {encoded_cipher}")
    return encoded_cipher

def encrypt_bytes(data_bytes, e, n, output_format="base64"):
    """Mã hóa bytes bằng RSA (e, n) và trả về dưới dạng base64 hoặc hex"""
    num = int.from_bytes(data_bytes, 'big')
    cipher_num = pow(num, e, n)
    cipher_bytes = cipher_num.to_bytes((n.bit_length() + 7) // 8, 'big')
    if output_format == "base64":
        return base64.b64encode(cipher_bytes).decode()
    else:
        return cipher_bytes.hex()

def decrypt(encoded_cipher, d, n, input_format="base64"):
    """Decrypts Base64 or Hex-encoded cipher and returns plaintext."""
    if input_format == "base64":
        cipher_bytes = base64.b64decode(encoded_cipher)
    else:
        cipher_bytes = bytes.fromhex(encoded_cipher)

    block_size = (n.bit_length() + 7) // 8
    cipher_blocks = [int.from_bytes(cipher_bytes[i:i+block_size], 'big') for i in range(0, len(cipher_bytes), block_size)]

    numeric_text = [pow(num, d, n) for num in cipher_blocks]
    decrypted_text = ''.join(chr(num) for num in numeric_text)

    print(f"\nDecrypted Message: {decrypted_text}")
    return decrypted_text

# Main Menu
def main():
    while True:
        print("\nRSA Implementation")
        print("1. Generate Keys")
        print("2. Encrypt a Message")
        print("3. Decrypt a Cipher")
        print("4. Input AES & RSA")
        print("5. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            e, n, d = generate_keys(1024)

        elif choice == "2":
            message = input("Enter message to encrypt: ")
            n = int(input("Enter modulus (n): ").strip())
            e = int(input("Enter public exponent (e): ").strip())
            output_format = input("Output format (base64/hex, default=base64): ").strip().lower() or "base64"
            encrypt(message, e, n, output_format)

        elif choice == "3":
            encoded_cipher = input("Enter cipher text: ").strip()
            n = int(input("Enter modulus (n): ").strip())
            d = int(input("Enter private exponent (d): ").strip())
            input_format = input("Cipher format (base64/hex, default=base64): ").strip().lower() or "base64"
            decrypt(encoded_cipher, d, n, input_format)

        elif choice == "4":
            n = int(input("Nhập modulus n: ").strip())
            e = int(input("Nhập public exponent e: ").strip())
            output_format = input("Chọn định dạng output (base64/hex, mặc định=base64): ").strip().lower() or "base64"
            input_aes_key_and_encrypt(e, n, output_format)
    
        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid option. Please try again.")

# Run the main function
if __name__ == "__main__":
    main()
