Project Agent Skill: Coffee Shop Operation + Loyal Customer Recognition & Auto Greeting System

Mục đích
File này giúp AI agent hiểu nhanh toàn bộ ngữ cảnh dự án, bao gồm cả hệ thống vận hành quán cà phê thông thường như POS, admin, quản lý hóa đơn, khách hàng, sản phẩm, ca làm việc, báo cáo; đồng thời tích hợp thêm module AI nhận diện khách hàng thân thiết và chào hỏi tự động.

Tên đề tài
Ứng dụng học máy trong nhận diện khách hàng thân thiết và chào hỏi tự động tại quán cà phê
English: Machine Learning-Based Loyal Customer Recognition and Automatic Greeting System for Coffee Shops

Bản chất dự án
Đây là một hệ thống quản lý quán cà phê hoàn chỉnh, trong đó:

- Phần lõi là các chức năng vận hành quán như POS, quản lý đơn hàng, hóa đơn, khách hàng, sản phẩm, bàn, nhân viên, ca làm việc, báo cáo và cấu hình hệ thống
- Phần mở rộng thông minh là module AI/CV dùng camera để nhận diện khách hàng, đối chiếu dữ liệu khuôn mặt với cơ sở dữ liệu khách hàng và xác định khách hàng thân thiết dựa trên lịch sử hóa đơn để tự động chào

AI agent phải luôn hiểu rằng:

- POS và dữ liệu vận hành là nguồn dữ liệu gốc
- AI nhận diện chỉ là một module bổ sung để nâng cao trải nghiệm khách hàng
- Hệ thống vẫn phải vận hành được đầy đủ như một phần mềm quản lý quán cà phê ngay cả khi module AI tạm thời không hoạt động

Mục tiêu hệ thống

- Hỗ trợ quán cà phê vận hành hằng ngày bằng các chức năng POS và admin
- Quản lý sản phẩm, menu, đơn hàng, hóa đơn, khách hàng, bàn, nhân viên, ca làm việc
- Ghi nhận và lưu trữ lịch sử hóa đơn làm cơ sở đánh giá khách hàng thân thiết
- Nhận diện khách hàng từ camera
- So khớp với dữ liệu khách hàng đã lưu
- Xác định khách hàng thân thiết dựa trên lịch sử hóa đơn
- Tự động chào khách quen
- Hiển thị sự kiện nhận diện và chào khách theo thời gian thực
- Hỗ trợ quản lý theo dõi hoạt động quán qua dashboard và báo cáo

Rule nghiệp vụ quan trọng nhất cho loyal customer
Khách hàng được xem là thân thiết nếu có từ 10 hóa đơn hợp lệ trong 30 ngày gần nhất.

Giải thích rule loyal customer

- Chỉ tính hóa đơn hợp lệ
- Không tính hóa đơn bị hủy, hoàn tiền hoặc test data
- Cửa sổ thời gian là rolling 30 days, không phải theo tháng lịch
- Điều kiện mặc định hiện tại: invoice_count >= 10 trong 30 ngày gần nhất
- Rule này cần được thiết kế mềm để sau này có thể chuyển thành config trong admin settings

Phạm vi nghiệp vụ chính

1. Vận hành quán cà phê

- POS bán hàng tại quầy
- Quản lý đơn hàng
- Quản lý hóa đơn và thanh toán
- Quản lý sản phẩm, menu, danh mục
- Quản lý bàn và trạng thái bàn nếu quán có phục vụ tại chỗ
- Quản lý khách hàng
- Quản lý nhân viên và tài khoản
- Quản lý ca làm việc
- Quản lý khuyến mãi, phụ thu, giảm giá nếu có
- Báo cáo doanh thu, số lượng đơn, hiệu suất vận hành
- Cấu hình hệ thống quán

2. AI nhận diện khách hàng thân thiết

- Nhận ảnh từ camera
- Phát hiện khuôn mặt
- So khớp với dữ liệu khuôn mặt khách hàng
- Kiểm tra rule loyal customer từ dữ liệu hóa đơn
- Tạo greeting event nếu đủ điều kiện
- Push sự kiện realtime lên dashboard

Luồng nghiệp vụ tổng quát của hệ thống

1. Nhân viên sử dụng POS để tạo đơn, thanh toán và phát hành hóa đơn
2. Hóa đơn được lưu vào hệ thống và là nguồn dữ liệu chính cho lịch sử mua hàng
3. Camera ghi nhận khách bước vào khu vực cửa
4. Hệ thống AI phát hiện khuôn mặt và thực hiện nhận diện
5. Nếu match được khách hàng với độ tin cậy đủ cao, backend lấy hồ sơ khách hàng
6. Backend kiểm tra số hóa đơn hợp lệ của khách trong 30 ngày gần nhất
7. Nếu đủ điều kiện loyal customer, hệ thống tạo greeting event
8. Dashboard realtime hiển thị khách vừa được nhận diện và trạng thái greeting
9. Toàn bộ recognition log và greeting log được lưu để phục vụ đánh giá, tra cứu và báo cáo

