import sys
import os

def decrypt_file_with_key(input_file, key_hex):
    # Chuyển chuỗi key hex thành bytes
    try:
        key_bytes = bytes.fromhex(key_hex)
    except ValueError:
        raise ValueError("Key không hợp lệ. Vui lòng nhập chuỗi hex hợp lệ.")
    
    if len(key_bytes) == 0:
        raise ValueError("Key không được rỗng.")
    
    # Đọc dữ liệu file mã hóa ở dạng nhị phân
    with open(input_file, "rb") as f_in:
        encrypted_data = f_in.read()
    
    # Thực hiện phép XOR: nếu key ngắn hơn dữ liệu, lặp lại key (cyclic)
    decrypted_data = bytes([encrypted_data[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(encrypted_data))])
    
    return decrypted_data

def main():
    if len(sys.argv) != 3:
        sys.exit(1)
    
    input_file = sys.argv[1]
    key_hex = sys.argv[2]
    
    try:
        decrypted_data = decrypt_file_with_key(input_file, key_hex)
        
        output_file = input_file
        with open(output_file, "wb") as f_out:
            f_out.write(decrypted_data)
        
        print(f"Đã giải mã file '{input_file}' thành '{output_file}' sử dụng key đã cho.")
    except Exception as e:
        print("Lỗi:", e)

if __name__ == "__main__":
    main()
