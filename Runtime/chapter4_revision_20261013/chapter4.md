# CHƯƠNG 4. TRIỂN KHAI VÀ ĐÁNH GIÁ HỆ THỐNG

Chương này trình bày quá trình hiện thực hóa hệ thống xử lý dữ liệu bán vé sự kiện theo thiết kế đã đề xuất. Nội dung tập trung vào môi trường triển khai, chương trình tạo dữ liệu, cơ chế đồng bộ, các mô hình biến đổi và luồng điều phối. Kết quả được đánh giá dựa trên mã nguồn, sản phẩm thực thi và số liệu đối chiếu đã ghi nhận, qua đó xác định mức độ đáp ứng yêu cầu cùng những giới hạn cần tiếp tục hoàn thiện.

## 4.1. Môi trường triển khai và tổ chức mã nguồn

### 4.1.1. Các thành phần triển khai

Hệ thống được triển khai trong môi trường cục bộ trên Windows, kết hợp các dịch vụ chạy bằng Docker với những ứng dụng được cài đặt trên máy. SQL Server lưu cơ sở dữ liệu nguồn; PostgreSQL lưu dữ liệu phân tích và dữ liệu vận hành của Airflow trong các cơ sở dữ liệu riêng. Airbyte được quản lý bằng công cụ `abctl`, còn Power BI Desktop được sử dụng để kết nối và xây dựng báo cáo.

Các phiên bản được xác định từ cấu hình xây dựng môi trường và tệp khai báo thư viện của project.

| Thành phần | Phiên bản hoặc cấu hình |
|---|---|
| Apache Airflow | 2.10.5 |
| Python trong môi trường Airflow | 3.11 |
| PostgreSQL trong Docker | 17.9 |
| dbt-core | 1.9.8 |
| dbt-postgres | 1.9.0 |
| Bộ thực thi Airflow | LocalExecutor |
| Múi giờ nghiệp vụ | `Asia/Ho_Chi_Minh` |

Môi trường dbt được đặt trong một môi trường Python riêng bên trong image ứng dụng. Cách tổ chức này tách các thư viện của dbt khỏi môi trường Python chính của Airflow, giúp quản lý phiên bản phụ thuộc theo chức năng. Khi xây dựng image, các thư viện được cài đặt theo phiên bản khai báo và kiểm tra sự tương thích của các gói.

Docker Compose tổ chức các dịch vụ kho dữ liệu, cơ sở dữ liệu siêu thông tin Airflow, khởi tạo Airflow, webserver và scheduler. Dịch vụ khởi tạo thực hiện nhiệm vụ chuẩn bị cấu trúc và cấu hình vận hành; sau khi hoàn tất, dịch vụ này không cần duy trì trạng thái chạy như webserver hoặc scheduler.

Từ máy Windows, giao diện Airflow sử dụng cổng 8080, Airbyte sử dụng cổng 8000 và kho PostgreSQL được công bố qua cổng 5433. Trong mạng Docker, PostgreSQL được truy cập bằng tên dịch vụ và cổng nội bộ 5432. Sự phân biệt này được áp dụng trong cấu hình kết nối của các thành phần.

### 4.1.2. Tổ chức mã nguồn và cấu hình

Mã nguồn được phân chia theo chức năng: tạo dữ liệu nguồn, điều phối, biến đổi, báo cáo và tài liệu. Trong phần điều phối, các DAG được nhóm theo Bronze, Silver và Gold; phần dùng chung quản lý kết nối dịch vụ, chờ công việc và thực thi dbt. Trong phần biến đổi, mô hình SQL được tổ chức theo tầng, còn các macro tập trung những quy tắc có thể tái sử dụng.

Cách phân chia này cho phép liên hệ một tác vụ với mô hình và bảng đầu ra tương ứng. Khi cần thay đổi nghiệp vụ, người thực hiện chỉnh sửa mô hình gốc và cấu hình liên quan thay vì sửa trực tiếp câu SQL đã biên dịch trong sản phẩm thực thi.

Các tham số kết nối được cung cấp qua cấu hình môi trường. Trong báo cáo, thông tin kết nối được trình bày theo vai trò và tên tham số; các giá trị xác thực không được đưa vào đoạn mã minh họa. Những cấu hình quan trọng như múi giờ, phạm vi mô hình và giới hạn thời gian thực thi được quản lý thống nhất với môi trường triển khai.

## 4.2. Triển khai cơ sở dữ liệu nguồn và chương trình sinh dữ liệu