Stack công nghệ

- AI/CV: Python, OpenCV, YOLO
- Backend API: FastAPI
- Database: PostgreSQL
- Frontend web quản lý: React
- Realtime dashboard: WebSocket

Nguyên tắc thiết kế

- POS và admin là nền tảng vận hành cốt lõi của hệ thống
- AI nhận diện là module nâng cao, không được làm ảnh hưởng luồng bán hàng chính
- Tách riêng AI inference logic và business logic
- Tách riêng recognition event và greeting event
- Tách dữ liệu giao dịch vận hành và dữ liệu AI nhưng vẫn liên kết được qua customer_id
- Không hard-code rule loyal customer ở nhiều nơi
- Ưu tiên log đầy đủ để debug và audit
- Cho phép hệ thống hoạt động ổn định dù camera hoặc model AI gặp lỗi
- Dữ liệu khuôn mặt và thông tin khách hàng là dữ liệu nhạy cảm, cần hạn chế truy cập

Phạm vi MVP

- POS cơ bản cho bán hàng
- Quản lý sản phẩm, menu, danh mục
- Quản lý hóa đơn
- Quản lý khách hàng
- Lưu ảnh khuôn mặt khách hàng
- Lưu lịch sử hóa đơn
- Phát hiện và nhận diện khách từ camera
- Kiểm tra loyal customer theo rule 10 bill / 30 ngày
- Tự động chào khách đủ điều kiện
- Dashboard realtime hiển thị recognition events và greeting events
- Trang admin quản lý dữ liệu khách hàng và lịch sử sự kiện

Ngoài phạm vi hiện tại

- Voice bot nâng cao
- Recommendation engine phức tạp
- Multi-branch enterprise scale
- Phân tích cảm xúc
- Marketing automation nâng cao
- Dự báo nhu cầu hoặc tối ưu nguyên liệu bằng ML nâng cao

Các phân hệ chính mà AI phải hiểu
POS module

- Tạo đơn hàng
- Thêm/xóa/sửa món
- Tính tiền
- Áp dụng giảm giá hoặc phụ thu
- Thanh toán
- In hoặc lưu hóa đơn
- Đóng/mở bill
- Xử lý bill hợp lệ, bill hủy, bill hoàn tiền

Admin module

- Quản lý tài khoản người dùng và phân quyền
- Quản lý sản phẩm, danh mục, giá bán
- Quản lý khách hàng
- Quản lý lịch sử hóa đơn
- Quản lý nhân viên và ca làm việc
- Quản lý camera và trạng thái thiết bị
- Xem recognition events và greeting events
- Xem dashboard realtime
- Quản lý cấu hình loyalty rule trong tương lai
- Cấu hình thông điệp chào, cooldown time và các ngưỡng hệ thống

AI recognition module

- Nhận frame từ camera
- Detect khuôn mặt hoặc người
- Crop và chuẩn hóa ảnh
- Tạo embedding hoặc feature
- So khớp với dữ liệu khuôn mặt đã lưu
- Trả về candidate và confidence

Loyalty module

- Nhận customer_id
- Query lịch sử hóa đơn
- Kiểm tra điều kiện loyal customer
- Trả về qualified true/false và invoice_count_30d

Greeting module

- Nhận kết quả match + loyal check
- Quyết định có chào hay không
- Tạo greeting event
- Push realtime event
- Chống greet lặp

Realtime dashboard module

- Hiển thị recognition.detected
- Hiển thị recognition.matched
- Hiển thị loyal_customer.verified
- Hiển thị greeting.triggered
- Hiển thị camera.status_changed
- Hiển thị system.alert

Các thực thể dữ liệu cốt lõi
Customer

- id
- full_name
- phone
- gender nullable
- birthday nullable
- note nullable
- created_at
- updated_at

CustomerFace

- id
- customer_id
- image_path hoặc image_url
- embedding hoặc feature_vector_ref
- quality_score
- is_primary
- created_at

Invoice

- id
- customer_id nullable
- invoice_code
- subtotal
- discount_amount
- surcharge_amount
- total_amount
- payment_status
- invoice_status
- created_by
- issued_at
- created_at
- updated_at

InvoiceItem

- id
- invoice_id
- product_id
- product_name_snapshot
- quantity
- unit_price
- line_total
- note nullable

Order

- id
- table_id nullable
- customer_id nullable
- order_status
- created_by
- created_at
- updated_at

Product

- id
- category_id
- sku nullable
- name
- price
- status
- image_url nullable
- created_at
- updated_at

