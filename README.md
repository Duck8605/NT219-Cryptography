# Applying Homomorphic Encryption in Finance Service (Credit Scoring)

## 1. Bối cảnh

Trong lĩnh vực tài chính, Ngân hàng A phải xử lý một lượng lớn dữ liệu cá nhân và tài chính nhạy cảm của khách hàng để tính toán điểm tín dụng. Để tối ưu hóa độ chính xác của mô hình và tận dụng chuyên môn bên ngoài, Ngân hàng A thường hợp tác với các Bên thứ ba (Fintech Partner) chuyên về phân tích dữ liệu.

Tuy nhiên, việc gửi dữ liệu thô của khách hàng cho Fintech Partner gây ra những rủi ro nghiêm trọng về bảo mật và quyền riêng tư, vi phạm các quy định bảo mật dữ liệu. Do đó, cần một giải pháp cho phép Fintech Partner thực hiện tính toán trên dữ liệu khách hàng mà không cần truy cập vào dữ liệu gốc, đảm bảo an toàn thông tin đầu-cuối. Hệ thống này yêu cầu một dịch vụ chuyên biệt cung cấp các chức năng mã hóa đồng cấu (homomorphic encryption), với cơ chế xác thực để kiểm soát việc truy cập và sử dụng dịch vụ.

## 2. Phương pháp truyền thống

Các phương pháp hiện tại thường bao gồm mã hóa dữ liệu khi lưu trữ và truyền tải. Tuy nhiên, hạn chế chính là dữ liệu *bắt buộc phải được giải mã* tại máy chủ của Fintech Partner trước khi thực hiện bất kỳ phép tính nào, làm mất đi tính riêng tư trong quá trình xử lý. Các logic nghiệp vụ phức tạp không thể được thực hiện trực tiếp trên dữ liệu đã mã hóa bằng các phương pháp này.

## 3. Đề xuất giải pháp mới

Chúng tôi đề xuất xây dựng một "Hệ thống Chấm điểm Tín dụng Bảo toàn Quyền riêng tư" sử dụng kỹ thuật **Mã hóa Đồng cấu Hoàn toàn (Fully Homomorphic Encryption - FHE)**, được hỗ trợ bởi một **Dịch vụ HE (HE Service)** chuyên biệt. Cơ chế xác thực truy cập HE Service sẽ dựa trên JWT và Khóa công khai định danh của Bank System.

**Luồng hoạt động chính của hệ thống:**

1.  **Xác thực Bank System với HE Service:**
    *   Bank System sở hữu một cặp khóa bất đối xứng định danh (ECDSA), gồm `Bank_Identity_SK` (Secret key) và `Bank_Identity_PK` (Public key).
    *   Khi Bank System muốn gọi **bất kỳ API nào** của HE Service (`/generate-keys`, `/encrypt`, `/decrypt`), nó sẽ:
        *   Tạo một JSON Web Token (JWT) chứa các thông tin cần thiết (ví dụ: `issuer`, `subject`, `expiration`).
        *   Ký JWT này bằng `Bank_Identity_SK`.
        *   Gửi yêu cầu đến HE Service, đính kèm JWT đã ký.
    *   **HE Service sẽ:**
        *   `Bank_Identity_PK` đã được thỏa thuận trước giữa Bank System và HE Service.
        *   Nhận JWT từ Bank System.
        *   Sử dụng `Bank_Identity_PK` này để xác minh chữ ký của JWT.
        *   Nếu JWT hợp lệ (chữ ký đúng, chưa hết hạn, đúng bên nhận, bên gửi), HE Service mới tiếp tục xử lý yêu cầu API tương ứng. Nếu không, yêu cầu sẽ bị từ chối.

2.  **Khởi tạo khóa HE (Thông qua HE Service):**
    *   Sau khi được HE Service xác thực, Bank System gọi `Generate HE Keys API` (`/generate-keys`).
    *   HE Service tạo cặp khóa FHE (gồm HE Public Key - `HE_PK`, và HE Secret Key - `HE_SK`).
    *   HE Service trả về `HE_PK` và `HE_SK` cho Bank System. Bank System lưu giữ `HE_SK` cẩn mật.

3.  **Mã hóa Dữ liệu (Bank System & HE Service):**
    *   Bank System lấy dữ liệu khách hàng từ **Transaction Database (SQL Server)**.
    *   Bank System (sau khi đã được HE Service xác thực như bước 1) gọi `Encrypt API` (`/encrypt`) của HE Service, gửi kèm dữ liệu cần mã hóa và `HE_PK` (đã có từ bước 2).
    *   HE Service mã hóa dữ liệu bằng `HE_PK` và trả về ciphertext cho Bank System.

4.  **Gửi Dữ liệu Mã hóa (Bank System đến Fintech Partner):** Bank System gửi ciphertext và `HE_PK` cho Đối tác Fintech.

