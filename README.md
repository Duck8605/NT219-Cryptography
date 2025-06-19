# Hệ thống Chấm điểm Tín dụng Liên ngân hàng sử dụng Mã hóa Đồng hình Ngưỡng
### A Secure, Multi-Party Credit Scoring System using Threshold Homomorphic Encryption

**Sinh viên thực hiện:**
*   Trần Hữu Đức - 23523021
*   Võ Minh An - 23520033
*   Nguyễn Gia Bảo - 23520122

**Giảng viên hướng dẫn:** TS. Nguyễn Ngọc Tự

---

## 1. Bối cảnh và Mục tiêu

Trong ngành tài chính hiện đại, việc đánh giá tín dụng một cách toàn diện đòi hỏi sự hợp tác giữa nhiều ngân hàng để có được cái nhìn đầy đủ về lịch sử tài chính của khách hàng. Tuy nhiên, việc chia sẻ dữ liệu nhạy cảm này bị cản trở nghiêm ngặt bởi các quy định về quyền riêng tư (như GDPR) và lo ngại về cạnh tranh. Các giải pháp truyền thống yêu cầu một bên thứ ba đáng tin cậy hoặc buộc các bên phải giải mã dữ liệu, tạo ra các điểm yếu bảo mật nghiêm trọng.

Dự án này đề xuất giải pháp: **xây dựng một hệ thống cho phép nhiều ngân hàng cùng nhau tính toán một điểm tín dụng chung mà không cần tiết lộ dữ liệu gốc của khách hàng cho bất kỳ ai**, kể cả cho nhau hay cho nền tảng trung gian. Chúng tôi đạt được điều này bằng cách áp dụng kỹ thuật **Mã hóa Đồng hình Ngưỡng (Threshold Homomorphic Encryption - THE)**, sử dụng thư viện mã nguồn mở tiên tiến **OpenFHE**.

**Mục tiêu chính của dự án:**
*   **Bảo mật tuyệt đối:** Đảm bảo dữ liệu tài chính của khách hàng luôn được mã hóa trong suốt vòng đời: từ khi gửi đi, lưu trữ, cho đến khi được xử lý.
*   **Kiểm soát phi tập trung:** Phân tán quyền giải mã cho các ngân hàng tham gia. Không một thực thể đơn lẻ nào có thể giải mã dữ liệu, yêu cầu sự đồng thuận theo ngưỡng đã định.
*   **Hợp tác an toàn:** Cho phép các ngân hàng kết hợp dữ liệu một cách an toàn để tạo ra một mô hình chấm điểm tín dụng chính xác và toàn diện hơn, giúp cải thiện quản lý rủi ro.
*   **Tuân thủ quy định:** Thiết kế hệ thống tuân thủ các quy định bảo mật dữ liệu nghiêm ngặt ngay từ đầu, tạo dựng lòng tin giữa các đối tác và với khách hàng.

## 2. Kiến trúc Hệ thống

Hệ thống của chúng tôi áp dụng mô hình "tính toán tập trung, tin cậy phân tán", kết hợp hiệu quả vận hành và bảo mật ở mức cao nhất.

