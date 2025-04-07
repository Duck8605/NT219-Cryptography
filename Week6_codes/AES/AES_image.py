# -*- coding: utf-8 -*-
"""
AES Encryption/Decryption Script with optional image handling.

- Generate/read key (hex or random)
- Select AES mode (ECB, CBC, CFB, OFB, CTR)
- If the input is an image (e.g. .jpg, .jpeg, .png):
    - Decode to raw pixel data before encryption
    - On decrypt, reconstruct the image from raw data
- Otherwise, treat the file as a generic binary
- Retain file extension or rename for clarity
"""

import sys
import os
import secrets
from mypackages import key_expansion, modes
from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def read_or_generate_key() -> bytes:
    """
    Prompt user for:
      - a key in hex (16, 24, or 32 bytes => 32,48,64 hex chars)
      - or 'random' to generate a 16-byte key.
    Returns the key as bytes.
    """
    while True:
        user_input = input(
            "\nEnter AES key in hex (16,24,32 bytes => 32,48,64 hex chars) "
            "or 'random' for a new random key:\n> "
        ).strip().lower()
        if user_input == "random":
            key = secrets.token_bytes(16)  # 128-bit
            print(f"Generated random 128-bit key (hex): {key.hex()}")
            return key
        else:
            try:
                key_bytes = bytes.fromhex(user_input)
                if len(key_bytes) not in [16, 24, 32]:
                    print("Error: Key must be 16, 24, or 32 bytes (128, 192, 256 bits). Try again.\n")
                    continue
                print(f"Using user-provided key (hex): {key_bytes.hex()}")
                return key_bytes
            except ValueError:
                print("Invalid hex input. Try again.\n")