### 4.2.1. Tạo cấu trúc dữ liệu nguồn

Cơ sở dữ liệu `TicketingDB` gồm năm bảng: `events`, `ticket_types`, `orders`, `order_items` và `payments`. Các bảng được xây dựng với khóa chính, khóa ngoại, ràng buộc duy nhất và ràng buộc giá trị theo thiết kế ở Chương 3.

Các ràng buộc được sử dụng để kiểm soát những điều kiện có thể biểu diễn trực tiếp tại cơ sở dữ liệu. Ví dụ, số lượng vé phải nằm trong phạm vi quy định; giá trị sau giảm giá phải bằng giá trị trước giảm giá trừ khoản giảm giá; hạng vé của dòng đơn phải thuộc cùng sự kiện với đơn hàng.

Đối với thanh toán, chỉ mục duy nhất có điều kiện được áp dụng trên mã đơn hàng khi trạng thái là `SUCCESS`. Điều này giới hạn tối đa một lần thanh toán thành công cho mỗi đơn trong cấu trúc nguồn. Những yêu cầu tổng hợp qua nhiều dòng, như tổng giá trị các dòng bằng tổng tiền đơn, được kiểm tra bổ sung trong chương trình sinh dữ liệu.

### 4.2.2. Sinh dữ liệu có quan hệ nghiệp vụ

Chương trình Python tạo dữ liệu theo thứ tự phụ thuộc: sự kiện, hạng vé, đơn hàng, chi tiết đơn hàng và thanh toán. Các đối tượng sử dụng chung bộ quy tắc sinh để giữ sự nhất quán khi xuất dữ liệu cho từng bảng.

Dữ liệu sự kiện gồm nhóm nội dung, địa điểm, thời gian và khoảng mở bán. Hạng vé được thiết lập theo sự kiện, với giá và hạn mức tương ứng. Đơn hàng được tạo trong khoảng mở bán, có kênh bán, trạng thái và một hoặc nhiều dòng vé. Các lần thử thanh toán được hình thành theo trạng thái của đơn.

Chương trình sử dụng các trọng số để tạo sự khác biệt giữa sự kiện, hạng vé và thời điểm đặt. Nhờ đó, dữ liệu có nhiều nhóm và trạng thái để phục vụ phân tích, thay vì mọi sự kiện có cùng số đơn hoặc mọi đơn có cấu trúc giống nhau. Những trọng số này là giả định của chương trình, không phải tham số được suy ra từ dữ liệu kinh doanh thực tế.

Trước khi xuất hoặc nạp, chương trình kiểm tra các quan hệ và tổng tiền. Những điều kiện được kiểm tra gồm sự phù hợp về sự kiện giữa đơn và hạng vé, giá trị dòng, tổng tiền đơn, số lần thanh toán thành công và số vé bán trong hạn mức.

### 4.2.3. Bổ sung dữ liệu lịch sử

Chương trình bổ sung lịch sử nhận các tham số về năm bắt đầu, năm kết thúc, số đơn mỗi năm và giá trị khởi tạo. Quy trình tách bước sinh dữ liệu khỏi bước nạp để người thực hiện có thể xác định phạm vi trước khi ghi vào nguồn.

Khi nạp một lô, chương trình xác định phạm vi khóa đã tồn tại và điều chỉnh khóa của dữ liệu mới cùng các tham chiếu liên quan. Các bảng được nạp theo thứ tự phụ thuộc trong một giao dịch cho từng năm. Nếu có lỗi trong quá trình nạp năm đó, giao dịch được hoàn tác.

Chương trình còn kiểm tra dấu hiệu lô đã được nạp theo thông tin nhận diện. Nếu lô tồn tại nhưng số lượng không phù hợp với cấu hình mới, quá trình nạp dừng để tránh sử dụng lại định danh cho một bộ dữ liệu khác. Hồ sơ lô ghi nhận tham số và kết quả nạp, hỗ trợ theo dõi quá trình mở rộng dữ liệu.

Giao dịch được tổ chức theo năm, nên một yêu cầu nạp nhiều năm không được hiểu là một giao dịch duy nhất cho toàn bộ giai đoạn.

## 4.3. Triển khai đồng bộ và điều phối tầng Bronze

### 4.3.1. Cấu hình đồng bộ bằng Airbyte

Airbyte sử dụng kết nối nguồn SQL Server và kết nối đích PostgreSQL. Năm bảng nghiệp vụ được đồng bộ vào lược đồ `bronze` theo chế độ Full Refresh Overwrite.

