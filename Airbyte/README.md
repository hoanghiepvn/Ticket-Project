# Thiết lập Airbyte local

## Cài nền tảng

Airbyte local đang dùng abctl 0.30.4. Binary nằm trong Airbyte/tools/abctl-0.30.4/abctl-v0.30.4-windows-amd64/abctl.exe. Từ thư mục project, dùng `./Scripts/airbyte.ps1 -Action credentials` để xem thông tin đăng nhập tại máy.

Lưu ý bảo mật: abctl hiện publish cổng 8000 trên 0.0.0.0 theo mặc định của công cụ, khác các cổng Compose chỉ bind localhost. Không mở thêm firewall hoặc port forwarding ra Internet; giữ xác thực Airbyte bật. Phạm vi truy cập LAN còn phụ thuộc firewall máy.

Docker Desktop phải đang chạy Linux containers. Script Scripts/install-airbyte.ps1 tải abctl Windows amd64 0.30.4, kiểm SHA256 từ release chính thức và giải nén trong Airbyte/tools; không đổi PATH hệ thống. Thêm -Deploy để cài Airbyte mới khi chưa có cluster. Airbyte tạo Kubernetes kind riêng trong Docker; cần RAM bổ sung cho SQL Server, PostgreSQL và Airflow.

Dùng abctl local status để xem trạng thái. Khi cài xong, mở http://localhost:8000. Chạy abctl local credentials tại máy để xem mật khẩu và client credentials; không gửi chúng vào chat hay commit lên Git. Nhập email/tên tổ chức của chính bạn nếu UI yêu cầu. Script không tự cung cấp thông tin cá nhân hoặc đăng ký dịch vụ Cloud.

## SQL Server source

Nguồn: TicketingDB trên Windows. Airbyte cần truy cập TCP từ container; Windows authentication của sqlcmd trên host không tự trở thành thông tin đăng nhập của Airbyte. Kiểm tra TCP và port của đúng instance trong SQL Server Configuration Manager. Dùng tài khoản SQL chỉ có SELECT trên năm bảng. Không dùng sa, không bật CDC ở bước đầu.

Host thử trên Docker Desktop là host.docker.internal, port 1433 đã kiểm tra được từ Windows host. Không dùng localhost trong connector vì đó là container connector. Không mở firewall rộng hoặc đổi xác thực toàn máy chỉ để thử kết nối. Dùng Check connection để xác minh đường đi từ connector. SQL Server hỗ trợ mixed authentication; vẫn cần tài khoản SQL đọc riêng.

Script Source/SqlServer/create_airbyte_reader.sql là mẫu chạy trên SQL Server có chủ đích bởi người quản trị. Nó không được chạy tự động và không có mật khẩu thật trong repository.

## PostgreSQL destination

Database phân tích là ticketing_analytics, user airbyte_loader, password theo AIRBYTE_DB_PASSWORD; schema mặc định bronze; schema nội bộ airbyte_internal. Chỉ user này có quyền ghi schema Bronze. Tên bảng phải giữ lowercase đúng 5 tên nguồn.

Nếu connector truy cập qua host.docker.internal thì port là 5433. Compose mặc định bind localhost để tránh lộ mạng; tùy Docker Desktop/kind, connector có thể không truy cập được host loopback. Không tự đổi sang 0.0.0.0. Có thể nối node Docker của kind vào network ticketing-elt_default rồi thử host warehouse-db:5432; cách này cần kiểm tra DNS/routing thực tế của pods và duy trì lại sau khi tạo lại cluster. Nếu chưa thông, chọn một địa chỉ riêng và firewall hẹp sau khi người dùng đồng ý. Trạng thái Check connection mới là bằng chứng, không chỉ container healthy.

## Connection

Chọn dbo.events, dbo.ticket_types, dbo.orders, dbo.order_items, dbo.payments. Không chọn bảng khác. Destination namespace dùng schema bronze, không lấy dbo từ source và không thêm prefix. Full Refresh / Overwrite cho cả năm bảng; Manual schedule; không tự propagate schema change chưa kiểm tra.

Mặc định vẫn dùng Full Refresh / Overwrite. Silver đã có dedup và MERGE, nhưng incremental ở dbt không đồng nghĩa Airbyte đã bật CDC. Chế độ append_history là lựa chọn riêng cần giữ đủ lịch sử Bronze và không tự xử lý delete events. Không giả định mọi connector đều có _airbyte_raw_* JSON tables.

## Kết nối Airflow

Điền trong .env:
AIRBYTE_API_URL=http://host.docker.internal:8000/api/public/v1
AIRBYTE_CLIENT_ID=<giá trị local>
AIRBYTE_CLIENT_SECRET=<giá trị local>
AIRBYTE_CONNECTION_ID=<UUID connection>

URL phải là Public API base của bản Airbyte cài thực tế, không dùng Configuration API /api/v1 thay thế. Client gọi POST applications/token, POST jobs với jobType=sync và GET jobs/{jobId}. Nếu ingress chặn Host từ container, kiểm tra cấu hình truy cập local theo tài liệu Airbyte; không tắt authentication.

Khởi tạo lại container ứng dụng bằng docker compose up -d --no-build sau khi sửa .env. DAG dừng ngay nếu thiếu credentials. Token không đưa vào XCom hoặc log; job id có thể được ghi để truy vết. Không bật lịch Airbyte riêng trong khi dùng Airflow.

## Nghiệm thu end to end

Người dùng tự nghiệm thu: Check connection source/destination, sync đủ 5 stream, DAG các tầng thành công, kiểm tra audit.current_publication và số liệu BI. YAML tests chạy tùy chọn, không mặc định chạy và không tuyên bố đã đạt.

Nguồn: https://docs.airbyte.com/platform/using-airbyte/getting-started/oss-quickstart và https://reference.airbyte.com/reference/createjob
