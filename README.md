# Đề xuất Đồ án: Hệ thống Chấm điểm Tín dụng Bảo toàn Quyền riêng tư sử dụng Mã hóa Đồng cấu và Dịch vụ HE Chuyên biệt

## 1️⃣ Bối cảnh (Context)

Trong lĩnh vực tài chính, các tổ chức tín dụng (Ngân hàng) phải xử lý một lượng lớn dữ liệu cá nhân và tài chính nhạy cảm của khách hàng (thu nhập, lịch sử giao dịch, nợ, v.v.) để tính toán điểm tín dụng. Để tối ưu hóa độ chính xác của mô hình chấm điểm và tận dụng chuyên môn bên ngoài, Ngân hàng thường hợp tác với các Bên thứ ba (Đối tác Fintech) chuyên về phân tích dữ liệu.

Tuy nhiên, việc chia sẻ dữ liệu thô của khách hàng cho Đối tác Fintech gây ra những rủi ro nghiêm trọng về bảo mật và quyền riêng tư, có thể vi phạm các quy định như GDPR hoặc Nghị định 13/2023/NĐ-CP của Việt Nam. Do đó, cần một giải pháp cho phép Đối tác Fintech thực hiện tính toán trên dữ liệu khách hàng mà không cần truy cập vào dữ liệu gốc, đảm bảo an toàn thông tin đầu-cuối. Hệ thống này cũng yêu cầu một dịch vụ chuyên biệt cung cấp các chức năng mã hóa và giải mã đồng cấu, có cơ chế xác thực mạnh mẽ.

## 2️⃣ Phương pháp truyền thống và Hạn chế (Traditional Methods and Limitations)

Các phương pháp hiện tại thường bao gồm mã hóa dữ liệu khi lưu trữ (at-rest) và truyền tải (in-transit) bằng AES hoặc RSA. Tuy nhiên, những hạn chế chính bao gồm:

*   **Dữ liệu phải được giải mã để xử lý:** Tại máy chủ của Đối tác Fintech, dữ liệu bắt buộc phải được giải mã về dạng rõ (plaintext) trước khi có thể thực hiện bất kỳ phép tính nào. Điều này tạo ra một cửa sổ rủi ro nơi dữ liệu nhạy cảm bị phơi bày.
*   **Không hỗ trợ tính toán trên dữ liệu mã hóa:** Các logic nghiệp vụ phức tạp, đặc biệt là các mô hình tính điểm, không thể được thực hiện trực tiếp trên dữ liệu đã mã hóa bằng các phương pháp truyền thống.

Những hạn chế này không đáp ứng được yêu cầu bảo mật dữ liệu đầu-cuối trong toàn bộ quy trình tính toán điểm tín dụng khi có sự tham gia của bên thứ ba.

## 3️⃣ Đề xuất giải pháp mới: Hệ thống Chấm điểm Tín dụng An toàn với Dịch vụ Mã hóa Đồng cấu (HE Service)

Chúng tôi đề xuất xây dựng một "Hệ thống Chấm điểm Tín dụng Bảo toàn Quyền riêng tư" sử dụng kỹ thuật **Mã hóa Đồng cấu Hoàn toàn (Fully Homomorphic Encryption - FHE)**, được hỗ trợ bởi một **Dịch vụ HE (HE Service)** chuyên biệt.

**Luồng hoạt động chính (theo sơ đồ):**
1.  **Khởi tạo khóa (Thông qua HE Service):** Bank System yêu cầu HE Service tạo cặp khóa FHE (Public Key - PK, Secret Key - SK). Bank System lưu giữ SK cẩn mật, và PK được sử dụng cho việc mã hóa và tính toán.
2.  **Mã hóa Dữ liệu (Bank System & HE Service):**
    *   Bank System lấy dữ liệu khách hàng từ **Transaction Database (SQL Server)**.
    *   Bank System gọi **Encrypt API** của HE Service, gửi kèm dữ liệu cần mã hóa, HE Public Key và **Token xác thực (JWT) + Public Key định danh của Bank System**.
    *   HE Service xác thực yêu cầu, sau đó mã hóa dữ liệu bằng HE Public Key và trả về ciphertext cho Bank System.