Sau khi đồng bộ thành công, các bảng Bronze cung cấp dữ liệu cho những mô hình Silver tương ứng. dbt khai báo các bảng này là nguồn, giúp phân biệt dữ liệu do Airbyte nạp với dữ liệu do mô hình biến đổi tạo ra.

Mã Connection ID được quản lý trong cấu hình dùng chung và được từng DAG lấy theo tên nghiệp vụ. Lịch chạy nằm trong DAG, nhờ đó việc thay đổi thời điểm đồng bộ không làm thay đổi định danh kết nối.

### 4.3.2. Kích hoạt và chờ công việc

DAG Bronze có hai tác vụ: kích hoạt Airbyte và chờ công việc hoàn tất. Đoạn mã sau trích cơ chế thực thi:

```python
run_airbyte = PythonOperator(
    task_id="trigger_airbyte",
    python_callable=trigger_sync,
    op_kwargs={"connection_id": CONNECTION_ID},
    retries=0,
)

wait_airbyte = AirbyteJobSensor(
    task_id="wait_for_complete",
    job_id=run_airbyte.output,
    outlets=OUTPUT_DATASETS,
    mode="reschedule",
    poke_interval=30,
    timeout=4 * 60 * 60,
)

run_airbyte >> wait_airbyte
```

Mã công việc trả về từ bước kích hoạt được truyền sang bộ cảm biến. Bộ cảm biến kiểm tra đúng công việc đó và chỉ hoàn thành khi trạng thái là `succeeded`. Các trạng thái đang chờ hoặc đang chạy tiếp tục được theo dõi; trạng thái kết thúc không thành công làm tác vụ báo lỗi.

Chế độ `reschedule` cho phép nhả vị trí thực thi giữa các lần kiểm tra. Giới hạn chờ được cấu hình để công việc không tiếp tục chờ vô thời hạn.

Bước gửi yêu cầu không tự thử lại theo cấu hình của DAG minh họa. Quyết định này hạn chế việc gửi thêm yêu cầu khi công việc bên ngoài có thể đã được tạo. Khi cần thực hiện lại, người vận hành phải đối chiếu mã và trạng thái công việc đã nhận.

Dataset được gắn với bước chờ, vì vậy tín hiệu hoàn thành Bronze tương ứng được phát sau khi tác vụ xác nhận đồng bộ thành công.

## 4.4. Triển khai các mô hình dbt

### 4.4.1. Cấu hình mô hình

:::changed
Phương thức tạo dữ liệu đầu ra được khai báo trực tiếp trong khối `config()` của từng mô hình SQL. Các mô hình Silver và bảng `fact_ticket_sales` sử dụng `materialized='incremental'` cùng `incremental_strategy='merge'`. Năm bảng chiều và bảng `agg_daily_sales` khai báo `materialized='table'`. Cách tổ chức này cho phép xác định và điều chỉnh chế độ xử lý khi đọc từng mô hình, thay vì phải tìm cấu hình kế thừa theo thư mục.

Cấu hình chung trong `dbt_project.yml` quản lý lược đồ, tag, mô tả, hợp đồng cấu trúc và quy tắc xử lý thay đổi cấu trúc. Phương thức tạo dữ liệu và chiến lược cập nhật không còn được đặt chung cho Silver hoặc Gold. Những thuộc tính riêng như khóa nhận diện, tên bảng và chỉ mục được khai báo cùng mô hình tương ứng.

