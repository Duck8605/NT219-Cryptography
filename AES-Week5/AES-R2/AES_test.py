# -*- coding: utf-8 -*-
# Ref: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf
# Mode: https://csrc.nist.gov/pubs/sp/800/38/a/sup/final
import sys, os
sys.path.append(os.getcwd())  
from mypackages import key_expansion, modes

def message_to_bin(message):
    """Chuyển đổi một chuỗi thành biểu diễn nhị phân bằng mã hóa UTF-8."""
    binary_message = ''.join(format(byte, '08b') for byte in message.encode('utf-8'))
    return binary_message

def aes_mode_test(mode):
    # key128 for testing, we may revide this funtion to def aes_mode_test(mode, key)
    key128 = "12345678abcdefgh"
    key_bytes_128 = key128.encode('utf-8')
    aes_mode = modes.modes(key_bytes_128)

    input_path = input("Enter name file to encrypt: ")
    with open(input_path, 'rb') as f:
        plaintext = f.read()

    print(f"Length of file {input_path} (bytes): ", len(plaintext))

    if mode == "ECB":
        cipher = aes_mode.ecb_encrypt(plaintext)
    elif mode == "CBC":
        cipher = aes_mode.cbc_encrypt(plaintext)
    elif mode == "CFB":
        cipher = aes_mode.cfb_encrypt(plaintext)
    elif mode == "OFB":
        cipher = aes_mode.ofb_encrypt(plaintext)
    elif mode == "CTR":
        cipher = aes_mode.ctr_encrypt(plaintext)
    else:
        print("Invalid mode!")
        return

    output_path = input("Enter name file to save: ")
    with open(output_path, 'wb') as f:
        f.write(cipher)
    print(f"Length of {output_path} (bytes): ", len(cipher), "\n")
    print(f"Recovered text has been written to {output_path}")
    
def encrypt_file(input_file, output_file, key, mode):
    """Mã hóa một tệp và lưu kết quả vào tệp đầu ra."""
    with open(input_file, 'rb') as f:
        plaintext_bytes = f.read()

    key_bytes = key.encode('utf-8') 
    aes_mode = modes.modes(key_bytes)

    if mode == "ECB":
        ciphertext = aes_mode.ecb_encrypt(plaintext_bytes)
    elif mode == "CBC":
        ciphertext = aes_mode.cbc_encrypt(plaintext_bytes)
    elif mode == "CFB":
        ciphertext = aes_mode.cfb_encrypt(plaintext_bytes)
    elif mode == "OFB":
        ciphertext = aes_mode.ofb_encrypt(plaintext_bytes)
    elif mode == "CTR":
        ciphertext = aes_mode.ctr_encrypt(plaintext_bytes)
    else:
        raise ValueError("Chế độ không hợp lệ!")

    with open(output_file, 'wb') as f:
        f.write(ciphertext)
    print(f"Đã mã hóa tệp {input_file} và lưu vào {output_file}")

def decrypt_file(input_file, output_file, key, mode):
    """Giải mã một tệp và lưu kết quả vào tệp đầu ra."""
    with open(input_file, 'rb') as f:
        ciphertext = f.read()

    key_bytes = key.encode('utf-8') 
    aes_mode = modes.modes(key_bytes)

    if mode == "ECB":
        plaintext_bytes = aes_mode.ecb_decrypt(ciphertext)
    elif mode == "CBC":
        plaintext_bytes = aes_mode.cbc_decrypt(ciphertext)
    elif mode == "CFB":
        plaintext_bytes = aes_mode.cfb_decrypt(ciphertext)
    elif mode == "OFB":
        plaintext_bytes = aes_mode.ofb_decrypt(ciphertext)
    elif mode == "CTR":
        plaintext_bytes = aes_mode.ctr_decrypt(ciphertext)
    else:
        raise ValueError("Chế độ không hợp lệ!")

    with open(output_file, 'wb') as f:
        f.write(plaintext_bytes)
    print(f"Đã giải mã tệp {input_file} và lưu vào {output_file}")

if __name__ == "__main__":
    print("Chọn thao tác:")
    print("1. Mã hóa/Giải mã chuỗi")
    print("2. Mã hóa tệp")
    print("3. Giải mã tệp")
    operation = input("Nhập lựa chọn (1/2/3): ")

    mode_map = {
        "1": "ECB",
        "2": "CBC",
        "3": "CFB",
        "4": "OFB",
        "5": "CTR"
    }

    if operation == "1":
        print("Chọn chế độ AES:")
        print("1. ECB")
        print("2. CBC")
        print("3. CFB")
        print("4. OFB")
        print("5. CTR")
        choice = input("Nhập lựa chọn (1/2/3/4/5): ")
        selected_mode = mode_map.get(choice)
        if selected_mode:
            aes_mode_test(selected_mode)
        else:
            print("Lựa chọn không hợp lệ!")
    elif operation == "2":
        input_file = input("Nhập đường dẫn tệp đầu vào: ")
        output_file = input("Nhập đường dẫn tệp đầu ra: ")
        key = input("Nhập khóa (16 ký tự cho AES-128): ")
        print("Chọn chế độ AES:")
        print("1. ECB")
        print("2. CBC")
        print("3. CFB")
        print("4. OFB")
        print("5. CTR")
        choice = input("Nhập lựa chọn (1/2/3/4/5): ")
        selected_mode = mode_map.get(choice)
        if selected_mode:
            encrypt_file(input_file, output_file, key, selected_mode)
        else:
            print("Lựa chọn không hợp lệ!")
    elif operation == "3":
        input_file = input("Nhập đường dẫn tệp đầu vào: ")
        output_file = input("Nhập đường dẫn tệp đầu ra: ")
        key = input("Nhập khóa (16 ký tự cho AES-128): ")
        print("Chọn chế độ AES:")
        print("1. ECB")
        print("2. CBC")
        print("3. CFB")
        print("4. OFB")
        print("5. CTR")
        choice = input("Nhập lựa chọn (1/2/3/4/5): ")
        selected_mode = mode_map.get(choice)
        if selected_mode:
            decrypt_file(input_file, output_file, key, selected_mode)
        else:
            print("Lựa chọn không hợp lệ!")
    else:
        print("Lựa chọn không hợp lệ!")

key128 = "12345678abcdefgh"
key_bytes_128 = key128.encode('utf-8')
AES128_keys = key_expansion.key_expansion(key_bytes_128).key_expansion_128()
print("\nKhóa mở rộng cho 10 vòng:", AES128_keys, "\nSố lượng từ (4 byte mỗi từ):", len(AES128_keys))

key192 = "12345678abcdefghvbnmfgds"
key_bytes_192 = key192.encode('utf-8')
AES192_keys = key_expansion.key_expansion(key_bytes_192).key_expansion_192()

key256 = "12345678abcdefghvbnmfgds12345678"
key_bytes_256 = key256.encode('utf-8')
AES256_keys = key_expansion.key_expansion(key_bytes_256).key_expansion_256()