# gray_ecb_visual.py
import sys
import os
import secrets
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from mypackages import modes  # Your AES modes implementation

def read_or_generate_key() -> bytes:
    """
    Prompt user for a key in hex or 'random' (16/24/32 bytes).
    Returns the key as raw bytes.
    """
    while True:
        user_input = input(
            "\nEnter AES key in hex (16,24,32 bytes => 32,48,64 hex chars)\n"
            "or 'random' for a new random key:\n> "
        ).strip().lower()
        if user_input == "random":
            key = secrets.token_bytes(16)  # 128-bit for example
            print(f"Generated random 128-bit key (hex): {key.hex()}")
            return key
        else:
            try:
                key_bytes = bytes.fromhex(user_input)
                if len(key_bytes) not in [16, 24, 32]:
                    print("Key must be 16, 24, or 32 bytes. Try again.\n")
                    continue
                print(f"Using user-provided key (hex): {key_bytes.hex()}")
                return key_bytes
            except ValueError:
                print("Invalid hex input. Try again.\n")

def select_mode() -> str:
    """
    Prompt user for AES mode (ECB, CBC, CFB, OFB, CTR).
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
        if choice in mode_map:
            return mode_map[choice]
        print("Invalid choice.")

def main():
    # 1) Get key + mode
    key_bytes = read_or_generate_key()
    mode_str = select_mode()
    print(f"Selected AES mode: {mode_str}")

    # 2) Create the AES mode object
    aes_mode = modes.modes(key_bytes)
    aes_mode.mode = mode_str

    # 3) Ask for input image
    input_file = input("\nEnter path to an image file (JPG, PNG, BMP): ").strip()
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)

    # 4) Load + convert to 8-bit grayscale
    img = Image.open(input_file).convert('L')
    w, h = img.size
    raw_data = img.tobytes()  # uncompressed grayscale data

    print(f"Loaded image '{input_file}': {w}x{h}, total {len(raw_data)} bytes in grayscale.")

    # 5) Display the original grayscale for reference
    original_arr = np.frombuffer(raw_data, dtype=np.uint8).reshape((h, w))

    # 6) Encrypt the raw grayscale data
    if mode_str == "ECB":
        ciphertext = aes_mode.ecb_encrypt(raw_data)
    elif mode_str == "CBC":
        ciphertext = aes_mode.cbc_encrypt(raw_data)
    elif mode_str == "CFB":
        ciphertext = aes_mode.cfb_encrypt(raw_data)
    elif mode_str == "OFB":
        ciphertext = aes_mode.ofb_encrypt(raw_data)
    elif mode_str == "CTR":
        ciphertext = aes_mode.ctr_encrypt(raw_data)
    else:
        raise ValueError(f"Unsupported mode: {mode_str}")

    print(f"Ciphertext length = {len(ciphertext)} bytes")

    # 7) For visualization, we'll interpret the ciphertext as a 2D array
    #    the same width/height as the original. If there's extra or missing data
    #    due to padding, we truncate or pad for the demonstration.
    needed = w * h
    ciph_len = len(ciphertext)
    if ciph_len < needed:
        print("Ciphertext is smaller. Zero-padding for visualization.")
        ciphertext += b"\x00" * (needed - ciph_len)
    elif ciph_len > needed:
        print("Ciphertext is larger. Truncating for visualization.")
        ciphertext = ciphertext[:needed]

    cipher_arr = np.frombuffer(ciphertext, dtype=np.uint8).reshape((h, w))

    # 8) Show side by side in matplotlib
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    ax_left, ax_right = axes.ravel()

    ax_left.imshow(original_arr, cmap='gray', vmin=0, vmax=255)
    ax_left.set_title("Original Grayscale")
    ax_left.axis("off")

    ax_right.imshow(cipher_arr, cmap='gray', vmin=0, vmax=255)
    ax_right.set_title(f"{mode_str} Cipher Visual")
    ax_right.axis("off")

    plt.show()

    # 9) Optionally save the ciphertext
    out_file = "cipher_grayscale.bin"
    with open(out_file, "wb") as f_out:
        # store width, height for potential decryption
        f_out.write(w.to_bytes(4, 'big'))
        f_out.write(h.to_bytes(4, 'big'))
        f_out.write(ciphertext)
    print(f"Ciphertext saved to '{out_file}' with (width, height) prepended.")

if __name__ == "__main__":
    main()
