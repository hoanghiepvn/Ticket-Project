# Dataset: nguồn → đích

- Bronze: transform_source_to_bronze_ticket_<table>
- Silver: transform_bronze_to_silver_ticket_<table>
- Gold dimension: transform_silver_to_gold_ticket_<dim_name>
- Fact: transform_gold_dimensions_to_gold_fact_ticket_sales
- Mart: transform_gold_fact_to_gold_agg_daily_sales

Tên được khai báo trực tiếp trong từng file DAG; producer và consumer phải trùng tên.
dag_id, task_id, lịch và quy tắc chờ không đổi.
Bronze all và Silver all phát thêm Dataset hậu tố all, đồng thời phát Dataset từng
bảng để các DAG phía sau vẫn hoạt động với cả chạy theo bảng và chạy all.
Gold all vẫn phát các Dataset tương ứng cho từng model.

Đổi tên Dataset tạo định danh Dataset mới trong Airflow. Sự kiện cũ không chuyển
sang tên mới; cần lần chạy upstream thành công mới để bắt đầu chuỗi mới.
Không tự phát sự kiện giả hoặc chạy đồng bộ dữ liệu khi đổi tên.
Dataset cũ có thể còn hiển thị trong lịch sử Airflow nhưng không được DAG mới sử dụng.
