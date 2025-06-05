# Hệ thống Chấm điểm Tín dụng Bảo toàn Quyền riêng tư sử dụng Mã hóa Đồng cấu (Homomorphic Encryption)

## Bối cảnh 

Trong lĩnh vực tài chính, các tổ chức tín dụng thường xuyên cần xử lý và tính toán điểm tín dụng của khách hàng. Quá trình này dựa trên các dữ liệu cá nhân và tài chính nhạy cảm như thu nhập, chi tiêu, lịch sử giao dịch, tình trạng nợ, v.v. Hiện nay, để nâng cao chất lượng mô hình và hiệu quả hoạt động, Ngân hàng có xu hướng hợp tác với các Bên thứ ba (ví dụ: các công ty Fintech chuyên về phân tích dữ liệu - sau đây gọi là "Đối tác Fintech") để thực hiện việc tính toán này.

Tuy nhiên, việc gửi dữ liệu thô của khách hàng đến Đối tác Fintech tiềm ẩn nguy cơ rò rỉ dữ liệu cá nhân nghiêm trọng. Điều này không chỉ ảnh hưởng đến quyền riêng tư của khách hàng mà còn vi phạm các quy định bảo mật dữ liệu ngày càng khắt khe (ví dụ: GDPR, Nghị định 13/2023/NĐ-CP về Bảo vệ dữ liệu cá nhân tại Việt Nam). Do đó, việc phát triển một giải pháp cho phép tính toán trên dữ liệu mà vẫn đảm bảo dữ liệu được mã hóa đầu-cuối (end-to-end privacy) đang trở thành một nhu cầu cấp thiết.

## Phương pháp truyền thống và Hạn chế 

Các phương pháp bảo vệ dữ liệu hiện tại mà các tổ chức tài chính thường áp dụng bao gồm:

*   **Mã hóa khi lưu trữ và truyền tải (Encryption at Rest & In Transit):** Sử dụng các thuật toán mã hóa đối xứng (AES) hoặc bất đối xứng (RSA) để bảo vệ dữ liệu khi được lưu trữ trong cơ sở dữ liệu hoặc khi truyền đi giữa các hệ thống.
    *   **Hạn chế:** Dữ liệu *bắt buộc phải được giải mã* tại máy chủ của Đối tác Fintech trước khi thực hiện bất kỳ phép tính nào (ví dụ: xây dựng mô hình, tính điểm tín dụng). Điều này tạo ra một "điểm yếu" nơi dữ liệu nhạy cảm bị phơi bày, làm mất đi tính riêng tư trong quá trình xử lý.
*   **Giải pháp che mờ/giải danh (Data Masking/Anonymization):**
    *   **Hạn chế:** Có thể làm giảm độ chính xác của mô hình tính điểm tín dụng. Dữ liệu giải danh vẫn có nguy cơ bị tái định danh (re-identification attack) khi kết hợp với các nguồn dữ liệu khác.

Đặc biệt, nếu logic tính điểm tín dụng bao gồm các điều kiện phức tạp (ví dụ: "NẾU thu nhập > X VÀ dư nợ < Y THÌ điểm tín dụng += Z"), các phương pháp truyền thống không thể thực hiện các phép toán này trực tiếp trên dữ liệu đã mã hóa. Chúng đòi hỏi dữ liệu phải ở dạng rõ (plaintext), điều này đi ngược lại yêu cầu bảo mật dữ liệu đầu-cuối trong quá trình tính toán.

## Đề xuất giải pháp mới: Hệ thống Chấm điểm Tín dụng An toàn sử dụng Mã hóa Đồng cấu Hoàn toàn (Fully Homomorphic Encryption - FHE)

Chúng tôi đề xuất xây dựng một "Hệ thống Chấm điểm Tín dụng Bảo toàn Quyền riêng tư" sử dụng kỹ thuật **Mã hóa Đồng cấu Hoàn toàn (Fully Homomorphic Encryption - FHE)**. FHE cho phép thực hiện một loạt các phép tính toán (bao gồm cộng, nhân, và các hàm phức tạp hơn có thể được xây dựng từ đó) trực tiếp trên dữ liệu đã được mã hóa (ciphertext) mà không cần giải mã chúng trước.

**Luồng hoạt động chính:**
1.  **Tại Ngân hàng:** Dữ liệu khách hàng được mã hóa bằng Khóa công khai (Public Key) của FHE.
2.  **Chuyển giao an toàn:** Dữ liệu đã mã hóa (ciphertext) được gửi đến Đối tác Fintech.
3.  **Tại Đối tác Fintech:** Thực hiện các thuật toán tính điểm tín dụng trực tiếp trên ciphertext, sử dụng Khóa công khai.
4.  **Trả kết quả:** Kết quả điểm tín dụng (vẫn ở dạng ciphertext) được trả về cho Ngân hàng.
5.  **Tại Ngân hàng:** Ngân hàng sử dụng Khóa bí mật (Secret Key) của mình để giải mã và thu được điểm tín dụng ở dạng rõ.

