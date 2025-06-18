# Hệ module mã hóa đồng hình nhiều ngân hàng (`he_crypto_module`)

## 1. Giới thiệu

`he_crypto_module` là một module Python được xây dựng dựa trên thư viện `tenseal` để thực hiện các hoạt động mã hóa đồng cấu đa bên (Multiparty Homomorphic Encryption). Module này cho phép nhiều bên (ví dụ: các ngân hàng) cùng nhau tham gia vào quá trình giải mã một dữ liệu đã được mã hóa mà không cần tiết lộ khóa bí mật riêng của từng bên. Điều này đảm bảo tính riêng tư và an toàn cho dữ liệu nhạy cảm.

Module được thiết kế để phục vụ cho kịch bản một đối tác (Fintech Partner) thực hiện tính toán trên dữ liệu được mã hóa và kết quả chỉ có thể được giải mã khi có sự hợp tác của tất cả các ngân hàng tham gia.

---

## 2. Cài đặt

Để sử dụng module này, bạn cần cài đặt thư viện `tenseal`:

```sh
pip install tenseal
```

---

## 3. Các chức năng chính

Module cung cấp các hàm để thực hiện toàn bộ luồng mã hóa đồng cấu đa bên.

### 3.1. `create_tenseal_context()`

Tạo và trả về một đối tượng context của TenSEAL. Context này chứa các tham số mã hóa (lược đồ, bậc đa thức, ...) và phải được sử dụng nhất quán trong suốt quá trình từ tạo khóa, mã hóa đến giải mã.

### 3.2. `generate_multiparty_keys(context, num_parties)`

-   **Mục đích**: Sinh khóa cho một kịch bản đa bên.
-   **Đầu vào**:
    -   `context`: Context TenSEAL đã được tạo.
    -   `num_parties`: Số lượng bên tham gia (ví dụ: 3 ngân hàng).
-   **Đầu ra**: Một tuple chứa:
    -   `joint_public_key`: Khóa công khai chung, được sử dụng để mã hóa.
    -   `secret_key_shares`: Một list chứa các phần khóa bí mật, mỗi phần dành cho một bên.

### 3.3. `encrypt_data(context, public_key, data)`

-   **Mục đích**: Mã hóa dữ liệu.
-   **Đầu vào**:
    -   `context`: Context TenSEAL.
    -   `public_key`: Khóa công khai (trong kịch bản này là `joint_public_key`).
    -   `data`: Dữ liệu cần mã hóa (dưới dạng list hoặc vector số).
-   **Đầu ra**: `CKKSTensor` đã được mã hóa (ciphertext).

### 3.4. `partial_decrypt(secret_key_share, encrypted_data)`

-   **Mục đích**: Mỗi bên thực hiện giải mã một phần.
-   **Đầu vào**:
    -   `secret_key_share`: Phần khóa bí mật của một bên.
    -   `encrypted_data`: Dữ liệu đã được mã hóa.
-   **Đầu ra**: Một phần giải mã (decryption share).

### 3.5. `combine_partial_decrypt(encrypted_data, decryption_shares)`

-   **Mục đích**: Tổng hợp các phần giải mã để có được kết quả cuối cùng.
-   **Đầu vào**:
    -   `encrypted_data`: Dữ liệu mã hóa gốc.
    -   `decryption_shares`: Một list chứa các phần giải mã từ tất cả các bên.
-   **Đầu ra**: Dữ liệu đã được giải mã hoàn toàn (dưới dạng list số).

### 3.6. Các hàm Serialize/Deserialize

Module cũng cung cấp các hàm để chuyển đổi khóa và ciphertext sang định dạng `base64` (string) để dễ dàng lưu trữ hoặc truyền tải qua mạng.

-   `serialize_...`: Chuyển đối tượng (context, key, ciphertext) thành chuỗi base64.
-   `deserialize_...`: Chuyển chuỗi base64 ngược lại thành đối tượng tương ứng.

---

## 4. Luồng hoạt động mẫu

File `test_multiparty.py` cung cấp một ví dụ hoàn chỉnh về cách sử dụng module này.

```python
import he_crypto_module as he

# 1. Thiết lập môi trường (chung cho tất cả các bên)
num_banks = 3
context = he.create_tenseal_context()

# 2. Sinh khóa đa bên (do một bên khởi tạo hoặc một bên thứ ba đáng tin cậy)
joint_pk, sk_shares = he.generate_multiparty_keys(context, num_banks)

# Phân phối các phần khóa bí mật cho từng ngân hàng
bank1_sk = sk_shares[0]
bank2_sk = sk_shares[1]
bank3_sk = sk_shares[2]

# 3. Mã hóa dữ liệu (do Fintech Partner thực hiện)
message = [10.5, 20.2, -5.7]
encrypted_message = he.encrypt_data(context, joint_pk, message)

# 4. Giải mã đa bên
# a. Mỗi ngân hàng tạo một phần giải mã
dec_share1 = he.partial_decrypt(bank1_sk, encrypted_message)
dec_share2 = he.partial_decrypt(bank2_sk, encrypted_message)
dec_share3 = he.partial_decrypt(bank3_sk, encrypted_message)

# b. Tập hợp và kết hợp các phần giải mã
all_shares = [dec_share1, dec_share2, dec_share3]
decrypted_message = he.combine_partial_decrypt(encrypted_message, all_shares)

# 5. In kết quả
print("Original Message:", message)
print("Decrypted Message:", decrypted_message)
```

---

## 5. Lưu ý quan trọng

-   **Context phải đồng nhất**: Tất cả các bên phải sử dụng cùng một `context` (với cùng tham số) trong suốt quá trình.
-   **Bảo mật khóa bí mật**: Mỗi bên phải giữ an toàn tuyệt đối phần khóa bí mật (`secret_key_share`) của mình.
-   **Đủ số lượng bên tham gia**: Quá trình giải mã chỉ thành công khi có đủ tất cả các phần giải mã từ các bên đã tham gia tạo khóa.

