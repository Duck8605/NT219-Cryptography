# -*- coding: utf-8 -*-
#Ref: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf
# Mode: https://csrc.nist.gov/pubs/sp/800/38/a/sup/final
import sys, os
sys.path.append(os.getcwd()) # get curent working dir and export to python paths
from mypackages import key_expansion,modes

# Convert text <--> bin
def message_to_bin(message):
    """Convert a string message to its binary representation using UTF-8 encoding."""
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
def aes_mode_test_decrypt(mode):
    # key128 for testing, we may revide this funtion to def aes_mode_test(mode, key)
    key128 = "12345678abcdefgh"
    key_bytes_128 = key128.encode('utf-8')
    aes_mode = modes.modes(key_bytes_128)

    input_path = input("Enter name file to decrypt: ")
    with open(input_path, 'rb') as f:
        ciphertext = f.read()

    print(f"Length of file {input_path} (bytes): ", len(ciphertext))

    if mode == "ECB":
        recovered_text = aes_mode.ecb_decrypt(ciphertext)
    elif mode == "CBC":
        recovered_text = aes_mode.cbc_decrypt(ciphertext)
    elif mode == "CFB":
        recovered_text = aes_mode.cfb_decrypt(ciphertext)
    elif mode == "OFB":
        recovered_text = aes_mode.ofb_decrypt(ciphertext)
    elif mode == "CTR":
        recovered_text = aes_mode.ctr_decrypt(ciphertext)
    else:
        print("Invalid mode!")
        return

    output_path = input("Enter name file to save: ")
    with open(output_path, 'wb') as f:
        f.write(recovered_text)
    print(f"Length of {output_path} (bytes): ", len(recovered_text), "\n")

##Main part
if __name__ == "__main__":
    print("Select AES mode:")
    print("1. ECB")
    print("2. CBC")
    print("3. CFB")
    print("4. OFB")
    print("5. CTR")
    choice = input("Enter choice (1/2/3/4/5): ")

    mode_map = {
        "1": "ECB",
        "2": "CBC",
        "3": "CFB",
        "4": "OFB",
        "5": "CTR"
    }

    selected_mode = mode_map.get(choice)
    if selected_mode:
        print("Enter to option: ")
        print("1. Encrypt")
        print("2. Decrypt")
        option = "3"
        while option != "1" and option != "2":
            option = input("Enter option(1/2): ")
            if option != "1" and option != "2":
                print("Invalid Choice")
        if option == "1":
            aes_mode_test(selected_mode)
        elif option == "2":
            aes_mode_test_decrypt(selected_mode)    
    else:
        print("Invalid choice!")

#Test key 128
key128="12345678abcdefgh"
key_bytes_128 = key128.encode('utf-8')
AES128_keys = key_expansion.key_expansion(key_bytes_128).key_expansion_128()
print("\n Extension key for 10 rounds:", AES128_keys, "\n Number of words (4 bytes each):",len(AES128_keys))

#Test key 192
key192="12345678abcdefghvbnmfgds"
key_bytes_192 = key192.encode('utf-8')
AES192_keys = key_expansion.key_expansion(key_bytes_192).key_expansion_192()
#print(AES192_keys,"number of words:",len(AES192_keys))

#Test key 256

key256="12345678abcdefghvbnmfgds12345678"
key_bytes_256=key256.encode('utf-8')
AES256_keys = key_expansion.key_expansion(key_bytes_256).key_expansion_256()
#print(AES256_keys,"number of words:",len(AES256_keys))