3.  **Gửi Dữ liệu Mã hóa (Bank System đến Fintech Partner):** Bank System gửi ciphertext và HE Public Key cho Đối tác Fintech.
4.  **Tính toán trên Ciphertext (Fintech Partner):** Đối tác Fintech sử dụng HE Public Key nhận được để thực hiện các thuật toán tính điểm tín dụng trực tiếp trên ciphertext.
5.  **Trả Kết quả Mã hóa (Fintech Partner đến Bank System):** Đối tác Fintech trả kết quả điểm tín dụng (vẫn ở dạng ciphertext) về cho Bank System.
6.  **Giải mã Kết quả (Bank System & HE Service):**
    *   Bank System nhận Encrypted Result.
    *   Bank System gọi **Decrypt API** của HE Service, gửi kèm ciphertext cần giải mã, **HE Secret Key** (do Bank System quản lý) và **Token xác thực (JWT) + Public Key định danh của Bank System**.
    *   HE Service xác thực yêu cầu, sau đó giải mã ciphertext bằng HE Secret Key và trả về kết quả điểm tín dụng dạng rõ cho Bank System.
7.  **Hiển thị Kết quả (Bank System):** Bank System hiển thị điểm tín dụng trên **Credit Score Dashboard** hoặc lưu vào cơ sở dữ liệu.

### 3.1 Kiến trúc hệ thống (System Architecture - Dựa trên sơ đồ)

*   **Bank System (Hệ thống Ngân hàng):**
    *   Tương tác với cơ sở dữ liệu **SQL Server** để lấy dữ liệu khách hàng.
    *   Quản lý và sử dụng **HE Secret Key**.
    *   Gọi các API của **HE Service** (Encrypt, Decrypt) để thực hiện các thao tác mã hóa.
    *   Xác thực với HE Service bằng **JWT và Public Key định danh**.
    *   Giao tiếp với **Fintech Partner** để gửi dữ liệu mã hóa và nhận kết quả mã hóa.
    *   Hiển thị kết quả cuối cùng.
*   **Fintech Partner System (Hệ thống Đối tác Fintech - Mô phỏng):**
    *   Nhận **HE Public Key** và ciphertext từ Bank System.
    *   Thực hiện tính toán điểm tín dụng trên ciphertext.
    *   Trả kết quả (ciphertext) về cho Bank System.
    *   **Không bao giờ có quyền truy cập vào HE Secret Key hoặc dữ liệu gốc của khách hàng.**
*   **HE Service (Dịch vụ Mã hóa Đồng cấu):**
    *   Cung cấp các API chuyên biệt:
        *   `Generate Key API`: Tạo cặp khóa HE (PK, SK) theo yêu cầu.
        *   `Encrypt API`: Nhận dữ liệu, HE Public Key, mã hóa và trả về ciphertext.
        *   `Decrypt API`: Nhận ciphertext, HE Secret Key, giải mã và trả về plaintext.
    *   **Xác thực và Ủy quyền:** Yêu cầu Bank System cung cấp Token (JWT) và Public Key định danh hợp lệ trước khi cho phép sử dụng các API của mình.
    *   **Không lưu trữ HE Secret Key của Bank System** (Bank System gửi SK kèm theo mỗi yêu cầu giải mã).

### 3.2 Kiểm soát truy cập và Bảo mật (Access Control and Security)

*   **Bank System:** Giữ toàn quyền kiểm soát HE Secret Key. Chỉ Bank System mới có thể khởi tạo yêu cầu giải mã dữ liệu.
*   **Fintech Partner:** Chỉ được cấp HE Public Key, chỉ có thể thực hiện tính toán trên ciphertext.
*   **HE Service:** Đóng vai trò là một "cỗ máy" thực thi mã hóa/giải mã. Việc sử dụng dịch vụ này được bảo vệ bởi cơ chế xác thực JWT và Public Key định danh, đảm bảo chỉ Bank System được ủy quyền mới có thể yêu cầu các thao tác liên quan đến khóa của mình. HE Secret Key được truyền từ Bank System đến HE Service cho mỗi thao tác giải mã và không được lưu trữ bởi HE Service.
*   **Mã hóa Đồng cấu Hoàn toàn (FHE) với TenSEAL:** Sử dụng lược đồ CKKS của TenSEAL để làm việc với dữ liệu số thực, cho phép các phép cộng và nhân cần thiết cho mô hình tính điểm.