![image](https://github.com/user-attachments/assets/95434080-d0e9-4b10-a0dd-1d998a354edc)
*Sơ đồ minh họa kiến trúc tổng thể của hệ thống.*

**Các bên tham gia (Stakeholders):**
1.  **Ngân hàng (A, B, C):** Là chủ sở hữu dữ liệu. Mỗi ngân hàng chịu trách nhiệm mã hóa dữ liệu của mình, giữ an toàn **phần khóa bí mật (private key share)** của mình trong HSM, và tham gia vào quy trình giải mã chung.
2.  **Công ty Fintech (Platform Operator):** Vận hành **Hệ thống Backend (BE) và Database (DB) chung**. Nền tảng này đóng vai trò điều phối, nhận dữ liệu đã mã hóa, thực hiện các phép tính đồng hình, và gửi trả kết quả mã hóa. **Fintech không bao giờ có quyền truy cập dữ liệu gốc hoặc các phần khóa bí mật.**

**Luồng hoạt động chính:**
1.  **Thiết lập Khóa chung (Multiparty Key Generation):** Ba ngân hàng cùng nhau thực hiện một giao thức mật mã để tạo ra một **khóa công khai chung (`pk_shared`)** và ba **phần khóa bí mật (`sk_shares`)** riêng biệt. `pk_shared` được chia sẻ cho Fintech, trong khi mỗi ngân hàng bảo vệ chặt chẽ `sk_share` của mình.
2.  **Gửi dữ liệu mã hóa:** Mỗi ngân hàng sử dụng `pk_shared` để mã hóa dữ liệu khách hàng và gửi đến API của Fintech. Định danh khách hàng được ẩn danh qua một giá trị băm (`customer_hash`).
3.  **Tính toán Đồng hình:** Hệ thống BE của Fintech truy vấn các bản ghi mã hóa có cùng `customer_hash` và thực hiện các phép tính (ví dụ: `EvalAdd`, `EvalMult`) để tính ra điểm tín dụng, kết quả vẫn ở dạng mã hóa (`encrypted_score`).
4.  **Giải mã Ngưỡng:**
    *   `encrypted_score` được gửi đến các ngân hàng.
    *   Mỗi ngân hàng sử dụng `sk_share` của mình để tạo ra một **phần giải mã (partial decryption)**.
    *   Việc giải mã chỉ thành công khi một bên được ủy quyền tổng hợp đủ các phần giải mã từ tất cả các ngân hàng tham gia.

## 3. Công nghệ sử dụng

| Thành phần | Công nghệ chính | Mục đích |
| :--- | :--- | :--- |
| **Mã hóa Đồng hình** | **OpenFHE (CKKS Scheme)** | Cung cấp nền tảng mã hóa đồng hình ngưỡng, cho phép tính toán trên số thực. |
| **Backend & API** | Python, FastAPI | Xây dựng API mạnh mẽ, hiệu năng cao để xử lý các yêu cầu từ ngân hàng. |
| **Database** | SQL Server | Lưu trữ an toàn và hiệu quả dữ liệu mã hóa có cấu trúc lớn. |
| **Giao tiếp mạng** | **TLS 1.3** | Đảm bảo tính bí mật và toàn vẹn cho tất cả các kênh truyền dữ liệu. |
| **Xác thực** | **OAuth 2.0** | Kiểm soát và xác thực truy cập API từ các ngân hàng. |
| **Bảo mật Khóa** | **HSM (Hardware Security Module)** | Nơi các ngân hàng lưu trữ an toàn các phần khóa bí mật của mình. |

## 4. Các bước thực hiện và Triển khai

1.  **Nghiên cứu & Thiết kế:** Nghiên cứu sâu về Mã hóa Đồng hình Ngưỡng (THE) và thư viện OpenFHE. Thiết kế kiến trúc chi tiết cho các thành phần và luồng dữ liệu.
2.  **Triển khai Giao thức Tạo khóa:** Xây dựng module cho phép ba bên thực hiện `MultiKeyGen` để tạo và phân phối khóa một cách an toàn.
3.  **Xây dựng Backend & Database:** Phát triển các API để nhận, lưu trữ dữ liệu mã hóa, và thực hiện các phép tính đồng hình theo công thức chấm điểm.
4.  **Xây dựng Hệ thống tại Ngân hàng:** Phát triển client-side logic để mã hóa dữ liệu, gọi API Fintech, và tham gia vào giao thức giải mã ngưỡng.
5.  **Tích hợp và Kiểm thử:** Kết nối tất cả các thành phần, thực hiện kiểm thử chức năng để đảm bảo tính chính xác của kết quả, và kiểm thử bảo mật (penetration testing) để xác minh khả năng chống lại các cuộc tấn công đã mô hình hóa.

## 5. Thách thức và Hướng phát triển

*   **Thách thức:**
    *   **Hiệu năng:** Tính toán đồng hình vẫn còn chậm so với tính toán trên dữ liệu thường, đòi hỏi tối ưu hóa và phần cứng mạnh mẽ.
    *   **Độ phức tạp:** Quản lý vòng đời khóa và điều phối giao thức giải mã giữa nhiều bên là một thách thức về mặt kỹ thuật và vận hành.
    *   **Kích thước dữ liệu:** Ciphertext có kích thước lớn, ảnh hưởng đến chi phí lưu trữ và băng thông mạng.

*   **Hướng phát triển tương lai:**
    *   **Tối ưu hóa hiệu năng:** Nghiên cứu các kỹ thuật tăng tốc phần cứng (FPGA/GPU) cho OpenFHE.
    *   **Mở rộng mô hình:** Tích hợp các mô hình Machine Learning phức tạp hơn để tính toán trên dữ liệu mã hóa.
    *   **Tăng cường khả năng kiểm toán:** Xây dựng một hệ thống logging phi tập trung (ví dụ: sử dụng Blockchain) để ghi lại các hoạt động một cách minh bạch và không thể thay đổi.