5.  **Tính toán trên Ciphertext (Fintech Partner):** Đối tác Fintech sử dụng `HE_PK` nhận được để thực hiện các thuật toán tính điểm tín dụng trực tiếp trên ciphertext.

6.  **Trả Kết quả Mã hóa (Fintech Partner đến Bank System):** Đối tác Fintech trả kết quả điểm tín dụng (vẫn ở dạng ciphertext) về cho Bank System.

7.  **Giải mã Kết quả (Bank System & HE Service):**
    *   Bank System nhận Encrypted Result.
    *   Bank System (sau khi đã được HE Service xác thực như bước 1) gọi `Decrypt API` (`/decrypt`) của HE Service, gửi kèm ciphertext cần giải mã và `HE_SK` (do Bank System quản lý và cung cấp cho HE Service trong mỗi yêu cầu giải mã).
    *   HE Service giải mã ciphertext bằng `HE_SK` và trả về kết quả điểm tín dụng dạng rõ cho Bank System.

8.  **Lưu trữ Kết quả (Bank System):** Bank System lưu vào cơ sở dữ liệu.

### 3.1. Kiến trúc hệ thống

Hệ thống được thiết kế với ba thành phần chính:

*   **Bank System (Hệ thống Ngân hàng):**
    *   Sở hữu một cặp khóa định danh (`Bank_Identity_SK`, `Bank_Identity_PK`).
    *   Quản lý và bảo vệ **HE Secret Key (`HE_SK`)**.
    *   Tương tác với **SQL Server** để quản lý dữ liệu khách hàng.
    *   Gọi các API của **HE Service**, thực hiện xác thực bằng JWT (ký bởi `Bank_Identity_SK`) và `Bank_Identity_PK`.
    *   Giao tiếp với **Fintech Partner**.
*   **Fintech Partner System (Hệ thống Đối tác Fintech - Mô phỏng):**
    *   Nhận **HE Public Key (`HE_PK`)** và ciphertext từ Bank System.
    *   Thực hiện tính toán điểm tín dụng trên ciphertext.
    *   **Không bao giờ có quyền truy cập vào `HE_SK` hoặc dữ liệu gốc.**
*   **HE Service (Dịch vụ Mã hóa Đồng cấu):**
    *   Cung cấp các API: `/generate-keys`, `/encrypt`, `/decrypt`.
    *   **Xác thực mọi yêu cầu API** bằng cách sử dụng `Bank_Identity_PK` (do Bank System gửi kèm) để xác minh chữ ký của JWT (do Bank System ký bằng `Bank_Identity_SK`).
    *   **Không lưu trữ `HE_SK` của Bank System.** `HE_SK` được Bank System cung cấp cho HE Service trong mỗi yêu cầu giải mã.

### 3.2. Kiểm soát truy cập và Bảo mật

*   **Xác thực nguồn gốc yêu cầu:** HE Service chỉ chấp nhận các yêu cầu API nếu JWT đi kèm được xác thực thành công bằng `Bank_Identity_PK` mà Bank System cung cấp. Điều này đảm bảo chỉ Bank System đã đăng ký và được biết đến mới có thể sử dụng dịch vụ.
*   **Quản lý khóa HE:** Bank System giữ toàn quyền kiểm soát `HE_SK`. Fintech Partner chỉ có `HE_PK`.
*   **Mã hóa Đồng cấu Hoàn toàn (FHE) với TenSEAL:** Sử dụng thư viện **TenSEAL** với lược đồ CKKS.

## 4. Triển khai Hệ thống Thực tế (Proof of Concept - PoC)

Đồ án sẽ tập trung vào việc xây dựng một Proof-of-Concept (PoC) với các thành phần sau:

*   **Bank System (Triển khai Backend):**
    *   **Framework:** FastAPI (Python).
    *   **Database:** **SQL Server** (sử dụng `SQLAlchemy`).
    *   **Xác thực với HE Service:** Tạo JWT, ký bằng `Bank_Identity_SK`, gửi JWT và `Bank_Identity_PK` khi gọi API của HE Service.
    *   **Tương tác HE:** Gọi `/generate-keys`, `/encrypt`, `/decrypt` của HE Service. Quản lý `HE_SK`.
    *   **Thư viện:** **TenSEAL** (quản lý cấu trúc khóa/ciphertext HE), `PyJWT`, thư viện cho khóa bất đối xứng (ví dụ: `cryptography`).
*   **Fintech Partner System (Mô phỏng Backend):**
    *   **Framework:** FastAPI (Python).
    *   **Tính toán HE:** Sử dụng **TenSEAL** và `HE_PK`.