## 4️⃣ Triển khai Hệ thống Thực tế (Proof of Concept - PoC)

Đồ án sẽ tập trung vào việc xây dựng một Proof-of-Concept (PoC) với các thành phần sau:

➡️ **Bank System (Triển khai Backend)**
*   **Framework:** FastAPI (Python).
*   **Database:** Kết nối và truy vấn **SQL Server** (sử dụng thư viện như `pyodbc` hoặc `SQLAlchemy`).
*   **Tương tác HE:** Gọi các API của HE Service để mã hóa và giải mã dữ liệu. Quản lý việc gửi HE Secret Key an toàn đến HE Service khi giải mã.
*   **Xác thực:** Tạo và gửi JWT + Public Key định danh đến HE Service.
*   **Thư viện HE (để quản lý khóa và hiểu cấu trúc dữ liệu):** **TenSEAL**.

➡️ **Fintech Partner System (Mô phỏng Backend)**
*   **Framework:** FastAPI (Python).
*   **Tính toán HE:** Sử dụng **TenSEAL** và HE Public Key nhận được để thực hiện các phép toán trên ciphertext.
*   **Chức năng API:** Endpoint nhận dữ liệu mã hóa, thực hiện tính toán, endpoint trả kết quả mã hóa.

➡️ **HE Service (Triển khai Backend)**
*   **Framework:** FastAPI (Python).
*   **Chức năng API:**
    *   `/generate-keys`: Tạo cặp khóa TenSEAL (context, public key, secret key).
    *   `/encrypt`: Nhận data, TenSEAL public key, mã hóa bằng TenSEAL. Yêu cầu JWT + Public Key định danh để xác thực.
    *   `/decrypt`: Nhận ciphertext, TenSEAL secret key, giải mã bằng TenSEAL. Yêu cầu JWT + Public Key định danh để xác thực.
*   **Thư viện HE:** **TenSEAL** để thực hiện các thao tác cốt lõi.
*   **Xác thực:** Triển khai logic xác thực JWT và Public Key định danh.

## 5️⃣ Công nghệ sử dụng (Proposed Technology Stack)

| Thành phần             | Công nghệ chính                                      | Mục đích                                                         |
| :--------------------- | :---------------------------------------------------- | :--------------------------------------------------------------- |
| **Bank System**        | Python, FastAPI                                     | Xây dựng API backend, logic nghiệp vụ, gọi HE Service           |
|                        | **SQL Server** (DB)                                   | Lưu trữ dữ liệu giao dịch của khách hàng                         |
|                        | `pyodbc` / `SQLAlchemy`                              | Kết nối và tương tác với SQL Server từ Python                     |
|                        | **TenSEAL**                                           | Để Bank System hiểu và quản lý các đối tượng khóa/ciphertext    |
|                        | Thư viện JWT (ví dụ: `PyJWT`)                         | Tạo và quản lý JWT cho việc xác thực với HE Service             |
| **Fintech Partner**    | Python, FastAPI                                     | Mô phỏng API backend, logic tính toán HE                       |
|                        | **TenSEAL**                                           | Thực hiện tính toán trên ciphertext bằng HE Public Key           |
| **HE Service**         | Python, FastAPI                                     | Cung cấp các API mã hóa, giải mã, sinh khóa chuyên biệt          |
|                        | **TenSEAL**                                           | Thư viện cốt lõi để thực hiện các phép toán HE                   |
|                        | Thư viện JWT (ví dụ: `PyJWT`)                         | Xác thực token từ Bank System                                  |

## 6️⃣ Mục tiêu Đồ án & Các bước thực hiện dự kiến (Project Goals & Initial Milestones)

