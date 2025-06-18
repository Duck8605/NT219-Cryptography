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
import numpy as np

# --- Giai đoạn 1: Thiết lập và tạo khóa ---
print("1. Setting up crypto context...")
cc = he.create_crypto_context()

# Ngân hàng A (Lead Party) tạo khóa đầu tiên
print("2. Bank A generates initial key pair...")
keys_A = he.keygen(cc)

# Ngân hàng B tham gia, sử dụng public key của A
print("3. Bank B joins, using Bank A's public key...")
keys_B = he.multiparty_keygen(cc, keys_A["public_key"])

# Ngân hàng C tham gia, sử dụng public key của B
print("4. Bank C joins, using Bank B's public key...")
keys_C = he.multiparty_keygen(cc, keys_B["public_key"])

# Khóa công khai của C chính là khóa công khai chung cuối cùng
joint_public_key = keys_C["public_key"]
print("   - Joint Public Key generated.")

# --- Giai đoạn 2: Mã hóa ---
# Fintech Partner mã hóa dữ liệu bằng khóa chung
print("5. Fintech Partner encrypts data...")
message = [1.0, 2.5, 3.0, 4.2]
ciphertext_b64 = he.encrypt(cc, joint_public_key, message)
print(f"   - Encryption complete.")

# --- Giai đoạn 3: Giải mã theo ngưỡng ---
print("6. Threshold decryption process starts...")

# Ngân hàng A (Lead Party) tạo phần giải mã đầu tiên
print("   - Bank A (lead) creates its partial decryption...")
part_A = he.partial_decrypt(cc, keys_A["secret_key"], ciphertext_b64, is_lead=True)

# Ngân hàng B và C tạo các phần giải mã của họ
print("   - Bank B creates its partial decryption...")
part_B = he.partial_decrypt(cc, keys_B["secret_key"], ciphertext_b64, is_lead=False)
print("   - Bank C creates its partial decryption...")
part_C = he.partial_decrypt(cc, keys_C["secret_key"], ciphertext_b64, is_lead=False)

# Tổng hợp tất cả các phần giải mã
print("7. Fusing all partial decryptions...")
all_parts = [part_A, part_B, part_C]
decrypted_message = he.combine_partial_decrypt(cc, all_parts)

# --- Giai đoạn 4: Kiểm tra kết quả ---
print("\n--- Verification ---")
print("Original Message:  ", message)
# So sánh với slice của mảng kết quả vì CKKS có thể trả về nhiều giá trị hơn batch size
print("Decrypted Message: ", np.round(decrypted_message[:len(message)], 2))

# Kiểm tra tính đúng đắn
is_correct = np.allclose(message, decrypted_message[:len(message)], atol=0.01)
print(f"Decryption successful: {is_correct}")

```

---

## 6. Lưu ý quan trọng

-   **Thứ tự là tối quan trọng**: Quá trình tạo khóa và giải mã phải tuân thủ đúng thứ tự và vai trò (lead/main party).
-   **Tính nhất quán của Context**: Cùng một `CryptoContext` phải được sử dụng cho tất cả các hoạt động liên quan đến một nhóm khóa.
-   **Bảo mật khóa bí mật**: Mỗi bên phải tự bảo vệ khóa bí mật của mình. Việc lộ một khóa bí mật sẽ phá vỡ an toàn của hệ thống.
-   **Quản lý khóa**: Trong môi trường thực tế, cần có một cơ chế an toàn để trao đổi các khóa công khai và các phần giải mã giữa các bên.

