# Hướng dẫn sử dụng module `he_crypto_module` với OpenFHE

## 1. Giới thiệu

`he_crypto_module` là một module Python sử dụng thư viện `openfhe-python` để triển khai một hệ thống mã hóa đồng cấu đa bên (Multiparty Homomorphic Encryption) hoàn chỉnh. Không giống như các hệ thống mã hóa truyền thống hoặc HE đơn giản, module này cho phép nhiều bên cùng hợp tác để tạo ra một khóa công khai chung và sau đó cùng nhau giải mã dữ liệu mà không cần tiết lộ khóa bí mật riêng của từng bên.

Luồng hoạt động này đặc biệt hữu ích trong các kịch bản tài chính, nơi nhiều ngân hàng cần hợp tác với một đối tác (ví dụ: Fintech) để phân tích dữ liệu nhạy cảm mà vẫn đảm bảo tính riêng tư tuyệt đối.

**Các tính năng chính:**
-   Tạo CryptoContext với lược đồ CKKS.
-   Luồng tạo khóa đa bên tuần tự (sequential multiparty key generation).
-   Luồng tạo khóa đánh giá phép nhân đa bên (multiparty evaluation key generation).
-   Mã hóa dữ liệu bằng khóa công khai chung.
-   Giải mã theo ngưỡng (Threshold Decryption), yêu cầu sự tham gia của các bên để có được kết quả cuối cùng.
-   Tất cả các khóa và bản mã được serialize sang định dạng Base64 để dễ dàng lưu trữ và truyền tải.

---

## 2. Cài đặt

Module này yêu cầu các thư viện sau:
-   `openfhe-python`
-   `numpy`

Bạn có thể cài đặt chúng bằng pip:
```sh
pip install openfhe-python numpy
```

---

## 3. Tổng quan về luồng hoạt động

Hệ thống hoạt động theo một quy trình nghiêm ngặt gồm nhiều giai đoạn:

1.  **Khởi tạo (Context Creation)**: Một `CryptoContext` được tạo ra với các tham số mã hóa được định sẵn. Context này phải được sử dụng nhất quán trong tất cả các bước tiếp theo.
2.  **Tạo khóa công khai chung (Joint Public Key Generation)**:
    a.  **Bên dẫn đầu (Lead Party)**: Bên đầu tiên (ví dụ: Ngân hàng A) gọi hàm `keygen()` để tạo cặp khóa đầu tiên.
    b.  **Các bên tiếp theo (Subsequent Parties)**: Các bên còn lại (Ngân hàng B, C,...) lần lượt gọi hàm `multiparty_keygen()`, sử dụng khóa công khai của bên ngay trước đó để đóng góp vào khóa chung. Khóa công khai cuối cùng là khóa công khai chung của cả nhóm.
3.  **Tạo khóa đánh giá phép nhân (EvalMult Key Generation)**: Tương tự như trên, các bên cùng nhau tạo ra một khóa đánh giá chung để cho phép thực hiện phép nhân trên dữ liệu mã hóa.
4.  **Mã hóa (Encryption)**: Một bên bất kỳ (ví dụ: Fintech Partner) sử dụng khóa công khai chung cuối cùng để mã hóa dữ liệu.
5.  **Giải mã theo ngưỡng (Threshold Decryption)**:
    a.  **Bên dẫn đầu (Lead Party)**: Bên dẫn đầu của quá trình giải mã (có thể là bên đã khởi tạo khóa) gọi hàm `partial_decrypt()` với cờ `is_lead=True`.
    b.  **Các bên còn lại**: Các bên khác gọi `partial_decrypt()` với cờ `is_lead=False`. Mỗi lệnh gọi sẽ tạo ra một "phần giải mã" (decryption share).
    c.  **Tổng hợp kết quả**: Các phần giải mã được thu thập và đưa vào hàm `combine_partial_decrypt()` để có được kết quả giải mã cuối cùng.

---

## 4. Mô tả các hàm

#### `create_crypto_context()`
Tạo và cấu hình các tham số cho mã hóa đồng cấu (lược đồ CKKS, độ sâu phép nhân, kích thước batch, ...).

#### `keygen(cc)`
Dành cho bên đầu tiên. Tạo ra cặp khóa public/private ban đầu.
-   **Đầu vào**: `cc` (CryptoContext).
-   **Đầu ra**: Dictionary chứa `public_key` và `secret_key` dưới dạng Base64.

#### `multiparty_keygen(cc, prev_pub_key_b64)`
Dành cho các bên tiếp theo. Đóng góp vào khóa công khai chung.
-   **Đầu vào**: `cc`, `prev_pub_key_b64` (khóa công khai của bên trước đó).
-   **Đầu ra**: Dictionary chứa khóa công khai *mới* và khóa bí mật của riêng bên này.

#### `encrypt(cc, pubkey_b64, message)`
Mã hóa một mảng dữ liệu.
-   **Đầu vào**: `cc`, `pubkey_b64` (khóa công khai chung cuối cùng), `message` (list/numpy array).
-   **Đầu ra**: Ciphertext dưới dạng Base64.

#### `partial_decrypt(cc, private_key_b64, ciphertext_b64, is_lead)`
Thực hiện giải mã một phần.
-   **Đầu vào**: `cc`, `private_key_b64` (khóa bí mật của bên thực hiện), `ciphertext_b64`, `is_lead` (cờ boolean xác định đây có phải bên dẫn đầu không).
-   **Đầu ra**: Một phần giải mã (decryption share) dưới dạng Base64.