def select_mode() -> str:
    """
    Prompt for AES mode: ECB, CBC, CFB, OFB, CTR.
    Returns e.g. "ECB".
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
        print("Invalid choice. Please try again.")

def select_operation() -> str:
    """
    Prompt user: encrypt or decrypt?
    Returns 'encrypt' or 'decrypt'.
    """
    while True:
        op = input("\nDo you want to encrypt or decrypt? (E/D): ").strip().lower()
        if op in ["e", "encrypt"]:
            return "encrypt"
        elif op in ["d", "decrypt"]:
            return "decrypt"
        print("Invalid choice. Please enter 'E' (encrypt) or 'D' (decrypt).")

def is_image_file(filename: str) -> bool:
    """
    Check extension to decide if we treat it as an image.
    """
    _, ext = os.path.splitext(filename)
    return ext.lower() in IMAGE_EXTENSIONS

def encode_image_to_raw_bytes(image_path: str) -> bytes:
    """
    Load an image (JPEG/PNG/etc.) with Pillow, convert to raw RGBA or L (grayscale).
    Return raw bytes representing uncompressed pixel data.
    
    NOTE: This discards original compression. 
    """
    img = Image.open(image_path)

    # For demonstration, let's convert to grayscale (mode 'L') 
    # or you can keep 'RGB'. 
    # If you'd like alpha, do 'RGBA'.
    img = img.convert('L')  

    # Extract raw pixel data
    raw_data = img.tobytes()
    # Optionally, we might store (width, height) somewhere if we need for re-creation
    return raw_data, img.size

def decode_raw_bytes_to_image(raw_data: bytes, size: tuple, out_path: str):
    """
    Convert raw pixel bytes back to an image (grayscale).
    Save as a PNG (or whatever format you prefer).
    """
    w, h = size
    # Create new grayscale image of the right size
    new_img = Image.frombytes('L', (w, h), raw_data)
    new_img.save(out_path)
    print(f"Decrypted image saved as: {out_path}")

def process_file(input_path: str, output_path: str, aes_mode_obj, operation: str):
    """
    - If input is an image AND we're encrypting:
        * decode image to raw bytes
        * encrypt raw bytes
        * write ciphertext to output_path (binary)
        
    - If input is ciphertext of an image AND we're decrypting:
        * read ciphertext
        * decrypt to raw bytes
        * re-create the image from raw data => e.g. write as .png

    - Otherwise, fallback: treat as generic binary file
    """
    if operation == "encrypt":
        if is_image_file(input_path):
            # Convert the image to raw uncompressed bytes
            raw_data, (width, height) = encode_image_to_raw_bytes(input_path)

            # Encrypt 
            mode = aes_mode_obj.mode
            if mode == "ECB":
                ciphertext = aes_mode_obj.ecb_encrypt(raw_data)
            elif mode == "CBC":
                ciphertext = aes_mode_obj.cbc_encrypt(raw_data)
            elif mode == "CFB":
                ciphertext = aes_mode_obj.cfb_encrypt(raw_data)
            elif mode == "OFB":
                ciphertext = aes_mode_obj.ofb_encrypt(raw_data)
            elif mode == "CTR":
                ciphertext = aes_mode_obj.ctr_encrypt(raw_data)
            else:
                raise ValueError(f"Unsupported mode: {mode}")

            # We should store the (width, height) so we can reconstruct
            # Easiest way: write them as 4-byte ints at the start of the output
            # Then write the ciphertext
            with open(output_path, "wb") as f_out:
                f_out.write(width.to_bytes(4, 'big'))
                f_out.write(height.to_bytes(4, 'big'))
                f_out.write(ciphertext)

            print(f"\nEncrypted image data saved to {output_path}")
            print("Width/Height stored in first 8 bytes for decoding.\n")

        else:
            # Generic binary encryption
            with open(input_path, "rb") as f_in:
                data = f_in.read()

            mode = aes_mode_obj.mode
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

            with open(output_path, "wb") as f_out:
                f_out.write(result)

            print(f"\nDone! Encrypted file saved as: {output_path}")

    else:  # operation == "decrypt"
        # We check if the file might be an "encrypted image" 
        # by reading the first 8 bytes => (width, height)
        # If that doesn't look valid, fallback to binary decrypt
        with open(input_path, "rb") as f_in:
            possibly_header = f_in.read(8)
            remainder = f_in.read()

        # Attempt to parse the first 8 bytes as width, height
        width = int.from_bytes(possibly_header[:4], 'big')
        height = int.from_bytes(possibly_header[4:], 'big')

        # A minimal check if the width & height are in some plausible range
        # e.g. not zero or extremely large
        if (1 <= width <= 10000) and (1 <= height <= 10000):
            print(f"Detected encrypted image with size {width}x{height}")
            ciphertext = remainder
            mode = aes_mode_obj.mode
            if mode == "ECB":
                decrypted = aes_mode_obj.ecb_decrypt(ciphertext)
            elif mode == "CBC":
                decrypted = aes_mode_obj.cbc_decrypt(ciphertext)
            elif mode == "CFB":
                decrypted = aes_mode_obj.cfb_decrypt(ciphertext)
            elif mode == "OFB":
                decrypted = aes_mode_obj.ofb_decrypt(ciphertext)
            elif mode == "CTR":
                decrypted = aes_mode_obj.ctr_decrypt(ciphertext)
            else:
                raise ValueError(f"Unsupported mode: {mode}")

            # Rebuild the image from raw data and save
            # We'll pick output_path + ".png" or so
            image_out_path = output_path + ".png"
            decode_raw_bytes_to_image(decrypted, (width, height), image_out_path)

        else:
            # Not an encrypted image => do normal binary decrypt
            data = possibly_header + remainder
            mode = aes_mode_obj.mode
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

            with open(output_path, "wb") as f_out:
                f_out.write(result)

            print(f"\nDone! Decrypted file saved as: {output_path}")

def main():
    # 1) Select or generate key
    key_bytes = read_or_generate_key()

    # 2) Select AES mode
    mode_str = select_mode()

    # 3) Create AES mode object
    aes_mode = modes.modes(key_bytes)
    aes_mode.mode = mode_str

    # 4) Choose operation
    operation = select_operation()

    # 5) Get input file
    input_file = input("\nEnter input file path: ").strip()
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)

    # 6) Construct output file name
    if operation == "encrypt":
        # If it's an image, e.g. kittens.jpeg => cipher_kittens.jpeg.bin
        # else => cipher_<filename>
        base, ext = os.path.splitext(input_file)
        output_file = f"cipher_{os.path.basename(base)}{ext}.bin"
    else:
        # If it ends with .enc or .bin, remove that 
        # or just "decrypted_<filename>"
        base, ext = os.path.splitext(input_file)
        if ext.lower() in [".enc", ".bin"]:
            output_file = f"{base}_decrypted"
        else:
            output_file = f"decrypted_{os.path.basename(input_file)}"

    # 7) Process
    process_file(input_file, output_file, aes_mode, operation)

if __name__ == "__main__":
    main()