*   **Mục tiêu chính:**
    1.  Nghiên cứu sâu về FHE, cụ thể là lược đồ CKKS của TenSEAL.
    2.  Thiết kế và triển khai thành công PoC với kiến trúc 3 thành phần (Bank System, Fintech Partner, HE Service) như sơ đồ.
    3.  Triển khai cơ chế xác thực JWT + Public Key định danh cho HE Service.
    4.  Chứng minh khả năng mã hóa dữ liệu từ SQL Server, gửi đi tính toán, nhận lại và giải mã thành công.
    5.  Đánh giá sơ bộ về hiệu năng của hệ thống.
*   **Các bước thực hiện dự kiến:**
    1.  Thiết lập môi trường, cài đặt các thư viện cần thiết (FastAPI, TenSEAL, pyodbc/SQLAlchemy, PyJWT).
    2.  **HE Service:**
        *   Triển khai API `/generate-keys`.
        *   Triển khai API `/encrypt` và `/decrypt` sử dụng TenSEAL.
        *   Tích hợp cơ chế xác thực JWT + Public Key định danh cho các API của HE Service.
    3.  **Bank System:**
        *   Triển khai logic gọi API `/generate-keys` của HE Service để lấy khóa, lưu SK an toàn.
        *   Kết nối SQL Server, lấy dữ liệu.
        *   Triển khai logic tạo JWT, gọi API `/encrypt` của HE Service.
        *   Triển khai logic gọi API `/decrypt` của HE Service, truyền SK một cách an toàn.
    4.  **Fintech Partner:** Triển khai API nhận ciphertext, thực hiện tính toán mẫu bằng TenSEAL, trả kết quả.
    5.  Kiểm thử toàn bộ luồng hoạt động của hệ thống.

## 7️⃣ Khó khăn và Thách thức (Potential Difficulties and Challenges)

*   **Độ phức tạp của FHE (TenSEAL/CKKS):** Hiểu rõ về tham số, quản lý "noise", đảm bảo độ chính xác (precision) cho CKKS.
*   **Triển khai Xác thực An toàn:** Đảm bảo cơ chế JWT và quản lý Public Key định danh được triển khai đúng cách và an toàn.
*   **Truyền Secret Key An toàn:** Việc Bank System gửi HE Secret Key đến HE Service cho mỗi yêu cầu giải mã cần được thực hiện qua kênh mã hóa mạnh (HTTPS) và HE Service không được lưu trữ SK này.
*   **Hiệu năng:** FHE vốn có chi phí tính toán cao. Việc gọi API qua mạng cho mỗi thao tác mã hóa/giải mã có thể tăng thêm độ trễ.
*   **Quản lý khóa:** Ngoài HE Secret Key, còn có các khóa dùng cho JWT, Public Key định danh. Việc quản lý vòng đời của tất cả các khóa này trong một hệ thống thực tế là phức tạp.
*   **Tích hợp SQL Server:** Đảm bảo kết nối và truy vấn dữ liệu từ SQL Server hiệu quả.

## 8️⃣ Hướng đi trong tương lai (Future Directions)

*   **Tối ưu hóa hiệu suất HE Service:** Nghiên cứu các kỹ thuật batching cho yêu cầu mã hóa/giải mã, hoặc sử dụng các giải pháp tăng tốc phần cứng (nếu có).
*   **Cơ chế quản lý HE Secret Key nâng cao:** Thay vì Bank System gửi SK mỗi lần, có thể nghiên cứu tích hợp HE Service với một Hardware Security Module (HSM) nơi SK của Bank được lưu trữ và HE Service chỉ gọi các hàm của HSM.
*   **Mô hình tính điểm phức tạp hơn:** Áp dụng cho các mô hình Machine Learning có thể được biểu diễn bằng các phép toán FHE hỗ trợ.
*   **Mở rộng HE Service:** Hỗ trợ nhiều lược đồ HE khác nhau, hoặc các cấu hình tham số linh hoạt hơn.
*   **Giám sát và Logging:** Xây dựng hệ thống giám sát hoạt động và ghi log chi tiết cho HE Service và các tương tác.