Ví dụ, mô hình sự kiện tại Silver có cấu hình:

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    alias='events',
    unique_key='event_id',
    indexes=[
        {'columns': ['event_id'], 'unique': true},
        {'columns': ['updated_at']}
    ]
) }}
```

Trong cấu hình này, `materialized` xác định cách duy trì bảng đầu ra; `incremental_strategy` xác định cách hợp nhất trên lượt chạy tăng dần; `unique_key` là khóa đối chiếu giữa bản ghi ứng viên và bảng đích. Khai báo `unique_key` không tự tạo ràng buộc duy nhất tại cơ sở dữ liệu, nên chỉ mục và kiểm tra khóa vẫn có trách nhiệm riêng.

Các khai báo YAML mô tả cột, kiểu dữ liệu và điều kiện kiểm tra, giúp cấu trúc đầu ra được quản lý cùng mã nguồn.
:::

Cấu hình `on_schema_change: fail` được sử dụng để dừng khi cấu trúc không phù hợp với trạng thái bảng đích. Cách xử lý này giúp thay đổi cấu trúc được xem xét có chủ đích trước khi tiếp tục biến đổi.

### 4.4.2. Chuẩn hóa và khử trùng tại Silver

Các mô hình Silver đọc dữ liệu bằng `source()`, chuyển đổi kiểu và chuẩn hóa văn bản. Những trường trạng thái, tiền tệ và kênh bán được biểu diễn nhất quán để sử dụng trong điều kiện tính toán.

Sau đó, mô hình tạo dấu vân tay và xếp hạng theo khóa. Đối với đơn hàng, cơ chế xếp hạng được hiện thực như sau:

```sql
row_number() over (
    partition by order_id
    order by
        updated_at desc nulls last,
        _source_extracted_at desc nulls last,
        _source_raw_id desc nulls last,
        _record_hash desc
) as version_rank
```

Bản ghi có thứ hạng đầu tiên được giữ trong tập ứng viên. Việc khử trùng được thực hiện trước phép hợp nhất, nhằm tránh nhiều bản ghi cùng khóa tác động đến một dòng đích.

Thông tin trích xuất được sử dụng trong lựa chọn bản ghi nhưng không được đưa vào dấu vân tay nội dung. Vì vậy, việc nhận lại cùng nội dung trong một lần đồng bộ mới không tự tạo ra thay đổi nghiệp vụ.

### 4.4.3. Hợp nhất bản ghi và quản lý trạng thái

Macro dùng chung đối chiếu ứng viên với bảng đích. Trên lần chạy tăng dần, các bản ghi được chọn để ghi khi khóa chưa tồn tại, dấu vân tay khác hoặc bản ghi đích đang bị đánh dấu xóa.

Điều kiện lựa chọn được thể hiện trong trích đoạn:

```sql
left join {{ this }} t
    on c.order_id = t.order_id
where t.order_id is null
   or c._record_hash is distinct from t._record_hash
   or t._is_deleted
```

Trích đoạn trên minh họa trường hợp khóa đơn hàng; macro thực tế nhận khóa và tập trường theo từng mô hình.

Đối với bản ghi đang có hiệu lực ở đích nhưng không còn trong tập ứng viên, macro tạo trạng thái xóa mềm. Khi khóa xuất hiện trở lại, điều kiện kiểm tra trạng thái xóa cho phép khôi phục dù nội dung không thay đổi.

Các bản ghi không đổi được giữ nguyên thay vì ghi lại. Cơ chế này giảm số dòng cần hợp nhất, nhưng vẫn phải đọc dữ liệu để tạo và đối chiếu tập ứng viên. `_loaded_at` được cập nhật khi bản ghi được ghi, nên không thể dùng riêng trường này để xác nhận thời điểm đồng bộ gần nhất của bảng.

:::changed
### 4.4.4. Cấu hình chỉ mục và phạm vi sử dụng phân vùng

Chỉ mục được khai báo trong thuộc tính `indexes` của mô hình. Mỗi phần tử trong danh sách biểu diễn một chỉ mục, còn `columns` xác định các cột của chỉ mục đó. dbt-postgres thực hiện tạo chỉ mục theo cấu hình khi hiện thực hóa mô hình [1].

Trong mô hình thanh toán, cấu hình gồm hai chỉ mục riêng biệt:

```sql
indexes=[
    {'columns': ['payment_id'], 'unique': true},
    {'columns': ['updated_at']}
]
```

Chỉ mục thứ nhất áp dụng trên `payment_id` với yêu cầu duy nhất, hỗ trợ kiểm soát khóa và tra cứu bản ghi thanh toán. Chỉ mục thứ hai áp dụng trên `updated_at`, có thể hỗ trợ truy vấn sử dụng điều kiện thời gian. Hai khai báo không tạo thành một chỉ mục ghép. Chỉ mục ghép được xác định khi nhiều cột cùng nằm trong một danh sách `columns`, và thứ tự cột ảnh hưởng đến cách sử dụng chỉ mục [2].

Chỉ mục không quyết định điều kiện cập nhật tăng dần. Mô hình hiện tại vẫn đối chiếu khóa, dấu vân tay và trạng thái bản ghi; việc có chỉ mục `updated_at` không có nghĩa hệ thống chỉ đọc các dòng sau một mốc thời gian. Hiệu quả sử dụng từng chỉ mục cần được xem xét qua kế hoạch và thời gian truy vấn, đồng thời tính đến chi phí lưu trữ và cập nhật chỉ mục.

Phiên bản triển khai hiện tại không cấu hình phân vùng vật lý cho các bảng dbt. PostgreSQL có khả năng chia một bảng thành các phần lưu trữ theo khóa phân vùng [3], nhưng cơ chế này cần một thiết kế tạo bảng và quản lý phân vùng riêng. Đề tài giữ cấu trúc bảng hiện tại để tập trung đánh giá đồng bộ, chuẩn hóa và cập nhật dữ liệu; việc phân vùng là nội dung có thể xem xét khi có yêu cầu và số đo phù hợp.

Mệnh đề `partition by order_id` trong hàm `row_number()` ở mục 4.4.2 chỉ nhóm các dòng phục vụ xếp hạng và khử trùng. Nó không chia bảng thành các phân vùng lưu trữ. Vì vậy, khử trùng bằng hàm cửa sổ, chỉ mục và phân vùng vật lý là ba cơ chế có vai trò khác nhau.
:::

## 4.5. Triển khai dữ liệu phân tích tại Gold

### 4.5.1. Các bảng chiều

Năm bảng chiều được xây dựng theo phương thức tạo lại bảng. Chiều sự kiện và hạng vé lấy các bản ghi chưa bị xóa mềm từ Silver. Chiều kênh bán và trạng thái sử dụng ánh xạ khóa cố định. Chiều ngày tạo dải ngày liên tục từ phạm vi ngày đặt đơn đang có hiệu lực.

Các bảng chiều cung cấp thuộc tính mô tả và khóa để liên kết với bảng fact. Giá niêm yết tại chiều hạng vé phục vụ ngữ cảnh phân tích; giá trị giao dịch được lấy từ dòng đơn để giữ đúng mức giá đã ghi nhận.

Việc tạo lại bảng phản ánh thuộc tính hiện tại, chưa lưu các phiên bản lịch sử của chiều. Do đó, phân tích giao dịch trước đây theo thuộc tính hiện tại cần được hiểu theo phạm vi của mô hình.

### 4.5.2. Bảng đo lường bán vé

Bảng `fact_ticket_sales` được xây dựng từ các dòng chi tiết có hiệu lực và đơn hàng liên quan. Mỗi bản ghi được nhận diện bằng `order_item_id`.

Ngày phân tích được lấy từ `ordered_at`. Các khóa kênh bán và trạng thái được tra cứu từ bảng chiều. Quy tắc chỉ tiêu bán được hiện thực bằng điều kiện trạng thái:

```sql
case when o.order_status = 'PAID'
     then i.quantity else 0
