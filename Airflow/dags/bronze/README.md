# Bronze Airbyte

- bronze_ticket_*.py: DAG người dùng, lịch và logging giữ nguyên.
- config.py: CONNECTIONS ánh xạ tên nghiệp vụ sang Airbyte Connection ID.
- airbyte_sync.py: hàm submit dùng chung; phải giữ để các DAG import.
- ../../plugins/ticketing/sensors.py: chờ Airbyte thành công và phát Dataset.
- ../../plugins/ticketing/data_assets.py: ánh xạ dag_id sang Dataset.

Mỗi DAG có trigger_airbyte → wait_for_complete.
Chỉ bật bronze_ticket_all HOẶC các DAG riêng cho cùng đợt đồng bộ.
Stream thực tế do cấu hình connection Airbyte quyết định, không phải tên DAG.
Nếu đổi dag_id, cập nhật ánh xạ BRONZE_DAG_TABLES trong data_assets.py.
Timeout/dừng DAG không hủy job Airbyte; kiểm tra Airbyte trước khi chạy lại.
Không ghi credentials vào code hoặc log.

