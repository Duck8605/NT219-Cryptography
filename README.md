# Applying Homomorphic Encryption in Finance Service (Credit Scoring)

## 1. Bối cảnh
Trong lĩnh vực tài chính, một liên minh gồm ba ngân hàng cần xử lý dữ liệu nhạy cảm của khách hàng để tính điểm tín dụng. Để tận dụng chuyên môn bên ngoài, các ngân hàng hợp tác với một Fintech Partner. Tuy nhiên, việc chia sẻ dữ liệu thô gây rủi ro bảo mật và vi phạm quyền riêng tư. Hệ thống này giải quyết bài toán cho phép Fintech Partner tính toán trên dữ liệu mã hóa mà không biết dữ liệu gốc, nhờ một module mã hóa đồng cấu đa bên (Multiparty Homomorphic Encryption - HE).

## 2. Phương pháp truyền thống
Các giải pháp mã hóa truyền thống chỉ bảo vệ dữ liệu khi lưu trữ/truyền tải, nhưng vẫn phải giải mã khi xử lý tại Fintech Partner, làm mất tính riêng tư. Không thể thực hiện các phép toán phức tạp trực tiếp trên dữ liệu mã hóa.

## 3. Đề xuất giải pháp mới
Chúng tôi đề xuất xây dựng một "Hệ thống Chấm điểm Tín dụng Bảo toàn Quyền riêng tư" sử dụng kỹ thuật Mã hóa Đồng cấu Đa bên. Thay vì một dịch vụ tập trung, hệ thống sử dụng một module Python (`he_crypto_module.py`) cho phép nhiều bên (ngân hàng) cùng tham gia vào quá trình mã hóa và giải mã mà không cần tiết lộ khóa bí mật của mình.

Luồng hoạt động chính của hệ thống:

-   **Các Ngân hàng** cùng nhau tạo ra một khóa công khai chung và mỗi ngân hàng giữ một phần của khóa bí mật.
-   **Fintech Partner** chỉ nhận khóa công khai chung để mã hóa dữ liệu và thực hiện tính toán.
-   **Giải mã** yêu cầu sự hợp tác của tất cả các ngân hàng, đảm bảo không một bên nào có thể đơn phương giải mã dữ liệu.

### 3.1. Kiến trúc hệ thống
Hệ thống được thiết kế với các thành phần chính:

**Hệ thống các Ngân hàng (Bank Systems):**
-   Mỗi ngân hàng trong liên minh (ví dụ: Bank A, Bank B, Bank C) giữ một phần bí mật của khóa giải mã (HE Secret Key fragment).
-   Các ngân hàng cùng nhau tạo ra một khóa công khai chung (Joint Public Key) và chia sẻ nó cho Fintech Partner.
-   Sử dụng module `he_crypto_module.py` để thực hiện các hoạt động mã hóa.

**Fintech Partner System (Hệ thống Đối tác Fintech):**
-   Nhận Joint Public Key và ciphertext.
-   Thực hiện tính toán điểm tín dụng trên ciphertext.
-   Không bao giờ có quyền truy cập vào bất kỳ phần nào của khóa bí mật hoặc dữ liệu gốc.

**HE Service (Module Mã hóa Đồng cấu):**
-   Là một module Python (`he_crypto_module.py`) cung cấp các hàm cho mã hóa đồng cấu đa bên.
-   Cung cấp các hàm: `generate_keys`, `encrypt_data`, và các hàm cần thiết cho việc giải mã đa bên.
-   Khóa bí mật được quản lý phân tán tại mỗi ngân hàng.

### 3.2. Kiểm soát truy cập và Bảo mật
-   Mỗi ngân hàng giữ toàn quyền kiểm soát phần khóa bí mật của mình. Fintech Partner chỉ có khóa công khai chung.
-   Quá trình giải mã đa bên đảm bảo rằng kết quả chỉ có thể được tiết lộ khi có sự đồng thuận của tất cả các bên tham gia.
-   Sử dụng thư viện TenSEAL với lược đồ CKKS để thực hiện các phép toán đồng cấu.

## 4. Triển khai Hệ thống Thực tế
Luồng triển khai chi tiết trong kịch bản 3 ngân hàng và 1 đối tác Fintech:

1.  **Bước 1: Tạo khóa đa bên (Multiparty Key Generation)**: Mỗi ngân hàng tự tạo ra một cặp khóa công khai/bí mật riêng. Sau đó, họ kết hợp các khóa công khai riêng lẻ để tạo thành một `joint_public_key` (khóa công khai chung). Khóa này được chia sẻ an toàn cho Fintech Partner. Mỗi ngân hàng giữ lại khóa bí mật của riêng mình.

2.  **Bước 2: Mã hóa dữ liệu**: Fintech Partner nhận dữ liệu từ khách hàng và sử dụng `joint_public_key` để mã hóa, tạo ra `ciphertext`.

3.  **Bước 3: Tính toán trên dữ liệu mã hóa**: Fintech Partner áp dụng mô hình chấm điểm tín dụng của mình trên `ciphertext`. Mọi tính toán đều được thực hiện đồng cấu, cho ra kết quả là một điểm tín dụng đã được mã hóa.

4.  **Bước 4: Giải mã đa bên (Multiparty Decryption)**:
    -   Kết quả mã hóa được gửi đến cả ba ngân hàng.
    -   Mỗi ngân hàng sử dụng khóa bí mật của mình để tạo ra một `partial_decryption` (phần giải mã).
    -   Các phần giải mã này được tập hợp lại và kết hợp để có được điểm tín dụng cuối cùng dưới dạng plaintext.

![image](https://github.com/user-attachments/assets/95434080-d0e9-4b10-a0dd-1d998a354edc)

## 5. Công nghệ sử dụng
| Thành phần      | Công nghệ chính                      | Mục đích                                                                        |
| --------------- | ------------------------------------ | ------------------------------------------------------------------------------- |
| Bank System     | Python, FastAPI, SQLAlchemy, TenSEAL | Xây dựng API backend, quản lý dữ liệu, mã hóa/giải mã, import he_crypto.pyd     |
| Fintech Partner | Python, FastAPI, TenSEAL             | Nhận ciphertext, tính toán trên ciphertext, không có HE_SK                      |
| HE Service      | TenSEAL, Python                      | Cung cấp các hàm mã hóa, giải mã, sinh khóa chuyên biệt dưới dạng thư viện .pyd |
| Bank Systems    | Python, TenSEAL                      | Tạo và quản lý các phần của khóa bí mật, tham gia vào quá trình giải mã đa bên |

## 6. Mục tiêu và các bước thực hiện
- Nghiên cứu FHE (TenSEAL/CKKS).
- Thiết kế, triển khai PoC kiến trúc 3 thành phần.
- Chứng minh luồng: tạo khóa đa bên, mã hóa, gửi đi tính toán, nhận lại, giải mã đa bên.

**Các bước:**
1.  Thiết lập môi trường, cài đặt thư viện (`pip install tenseal`).
2.  Chạy script `test_multiparty.py` để mô phỏng quá trình.
3.  Script sẽ sinh ra các khóa riêng cho 3 ngân hàng, một khóa công khai chung, và mã hóa một tin nhắn mẫu.
4.  Script thực hiện giải mã đa bên và xác minh kết quả.

**Chạy kịch bản mô phỏng (Running the Simulation Script)**
Kịch bản `test_multiparty.py` trong thư mục `HE_service` mô phỏng toàn bộ luồng làm việc trên.

Để chạy thử nghiệm:
```bash
python test_multiparty.py
```
Script sẽ in ra tin nhắn gốc, tin nhắn đã giải mã, và xác nhận tính đúng đắn. Đồng thời, nó sẽ tạo ra các file sau:
-   `bank1_sk.txt`, `bank2_sk.txt`, `bank3_sk.txt`: Các phần khóa bí mật của mỗi ngân hàng.
-   `joint_pk.txt`: Khóa công khai chung.
-   `ciphertext.txt`: Dữ liệu đã được mã hóa.

## 7. Khó khăn và thách thức
- Độ phức tạp FHE (tham số, noise, độ chính xác).
- Quản lý HE_SK an toàn.
- Hiệu năng FHE.
- Quản lý vòng đời khóa trong môi trường đa bên.
- Đảm bảo tính toàn vẹn và thứ tự của các phần giải mã.

## 8. Hướng phát triển tương lai
- Tối ưu hiệu suất HE Service.
- Nâng cao quản lý HE_SK.
- Mô hình tính điểm phức tạp hơn.
- Giám sát, logging, alerting.
- Đăng ký/quản lý Bank_Identity_PK động cho HE Service.