### 3.1 Kiến trúc hệ thống (System Architecture)

Hệ thống dự kiến bao gồm các thành phần chính:

*   **Bank System (Hệ thống Ngân hàng):**
    *   Chịu trách nhiệm mã hóa dữ liệu thô của khách hàng bằng Public Key (PK) của FHE.
    *   Gửi ciphertext và PK (nếu Đối tác Fintech chưa có) sang Đối tác Fintech.
    *   Lưu giữ an toàn Secret Key (SK).
    *   Nhận kết quả điểm tín dụng đã mã hóa từ Đối tác Fintech và giải mã bằng SK.
*   **Fintech Partner System (Hệ thống Đối tác Fintech - Mô phỏng):**
    *   Nhận ciphertext và PK từ Bank System.
    *   Thực hiện các logic tính toán điểm tín dụng (ví dụ: theo một mô hình được định sẵn) trực tiếp trên ciphertext.
    *   Trả kết quả điểm tín dụng (vẫn ở dạng ciphertext) về cho Bank System.
    *   **Quan trọng:** Không bao giờ có quyền truy cập vào SK hoặc dữ liệu gốc của khách hàng.
*   **HE Service (Dịch vụ Mã hóa Đồng cấu - Tích hợp vào Bank System trong PoC):**
    *   Chịu trách nhiệm tạo và quản lý các tham số hệ thống FHE.
    *   Tạo cặp khóa Public Key (PK) và Secret Key (SK). (SK sẽ do Bank System trực tiếp quản lý và lưu giữ.)
    *   Cung cấp các API/chức năng hỗ trợ cho Bank System trong việc mã hóa, giải mã.

### 3.2 Kiểm soát truy cập và Bảo mật 

*   **Phân tách vai trò rõ ràng:**
    *   Bank System sở hữu và kiểm soát hoàn toàn Secret Key, là bên duy nhất có khả năng giải mã dữ liệu.
    *   Fintech Partner System chỉ có thể thao tác trên ciphertext bằng Public Key và không thể suy ra dữ liệu gốc.
*   **Mã hóa đầu-cuối cho quá trình tính toán:** Dữ liệu nhạy cảm của khách hàng được bảo vệ từ lúc rời khỏi Bank System, trong suốt quá trình tính toán tại Fintech Partner, cho đến khi kết quả được giải mã tại Bank System.
*   **Sử dụng lược đồ FHE:** Đồ án sẽ tập trung vào việc sử dụng một thư viện **TenSEAL** (sử dụng lược đồ CKKS cho dữ liệu số thực gần đúng), để hỗ trợ các phép cộng và nhân trên dữ liệu mã hóa, nền tảng cho các mô hình tính điểm phức tạp hơn.

## Triển khai Hệ thống Thực tế 

Đồ án sẽ tập trung vào việc xây dựng một Proof-of-Concept (PoC) với các thành phần sau:

➡️ **Bank System (Triển khai Backend)**
*   **Framework:** FastAPI (Python).
*   **Mã hóa/Giải mã dữ liệu:** Sử dụng thư viện **TenSEAL** với lược đồ CKKS để mã hóa/giải mã dữ liệu số thực (ví dụ: thu nhập, tỷ lệ nợ).
*   **Chức năng API:**
    *   Endpoint để nhận dữ liệu khách hàng (mô phỏng).
    *   Logic mã hóa dữ liệu bằng TenSEAL.
    *   Logic gọi API của Fintech Partner để gửi dữ liệu mã hóa.
    *   Endpoint để nhận kết quả mã hóa từ Fintech Partner.
    *   Logic giải mã kết quả bằng TenSEAL.

➡️ **Fintech Partner System (Mô phỏng Backend)**
*   **Framework:** FastAPI (Python).
*   **Chức năng API:**
    *   Endpoint để nhận ciphertext (định dạng của TenSEAL) và Public Key từ Bank System.
    *   Logic thực hiện tính toán điểm tín dụng (ví dụ: một công thức tuyến tính `Score = w1*data1 + w2*data2 + ...`) trực tiếp trên ciphertext bằng các phép toán được TenSEAL hỗ trợ.
    *   Endpoint để trả kết quả (ciphertext) về Bank System.

➡️ **HE Service (Logic tích hợp)**
*   **Chức năng:** Sinh khóa (Context, Public Key, Secret Key) và các tham số hệ thống FHE cần thiết cho TenSEAL.
*   **Triển khai:** Sẽ được tích hợp vào Bank System trong giai đoạn PoC này.

## Công nghệ sử dụng (Proposed Technology Stack)

