# Đề xuất Đồ án: Hệ thống Chấm điểm Tín dụng Bảo toàn Quyền riêng tư sử dụng Mã hóa Đồng cấu và Dịch vụ HE Chuyên biệt

## 1. Bối cảnh

Trong lĩnh vực tài chính, các tổ chức tín dụng (Ngân hàng) phải xử lý một lượng lớn dữ liệu cá nhân và tài chính nhạy cảm của khách hàng (thu nhập, lịch sử giao dịch, nợ, v.v.) để tính toán điểm tín dụng. Để tối ưu hóa độ chính xác của mô hình chấm điểm và tận dụng chuyên môn bên ngoài, Ngân hàng thường hợp tác với các Bên thứ ba (Đối tác Fintech) chuyên về phân tích dữ liệu.

Tuy nhiên, việc gửi dữ liệu thô của khách hàng cho Đối tác Fintech gây ra những rủi ro nghiêm trọng về bảo mật và quyền riêng tư, có thể vi phạm các quy định như GDPR hoặc Nghị định 13/2023/NĐ-CP của Việt Nam về Bảo vệ dữ liệu cá nhân. Do đó, cần một giải pháp cho phép Đối tác Fintech thực hiện tính toán trên dữ liệu khách hàng mà không cần truy cập vào dữ liệu gốc, đảm bảo an toàn thông tin đầu-cuối. Hệ thống này yêu cầu một dịch vụ chuyên biệt cung cấp các chức năng mã hóa và giải mã đồng cấu, có cơ chế xác thực mạnh mẽ để kiểm soát truy cập.

## 2. Phương pháp truyền thống và Hạn chế

Các phương pháp bảo vệ dữ liệu hiện tại mà các tổ chức tài chính thường áp dụng bao gồm:

*   **Mã hóa khi lưu trữ và truyền tải (Encryption at Rest & In Transit):** Sử dụng các thuật toán mã hóa đối xứng (AES) hoặc bất đối xứng (RSA) để bảo vệ dữ liệu khi được lưu trữ trong cơ sở dữ liệu hoặc khi truyền đi giữa các hệ thống.
    *   **Hạn chế:** Dữ liệu *bắt buộc phải được giải mã* tại máy chủ của Đối tác Fintech trước khi thực hiện bất kỳ phép tính nào (ví dụ: xây dựng mô hình, tính điểm tín dụng). Điều này tạo ra một "điểm yếu" nơi dữ liệu nhạy cảm bị phơi bày, làm mất đi tính riêng tư trong quá trình xử lý.
*   **Giải pháp che mờ/giải danh (Data Masking/Anonymization):**
    *   **Hạn chế:** Có thể làm giảm độ chính xác của mô hình tính điểm tín dụng. Dữ liệu giải danh vẫn có nguy cơ bị tái định danh (re-identification attack) khi kết hợp với các nguồn dữ liệu khác.

Những hạn chế này không đáp ứng được yêu cầu bảo mật dữ liệu đầu-cuối trong toàn bộ quy trình tính toán điểm tín dụng khi có sự tham gia của bên thứ ba.

## 3. Đề xuất giải pháp mới: Hệ thống Chấm điểm Tín dụng An toàn với Dịch vụ Mã hóa Đồng cấu (HE Service)

Chúng tôi đề xuất xây dựng một "Hệ thống Chấm điểm Tín dụng Bảo toàn Quyền riêng tư" sử dụng kỹ thuật **Mã hóa Đồng cấu Hoàn toàn (Fully Homomorphic Encryption - FHE)**, được hỗ trợ bởi một **Dịch vụ HE (HE Service)** chuyên biệt và có cơ chế xác thực.