*   **HE Service (Triển khai Backend):**
    *   **Framework:** FastAPI (Python).
    *   **API Endpoints:** `/generate-keys`, `/encrypt`, `/decrypt`.
    *   **Xác thực:** Triển khai logic xác minh JWT bằng `Bank_Identity_PK` nhận được.
    *   **Thư viện HE:** **TenSEAL**.
    *   **Thư viện Xác thực:** `PyJWT`, thư viện cho khóa bất đối xứng (ví dụ: `cryptography`).

## 5. Công nghệ sử dụng

| Thành phần          | Công nghệ chính     | Mục đích                                                        |
| :------------------ | :------------------ | :-------------------------------------------------------------- |
| **Bank System**     | Python, FastAPI     | Xây dựng API backend, logic nghiệp vụ, gọi HE Service           |
|                     | **SQL Server** (DB) | Lưu trữ dữ liệu giao dịch của khách hàng                        |
|                     | `SQLAlchemy`        | Kết nối và tương tác với SQL Server từ Python                   |
|                     | **TenSEAL**         | Để Bank System hiểu và quản lý các đối tượng khóa/ciphertext HE |
|                     | `PyJWT`             | Tạo/ký JWT, quản lý cặp khóa định danh của Bank System          |
| **Fintech Partner** | Python, FastAPI     | Mô phỏng API backend, logic tính toán HE                        |
|                     | **TenSEAL**         | Thực hiện tính toán trên ciphertext bằng `HE_PK`                |
| **HE Service**      | Python, FastAPI     | Cung cấp các API mã hóa, giải mã, sinh khóa chuyên biệt         |
|                     | **TenSEAL**         | Thư viện cốt lõi để thực hiện các phép toán HE                  |
|                     | `PyJWT`             | Xác thực JWT bằng `Bank_Identity_PK` nhận được                  |

## 6. Mục tiêu Đồ án và Các bước thực hiện dự kiến

*   **Mục tiêu chính:**
    1.  Nghiên cứu sâu về FHE (TenSEAL/CKKS).
    2.  Thiết kế và triển khai PoC với kiến trúc 3 thành phần.
    3.  Chứng minh luồng hoạt động hoàn chỉnh: từ lấy dữ liệu SQL Server, xác thực với HE Service, mã hóa, gửi đi tính toán, nhận lại, giải mã.
    4.  Đánh giá sơ bộ hiệu năng.
*   **Các bước thực hiện dự kiến:**
    1.  Thiết lập môi trường, cài đặt thư viện.
    2.  **Bank System:** Tạo cặp khóa định danh (`Bank_Identity_SK`, `Bank_Identity_PK`).
    3.  **HE Service:**
        *   Triển khai API `/generate-keys`, `/encrypt`, `/decrypt`.
        *   Tích hợp logic xác thực JWT (sử dụng `Bank_Identity_PK` nhận được từ Bank System).
    4.  **Bank System:**
        *   Triển khai logic tạo và ký JWT bằng `Bank_Identity_SK`.
        *   Gọi API `/generate-keys` (kèm JWT và `Bank_Identity_PK`) để lấy `HE_PK`, `HE_SK`. Lưu `HE_SK`.
        *   Kết nối SQL Server, lấy dữ liệu.
        *   Gọi API `/encrypt` (kèm JWT, `Bank_Identity_PK`, data, `HE_PK`).
        *   Gọi API `/decrypt` (kèm JWT, `Bank_Identity_PK`, encrypted result, `HE_SK`).
    5.  **Fintech Partner:** Triển khai API nhận ciphertext, tính toán mẫu, trả kết quả.
    6.  Kiểm thử toàn bộ luồng.

## 7. Khó khăn và Thách thức

*   **Độ phức tạp của FHE (TenSEAL/CKKS):** Tham số, quản lý "noise", độ chính xác.
*   **Triển khai Xác thực An toàn:** Đảm bảo JWT và việc sử dụng `Bank_Identity_PK` để xác minh là an toàn, chống giả mạo. Đăng ký và quản lý `Bank_Identity_PK` của các Bank System client tại HE Service.
*   **Truyền `HE_SK` An toàn:** Việc Bank System gửi `HE_SK` đến HE Service cho yêu cầu giải mã phải qua kênh mã hóa (HTTPS).
*   **Hiệu năng:** FHE, gọi API qua mạng, xác thực JWT.
*   **Quản lý Vòng đời Khóa:** `HE_SK`, `Bank_Identity_SK`/`PK`.
*   **Tích hợp SQL Server:** Kết nối, truy vấn, xử lý kiểu dữ liệu.

## 8. Hướng đi trong tương lai

*   **Tối ưu hóa hiệu suất HE Service.**
*   **Nâng cao cơ chế quản lý `HE_SK`.**
*   **Mô hình tính điểm phức tạp hơn.**
*   **Giám sát, Logging và Alerting.**
*   **Đăng ký và quản lý `Bank_Identity_PK`:** Xây dựng cơ chế cho HE Service để quản lý danh sách các `Bank_Identity_PK` được phép truy cập.
