# Dữ liệu nguồn SQL Server

Database hiện hành: **TicketingDB**, server localhost, Windows Authentication.
Dữ liệu được mô phỏng cho khóa luận, không phải giao dịch chính thức của Ticketbox. Không chứa khách hàng.

## Nội dung


Dùng append_history.py cho database đã có dữ liệu. Năm script cũ vẫn dành cho
việc tạo bộ dữ liệu vào database trống.

Từ thư mục Ticket_Project, chạy:

```powershell
python .\Source\SqlServer\append_history.py --load
```

Mặc định bổ sung 2022: 30.000 đơn; 2023: 40.000; 2024: 55.000; 2025: 70.000.
Script cũng hỗ trợ năm 2021 (mặc định 10.000 đơn khi chọn năm này):

```powershell
python .\Source\SqlServer\append_history.py --start-year 2019 --end-year 2019 --orders-per-year 30000 --seed 2020 --load
```

Phân bố năm 2021 là giả lập, không tái hiện tác động dịch bệnh hay thị trường thực tế.
Mỗi năm có 36 sự kiện, 108 hạng vé; đơn trải từ tháng 1 đến tháng 12.
Đây là dữ liệu mô phỏng: xu hướng tăng trưởng, giá vé và tỷ lệ WEB/APP được thiết kế,
không dùng để kết luận về thị trường bán vé thực tế.

- Không có --load: chỉ sinh và kiểm tra trong bộ nhớ, lưu manifest, chưa ghi DB.
- Có --load: thêm cả năm bảng trong một transaction cho mỗi năm.
- Lấy ID mới sau MAX(id) đang có, không UPDATE/DELETE dữ liệu cũ.
- Cùng năm + seed + số đơn: chạy lại sẽ bỏ qua batch đã nạp.
- Cùng năm + seed nhưng khác số đơn: báo lỗi, không ghi thêm.
- Đổi seed tạo một batch sự kiện/đơn mới độc lập trong năm đó.
- Nếu có lỗi, năm đang nạp rollback; các năm đã commit vẫn giữ.
- Không chạy Airbyte sync trong lúc đang nạp. Chờ toàn bộ lệnh hoàn thành.

Ví dụ bổ sung thêm 10.000 đơn năm 2024 thuộc một batch mới:

```powershell
python .\Source\SqlServer\append_history.py --start-year 2020 --end-year 2020 --orders-per-year 2000 --seed 3 --load
```

Chỉ tạo thử, chưa ghi database:

```powershell
python .\Source\SqlServer\append_history.py --start-year 2022 --end-year 2022 --orders-per-year 1000
```

Yêu cầu Python + pyodbc + ODBC Driver 17/18, SQL Server localhost,
TicketingDB và Windows Authentication. Nếu thiếu pyodbc:
```powershell
python -m pip install pyodbc
```

Manifest từng lần chạy nằm trong history_batches/.
Sau khi nạp xong: đồng bộ đủ 5 bảng Airbyte → chờ Silver/Gold → Refresh Power BI.
dbt vẫn full_refresh=false. Dữ liệu có ngày cũ vẫn được incremental xử lý vì
model so sánh hash toàn snapshot, không chỉ lọc ngày lớn nhất.

- events.py, ticket_types.py, orders.py, order_items.py, payments.py: năm entry point sinh dữ liệu; engine chung trong events.py.
- schema.sql: định nghĩa năm bảng, khóa, ràng buộc và index.
- create_database.sql: chỉ tạo database mới, từ chối nếu đã tồn tại.
- generated/: bộ SQL hiện hành phiên bản 1.1, 100000 đơn; manifest, checksum và preview đi kèm.
- reload_ticketingdb.sql: thay toàn bộ dữ liệu năm bảng bằng bộ generated, có tính phá hủy; KHÔNG chạy để mở hoặc xem database.
- DATA_DICTIONARY.md: từ điển dữ liệu.

Giữ bộ generated hiện hành; các file kiểm thử độc lập đã được bỏ theo yêu cầu.
Không nạp lại chỉ vì đổi vị trí thư mục: database SQL Server đang có không bị thay đổi.

## Tạo bộ mới, không nạp database

Yêu cầu Python 3.10+, không cần thư viện bổ sung. Mở terminal tại Source/SqlServer:

```powershell
python events.py --output generated_new
python ticket_types.py --output generated_new
python orders.py --output generated_new
python order_items.py --output generated_new
python payments.py --output generated_new
```

Muốn thử ít dữ liệu: thêm cùng --orders 30 --seed 42 cho cả năm lệnh, dùng thư mục output riêng.
Phải dùng cùng tham số cho năm script. Không trộn các bộ có ID bắt đầu từ đầu vào cùng database.
Năm entry point cũ không có append; để bổ sung vào DB đang có dùng append_history.py ở trên.

## Nạp vào database mới

Chỉ thực hiện có chủ đích khi database đích trống:

1. Kiểm tra tên database trong create_database.sql trước khi chạy.
2. Chạy schema.sql trên database mới.
3. Dùng sqlcmd hoặc SSMS SQLCMD Mode chạy năm SQL trong generated theo thứ tự 01 đến 05.
4. Tự kiểm tra dữ liệu bằng truy vấn nghiệp vụ của bạn.
Các file generated hiện trỏ USE TicketingDB; muốn database khác phải sinh bộ mới với --database TenDatabase.

Thời gian nghiệp vụ là UTC+07:00; tiền nguyên VND. updated_at không tự thay đổi khi UPDATE: ứng dụng phải cập nhật đúng.
Batch gốc: 36 sự kiện, 108 hạng vé, 100000 đơn, 111949 chi tiết và 118430 lần thanh toán.
Sau đợt lịch sử seed 20221004: 180 sự kiện, 540 hạng vé, 295000 đơn,
330289 chi tiết đơn và 348406 lần thanh toán.
Không chạy script reload trong lúc Airbyte đang đồng bộ.