Category

- id
- name
- status
- sort_order

Table

- id
- name
- area nullable
- status
- capacity nullable

Payment

- id
- invoice_id
- method
- amount
- paid_at
- reference_code nullable

User

- id
- username
- full_name
- role
- status
- created_at
- updated_at

EmployeeShift

- id
- user_id
- shift_date
- start_time
- end_time
- status

RecognitionEvent

- id
- camera_id
- customer_id nullable
- confidence
- snapshot_path
- result_status
- recognized_at
- created_at

GreetingEvent

- id
- recognition_event_id
- customer_id
- greeting_message
- status
- greeted_at
- created_at

Camera

- id
- name
- location
- status
- stream_source nullable
- created_at
- updated_at

SystemSetting

- id
- key
- value
- description nullable
- updated_at

Nghiệp vụ cốt lõi cần nhớ

- Hóa đơn từ POS là nguồn dữ liệu chính để tính loyal customer
- Nếu customer chưa gắn vào invoice thì invoice đó không được dùng để tính loyalty cho customer đó
- Bill hủy, refund, test hoặc invalid không được tính
- Recognition event không đồng nghĩa với greeting event
- Một khách có thể được nhận diện nhưng không được chào nếu không đạt đủ điều kiện
- Admin có thể cần tra cứu vì sao một khách được hoặc không được xác định là loyal customer

Tiêu chí ra quyết định khi greet
Chỉ greet khi thỏa tất cả điều kiện sau:

- Match được khách hàng với confidence đủ cao
- Khách thỏa điều kiện loyal customer
- Khách chưa bị greet lặp trong thời gian cooldown
- Recognition hiện tại không phải duplicate ngay sau một recognition gần nhất
- Camera và hệ thống đang ở trạng thái hoạt động bình thường

Fallback khi không chắc chắn

- Nếu confidence thấp: chỉ log recognition event, không greet
- Nếu match mơ hồ: đánh dấu cần xác minh thủ công
- Nếu không tìm thấy khách: ghi nhận unknown visitor
- Nếu chưa đủ dữ liệu hóa đơn: không greet, nhưng vẫn cho phép admin tra cứu
- Nếu camera lỗi hoặc model lỗi: gửi system alert lên dashboard
- Nếu POS hoặc DB tạm thời lỗi: không được tạo loyalty result sai

Các chỉ số hệ thống cần theo dõi
Về vận hành quán

- Tổng số đơn hàng
- Tổng doanh thu
- Số bill theo ngày
- Giá trị bill trung bình
- Số lượng khách hàng quay lại
- Hiệu suất theo ca làm việc nếu có

Về AI và loyalty

- Accuracy nhận diện
- Precision / Recall / F1 nếu có ground truth
- False positive rate
- False negative rate
- Thời gian phản hồi từ lúc phát hiện đến lúc ra quyết định
- Tỷ lệ greeting thành công
- Số lượng loyal customers được nhận diện mỗi ngày
- Tỷ lệ match nhưng không đạt điều kiện loyal
- Tỷ lệ unknown visitors

Yêu cầu phi chức năng

- Luồng POS phải ổn định và ưu tiên cao nhất
- API rõ ràng, dễ bảo trì
- Dashboard realtime hoạt động ổn định
- Có log để audit
- Có thể mở rộng thêm camera
- Có bảo mật dữ liệu khách hàng và khuôn mặt
- Có khả năng đổi rule loyal customer sau này
- Có thể chạy trong môi trường quán cà phê thực tế với ánh sáng và góc nhìn không lý tưởng

Bảo mật và quyền riêng tư

- Ảnh khuôn mặt và embedding là dữ liệu nhạy cảm
- Chỉ user có quyền mới được xem hoặc quản lý dữ liệu này
- Không public link ảnh mặt
- Nên có audit log cho thao tác xem, sửa, xóa dữ liệu khách hàng
- Không dùng ảnh khách hàng ngoài mục đích hệ thống khi chưa được cho phép
- Dữ liệu POS và dữ liệu khách hàng phải có phân quyền rõ giữa staff, manager, admin

Quy ước cho AI agent khi hỗ trợ code

- Luôn xem đây là hệ thống coffee shop management có tích hợp AI, không phải chỉ là demo nhận diện khuôn mặt
- Luôn giữ POS flow ổn định khi đề xuất thay đổi
- Hóa đơn từ POS là source of truth cho loyalty
- Không nhúng business rule rải rác trong UI
- Ưu tiên viết code tách lớp: router, service, repository, schema, model
- Khi sửa API phải kiểm tra luôn response model, validation và tác động tới frontend
- Khi thêm field DB phải nghĩ đến migration, index và backward compatibility
- Khi thêm event realtime phải mô tả rõ event name và payload
- Khi xử lý AI output phải luôn có confidence threshold và fallback path
- Không giả định dữ liệu luôn sạch hoặc đầy đủ
- Khi sửa logic invoice phải kiểm tra lại loyalty calculation
- Khi sửa customer flow phải kiểm tra tác động tới recognition matching
- Khi viết test phải có case biên: 9 bill, 10 bill, 11 bill trong 30 ngày