#### `combine_partial_decrypt(cc, part_b64_list)`
Tổng hợp các phần giải mã.
-   **Đầu vào**: `cc`, `part_b64_list` (list các phần giải mã từ tất cả các bên).
-   **Đầu ra**: Dữ liệu đã được giải mã hoàn toàn (numpy array).

---

## 5. Ví dụ: Kịch bản 3 Ngân hàng

```python
import he_crypto_module as he
import base64

def test_multiparty_encryption():
    """
    A simple test case to demonstrate the multiparty key generation and
    encryption process for a 3-party system (e.g., three banks).
    """
    print("--- 1. Setting up CryptoContext ---")
    # All parties must use the same crypto context
    cc = he.create_crypto_context()
    print("CryptoContext created successfully.\n")

    # --- Stage 1: Bank 1 (Lead) generates the first key pair ---
    print("--- 2. Bank 1 (Lead) generating initial key pair ---")
    bank1_keys = he.keygen(cc)
    with open("bank1_sk.txt", "w") as f:
        f.write(bank1_keys["secret_key"])
    print("Bank 1 Public Key (b64):", bank1_keys["public_key"][:30] + "...")
    print("Bank 1 Secret Key saved to bank1_sk.txt")
    print("Bank 1 finished.\n")

    # --- Stage 2: Bank 2 joins and contributes to the public key ---
    print("--- 3. Bank 2 contributing to the public key ---")
    bank2_keys = he.multiparty_keygen(cc, bank1_keys["public_key"])
    with open("bank2_sk.txt", "w") as f:
        f.write(bank2_keys["secret_key"])
    print("Bank 2 (Joint) Public Key (b64):", bank2_keys["public_key"][:30] + "...")
    print("Bank 2 Secret Key saved to bank2_sk.txt")
    print("Bank 2 finished.\n")

    # --- Stage 3: Bank 3 joins and contributes, creating the final public key ---
    print("--- 4. Bank 3 contributing to the final public key ---")
    bank3_keys = he.multiparty_keygen(cc, bank2_keys["public_key"])
    final_public_key = bank3_keys["public_key"]
    with open("bank3_sk.txt", "w") as f:
        f.write(bank3_keys["secret_key"])
    with open("joint_pk.txt", "w") as f:
        f.write(final_public_key)
    print("Bank 3 (Final Joint) Public Key saved to joint_pk.txt")
    print("Bank 3 Secret Key saved to bank3_sk.txt")
    print("Multiparty key generation complete.\n")

    # --- Stage 4: Encrypting data with the final joint public key ---
    print("--- 5. Encrypting data with the final joint public key ---")
    # Sample financial data to be encrypted
    message_to_encrypt = [1200.5]
    print("Original Message:", message_to_encrypt)

    ciphertext_b64 = he.encrypt(cc, final_public_key, message_to_encrypt)
    with open("ciphertext.txt", "w") as f:
        f.write(ciphertext_b64)
    print("Encryption successful!")
    print("Final Ciphertext saved to ciphertext.txt")

    # --- Stage 5: Multiparty Decryption ---
    print("\n--- 6. Performing multiparty decryption ---")

    # Each party generates a partial decryption share
    # Bank 1 (Lead)
    partial_decryption1 = he.partial_decrypt(cc, bank1_keys["secret_key"], ciphertext_b64, is_lead=True)
    print("Bank 1 created partial decryption share.")

    # Bank 2
    partial_decryption2 = he.partial_decrypt(cc, bank2_keys["secret_key"], ciphertext_b64, is_lead=False)
    print("Bank 2 created partial decryption share.")

    # Bank 3
    partial_decryption3 = he.partial_decrypt(cc, bank3_keys["secret_key"], ciphertext_b64, is_lead=False)
    print("Bank 3 created partial decryption share.")

    # --- Stage 6: Combine partial decryptions ---
    print("\n--- 7. Combining partial decryptions to recover data ---")
    decryption_shares = [partial_decryption1, partial_decryption2, partial_decryption3]
    
    decrypted_message = he.combine_partial_decrypt(cc, decryption_shares)
    print("Decryption successful!")
    print("Decrypted Message:", decrypted_message)

    # --- Verification ---
    print("\n--- 8. Verifying the result ---")
    # Using numpy to compare floating point numbers with a tolerance
    import numpy as np
    print(message_to_encrypt)
    is_correct = np.allclose(message_to_encrypt, decrypted_message, atol=0.0001)
    
    if is_correct:
        print("SUCCESS: Decrypted data matches the original message.")
    else:
        print("FAILURE: Decrypted data does not match the original message.")


if __name__ == "__main__":
    test_multiparty_encryption()


```

---

## 6. Lưu ý quan trọng

-   **Thứ tự là tối quan trọng**: Quá trình tạo khóa và giải mã phải tuân thủ đúng thứ tự và vai trò (lead/main party).
-   **Tính nhất quán của Context**: Cùng một `CryptoContext` phải được sử dụng cho tất cả các hoạt động liên quan đến một nhóm khóa.
-   **Bảo mật khóa bí mật**: Mỗi bên phải tự bảo vệ khóa bí mật của mình. Việc lộ một khóa bí mật sẽ phá vỡ an toàn của hệ thống.
-   **Quản lý khóa**: Trong môi trường thực tế, cần có một cơ chế an toàn để trao đổi các khóa công khai và các phần giải mã giữa các bên.