end as sold_quantity,

case when o.order_status = 'PAID'
     then i.line_amount else 0
end as sales_amount
```

Mô hình xem xét lại các dòng đang có hiệu lực cùng đơn hàng ở mỗi lần chạy. Nhờ đó, thay đổi trạng thái đơn hàng được phản ánh vào tập ứng viên fact, ngay cả khi bản thân dòng chi tiết không thay đổi.

Bảng thanh toán không được nối trực tiếp vào phép tính để tránh nhân bản dòng vé theo số lần thử. Các chỉ tiêu hiện tại sử dụng trạng thái đơn làm căn cứ, còn thanh toán được giữ tại Silver cho những nhu cầu kiểm tra và mở rộng.

Fact sử dụng `merge` theo khóa dòng đơn. Những dòng không còn thuộc tập ứng viên được nhận diện qua cơ chế dùng chung, sau đó loại khỏi bảng công bố bằng bước xử lý sau mô hình.

### 4.5.3. Bảng tổng hợp

Bảng `agg_daily_sales` được tạo lại từ fact, nhóm theo ngày đặt đơn, sự kiện và kênh bán. Các giá trị vé và tiền được cộng; số đơn được đếm phân biệt theo mã đơn.

Mức tổng hợp này phù hợp với các chỉ tiêu theo thời gian, sự kiện và kênh. Phân tích hạng vé sử dụng fact chi tiết, vì bảng tổng hợp không chứa khóa hạng vé.

Bảng tổng hợp được điều phối sau fact. Tuy nhiên, các mô hình Gold được cập nhật riêng, nên việc hoàn thành một mô hình chưa có nghĩa toàn bộ Gold đã được công bố đồng thời.

## 4.6. Triển khai điều phối Silver và Gold

### 4.6.1. Thực thi mô hình theo Dataset

Các DAG Silver sử dụng Dataset từ Bronze làm điều kiện lập lịch. Khi mô hình hoàn thành, tác vụ phát Dataset cho đầu ra Silver. Lệnh chạy được thể hiện trực tiếp trong DAG để xác định phạm vi xử lý.

Ví dụ, tác vụ chạy mô hình đơn hàng sử dụng:

```python
run_model = DbtBashOperator(
    task_id="run_silver_orders",
    stage="silver",
    bash_command=(
        "dbt run --select "
        "path:models/silver/silver_orders.sql"
    ),
    outlets=OUTPUTS,
)
```

Bộ thực thi bổ sung các tham số về project, cấu hình kết nối và nơi lưu sản phẩm chạy. Trước khi gọi dbt, phạm vi lựa chọn được kiểm tra để phù hợp với tầng của DAG.

Các DAG chiều Gold chờ nhóm tín hiệu của năm bảng Silver. Fact chờ các tín hiệu của năm bảng chiều, còn bảng tổng hợp chờ fact. Cấu trúc này thể hiện trình tự thực thi từ dữ liệu chuẩn hóa đến đầu ra phân tích.

### 4.6.2. Kiểm soát chạy lại và cạnh tranh ghi

Các lượt chạy dbt có thư mục sản phẩm riêng để lưu nhật ký và kết quả thực thi. Điều này hỗ trợ kiểm tra trạng thái của từng mô hình mà không phụ thuộc vào một tệp kết quả chung bị ghi đè liên tục.

Cơ chế khóa tư vấn của PostgreSQL được sử dụng theo tên mô hình để hạn chế hai tác vụ cùng ghi vào một bảng. Khi chạy toàn tầng, các khóa được lấy theo thứ tự xác định. Cơ chế này hỗ trợ kiểm soát cạnh tranh giữa DAG riêng và DAG toàn tầng.

Giới hạn một lượt đang chạy của từng DAG không thay thế khóa giữa các DAG khác nhau. Đồng thời, khóa theo mô hình không bảo đảm toàn bộ đầu vào được giữ nguyên trong suốt chuỗi xử lý.

Tham số `full_refresh` mặc định không bật trong vận hành thường xuyên. Khi cần khởi tạo lại hoặc thay đổi cấu trúc, người thực hiện phải xác định phạm vi mô hình và kiểm soát những tác vụ có thể chạy đồng thời.

## 4.7. Khai thác dữ liệu bằng Power BI

Tệp báo cáo hiện có bốn trang:

| Trang | Mục đích khai thác |
|---|---|
| Tổng quan | Theo dõi các chỉ tiêu chính trong phạm vi thời gian lựa chọn |
| Hiệu quả các sự kiện | So sánh kết quả bán giữa các sự kiện |
| Chi tiết sự kiện | Xem dữ liệu chi tiết và phân tích hạng vé |
| Kênh bán & trạng thái đơn | Phân tích kênh và cơ cấu trạng thái |

Dữ liệu báo cáo được lấy từ Gold. Số vé đã bán sử dụng `sold_quantity`; giá trị bán vé sử dụng `sales_amount`; số đơn được xác định bằng mã đơn phân biệt. Tỷ lệ thanh toán được tính từ số đơn `PAID` trên tổng số đơn trong cùng phạm vi lọc.

Các bảng chiều tạo ngữ cảnh lọc cho bảng đo lường. Khóa định danh được sử dụng để liên kết; các cột kỹ thuật có thể được ẩn trong giao diện khai thác để tránh nhầm với chỉ tiêu nghiệp vụ.

Power BI minh họa khả năng sử dụng đầu ra, đồng thời cung cấp một điểm đối chiếu với SQL. Báo cáo cần được làm mới sau khi các mô hình cần thiết hoàn thành. Khi so sánh chỉ tiêu, hai phía phải dùng cùng điều kiện về ngày, sự kiện và kênh bán.

Phạm vi hiện tại sử dụng Power BI Desktop. Việc tự động làm mới trên dịch vụ trực tuyến chưa được xem là kết quả triển khai của khóa luận.

## 4.8. Kết quả thực thi và đối chiếu dữ liệu

### 4.8.1. Kết quả thực thi mô hình dbt

Các tệp kết quả dbt lưu ngày 13/10/2026 ghi nhận trạng thái `success` cho cả năm mô hình Silver và bảy mô hình Gold. Bảng sau sử dụng kết quả gần nhất của từng mô hình tại thời điểm đọc hồ sơ.

| Mô hình | Trạng thái | Thời gian thực thi (giây) |
|---|---|---:|
| `silver_events` | Thành công | 2,441 |
| `silver_ticket_types` | Thành công | 3,724 |
| `silver_orders` | Thành công | 7,264 |
| `silver_order_items` | Thành công | 29,972 |
| `silver_payments` | Thành công | 19,105 |
| `dim_event` | Thành công | 0,631 |
| `dim_ticket_type` | Thành công | 1,275 |
| `dim_channel` | Thành công | 1,243 |
| `dim_status` | Thành công | 1,266 |
| `dim_date` | Thành công | 1,279 |
| `fact_ticket_sales` | Thành công | 6,936 |
| `agg_daily_sales` | Thành công | 2,729 |

Những kết quả này cung cấp bằng chứng các mô hình đã thực thi thành công trên môi trường được ghi nhận. Chúng không xác nhận toàn bộ nội dung dữ liệu đã được đối chiếu hoặc mọi tình huống thay đổi đã được kiểm thử.

Các thời gian là quan sát riêng lẻ từ những lượt chạy của từng mô hình. Không cộng trực tiếp các giá trị này để suy ra thời gian toàn tuyến, do các tác vụ có thể được điều phối tại thời điểm khác nhau và có phần chạy song song.

Ở các lượt gần nhất của Silver và fact, phản hồi của câu lệnh chính ghi nhận số dòng bị tác động bằng không. Điều này phù hợp với một lượt không chọn được bản ghi cần hợp nhất, nhưng chưa đủ để khẳng định nguồn không thay đổi hoặc toàn bộ bước xử lý không thực hiện thao tác khác.

### 4.8.2. Quy mô dữ liệu tại thời điểm khảo sát

Hồ sơ khảo sát ngày 04/10/2026 ghi nhận quy mô nguồn như sau:

| Bảng nguồn | Số bản ghi |
|---|---:|
| `events` | 360 |
| `ticket_types` | 1.080 |
| `orders` | 357.000 |
| `order_items` | 399.696 |
| `payments` | 420.792 |

Số dòng chi tiết lớn hơn số đơn phản ánh việc một đơn có thể chứa nhiều dòng vé. Số lần thử thanh toán lớn hơn số đơn phù hợp với cấu trúc cho phép nhiều lần thử.

Những số liệu này thuộc trạng thái ngày 04/10/2026, không được trình bày như số lượng hiện tại sau các lần bổ sung dữ liệu. Chúng được giữ riêng với nhật ký thực thi ngày 13/10/2026 để tránh sử dụng hai trạng thái khác nhau trong cùng phép đối chiếu.

### 4.8.3. Đối chiếu nguồn và dữ liệu phân tích

Trong lần khảo sát ngày 04/10/2026, bảng đơn hàng tại Bronze và Silver đều có 357.000 bản ghi. Bảng `fact_ticket_sales` có 399.696 bản ghi, tương ứng với số dòng chi tiết nguồn được ghi nhận.

Sự tương ứng phù hợp với mức chi tiết của thiết kế tại thời điểm đó. Tuy nhiên, đối chiếu số lượng mới xác nhận một phần kết quả. Để đánh giá toàn bộ nội dung, cần so sánh thêm tập khóa, thuộc tính và các quy tắc lọc.

Khi Silver có bản ghi xóa mềm, việc đối chiếu với Bronze phải xét các bản ghi đang có hiệu lực. Đối với fact, tập khóa kỳ vọng phụ thuộc vào dòng chi tiết và đơn hàng liên quan còn hiệu lực, không chỉ vào số lượng vật lý của bảng nguồn.

### 4.8.4. Kết quả chỉ tiêu bán vé

Tổng hợp tại Gold trong hồ sơ ngày 04/10/2026 ghi nhận:

| Trạng thái đơn | Số đơn | Số vé đã bán | Giá trị bán vé (VND) |
|---|---:|---:|---:|
| `PAID` | 293.274 | 636.959 | 188.306.020.500 |
| `EXPIRED` | 47.059 | 0 | 0 |
| `CANCELLED` | 16.657 | 0 | 0 |
| `PENDING` | 10 | 0 | 0 |

Các trạng thái ngoài `PAID` không đóng góp vào số vé đã bán và giá trị bán vé, phù hợp với quy tắc tính toán của mô hình. Tỷ lệ đơn đã thanh toán trong tập quan sát xấp xỉ 82,15%.

Các chỉ tiêu phản ánh bộ dữ liệu tổng hợp và trạng thái được ghi nhận, không được sử dụng để kết luận về thị trường hoặc hiệu quả thực tế của một doanh nghiệp.

## 4.9. Đánh giá và thảo luận

### 4.9.1. Mức độ đáp ứng yêu cầu

Về triển khai, project đã có các thành phần đồng bộ, mô hình biến đổi, cấu trúc phân tích và cơ chế điều phối theo từng tầng. Mã nguồn thể hiện các quy tắc chuẩn hóa, khử trùng, hợp nhất và xử lý trạng thái bản ghi.

Về thực thi, sản phẩm dbt ghi nhận các mô hình Silver và Gold hoàn thành thành công. Hồ sơ đối chiếu cung cấp bằng chứng về quy mô nguồn và sự tương ứng của một số bảng đích. Báo cáo Power BI thể hiện khả năng khai thác các đầu ra theo những câu hỏi phân tích đã xác định.

Mức độ đáp ứng yêu cầu cần được xem xét theo từng loại bằng chứng. Mã nguồn xác nhận cơ chế đã được hiện thực; nhật ký xác nhận một lượt đã thực thi; truy vấn đối chiếu xác nhận kết quả trong phạm vi dữ liệu và điều kiện cụ thể. Các bằng chứng này bổ sung cho nhau nhưng không thay thế hoàn toàn.

### 4.9.2. Khả năng cập nhật và hiệu năng

Cơ chế tăng dần lựa chọn bản ghi theo khóa, dấu vân tay và trạng thái xóa. Thiết kế có khả năng xử lý thay đổi ở đơn hàng làm ảnh hưởng đến các dòng fact, đồng thời xét trường hợp bản ghi biến mất và xuất hiện trở lại.

Để xác nhận đầy đủ hành vi, cần các ca kiểm thử có trạng thái trước và sau đối với thêm mới, sửa đơn cũ, xóa, khôi phục và chạy lại cùng đầu vào. Những ca chưa có hồ sơ hoàn tất không được kết luận là đã đạt chỉ từ việc nhánh xử lý tồn tại trong mã nguồn.

Về hiệu năng, các thời gian ghi nhận cho thấy thời gian thực thi trong một số lượt vận hành, chưa hình thành một phép so sánh có kiểm soát giữa tạo lại toàn bộ và cập nhật tăng dần. Vì vậy, kết luận hiện tại tập trung vào cơ chế hạn chế ghi bản ghi không đổi; mức cải thiện thời gian cần được đo trên cùng dữ liệu và điều kiện.

### 4.9.3. Giới hạn về dữ liệu và tính nhất quán

Nhận diện bản ghi biến mất phụ thuộc vào độ đầy đủ của bản chụp. Nếu đầu vào bị thiếu do phạm vi đồng bộ hoặc trạng thái công việc, kết quả xóa mềm có thể không phản ánh đúng thay đổi nguồn.

Dataset quản lý tín hiệu hoàn thành, chưa tự xác nhận các bảng thuộc cùng một lô. Các mô hình Gold cũng được cập nhật riêng, nên người đọc dữ liệu trong lúc xử lý có thể gặp những bảng ở thời điểm cập nhật khác nhau.

Bronze sử dụng ghi đè và Silver lưu trạng thái hiện tại cùng dấu xóa mềm. Cấu trúc này chưa hỗ trợ đầy đủ lịch sử phiên bản. Tái lập một lượt xử lý cũ vì vậy cần giữ được dữ liệu đầu vào và phiên bản mã nguồn tương ứng.

Cuối cùng, dữ liệu tổng hợp có ưu điểm về khả năng kiểm soát nhưng chưa phản ánh đầy đủ những sai lệch của dữ liệu thực tế. Các kết quả triển khai là cơ sở đánh giá giải pháp trong phạm vi khóa luận; việc mở rộng sang môi trường doanh nghiệp cần kiểm chứng thêm về chất lượng dữ liệu, nhất quán theo lô và khả năng vận hành.

:::changed
## Tài liệu tham khảo cho nội dung bổ sung

[1] dbt Labs. Postgres configurations. https://docs.getdbt.com/reference/resource-configs/postgres-configs. Truy cập ngày 13/10/2026.

[2] PostgreSQL Global Development Group. Multicolumn Indexes, PostgreSQL 17. https://www.postgresql.org/docs/17/indexes-multicolumn.html. Truy cập ngày 13/10/2026.

[3] PostgreSQL Global Development Group. Table Partitioning, PostgreSQL 17. https://www.postgresql.org/docs/17/ddl-partitioning.html. Truy cập ngày 13/10/2026.
:::