| Thành phần             | Công nghệ chính                                       | Mục đích                                     |
| :--------------------- | :---------------------------------------------------- | :------------------------------------------- |
| **Bank System**        | Python, FastAPI                                       | Xây dựng API backend, xử lý logic nghiệp vụ  |
|                        | **TenSEAL (FHE - CKKS)**                              | Mã hóa/giải mã, tính toán FHE trên số thực   |
| **Fintech Partner**    | Python, FastAPI                                       | Mô phỏng API backend, xử lý logic tính toán  |
|                        | **TenSEAL (FHE - CKKS)**                              | Thực hiện tính toán trên ciphertext          |
| **Database**           | SQL Server                                            | Lưu trữ dữ liệu mẫu cho PoC (nhanh chóng)    |

## Mục tiêu Đồ án & Các bước thực hiện dự kiến 

*   **Mục tiêu chính:**
    1.  Nghiên cứu sâu về các khái niệm và lược đồ Mã hóa Đồng cấu Hoàn toàn (FHE), cụ thể là CKKS qua thư viện TenSEAL.
    2.  Thiết kế và triển khai thành công một hệ thống PoC cho việc chấm điểm tín dụng bảo toàn quyền riêng tư sử dụng FHE.
    3.  Chứng minh khả năng thực hiện các phép toán cộng và nhân trên dữ liệu số thực đã mã hóa, nền tảng cho mô hình tính điểm.
    4.  Đánh giá sơ bộ về hiệu năng (thời gian mã hóa, giải mã, tính toán) và kích thước dữ liệu mã hóa của giải pháp sử dụng TenSEAL.
*   **Các bước thực hiện dự kiến:**
    1.  Thiết lập môi trường, cài đặt thư viện TenSEAL.
    2.  Xây dựng module sinh khóa (TenSEAL context, public/secret keys) và quản lý khóa cơ bản.
    3.  Triển khai API cho Bank System: mã hóa dữ liệu, gửi yêu cầu.
    4.  Triển khai API cho Fintech Partner: nhận dữ liệu mã hóa, thực hiện tính toán (cộng, nhân) trên ciphertext.
    5.  Hoàn thiện luồng: Bank System nhận kết quả mã hóa và giải mã.
    6.  Kiểm thử toàn bộ hệ thống với dữ liệu số thực mẫu (ví dụ: thu nhập, các chỉ số tài chính).
    7.  Tài liệu hóa các tham số, quá trình scaling (nếu cần cho CKKS) và kết quả.

## Khó khăn và Thách thức

*   **Độ phức tạp của FHE:** Hiểu và áp dụng đúng các khái niệm, tham số của FHE (đặc biệt là CKKS với việc quản lý "noise" và precision) đòi hỏi nỗ lực nghiên cứu.
*   **Hạn chế về các phép toán logic phức tạp:** Mặc dù FHE mạnh mẽ, việc triển khai các phép toán logic như so sánh trực tiếp hoặc if-else trên CKKS có thể không tầm thường và yêu cầu các kỹ thuật xấp xỉ hoặc các hàm đa thức. Đồ án này sẽ tập trung vào các phép toán số học cơ bản.
*   **Hiệu năng:** Các phép toán trên dữ liệu mã hóa FHE thường chậm và tạo ra bản mã lớn. Cần đánh giá và ý thức về vấn đề này, đặc biệt với các tính toán lặp lại hoặc sâu.
*   **Quản lý khóa (Key Management):** Mặc dù PoC sẽ đơn giản hóa, việc quản lý khóa an toàn trong thực tế là một thách thức lớn.
*   **Độ chính xác (Precision):** Lược đồ CKKS là mã hóa gần đúng cho số thực. Cần quản lý cẩn thận các tham số (scale, polynomial modulus degree) để cân bằng giữa độ chính xác và hiệu năng/an ninh.

## Hướng đi trong tương lai

*   **Khám phá các phép toán FHE nâng cao:** Nghiên cứu sâu hơn về cách thực hiện các hàm phức tạp hơn (ví dụ: hàm kích hoạt trong mạng nơ-ron, hàm đa thức) bằng TenSEAL hoặc các thư viện FHE khác như Pyfhel (nếu muốn so sánh).
*   **Tối ưu hóa hiệu suất:** Nghiên cứu các kỹ thuật như batching (xử lý nhiều giá trị trong một ciphertext), lựa chọn tham số FHE tối ưu, và các thủ tục quản lý "noise" (relinearization, bootstrapping nếu thư viện hỗ trợ và cần thiết).
*   **Mô hình tính điểm nâng cao:** Áp dụng FHE cho các mô hình Machine Learning đơn giản có thể huấn luyện hoặc dự đoán trên dữ liệu mã hóa (ví dụ: hồi quy tuyến tính, hồi quy logistic).
*   **Cơ chế quản lý khóa nâng cao:** Nghiên cứu các giải pháp quản lý khóa (Key Management System - KMS) và các kỹ thuật như threshold cryptography để tăng cường an toàn cho khóa bí mật trong môi trường thực tế.
*   **Đánh giá an ninh toàn diện:** Phân tích các nguy cơ tấn công tiềm ẩn khác và đề xuất biện pháp phòng chống phù hợp với FHE.