Những việc AI nên ưu tiên hỗ trợ

- Thiết kế database schema cho POS + AI
- Viết FastAPI routes, services, Pydantic schemas
- Viết query loyal customer
- Viết logic invoice valid/invalid cho loyalty
- Tạo WebSocket event schema
- Viết React pages cho dashboard quản lý
- Viết React pages cho admin POS nếu cần
- Viết test cases cho POS flow, recognition flow và loyalty rule
- Đề xuất logging, monitoring, error handling
- Refactor code để tách AI logic, POS logic và business logic

Những điều AI không nên tự ý làm

- Không tự đổi định nghĩa loyal customer nếu chưa được yêu cầu
- Không coi recognition result là dữ liệu chắc chắn 100%
- Không hard-code magic number ở nhiều file
- Không bỏ qua privacy concerns
- Không gắn logic loyalty vào frontend nếu backend mới là nguồn quyết định
- Không chỉnh sửa flow POS mà không xem tác động tới invoice history
- Không giả định mọi quán đều có quy trình giống nhau nếu chưa xác nhận

Câu hỏi mặc định AI nên tự kiểm tra trước khi đề xuất thay đổi

- Thay đổi này có làm sai POS flow không?
- Thay đổi này có làm sai rule 10 bill / 30 ngày không?
- Dữ liệu nào là source of truth trong thay đổi này?
- Có cần migration DB không?
- Có cần sửa response schema hoặc event payload không?
- Có cần thêm log, test case hoặc fallback không?
- Có phát sinh vấn đề bảo mật dữ liệu khuôn mặt hoặc dữ liệu khách hàng không?
- Nếu module AI lỗi thì hệ thống POS có còn chạy bình thường không?

Ví dụ event payload chuẩn hóa
recognition.matched
{
"event": "recognition.matched",
"camera_id": "cam_01",
"customer_id": 123,
"customer_name": "Nguyen Van A",
"confidence": 0.92,
"recognized_at": "2026-03-25T10:00:00Z"
}

loyal_customer.verified
{
"event": "loyal_customer.verified",
"customer_id": 123,
"invoice_count_30d": 12,
"qualified": true,
"checked_at": "2026-03-25T10:00:01Z"
}

greeting.triggered
{
"event": "greeting.triggered",
"customer_id": 123,
"customer_name": "Nguyen Van A",
"message": "Xin chào anh A, rất vui được gặp lại anh tại quán.",
"greeted_at": "2026-03-25T10:00:02Z"
}

Prompt ngắn để AI hiểu nhanh dự án
Bạn đang làm việc trên một hệ thống quản lý quán cà phê có tích hợp AI nhận diện khách hàng thân thiết. Hệ thống gồm POS, admin, quản lý sản phẩm, đơn hàng, hóa đơn, khách hàng, người dùng, báo cáo, cùng với module AI/CV dùng Python + OpenCV + YOLO để nhận diện khách qua camera. Backend dùng FastAPI, database dùng PostgreSQL, frontend quản lý dùng React và realtime dashboard dùng WebSocket. Hóa đơn từ POS là nguồn dữ liệu chính để xác định loyal customer. Một khách được xem là thân thiết nếu có từ 10 hóa đơn hợp lệ trong 30 ngày gần nhất. Nếu nhận diện đủ tin cậy và khách đủ điều kiện loyal customer thì hệ thống tự động chào và ghi log sự kiện. Khi hỗ trợ dự án này, hãy ưu tiên tính ổn định của POS flow, tách AI logic với business logic, đảm bảo bảo mật dữ liệu khuôn mặt và luôn có fallback khi độ tin cậy thấp hoặc hệ thống AI gặp lỗi.

Từ khóa nội bộ quan trọng

- coffee shop management
- POS
- admin dashboard
- loyal customer
- recognition event
- greeting event
- 10 invoices in last 30 days
- face matching confidence
- realtime dashboard
- auto greeting
- privacy-aware face recognition
- invoice is source of truth

Mục tiêu cuối cùng
Tạo ra một hệ thống có thể vận hành thực tế cho quán cà phê, vừa hỗ trợ bán hàng và quản lý như một phần mềm POS/admin hoàn chỉnh, vừa có khả năng nhận diện khách quen đủ tin cậy để tự động chào đón họ và hỗ trợ quản lý theo dõi toàn bộ hoạt động qua dashboard realtime.
