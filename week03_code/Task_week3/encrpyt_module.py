import sys
import os

def encrypt_file_with_key(input_file, key_hex):
    # Chuyển chuỗi key hex thành bytes
    try:
        key_bytes = bytes.fromhex(key_hex)
    except ValueError:
        raise ValueError("Key không hợp lệ. Vui lòng nhập chuỗi hex hợp lệ.")
    
    if len(key_bytes) == 0:
        raise ValueError("Key không được rỗng.")

    # Đọc dữ liệu file ở dạng nhị phân
    with open(input_file, "rb") as f_in:
        data = f_in.read()
    
    # Thực hiện phép XOR: nếu key ngắn hơn dữ liệu, lặp lại key (cyclic)
    encrypted_data = bytes([data[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data))])
    
    return encrypted_data

def main():
    if len(sys.argv) != 3:
        sys.exit(1)
    
    input_file = sys.argv[1]
    key_hex = sys.argv[2]
    
    try:
        encrypted_data = encrypt_file_with_key(input_file, key_hex)
        
        output_file = input_file
        with open(output_file, "wb") as f_out:
            f_out.write(encrypted_data)
        
        print(f"Đã mã hóa file '{input_file}' thành '{output_file}' sử dụng key đã cho.")
    except Exception as e:
        print("Lỗi:", e)

if __name__ == "__main__":
    main()
