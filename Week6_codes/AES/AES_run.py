# -*- coding: utf-8 -*-
"""
AES Encryption/Decryption Script

- Generate or read key from user (hex or random)
- Select AES mode (ECB, CBC, CFB, OFB, CTR)
- Encrypt or decrypt a binary file
- Retain file extension on encryption by appending ".enc"
- On decryption, remove ".enc" suffix to restore original extension
"""
import sys
import os
import secrets  # for random key generation
from mypackages import key_expansion, modes

def read_or_generate_key() -> bytes:
    """
    Prompt the user to enter a key in hex format (16, 24, or 32 bytes => 32,48,64 hex chars)
    or type 'random' to generate a new 16-byte (128-bit) key.
    Returns the key as bytes.
    """
    while True:
        user_input = input(
            "\nEnter AES key in hex (16,24,32 bytes => 32,48,64 hex chars) or 'random' for a new random key:\n> "
        ).strip().lower()
        if user_input == "random":
            # For demonstration, generate a 16-byte (128-bit) key
            key = secrets.token_bytes(16)
            print(f"Generated random 128-bit key (hex): {key.hex()}")
            return key
        else:
            # Try to parse the hex input
            try:
                key_bytes = bytes.fromhex(user_input)
                if len(key_bytes) not in [16, 24, 32]:
                    print("Error: Key must be 16, 24, or 32 bytes (128, 192, or 256 bits). Try again.\n")
                    continue
                print(f"Using user-provided key (hex): {key_bytes.hex()}")
                return key_bytes
            except ValueError:
                print("Invalid hex input. Try again.\n")

def select_mode() -> str:
    """
    Prompt the user for AES mode: ECB, CBC, CFB, OFB, CTR.
    Returns a string indicating the chosen mode.
    """
    print("\nSelect AES mode:")
    print("1. ECB")
    print("2. CBC")
    print("3. CFB")
    print("4. OFB")
    print("5. CTR")

    mode_map = {
        "1": "ECB",
        "2": "CBC",
        "3": "CFB",
        "4": "OFB",
        "5": "CTR"
    }

    while True:
        choice = input("Enter choice (1/2/3/4/5): ").strip()
        selected_mode = mode_map.get(choice)
        if selected_mode:
            print(f"Selected mode: {selected_mode}")
            return selected_mode
        else:
            print("Invalid choice. Please try again.")

def select_operation() -> str:
    """
    Prompt the user to choose encryption or decryption.
    Returns 'encrypt' or 'decrypt'.
    """
    while True:
        op = input("\nDo you want to encrypt or decrypt? (E/D): ").strip().lower()
        if op in ["e", "encrypt"]:
            return "encrypt"
        elif op in ["d", "decrypt"]:
            return "decrypt"
        print("Invalid choice. Please enter 'E' for encrypt or 'D' for decrypt.")

def process_file(input_path: str, output_path: str, aes_mode_obj, operation: str):
    """
    Read input file (binary) -> encrypt/decrypt -> write output file (binary).
    'aes_mode_obj' is an instance of modes.modes(...) with the selected key + mode.
    'operation' is either 'encrypt' or 'decrypt'.
    """
    # 1) Read the entire input file as bytes
    with open(input_path, "rb") as f_in:
        data = f_in.read()

    # 2) Perform encryption or decryption in the chosen mode
    mode = aes_mode_obj.mode
    if operation == "encrypt":
        if mode == "ECB":
            result = aes_mode_obj.ecb_encrypt(data)
        elif mode == "CBC":
            result = aes_mode_obj.cbc_encrypt(data)
        elif mode == "CFB":
            result = aes_mode_obj.cfb_encrypt(data)
        elif mode == "OFB":
            result = aes_mode_obj.ofb_encrypt(data)
        elif mode == "CTR":
            result = aes_mode_obj.ctr_encrypt(data)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
    else:  # operation == "decrypt"
        if mode == "ECB":
            result = aes_mode_obj.ecb_decrypt(data)
        elif mode == "CBC":
            result = aes_mode_obj.cbc_decrypt(data)
        elif mode == "CFB":
            result = aes_mode_obj.cfb_decrypt(data)
        elif mode == "OFB":
            result = aes_mode_obj.ofb_decrypt(data)
        elif mode == "CTR":
            result = aes_mode_obj.ctr_decrypt(data)
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    # 3) Write the result to the output file
    with open(output_path, "wb") as f_out:
        f_out.write(result)

    print(f"\nDone! {operation.title()}ed file saved as: {output_path}")

def main():
    # 1) Select or generate key
    key_bytes = read_or_generate_key()

    # 2) Select AES mode
    mode_str = select_mode()

    # 3) Create the AES mode object
    #    (Assuming your "modes" class sets its internal 'mode' variable)
    aes_mode = modes.modes(key_bytes)
    aes_mode.mode = mode_str  # or adapt if needed

    # 4) Choose encrypt or decrypt
    operation = select_operation()

    # 5) Get input file path
    input_file = input("\nEnter input file path (binary): ").strip()
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)

    # 6) Determine output file path
    #    a) If encrypting, append ".enc"
    #    b) If decrypting and file ends with ".enc", remove it
    if operation == "encrypt":
        output_file = "cipher_"+input_file
    else:
        # If the input ends with ".enc", remove that suffix
        if input_file.lower().endswith(".enc"):
            output_file = input_file[: -4]  # remove the last 4 chars (.enc)
        else:
            # Otherwise just keep original extention
            output_file = "decrypt_"+input_file

    # 7) Process the file (encrypt or decrypt)
    process_file(input_file, output_file, aes_mode, operation)

    # Optionally, show round keys or debug info:
    # expanded_keys = key_expansion.key_expansion(key_bytes).key_expansion_128()
    # print("Round keys for 128-bit key:", expanded_keys)

if __name__ == "__main__":
    main()
