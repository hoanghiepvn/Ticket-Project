# Thiết kế dữ liệu và điều phối

## Các ranh giới

airbyte_internal: bảng nội bộ connector, không sửa tay hoặc làm phụ thuộc nghiệp vụ vào cấu trúc nội bộ.
bronze: bảng đích được Airbyte xuất ra với business fields và metadata.
Không dùng work_bronze. dbt source('bronze',...) trỏ trực tiếp schema bronze do Airbyte quản lý.
silver: trạng thái đã ép kiểu, trim, dedup, incremental MERGE.
gold_build: dimension, fact, mart đang xây.
gold: dimension/fact/mart do dbt ghi trực tiếp. BI chỉ đọc sau DAG thành công.
audit: run đang xử lý, xác nhận đầu vào và lịch sử publish, số dòng công bố. Cột frozen_at cũ giữ tên để tương thích, nay ghi thời điểm xác nhận Bronze.

Đây là các schema trong một database ticketing_analytics, không phải nhiều database.

## dbt

Không có models/bronze. Mỗi model Silver tự đọc source Bronze, cast kiểu, trim chuỗi và tính hash trong các CTE rồi dedup/MERGE. Không tạo bảng stg_* trung gian.
models/silver: mỗi bảng có khóa nghiệp vụ unique_key và index; row_number chọn phiên bản mới nhất theo updated_at, thời gian trích xuất, raw ID và hash để phá hòa.
Nếu hai phiên bản cùng updated_at nhưng nội dung khác, nguồn cần timestamp/version đáng tin cậy; lựa chọn phá hòa chỉ đảm bảo xác định, không chứng minh đúng nghiệp vụ.

MERGE ghi các khóa mới, hash thay đổi hoặc được phục hồi. Không dùng max(updated_at) toàn bảng, nên cập nhật đến muộn vẫn được so sánh.
full_snapshot: khóa biến mất đánh _is_deleted=true; dòng giữ lại để theo dõi xóa logic.
append_history: không suy diễn xóa từ khóa vắng. Chỉ dùng khi Bronze giữ đủ lịch sử phiên bản; không có CDC delete-event handling.
_loaded_at là thời điểm xử lý gần nhất; _record_hash hash business fields.
Đây là Type 1/current-state, không phải SCD2/time travel.

models/gold/dimensions: bảng dimension nhỏ rebuild.
models/gold/facts: một dòng mỗi order_item_id, incremental merge. Khi đơn hàng đổi trạng thái, dòng fact cũ được tính lại.
Không join trực tiếp payments vào fact bán vé vì một order có thể có nhiều lần thanh toán.
sales_amount và sold_quantity chỉ ghi nhận order_status=PAID; doanh thu ghi theo ngày đặt hàng, không phải ngày tiền về.
models/gold/marts: tổng hợp ngày/sự kiện/kênh rebuild để không sót nhóm cũ khi dữ liệu chuyển ngày hoặc kênh.
Không cộng paid_orders tùy tiện qua mọi chiều; phải tuân thủ grain đơn hàng.
YAML khai báo kiểu cột, mô tả, contracts, PK tests, quan hệ, accepted values và một số phương trình nghiệp vụ. Không phải bộ kiểm thử đầy đủ mọi yêu cầu nghiệp vụ.

## Airflow

preflight → airbyte.submit_sync → airbyte.wait_for_sync
→ bronze.confirm_loaded
→ 5 task silver_* → silver.complete_and_optional_tests
→ 5 task dim_* → fact_ticket_sales → agg_daily_sales
→ gold.complete_and_optional_tests → gold.record_completion.

Mỗi model có một task và thư mục artifacts/logs riêng. Các model độc lập trong cùng tầng có thể chạy song song (tối đa 2 task); tầng sau đợi toàn bộ tầng trước thành công.
Không có bản sao cách ly đầu vào: phải tắt lịch Airbyte riêng và không sync thủ công khi DAG đang chạy. Gold ghi trực tiếp từng model; không refresh BI giữa các task.

Mỗi DAG có max_active_runs=1. Bronze chờ Silver, Silver chờ Gold bằng sensor reschedule để giữ cả chuỗi tuần tự. Preflight từ chối một pipeline khác đang chạy; không chạy sync hoặc dbt độc lập cùng lúc.
Retry có giới hạn cho thao tác idempotent; submit POST Airbyte retries=0 và lưu checkpoint.
TaskGroups giúp xem từng tầng; Params kiểm soát full refresh, tests và kiểu Bronze.
Không giữ worker trong vòng lặp chờ Airbyte; sensor nhả worker giữa các lần poll.
Không gọi API/DB khi import DAG.
Mỗi model Gold có transaction riêng, không có atomic publication toàn bộ tầng. Fact xóa các dòng _is_deleted trong post-hook cùng transaction để BI không đếm tombstone.
Khi run_tests=false, không có cổng kiểm thử chất lượng trước publish. Người dùng chịu trách nhiệm bật/chạy khi cần.
Power BI Import chỉ refresh sau DAG thành công, khi không có run mới đang chạy.

## Tương thích

PostgreSQL 15+ để dùng MERGE; Compose dùng 17.9.
dbt-core 1.9.8 / dbt-postgres 1.9.0; môi trường venv riêng khỏi Airflow.
Tham khảo: https://docs.getdbt.com/reference/resource-configs/postgres-configs