**Luồng hoạt động chính của hệ thống:**
1.  **Khởi tạo khóa (Thông qua HE Service):** Bank System yêu cầu HE Service (thông qua `Generate Key API`) tạo cặp khóa FHE (Public Key - PK, Secret Key - SK). Bank System lưu giữ SK cẩn mật, và PK được sử dụng cho việc mã hóa và tính toán.
2.  **Mã hóa Dữ liệu (Bank System & HE Service):**
    *   Bank System lấy dữ liệu khách hàng từ **Transaction Database (SQL Server)**.
    *   Bank System gọi **Encrypt API** của HE Service. Để sử dụng API này, Bank System phải gửi kèm dữ liệu cần mã hóa, HE Public Key, cùng với **Token xác thực (JWT)** và **Public Key định danh của Bank System** (Bank's PK for ID) để HE Service xác thực.
    *   Sau khi xác thực thành công, HE Service mã hóa dữ liệu bằng HE Public Key và trả về ciphertext cho Bank System.
3.  **Gửi Dữ liệu Mã hóa (Bank System đến Fintech Partner):** Bank System gửi ciphertext và HE Public Key cho Đối tác Fintech.
4.  **Tính toán trên Ciphertext (Fintech Partner):** Đối tác Fintech sử dụng HE Public Key nhận được để thực hiện các thuật toán tính điểm tín dụng trực tiếp trên ciphertext.
5.  **Trả Kết quả Mã hóa (Fintech Partner đến Bank System):** Đối tác Fintech trả kết quả điểm tín dụng (vẫn ở dạng ciphertext) về cho Bank System.
6.  **Giải mã Kết quả (Bank System & HE Service):**
    *   Bank System nhận Encrypted Result.
    *   Bank System gọi **Decrypt API** của HE Service. Để sử dụng API này, Bank System phải gửi kèm ciphertext cần giải mã, **HE Secret Key** (do Bank System quản lý và cung cấp cho HE Service trong mỗi yêu cầu giải mã), cùng với **Token xác thực (JWT)** và **Public Key định danh của Bank System**.
    *   Sau khi xác thực thành công, HE Service giải mã ciphertext bằng HE Secret Key và trả về kết quả điểm tín dụng dạng rõ cho Bank System.
7.  **Hiển thị/Lưu trữ Kết quả (Bank System):** Bank System hiển thị điểm tín dụng trên **Credit Score Dashboard** hoặc lưu vào cơ sở dữ liệu.

### 3.1. Kiến trúc hệ thống

Hệ thống được thiết kế với ba thành phần chính:

*   **Bank System (Hệ thống Ngân hàng):**
    *   Là chủ sở hữu dữ liệu và người dùng cuối của điểm tín dụng.
    *   Tương tác với cơ sở dữ liệu **SQL Server** để quản lý dữ liệu khách hàng.
    *   Quản lý và bảo vệ **HE Secret Key**.
    *   Gọi các API của **HE Service** để thực hiện các thao tác mã hóa (sinh khóa, mã hóa, giải mã).
    *   Thực hiện xác thực với HE Service bằng cách gửi **JWT và Public Key định danh** của mình.
    *   Giao tiếp với **Fintech Partner** để gửi dữ liệu mã hóa và nhận kết quả mã hóa.
*   **Fintech Partner System (Hệ thống Đối tác Fintech - Mô phỏng):**
    *   Đóng vai trò là bên xử lý dữ liệu (tính toán điểm tín dụng).
    *   Nhận **HE Public Key** và ciphertext từ Bank System.
    *   Thực hiện tính toán điểm tín dụng trên ciphertext.
    *   Trả kết quả (ciphertext) về cho Bank System.
    *   **Quan trọng:** Không bao giờ có quyền truy cập vào HE Secret Key hoặc dữ liệu gốc của khách hàng.
*   **HE Service (Dịch vụ Mã hóa Đồng cấu):**
    *   Là một dịch vụ chuyên biệt, cung cấp các chức năng cốt lõi của mã hóa đồng cấu qua API:
        *   `Generate Key API`: Tạo cặp khóa HE (PK, SK) theo yêu cầu.
        *   `Encrypt API`: Nhận dữ liệu, HE Public Key, mã hóa và trả về ciphertext.
        *   `Decrypt API`: Nhận ciphertext, HE Secret Key, giải mã và trả về plaintext.
    *   **Xác thực và Ủy quyền:** Yêu cầu Bank System cung cấp Token (JWT) và Public Key định danh hợp lệ trước khi cho phép sử dụng các API của mình. Điều này đảm bảo chỉ Bank System được ủy quyền mới có thể yêu cầu các thao tác liên quan đến khóa của mình.
    *   **Không lưu trữ HE Secret Key của Bank System:** HE Secret Key được Bank System cung cấp cho HE Service trong mỗi yêu cầu giải mã và không được HE Service lưu trữ dài hạn.

### 3.2. Kiểm soát truy cập và Bảo mật

*   **Bank System:** Giữ toàn quyền kiểm soát HE Secret Key. Chỉ Bank System mới có thể khởi tạo yêu cầu giải mã dữ liệu và cung cấp SK cần thiết cho HE Service.
*   **Fintech Partner:** Chỉ được cấp HE Public Key, chỉ có thể thực hiện tính toán trên ciphertext.
*   **HE Service:** Hoạt động như một "bộ xử lý mật mã" được bảo vệ. Việc truy cập và sử dụng dịch vụ được kiểm soát chặt chẽ thông qua xác thực JWT và Public Key định danh của Bank System. Điều này giúp ngăn chặn việc lạm dụng dịch vụ.
*   **Mã hóa Đồng cấu Hoàn toàn (FHE) với TenSEAL:** Sử dụng thư viện **TenSEAL** với lược đồ CKKS để làm việc với dữ liệu số thực (sau khi đã được xử lý phù hợp), cho phép các phép cộng và nhân cần thiết cho mô hình tính điểm.

## 4. Triển khai Hệ thống Thực tế (Proof of Concept - PoC)

Đồ án sẽ tập trung vào việc xây dựng một Proof-of-Concept (PoC) với các thành phần sau:

*   **Bank System (Triển khai Backend):**
    *   **Framework:** FastAPI (Python).
    *   **Database:** Kết nối và truy vấn **SQL Server** (sử dụng thư viện như `pyodbc` hoặc `SQLAlchemy`).
    *   **Tương tác HE:** Gọi các API của HE Service (Generate Key, Encrypt, Decrypt). Quản lý việc lưu trữ HE Secret Key và cung cấp nó cho HE Service khi giải mã.
    *   **Xác thực:** Tạo và gửi JWT + Public Key định danh đến HE Service cho mỗi yêu cầu tới HE Service.
    *   **Thư viện HE (để quản lý cấu trúc khóa/ciphertext):** **TenSEAL**.
*   **Fintech Partner System (Mô phỏng Backend):**
    *   **Framework:** FastAPI (Python).
    *   **Tính toán HE:** Sử dụng **TenSEAL** và HE Public Key nhận được để thực hiện các phép toán trên ciphertext.
    *   **Chức năng API:** Endpoint nhận dữ liệu mã hóa, thực hiện tính toán, endpoint trả kết quả mã hóa.
*   **HE Service (Triển khai Backend):**
    *   **Framework:** FastAPI (Python).
    *   **Chức năng API:**
        *   `/generate-keys`: Tạo cặp khóa TenSEAL (context, public key, secret key).
        *   `/encrypt`: Nhận data, TenSEAL public key, mã hóa bằng TenSEAL. Xác thực yêu cầu dựa trên JWT + Public Key định danh của Bank System.
        *   `/decrypt`: Nhận ciphertext, TenSEAL secret key (do Bank System gửi), giải mã bằng TenSEAL. Xác thực yêu cầu dựa trên JWT + Public Key định danh của Bank System.
    *   **Thư viện HE:** **TenSEAL** để thực hiện các thao tác cốt lõi.
    *   **Xác thực:** Triển khai logic xác thực JWT và Public Key định danh của Bank System.

## 5. Công nghệ sử dụng

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
|                        | Thư viện JWT (ví dụ: `PyJWT`)                         | Xác thực token và Public Key định danh từ Bank System            |

## 6. Mục tiêu Đồ án và Các bước thực hiện dự kiến

*   **Mục tiêu chính:**
    1.  Nghiên cứu sâu về FHE, cụ thể là lược đồ CKKS của TenSEAL và các yêu cầu về tham số.
    2.  Thiết kế và triển khai thành công PoC với kiến trúc 3 thành phần (Bank System, Fintech Partner, HE Service) như đã mô tả.
    3.  Triển khai cơ chế xác thực hai yếu tố (JWT + Public Key định danh của Bank System) cho việc truy cập các API của HE Service.
    4.  Chứng minh khả năng mã hóa dữ liệu từ SQL Server, gửi đi tính toán, nhận lại và giải mã thành công, toàn bộ luồng được bảo vệ.
    5.  Đánh giá sơ bộ về hiệu năng (độ trễ, throughput) của hệ thống, đặc biệt là các API của HE Service.
*   **Các bước thực hiện dự kiến:**
    1.  Thiết lập môi trường, cài đặt các thư viện cần thiết (FastAPI, TenSEAL, pyodbc/SQLAlchemy, PyJWT).
    2.  **HE Service:**
        *   Triển khai API `/generate-keys` để tạo và trả về cặp khóa TenSEAL.
        *   Triển khai API `/encrypt` và `/decrypt` sử dụng TenSEAL, tích hợp logic xác thực JWT + Public Key định danh.
    3.  **Bank System:**
        *   Triển khai logic gọi API `/generate-keys` của HE Service để lấy khóa, lưu SK an toàn.
        *   Thiết lập kết nối tới SQL Server, chuẩn bị logic truy vấn dữ liệu mẫu.
        *   Triển khai logic tạo JWT, chuẩn bị Public Key định danh.
        *   Triển khai logic gọi API `/encrypt` của HE Service (kèm xác thực).
        *   Triển khai logic gọi API `/decrypt` của HE Service (kèm xác thực và cung cấp SK).
    4.  **Fintech Partner:** Triển khai API nhận ciphertext, thực hiện tính toán mẫu bằng TenSEAL, trả kết quả.
    5.  Kiểm thử toàn bộ luồng hoạt động của hệ thống với dữ liệu mẫu từ SQL Server.

## 7. Khó khăn và Thách thức

*   **Độ phức tạp của FHE (TenSEAL/CKKS):** Hiểu rõ về việc chọn tham số (polynomial modulus degree, coefficient modulus primes, scale), quản lý "noise" tích lũy và đảm bảo độ chính xác (precision) cho các phép toán trên số thực gần đúng của CKKS.
*   **Triển khai Xác thực An toàn:** Đảm bảo cơ chế JWT (tạo, ký, xác minh) và việc quản lý/sử dụng Public Key định danh của Bank System được triển khai đúng cách, an toàn, chống lại các tấn công phát lại (replay attacks) hoặc giả mạo.
*   **Truyền Secret Key An toàn và Quản lý:** Việc Bank System gửi HE Secret Key đến HE Service cho mỗi yêu cầu giải mã phải được thực hiện qua kênh mã hóa mạnh (HTTPS). HE Service không lưu trữ SK này, nhưng cần đảm bảo SK không bị lộ trong quá trình xử lý.
*   **Hiệu năng:** FHE vốn có chi phí tính toán cao. Việc gọi API qua mạng cho mỗi thao tác mã hóa/giải mã, cộng thêm overhead của xác thực, có thể ảnh hưởng đến độ trễ tổng thể của hệ thống.
*   **Quản lý Vòng đời Khóa:** Ngoài HE Secret Key, còn có các khóa dùng cho JWT, Public Key định danh của Bank. Việc quản lý, xoay vòng (key rotation) các khóa này trong một hệ thống thực tế là phức tạp.
*   **Tích hợp và làm việc với SQL Server:** Đảm bảo kết nối, truy vấn dữ liệu từ SQL Server một cách hiệu quả và an toàn. Xử lý các kiểu dữ liệu từ SQL Server để phù hợp với yêu cầu đầu vào của TenSEAL.

## 8. Hướng đi trong tương lai

*   **Tối ưu hóa hiệu suất HE Service:**
    *   Nghiên cứu khả năng xử lý batch các yêu cầu mã hóa/giải mã để giảm overhead.
    *   Khám phá các phương pháp tối ưu hóa tham số TenSEAL cho các kịch bản cụ thể.
*   **Nâng cao cơ chế quản lý HE Secret Key:**
    *   Xem xét các giải pháp như sử dụng Hardware Security Module (HSM) tại Bank System để lưu trữ HE Secret Key, và HE Service có thể tương tác với HSM (nếu kiến trúc cho phép và an toàn).
    *   Nghiên cứu các kỹ thuật mã hóa khóa (Key Encryption Keys - KEKs) để bảo vệ HE Secret Key khi truyền đi.
*   **Mô hình tính điểm phức tạp hơn:** Mở rộng khả năng tính toán của Fintech Partner để hỗ trợ các mô hình Machine Learning đơn giản có thể được biểu diễn bằng các phép toán số học mà FHE hỗ trợ.
*   **Giám sát, Logging và Alerting:** Xây dựng hệ thống giám sát chi tiết hoạt động của HE Service, ghi log các yêu cầu, và thiết lập cảnh báo cho các hoạt động bất thường hoặc lỗi.
*   **Mở rộng chính sách xác thực:** Xem xét các chính sách xác thực và ủy quyền chi tiết hơn cho HE Service, ví dụ: giới hạn số lần gọi API, giới hạn độ sâu tính toán cho một yêu cầu.
