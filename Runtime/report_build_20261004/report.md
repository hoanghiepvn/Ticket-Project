# Chương 1 Tổng quan đề tài
## Bối cảnh và vấn đề nghiên cứu
Hệ thống bán vé sự kiện phải quản lý danh mục chương trình, các hạng vé, đơn đặt và nhiều lần thử thanh toán. Cơ sở dữ liệu giao dịch tổ chức các thông tin này thành những bảng liên quan để hạn chế dư thừa và bảo vệ toàn vẹn. Cách tổ chức đó phù hợp với việc ghi nhận một đơn mới hoặc cập nhật kết quả thanh toán. Tuy nhiên, người quản lý thường cần tổng hợp theo ngày, địa điểm, sự kiện và kênh bán. Những câu hỏi phân tích lặp lại đòi hỏi một lớp dữ liệu có quy tắc tính thống nhất.

Một khó khăn đặc trưng là sự khác nhau về mức chi tiết giữa đơn hàng, chi tiết đơn và lần thử thanh toán. Một đơn có thể chứa hai hạng vé và ba lần thanh toán. Nếu nối cả ba bảng rồi cộng tiền chi tiết, cùng một dòng vé có thể xuất hiện ba lần. Sai lệch vẫn có thể tạo ra biểu đồ hợp lệ về mặt hình thức. Vì vậy, xác định grain và kiểm soát quan hệ là yêu cầu trung tâm của hệ thống phân tích.

Đề tài xây dựng một kho phân tích tách khỏi SQL Server nguồn. Airbyte sao chép dữ liệu vào PostgreSQL, dbt-postgres biến đổi dữ liệu, Airflow điều phối công việc và Power BI trình bày chỉ tiêu. Bản triển khai ưu tiên khả năng giải thích và vận hành trên máy cá nhân. Các quyết định thiết kế được đánh giá trong phạm vi một bộ dữ liệu mô phỏng, không suy rộng thành hiệu quả kinh doanh thực tế.

## Mục tiêu của đề tài
Mục tiêu tổng quát là thiết kế và triển khai quy trình ELT xử lý dữ liệu bán vé sự kiện theo ba tầng Bronze, Silver và Gold, kết hợp mô hình dữ liệu chiều để hỗ trợ phân tích. ELT trong đề tài có nghĩa dữ liệu được trích xuất và nạp vào kho trước khi các phép biến đổi nghiệp vụ diễn ra ở hệ thống đích.

Mục tiêu cụ thể gồm xây dựng dữ liệu nguồn có quan hệ nhất quán; cấu hình đồng bộ bằng Airbyte; chuẩn hóa và khử trùng ở Silver; xây dựng fact, dimension và mart ở Gold; điều phối các DAG theo trạng thái hoàn tất của dữ liệu; và cung cấp báo cáo tương tác cho người dùng nghiệp vụ. Khả năng đọc được mã SQL và truy ngược một chỉ tiêu đến nguồn cũng là tiêu chí thiết kế.

Đề tài trả lời các câu hỏi kỹ thuật: làm thế nào kết hợp Airbyte Full Refresh Overwrite với dbt incremental; làm thế nào xử lý một đơn cũ đổi trạng thái mà không phụ thuộc hoàn toàn vào watermark; tại sao phải chờ Airbyte hoàn thành; và làm thế nào tránh nhân đôi doanh số khi nguồn có nhiều payment attempts. Các câu hỏi này định hướng phần triển khai và đánh giá.

## Phạm vi và sản phẩm
Phạm vi dữ liệu gồm năm bảng events, ticket_types, orders, order_items và payments. Hệ thống không thu thập khách hàng, thông tin cá nhân, số thẻ hay thông tin thanh toán nhạy cảm. Đối soát giao dịch với đối tác và gửi email chênh lệch không thuộc phạm vi cuối cùng. Bảng payments vẫn được giữ như dữ liệu nghiệp vụ nguồn và dữ liệu chuẩn hóa, nhưng không nối trực tiếp vào fact bán vé.

Sản phẩm gồm bộ sinh dữ liệu Python, DDL SQL Server, cấu hình Airbyte local, Docker Compose, các DAG Airflow, dự án dbt-postgres và file Dashboards.pbix. Báo cáo trình bày kiến trúc, hợp đồng dữ liệu, logic xử lý, kết quả đọc hiện tại và các hạn chế. Các phụ lục cung cấp từ điển dữ liệu và mã tiêu biểu để tái lập.

Đây là môi trường nghiên cứu local. Hệ thống chưa có cam kết SLA, cơ chế xuất bản nguyên tử toàn bộ Gold hoặc kiểm soát batch chung giữa mọi stream. Việc có các bảng và DAG chạy thành công không đồng nghĩa mọi tình huống lỗi đã được nghiệm thu. Phần đánh giá phân biệt kết quả quan sát với các kịch bản cần thực hiện thêm.

## Phương pháp và đóng góp
Phương pháp triển khai bắt đầu từ mô hình nghiệp vụ, xác định khóa và grain, sau đó thiết kế ánh xạ dữ liệu qua từng tầng. Bộ dữ liệu mô phỏng cho phép thay đổi quy mô và tạo các trạng thái đơn có kiểm soát. Các phép biến đổi được thể hiện bằng SQL để có thể kiểm tra từng bước, thay vì che toàn bộ logic trong mã điều phối.

Đóng góp chính là một hệ thống tích hợp có phân công rõ trách nhiệm và quy tắc chỉ tiêu. Airbyte đảm nhiệm đồng bộ, Airflow kiểm soát lịch và phụ thuộc, dbt quản lý phép biến đổi, PostgreSQL thực thi SQL, Power BI phục vụ phân tích. Đề tài không đề xuất thuật toán phân tán mới. Giá trị kỹ thuật nằm ở thiết kế luồng, xử lý thay đổi dữ liệu và tránh các lỗi mô hình hóa thường gặp.

# Chương 2 Cơ sở lý thuyết và lựa chọn công nghệ
## ELT và phân tầng Medallion
Trong ETL, phần biến đổi thường diễn ra trước khi dữ liệu được nạp vào đích phân tích. Với ELT, dữ liệu được nạp trước rồi biến đổi tại đích. Lựa chọn ELT giúp lưu lại dữ liệu gần nguồn để đối chiếu, đồng thời tận dụng năng lực truy vấn của PostgreSQL. Việc chọn ELT không loại bỏ nhu cầu kiểm tra chất lượng và quản lý trạng thái đồng bộ.

Bronze chứa các bảng do Airbyte nạp. Silver giữ dữ liệu có kiểu nhất quán, quy tắc khử trùng và trạng thái xóa mềm. Gold tổ chức dữ liệu theo câu hỏi phân tích. Ba tầng là ranh giới trách nhiệm logic. Trong đề tài, chúng được triển khai bằng schema PostgreSQL, không phải các database độc lập và không sử dụng định dạng bảng Lakehouse.

Full Refresh Overwrite làm Bronze phản ánh trạng thái hiện tại sau mỗi lượt đồng bộ thành công. Do dữ liệu cũ bị thay thế, Bronze không phải nhật ký lịch sử bất biến. Việc lưu lịch sử các phiên bản, time travel hoặc phát lại từng giao dịch cần một cơ chế khác. Đề tài không sử dụng Iceberg, MinIO hay Lakekeeper và không tuyên bố có các khả năng đó.

## Mô hình dữ liệu chiều
Mô hình sao tách các giá trị đo lường trong fact khỏi thuộc tính phân loại trong dimension. Trong bài toán này, fact lưu số lượng và giá trị ở mức một dòng hạng vé trong đơn. Các dimension mô tả ngày, sự kiện, hạng vé, kênh bán và trạng thái. Grain phải được xác định trước các chỉ tiêu để tránh trộn mức chi tiết [3].

Một measure cộng được theo sự kiện không nhất thiết cộng được theo mọi chiều. Tổng tiền của dòng vé có thể cộng, nhưng số đơn cần đếm phân biệt vì một đơn có nhiều dòng. Tỷ lệ thanh toán phải tính lại từ tử số và mẫu số trong ngữ cảnh lọc, không lấy trung bình đơn giản của các tỷ lệ theo ngày. Đây là các quyết định ngữ nghĩa, không thể giao hoàn toàn cho tùy chọn Sum mặc định của Power BI.

Mô hình hiện tại lưu thuộc tính hiện hành của sự kiện và hạng vé. Không có cặp hiệu lực thời gian để triển khai Slowly Changing Dimension Type 2. Do đó, thay đổi tên sự kiện hoặc quota có thể ảnh hưởng cách hiển thị lịch sử. Báo cáo theo thời điểm quá khứ tuyệt đối cần mô hình lịch sử riêng.

## Airbyte và chế độ đồng bộ
Airbyte kết nối nguồn với đích thông qua connection, trong đó xác định các stream và chế độ đồng bộ. Connection ID định danh cấu hình đồng bộ, còn Job ID định danh một lần thực thi. Workspace ID chỉ định không gian làm việc. Nhầm ba loại định danh dẫn đến việc gọi API sai hoặc theo dõi nhầm lượt chạy.

Đề tài sử dụng Full Refresh Overwrite để ưu tiên tính đơn giản khi xác lập snapshot hiện tại. Mọi bảng nguồn được đọc lại theo cấu hình connection. Cách này có chi phí đọc lặp lại, nhưng giúp phát hiện bản ghi không còn tồn tại khi và chỉ khi snapshot đầu vào đầy đủ. Việc đổi sang Incremental Append mà giữ nguyên logic phát hiện xóa sẽ tạo kết quả sai.

Airbyte chạy local bằng abctl trong môi trường kind. Vòng đời Airbyte tách khỏi Docker Compose của kho dữ liệu và Airflow. Vì vậy, Compose hoạt động không bảo đảm Airbyte đã sẵn sàng. Cổng 8000 phục vụ giao diện/API local, trong khi từ container Airflow cần sử dụng địa chỉ host phù hợp thay cho localhost.

## dbt và chiến lược incremental
Model dbt là truy vấn SQL cùng cấu hình materialization. source khai báo bảng đầu vào do công cụ khác quản lý. ref biểu diễn quan hệ giữa các model và hỗ trợ dbt xây dựng đồ thị phụ thuộc. Adapter dbt-postgres gửi SQL đến PostgreSQL để thực thi. Bản triển khai sử dụng dbt-core 1.9.8 và dbt-postgres 1.9.0 theo cấu hình môi trường.

Incremental không có nghĩa dữ liệu nguồn bắt buộc phải được nạp incremental. Một snapshot đầy đủ vẫn có thể được so sánh với đích để chỉ ghi khóa mới hoặc dòng thay đổi. unique_key xác định cách ghép bản ghi trong chiến lược merge. Điều kiện is_incremental() phân biệt lần tạo đầu hoặc full refresh với các lần cập nhật tiếp theo [2].

Trong đề tài, hash các cột nghiệp vụ xác định thay đổi. Dòng không đổi không cần ghi lại, nhưng truy vấn vẫn đọc snapshot ứng viên và so sánh khóa. Vì vậy, thiết kế giảm số thao tác ghi trong trường hợp ít thay đổi, chưa đủ cơ sở kết luận tổng thời gian chạy giảm bao nhiêu. Benchmark phải đo trên cùng tập dữ liệu và điều kiện tài nguyên.

## Airflow và lịch theo Dataset
Airflow dùng DAG để mô tả công việc và phụ thuộc. Với Dataset scheduling, một task thành công có thể công bố sự kiện cập nhật cho Dataset ở outlets. DAG khác dùng cùng định danh trong schedule để chờ dữ liệu. Airflow chỉ phát sự kiện khi task thành công, còn task thất bại hoặc bị bỏ qua không công bố cập nhật [1].

Danh sách nhiều Dataset có ý nghĩa tất cả đã cập nhật ít nhất một lần kể từ lượt chạy trước của DAG nhận. Cơ chế này không tự kiểm tra cùng ngày nghiệp vụ hoặc cùng batch. Một sự kiện cập nhật cũ và một cập nhật mới vẫn có thể thỏa điều kiện nếu chưa được tiêu thụ. Thiết kế sản xuất cần bổ sung batch ID hoặc điều kiện xác nhận phiên bản khi yêu cầu nhất quán cao.

Dataset là tín hiệu điều phối, không chứa toàn bộ bảng và không tự kiểm tra số dòng. URI của Dataset trong đề tài là tên dễ đọc theo nguồn và đích, ví dụ transform_bronze_to_silver_ticket_events. Không đưa mật khẩu hoặc client secret vào tên Dataset vì các định danh này nằm trong metadata của Airflow.

## Lý do chọn PostgreSQL và Docker
PostgreSQL cung cấp SQL, schema, transaction và khả năng thực thi MERGE phù hợp với mô hình hiện tại. Chọn một hệ quản trị quan hệ làm kho giúp giảm số thành phần vận hành so với phương án Spark và object storage. Quy mô hiện có phục vụ việc kiểm chứng luồng trên máy cá nhân, chưa phải bằng chứng rằng mọi quy mô lớn đều phù hợp với kiến trúc này.

Docker Compose mô tả dịch vụ kho, metadata Airflow, scheduler, webserver và bước khởi tạo. dbt nằm trong môi trường Python riêng trong image ứng dụng. Tách môi trường giúp hạn chế xung đột thư viện với Airflow. Volume giữ dữ liệu và log qua lần khởi động lại, nhưng không thay thế sao lưu.

# Chương 3 Dữ liệu nguồn và yêu cầu nghiệp vụ
## Nguồn gốc và khả năng tái lập
Dataset do chương trình Python trong Source/SqlServer tạo tổng hợp. SQL Server là hệ thống lưu trữ đầu vào, không phải nguồn gốc thu thập thực tế của dữ liệu. Các tên chương trình, địa điểm, số lượng và giao dịch phục vụ mô phỏng. Không sử dụng dữ liệu khách hàng hoặc giao dịch nội bộ của Ticketbox hay doanh nghiệp để suy luận kết quả.

Bộ sinh sử dụng seed nhằm tái lập lựa chọn ngẫu nhiên. Các sự kiện phân bố theo nhóm chương trình, địa điểm và hạng vé. Các đơn có trạng thái PAID, EXPIRED, CANCELLED hoặc PENDING, có thể có nhiều lần thử thanh toán. Bộ sinh lịch sử cho phép thêm lô theo năm mà không thay thế dữ liệu đã có.

Giá, tỷ trọng kênh và xác suất thanh toán theo năm được đặt bằng quy tắc trong mã. Vì vậy, xu hướng tăng số đơn hoặc doanh số có thể xuất phát trực tiếp từ tham số sinh và số lô đã nạp. Không diễn giải các đồ thị này thành bằng chứng tăng trưởng thị trường hoặc ảnh hưởng của dịch bệnh. Dữ liệu 2020 trong đề tài cũng là mô phỏng, không phản ánh lịch sự kiện thực tế của năm đó.

## Quy mô tại thời điểm khảo sát
Truy vấn đọc ngày 04 tháng 10 năm 2026 trên TicketingDB ghi nhận 360 sự kiện, 1.080 hạng vé, 357.000 đơn, 399.696 chi tiết đơn và 420.792 lần thử thanh toán. Số lần thử lớn hơn số đơn phù hợp cấu trúc một đơn có thể thanh toán lại. Các con số là trạng thái tại thời điểm đọc, có thể thay đổi sau các lô nạp mới.

Phân bố theo năm đặt đơn lần lượt là 42.000 đơn năm 2020, 20.000 năm 2021, 30.000 năm 2022, 40.000 năm 2023, 55.000 năm 2024, 70.867 năm 2025 và 99.133 năm 2026. Số năm 2025 bao gồm các đơn của bộ ban đầu có thời điểm đặt trước năm diễn ra sự kiện. Không đồng nhất năm của sự kiện với năm đặt đơn.

Mốc AS_OF của bộ sinh ban đầu là ngày 01 tháng 09 năm 2026. Do đó, năm 2026 chưa đủ một chu kỳ 12 tháng. So sánh toàn năm 2025 với phần năm 2026 có thể dẫn đến cách hiểu sai. Báo cáo cần chọn các khoảng thời gian tương ứng hoặc ghi rõ độ bao phủ.

## Nghiệp vụ sự kiện và hạng vé
Mỗi sự kiện có một mã, tên, nhóm chương trình, đơn vị tổ chức, địa điểm, sức chứa và cửa sổ mở bán. Mỗi hạng vé thuộc đúng một sự kiện. Giá niêm yết và quota của hạng vé là thuộc tính danh mục. Giá giao dịch tại lúc đặt được lưu ở order_items để không phải tính lại từ danh mục sau này.

Khóa duy nhất theo event_id và ticket_type_code ngăn trùng mã hạng trong cùng sự kiện. Quota dương và sức chứa dương là ràng buộc ở nguồn. Quan hệ giữa tổng quota và capacity là quy tắc cần đối chiếu ở cấp tập dòng, không thể suy ra chỉ từ việc từng cột đều dương.

Một hệ thống thực tế có thể có nhiều suất diễn, nhiều đợt mở bán và ghế định danh. Đề tài đơn giản hóa một sự kiện tương ứng một suất trong bộ dữ liệu. Vé chưa được mô hình hóa thành từng mã QR để kiểm soát check-in. Số vé trong báo cáo được tính từ quantity, không phải số bản ghi vé điện tử riêng.

## Nghiệp vụ đơn hàng và thanh toán
Đơn hàng lưu thông tin chung như thời điểm đặt, kênh, trạng thái và tổng tiền. Một đơn chỉ thuộc một sự kiện nhưng có thể chứa nhiều hạng vé. Mỗi dòng chi tiết có quantity, unit_price, discount_amount và line_amount. Khóa ngoại ghép giữa đơn, sự kiện và hạng vé giới hạn việc ghép nhầm hạng của sự kiện khác.

payments lưu từng lần thử, phân biệt mã giao dịch nội bộ với mã đối tác. Các trạng thái gồm SUCCESS, FAILED và PENDING. Những thời điểm hoàn tất hoặc thanh toán thành công có thể NULL tùy trạng thái. Chỉ mục duy nhất có điều kiện ở nguồn giới hạn tối đa một payment SUCCESS cho mỗi đơn trong nghiệp vụ mô phỏng.

Trạng thái đơn PAID là điều kiện ghi nhận chỉ tiêu bán vé hiện tại. Bảng fact không cộng payment_amount để đo doanh số, vì nhiều lần thử có thể mang cùng số tiền. Thanh toán từng phần, hoàn tiền, phí dịch vụ và quyết toán chưa được mô hình hóa. Nếu bổ sung các nghiệp vụ đó, cần thiết kế thêm fact thanh toán hoặc hoàn tiền với grain tương ứng.

## Quy tắc tiền tệ và thời gian
Tiền sử dụng VND nguyên đồng, lưu numeric hoặc decimal có độ chính xác 18 chữ số và phần thập phân bằng 0. Giá trị gross của dòng bằng quantity nhân unit_price. Giá trị net bằng gross trừ discount_amount và tương ứng line_amount. Tổng tiền đơn là tổng các dòng hợp lệ trong phạm vi nghiệp vụ nguồn.

Timestamp nghiệp vụ không kèm timezone được hiểu theo Asia/Ho_Chi_Minh. Timestamp vận hành như _loaded_at có thể dùng timestamptz ở PostgreSQL. Hai loại thời gian trả lời hai câu hỏi khác nhau: đơn phát sinh lúc nào và pipeline ghi dòng này lúc nào. Power BI dùng ngày đặt đơn từ dim_date cho các báo cáo hiện tại.

Nếu hệ thống nguồn chuyển sang UTC, cần chuyển đổi rõ ràng trước khi tạo date_key. Việc bỏ timezone mà không đổi múi giờ có thể chuyển một giao dịch gần nửa đêm sang sai ngày. Cấu hình UTC+7 của giao diện Airflow chỉ thay cách hiển thị và lập lịch, không tự sửa các timestamp nghiệp vụ đã lưu.

## Yêu cầu chức năng và phi chức năng
Các chức năng chính là nạp năm bảng, biến đổi từng bảng theo tầng, chạy lại khi cần và cung cấp chỉ tiêu theo chiều phân tích. Người vận hành phải nhận biết Airbyte đã kết thúc, model dbt nào đang chạy và lỗi nằm ở bước nào. Đường dẫn SQL hiển thị trong DAG hỗ trợ truy vết khi sửa lỗi.

Yêu cầu phi chức năng tập trung vào khả năng bảo trì, tái lập và bảo mật tối thiểu. Cấu hình bí mật đặt ngoài tài liệu báo cáo. Các khóa chính phải ổn định giữa những lần cập nhật. Chạy lại trên cùng snapshot cần tạo cùng dữ liệu nghiệp vụ, dù metadata thời điểm tải có thể khác ở một số trường hợp tái tạo bảng.

Đề tài chưa đặt ngưỡng thời gian đáp ứng hoặc thông lượng đã nghiệm thu. Các chỉ số đó cần được đo khi xác định phần cứng, chế độ chạy và quy mô chuẩn. Không lấy tổng thời gian của một lần chạy đơn lẻ làm SLA hoặc kết luận hiệu năng cho môi trường sản xuất.

# Chương 4 Thiết kế và triển khai hệ thống
## Kiến trúc thành phần
Luồng dữ liệu chuẩn bắt đầu tại TicketingDB trên SQL Server. Airbyte ghi vào schema bronze trong ticketing_analytics của PostgreSQL. Các model Silver sử dụng source('bronze', ...) để đọc các bảng đó. Gold dùng ref để phụ thuộc các model đã chuẩn hóa. Power BI kết nối các bảng Gold phục vụ mô hình sao và tổng hợp.

Luồng điều phối đi song song với luồng dữ liệu. Airflow không trung chuyển từng bản ghi bán vé qua XCom. Nó gửi yêu cầu đồng bộ, nhận Job ID, chờ trạng thái Airbyte và chạy câu lệnh dbt. Dataset truyền tín hiệu đã hoàn tất, còn nội dung dữ liệu vẫn nằm trong PostgreSQL.

Không có bước sao chép sang work_bronze hoặc xây dựng gold_build trong đường chạy hiện tại. Cách triển khai giảm tầng trung gian nhưng làm tăng yêu cầu vận hành để tránh đọc khi Bronze bị ghi đè. Từng model cập nhật đích riêng, không có transaction chung bao phủ toàn bộ Gold.

## Cấu trúc thư mục
Source/SqlServer chứa DDL và bộ sinh dữ liệu. Airbyte giữ tài liệu và công cụ local. Airflow tách dags theo bronze, silver, gold, còn plugins chứa các thao tác dùng chung. Dbt/Dbt-Postgres chứa model, macro, YAML và cấu hình adapter. Docker cùng compose.yaml mô tả môi trường thực thi.

PowerBI chứa Dashboards.pbix và tài liệu chỉ tiêu. Reports lưu tài liệu đồ án. Runtime chứa log và sản phẩm thực thi, không được coi là nguồn cấu hình chính. Các file target hoặc compiled giúp xem SQL đã biên dịch nhưng không nên sửa để thay đổi logic model. Thay đổi cần thực hiện ở SQL gốc trong models.

Phân chia này làm rõ ranh giới giữa mã nguồn, cấu hình, sản phẩm và dữ liệu vận hành. Khi chuyển máy, cần sao lưu cả mã nguồn và các volume hoặc bản dump phù hợp. Chỉ sao chép thư mục project không tự mang theo toàn bộ PostgreSQL và metadata Airbyte đang nằm trong Docker.

## Docker và đường kết nối
Compose khai báo warehouse-db và airflow-db là hai dịch vụ PostgreSQL khác mục đích. warehouse-db chứa dữ liệu phân tích, còn airflow-db chứa trạng thái DAG, task và lịch. airflow-init là công việc khởi tạo, kết thúc thành công sau migration không phải lỗi dịch vụ. Webserver và scheduler mới là những thành phần cần duy trì hoạt động.

Trên Windows, Power BI hoặc DBeaver truy cập kho qua localhost:5433. Bên trong Compose, ứng dụng sử dụng warehouse-db:5432. Container Airflow gọi Airbyte qua host.docker.internal:8000 theo cấu hình local. localhost trong container chỉ chính container đó, không chỉ máy Windows hoặc container khác.

Các cổng public của kho và Airflow trong Compose gắn với loopback. Bí mật nên được cấp qua biến môi trường hoặc kho bí mật thay vì ghi trong slide, Git hoặc ảnh minh họa. Những giá trị mặc định phục vụ local cần đổi trước khi triển khai ra mạng khác. Báo cáo không sao chép mật khẩu vận hành.

## Thiết kế DAG Bronze
Mỗi DAG Bronze quản lý một nghiệp vụ đồng bộ. Connection ID lấy từ file cấu hình dùng chung, còn dag_id, lịch cron và Dataset đầu ra nằm rõ trong file DAG. Ví dụ bronze_ticket_events đặt lịch 01 giờ theo Asia/Ho_Chi_Minh trong mã tại thời điểm khảo sát. catchup=False tránh tự chạy toàn bộ kỳ lịch đã bỏ qua.

Task trigger_airbyte gọi thao tác tạo sync và trả về Job ID. Task wait_for_complete theo dõi chính lượt đó ở chế độ reschedule, nhả worker giữa các lần kiểm tra. Chỉ sensor thành công mới phát Dataset transform_source_to_bronze_ticket_events. Nếu chỉ đặt outlet ở task tạo job, Silver có thể đọc trước khi Airbyte hoàn tất.

Thao tác POST tạo job không tự retry trong DAG mẫu để hạn chế tạo sync trùng khi mất phản hồi. Người vận hành cần kiểm tra Airbyte khi không rõ yêu cầu đã được tiếp nhận hay chưa. Retry truy vấn trạng thái ít rủi ro hơn retry thao tác tạo job. DAG all và các DAG riêng không nên kích hoạt chồng nhau cho cùng dữ liệu.

## Thiết kế DAG Silver và Gold
Silver có một DAG cho mỗi bảng và một DAG all phục vụ thao tác thủ công. Mỗi DAG theo bảng chờ Dataset Bronze tương ứng và chạy model SQL được chọn bằng đường dẫn. Ví dụ silver_ticket_events chạy dbt run --select path:models/silver/silver_events.sql. doc_md cũng ghi đường dẫn để người vận hành mở đúng file.

Năm DAG dimension Gold cùng chờ đủ năm Dataset Silver. Cách này tạo rào phụ thuộc rộng hơn đồ thị SQL tối thiểu, giúp các dimensions bắt đầu sau một đợt cập nhật Silver tương đối đầy đủ. Fact chờ đủ năm dimensions, còn agg_daily_sales chờ fact. Các DAG all là công cụ thủ công và không thay thế việc hiểu các sự kiện đã được phát.

DbtBashOperator dùng cấu hình chung cho timeout, full_refresh và đường dẫn artifacts. full_refresh mặc định false. Cờ bronze_mode không còn là tham số nhập thường ngày trên UI, vì luồng chỉ hỗ trợ snapshot đầy đủ. Việc giữ giả định này cố định hạn chế người dùng vô tình bật phát hiện xóa trên dữ liệu append.

## Hợp đồng model dbt
sources.yml mô tả năm bảng Bronze. schema.yml của Silver và Gold khai báo tên model, cột, kiểu và các kiểm tra chất lượng. contract enforced yêu cầu cấu trúc kết quả phù hợp khai báo. on_schema_change fail giúp thay đổi cột không âm thầm đi vào bảng incremental mà chưa được xem xét.

Hợp đồng cấu trúc không thay thế kiểm thử dữ liệu. Một cột đúng kiểu bigint vẫn có thể chứa khóa ngoại không tồn tại hoặc giá trị sai nghiệp vụ. Tương tự, dbt run chỉ thực thi model, không tự chạy toàn bộ test khai báo. Các DAG hiện tại dùng dbt run nên cần phân biệt kiểm tra khai báo với kiểm tra đã thực thi.

Khi thay đổi schema của bảng incremental, cần kế hoạch migration hoặc full refresh có chủ đích. Full refresh tạo lại bảng theo toàn bộ nguồn hiện tại, có chi phí và có thể làm mất metadata cũ. Không bật cờ này hàng ngày chỉ vì thấy lỗi, trước hết phải đọc log và xác định thay đổi nào gây không tương thích.

## Quy trình chuẩn hóa Silver
Model Silver gồm các bước source_data, hashed, ranked, deduplicated và final. source_data chọn rõ cột, ép kiểu, trim chuỗi và chuyển chuỗi rỗng thành NULL. Các mã trạng thái và kênh dùng chữ hoa nhất quán. Metadata Airbyte hỗ trợ thứ tự lựa chọn, nhưng không được trộn vào chỉ tiêu kinh doanh.

hashed tính _record_hash bằng md5 trên jsonb_build_array của danh sách cột nghiệp vụ. Cách biểu diễn mảng giữ ranh giới giữa các giá trị và NULL rõ hơn nối chuỗi đơn giản không có phân tách. Hash là công cụ phát hiện thay đổi trong bộ dữ liệu này, không phải chữ ký bảo mật hoặc bằng chứng chống sửa dữ liệu.

ranked dùng ROW_NUMBER theo khóa chính. Thứ tự ưu tiên updated_at giảm dần, thời điểm trích xuất Airbyte, raw ID và hash. Các trường phụ giúp lựa chọn xác định khi timestamp trùng, nhưng raw ID không mang nghĩa thứ tự nghiệp vụ. Trường hợp hai phiên bản mâu thuẫn có cùng updated_at vẫn cần điều tra nguồn thay vì coi dedup là bằng chứng phiên bản đúng.

## Merge và xử lý bản ghi biến mất
Macro incremental_changes so sánh tập ứng viên với bảng đích theo khóa. Khóa chưa có được đưa vào tập ghi. Khóa có hash khác hoặc đang xóa mềm cũng được đưa vào. Các dòng không đổi bị loại khỏi tập ghi incremental. Không sử dụng điều kiện lớn hơn MAX(updated_at), vì một cập nhật muộn có thể có timestamp nhỏ hơn mốc lớn nhất toàn bảng.

Với snapshot đầy đủ, khóa đang hoạt động ở đích nhưng không còn trong ứng viên được đánh dấu _is_deleted=true. Các giá trị nghiệp vụ cũ vẫn được giữ trong Silver. Nếu khóa xuất hiện lại, dòng trở về hoạt động. Điều kiện quan trọng là Airbyte phải đọc thành công toàn bộ phạm vi bảng, không chỉ một phần hoặc một khoảng ngày.

Ở fact Gold, post-hook xóa các dòng đã đánh dấu xóa để tập công bố không giữ các dòng không còn hợp lệ. Silver xóa mềm và Gold loại khỏi báo cáo là hai trách nhiệm khác nhau. Không được hiểu đây là lưu trữ lịch sử phiên bản đầy đủ, vì model chỉ duy trì trạng thái hiện tại cùng dấu xóa của khóa.

## Thiết kế fact và các dimension
fact_ticket_sales lấy order_items hoạt động, ghép với orders hoạt động theo order_id và tra dim_channel, dim_status. date_key lấy từ ordered_at. quantity, gross_amount, discount_amount và net_amount mô tả dòng đặt vé. sold_quantity và sales_amount chỉ khác 0 khi order_status bằng PAID.

Một đơn cũ đổi từ PENDING sang PAID cần làm thay đổi fact dù chi tiết đơn không đổi. Vì vậy, fact đánh giá lại toàn bộ ứng viên đang hoạt động, sau đó hash phát hiện các dòng cần ghi. Logic này xử lý phụ thuộc ở cấp dòng mà một watermark chỉ trên order_items có thể bỏ sót.

dim_event và dim_ticket_type chứa thuộc tính hiện hành. dim_channel định nghĩa WEB và APP, dim_status định nghĩa PAID, EXPIRED, CANCELLED và PENDING. dim_date tạo dải ngày từ ngày nhỏ nhất đến lớn nhất của các đơn hoạt động. Dải này chưa phải lịch kế hoạch có sẵn nhiều năm tương lai.

## Mart tổng hợp và hiệu lực công bố
agg_daily_sales nhóm theo date_key, event_id và channel_key. Nó tổng hợp sales_amount, sold_quantity và các số đếm đơn. Grain của mart không còn chứa ticket_type_id hoặc status_key. Do đó, không dùng mart để vẽ phân tích theo hạng vé khi không có chiều đó trong dữ liệu tổng hợp.

Năm dimensions và mart materialize dạng table, trong khi năm Silver và fact dùng incremental merge. Thiết kế kết hợp này cần được mô tả đúng, không gọi toàn bộ project là incremental hoàn toàn. Các bảng nhỏ hoặc tổng hợp tạo lại dễ kiểm soát hơn, còn fact lớn hưởng lợi từ tránh ghi các dòng không đổi.

Gold được cập nhật từng model. Một refresh Power BI gồm nhiều truy vấn có thể đọc các thời điểm khác nhau nếu trùng lúc pipeline ghi. Quy ước vận hành là đợi mart thành công và tránh lượt ghi mới trong thời gian refresh. Một lớp công bố snapshot chung hoặc batch version là hướng mở rộng để giảm phụ thuộc quy ước này.

# Chương 5 Xây dựng báo cáo Power BI
## Mô hình ngữ nghĩa
File PowerBI/Dashboards.pbix có bốn trang tại thời điểm khảo sát. Các bảng dimension liên kết một chiều từ phía 1 sang fact phía nhiều. ticket_type_id là khóa phân loại, không phải giá trị cần cộng. Biểu tượng tổng trên cột số không tự làm sai quan hệ, nhưng nên đặt các khóa ở chế độ không tổng hợp để tránh dùng nhầm trong biểu đồ.

Mối quan hệ trực tiếp giữa dim_event và dim_ticket_type có thể tạo thêm đường lọc khi cả hai đã nối fact. Mô hình báo cáo nên giữ quan hệ dimension tới fact rõ ràng và tránh đường lọc mơ hồ. Khi cần tính quota của hạng theo sự kiện, có thể truyền tập event_id bằng measure phù hợp thay vì bật bidirectional đại trà.

agg_daily_sales là lựa chọn tổng hợp riêng. Nếu đã dùng fact cho các measure trên cùng visual, không cộng thêm doanh số từ mart. Hai bảng chứa cùng hoạt động ở các mức tổng hợp khác nhau. Những cột kỹ thuật _record_hash, _loaded_at và _is_deleted nên ẩn khỏi danh sách dùng cho người đọc thông thường.

## Định nghĩa các chỉ tiêu chính
Doanh thu vé trong giao diện biểu diễn tổng sales_amount. Thuật ngữ trong phân tích được hiểu chính xác là giá trị vé của các đơn đang PAID. Chỉ tiêu không trừ hoàn tiền, phí đối tác hoặc chi phí tổ chức vì các dữ liệu đó chưa có. Không sử dụng nó để kết luận lợi nhuận hoặc tiền đã được quyết toán.

Số vé đã bán bằng tổng sold_quantity. Tổng số đơn dùng DISTINCTCOUNT order_id. Số đơn thanh toán thêm điều kiện trạng thái PAID. Tỷ lệ thanh toán lấy số đơn PAID chia tổng số đơn trong cùng ngữ cảnh. Giá trị trung bình mỗi đơn thanh toán bằng doanh thu vé chia số đơn thanh toán, sử dụng DIVIDE để xử lý mẫu số bằng 0.

Ngày phân tích là ngày đặt đơn. Nếu trạng thái của đơn cũ thay đổi, doanh số của ngày cũ có thể thay đổi theo lần refresh mới. Đây là phân tích trạng thái hiện tại theo ngày đặt, không phải chuỗi tiền thu đúng ngày paid_at. Khi nghiệp vụ cần báo cáo dòng tiền, phải bổ sung mô hình và measure theo thời điểm thanh toán.

## Trang Tổng quan
Trang Tổng quan cung cấp điểm bắt đầu của báo cáo. Người dùng xác định khoảng ngày rồi đọc số đơn, giá trị vé và số vé bán trong cùng bộ lọc. Xu hướng theo thời gian giúp nhận biết phân bố dữ liệu và chọn giai đoạn cần xem sâu. Trang này không thay thế phần so sánh từng sự kiện.

Khi trình diễn, cần chỉ rõ ngày đang lọc và đơn vị tiền. Một giá trị 188,31 tỷ trên card là cách làm tròn của số tiền nguyên đồng, không phải con số độc lập. Nếu so sánh năm, phải cân nhắc 2026 chưa đủ năm và dữ liệu nhiều năm được thêm theo số lô mô phỏng khác nhau.

Người đọc có thể bắt đầu bằng tổng quan toàn bộ, sau đó giới hạn một năm hoặc một khoảng tháng. Sự thay đổi đồng thời của card và đồ thị là thao tác kiểm tra tương tác cơ bản. Một visual không thay đổi có thể do cấu hình interaction, quan hệ hoặc measure đã bỏ filter, chưa thể kết luận do dữ liệu không biến động.

## Trang Hiệu quả các sự kiện
Trang này trả lời sự kiện nào đóng góp nhiều giá trị vé và số vé trong khoảng đã chọn. Xếp hạng theo doanh số giúp tìm chương trình đóng góp lớn, còn số lượng vé giúp phân biệt tác động của quy mô và giá bán. Một chương trình có giá cao có thể dẫn đầu doanh số dù bán ít vé hơn chương trình khác.

Khi dùng tỷ lệ bán trên quota, mẫu số cần đúng phạm vi sự kiện và hạng vé. Quota hiện hành không phải số ghế trống tại mọi thời điểm vì hệ thống chưa mô hình hóa giữ chỗ đang chờ. Tên chỉ tiêu nên phản ánh đây là tỷ lệ vé PAID trên quota thay vì cam kết số chỗ còn mua được.

Phân tích cần phân biệt chương trình đã kết thúc với chương trình đang mở bán. So sánh trực tiếp hai chương trình ở các giai đoạn vòng đời khác nhau có thể gây thiên lệch. Với dữ liệu mô phỏng, trang này kiểm chứng khả năng phân loại và drill, không chứng minh hiệu quả thực tế của đơn vị tổ chức.

## Trang Chi tiết sự kiện
Trang Chi tiết sự kiện tập trung một chương trình và cơ cấu các hạng vé. Người dùng xem hạng phổ thông, ưu tiên và VIP cùng số lượng và giá trị đóng góp. Mức phân tích này sử dụng fact chi tiết vì mart ngày không giữ ticket_type_id.

Giá niêm yết ở dim_ticket_type không dùng để tính lại số tiền đã bán. Đơn giá đã chốt và mức giảm giá nằm trong order_items rồi đi vào fact. Nếu lấy list_price hiện hành nhân số lượng, báo cáo có thể lệch sau khi danh mục thay đổi hoặc có chương trình giảm giá.

Điểm kiểm tra quan trọng là bộ lọc sự kiện có thực sự giới hạn các dòng fact và visual hạng vé. Nếu danh sách hạng vẫn hiển thị tên chung, cần phân biệt tên hạng lặp giữa sự kiện với ticket_type_id duy nhất. Bảng hiển thị có thể thêm tên sự kiện để làm rõ ngữ cảnh mà không đổi khóa mô hình.

## Trang Kênh bán và trạng thái đơn
Trang cuối phân tích WEB và APP cùng cơ cấu PAID, EXPIRED, CANCELLED, PENDING. Giá trị vé và số đơn thanh toán đánh giá kết quả bán, trong khi số đơn hết hạn hoặc hủy giúp quan sát phần chưa chuyển thành thanh toán. Tỷ lệ PAID cần tính trên cùng kênh và khoảng ngày.

Không gọi tỷ lệ này là tỷ lệ chuyển đổi từ người truy cập, vì dữ liệu không có lượt xem hay phiên truy cập. Nó chỉ mô tả tỷ lệ đơn đã thanh toán trên các đơn tồn tại trong fact. Tương tự, không kết luận APP có trải nghiệm tốt hơn chỉ từ khác biệt trong bộ dữ liệu do chương trình sinh.

Người dùng có thể chọn cùng sự kiện và thời gian để giảm khác biệt cơ cấu khi so sánh hai kênh. Mọi nhận định về nguyên nhân cần thêm dữ liệu hoặc thử nghiệm. Bộ báo cáo hiện tại hỗ trợ tìm khu vực cần kiểm tra, không tự xác định nguyên nhân kinh doanh.

# Chương 6 Kết quả quan sát và phương pháp đánh giá
## Môi trường và cách thu thập bằng chứng
Kết quả trong chương được thu từ truy vấn đọc SQL Server và PostgreSQL ngày 04 tháng 10 năm 2026, kết hợp kiểm tra các file cấu hình và metadata trang trong PBIX. Các truy vấn chỉ đọc không thay đổi dữ liệu và không kích hoạt lại pipeline. Vì các dịch vụ có thể tiếp tục chạy, số liệu cần gắn với thời điểm quan sát.

Metadata PBIX xác nhận bốn tên trang là Tổng quan, Hiệu quả các sự kiện, Chi tiết sự kiện và Kênh bán & trạng thái đơn. Có 33 visual containers trong định nghĩa báo cáo, bao gồm cả bộ lọc hoặc đối tượng không phải biểu đồ. Con số này không được hiểu là 33 biểu đồ phân tích hoặc bằng chứng nghiệm thu giao diện.

Không thực thi mới bộ test nghiệp vụ hoặc benchmark hiệu năng trong lần biên soạn này. Các test khai báo và mã xử lý được trình bày như thiết kế có thể kiểm chứng. Những trường hợp cần mô phỏng thay đổi, xóa hoặc lỗi API được liệt kê thành kế hoạch nghiệm thu, không gắn kết quả đạt giả định.

## Kết quả số lượng và chỉ tiêu
SQL Server có 357.000 đơn và 399.696 chi tiết đơn. PostgreSQL tại thời điểm đọc có 357.000 dòng silver.orders và 399.696 dòng gold.fact_ticket_sales. Bronze orders cũng có 357.000 dòng. Sự tương ứng số lượng phù hợp với kỳ vọng hiện tại nhưng chưa chứng minh từng khóa hoặc từng giá trị đều bằng nhau.

Gold ghi nhận 293.274 đơn PAID, 47.059 đơn EXPIRED, 16.657 đơn CANCELLED và 10 đơn PENDING. Tổng các trạng thái bằng 357.000 đơn. Tổng sold_quantity là 636.959 và sales_amount là 188.306.020.500 VND. Chỉ nhóm PAID đóng góp các chỉ tiêu bán vé trong truy vấn phân nhóm đã đọc.

Tỷ lệ đơn thanh toán tính từ hai số đếm là khoảng 82,15%. Đây là kết quả trên toàn bộ phạm vi hiện tại, không phải tỷ lệ riêng của năm 2026. dim_date có 2.435 dòng ngày và agg_daily_sales có 26.466 tổ hợp ngày, sự kiện, kênh. Không suy ra mọi ngày đều phát sinh giao dịch ở mọi sự kiện.

## Đánh giá tính đúng của mô hình
Grain order_item_id làm rõ cách tính số vé và doanh số. Việc không ghép payments vào fact tránh nhân bản dòng theo số lần thử. Đếm phân biệt order_id làm số đơn không bị tăng theo số hạng trong đơn. Những lựa chọn này giải quyết lỗi mô hình hóa có thể kiểm tra trực tiếp trên SQL.

Logic incremental xem lại toàn bộ ứng viên nên có khả năng đưa thay đổi trạng thái đơn cũ vào fact. Macro so sánh hash cũng có nhánh khôi phục bản ghi đang xóa mềm. Đây là nhận xét từ mã nguồn. Muốn xác nhận bằng thực nghiệm cần tạo các ca thay đổi có kiểm soát rồi so sánh trước và sau ở từng tầng.

Số lượng nguồn và đích bằng nhau là điều kiện cần trong snapshot không lọc, nhưng không đủ. Hai lỗi mất dòng và nhân đôi có thể bù số lượng. Tổng tiền bằng nhau cũng có thể che hai sai số trái dấu. Vì vậy, nghiệm thu cần đối chiếu khóa và giá trị theo dòng, sau đó kiểm tra aggregate ở nhiều chiều.

## Kế hoạch kiểm thử bổ sung
Ca nạp ban đầu cần kiểm tra mọi khóa nguồn có ở Bronze và mọi dòng hợp lệ có ở Silver. Ca chạy lại trên cùng snapshot cần so sánh tập khóa, hash và KPI để xác nhận không nhân đôi. Ca thêm đơn phải đi kèm chi tiết và trạng thái hợp lệ, sau đó tăng đúng các chỉ tiêu liên quan.

Ca cập nhật nên dùng một đơn cũ đổi từ PENDING sang PAID, kiểm tra fact ở ngày đặt ban đầu. Ca xóa cần thực hiện trong môi trường thử riêng, bảo đảm Airbyte trả snapshot đầy đủ rồi xác nhận Silver đánh dấu xóa và Gold loại dòng. Ca khôi phục kiểm tra khóa quay lại không tạo bản sao và được tính trở lại đúng điều kiện.

Ca lỗi Airbyte phải chứng minh sensor không phát Dataset thành công. Ca lỗi dbt phải chứng minh tầng sau không nhận sự kiện mới từ task thất bại. Cần kiểm tra cả trường hợp Dataset cũ vẫn đang chờ, vì trạng thái đó có thể làm hành vi điều phối khác kỳ vọng cùng batch. Kết quả từng ca cần lưu log và truy vấn đối chiếu.

## Kế hoạch đo hiệu năng
Benchmark nên giữ cùng phần cứng, cấu hình PostgreSQL, số luồng dbt và dữ liệu. Có thể so sánh full refresh với incremental khi dữ liệu không đổi, khi một tỷ lệ nhỏ dòng thay đổi và khi thay đổi nhiều. Mỗi cấu hình nên lặp nhiều lần, ghi median cùng độ phân tán thay vì chọn lượt nhanh nhất.

Thời gian toàn tuyến gồm đọc nguồn, nạp Bronze, chờ scheduler, biến đổi và refresh Power BI. Thời gian riêng dbt không phản ánh toàn bộ độ trễ người dùng nhận dữ liệu. Ngoài elapsed time, nên quan sát số dòng ghi, CPU, bộ nhớ và I/O nếu công cụ cho phép. Hiện chưa có bộ số đo để tuyên bố mức tăng tốc.

Full Refresh Overwrite vẫn đọc toàn bộ nguồn, còn hash incremental vẫn quét ứng viên. Khi dữ liệu lớn lên, chi phí này có thể chiếm ưu thế. Nếu cần giảm độ trễ, CDC hoặc incremental source có thể phù hợp, nhưng phải thay thiết kế phát hiện xóa và kiểm soát phiên bản, không chỉ đổi một tùy chọn Airbyte.

## Hạn chế và rủi ro
Rủi ro lớn nhất của phát hiện xóa bằng anti-join là snapshot thiếu. Một sync bị giới hạn stream, thay bộ lọc hoặc lỗi dữ liệu có thể làm nhiều khóa không xuất hiện. Nếu vẫn chạy Silver, chúng có thể bị đánh dấu xóa. Cần bổ sung kiểm tra độ đầy đủ và chặn bất thường trước khi mở rộng sử dụng.

Dataset list chưa bảo đảm các bảng cùng một thời điểm nguồn. Bronze cũng không được đóng băng trong vùng làm việc riêng. Nguồn thay đổi trong lúc sync hoặc sync mới chồng lúc dbt đọc có thể gây không nhất quán. Quy tắc không chạy chồng và giữ nguồn ổn định trong buổi trình diễn giảm rủi ro, nhưng không thay thế thiết kế batch và snapshot.

Dimensions lưu hiện hành và fact chưa mô hình hóa hoàn tiền, chuyển nhượng vé hoặc check-in. Gold cập nhật từng model nên Power BI phải refresh theo cửa sổ vận hành phù hợp. Dữ liệu mô phỏng không có tính đại diện thống kê cho người mua thật. Những giới hạn này xác định phạm vi sử dụng hợp lý của kết quả.

# Chương 7 Kết luận và hướng phát triển
## Kết luận
Đề tài đã hình thành bộ thành phần ELT phục vụ phân tích bán vé ở môi trường local: dữ liệu SQL Server, nạp Bronze qua Airbyte, biến đổi bằng dbt-postgres, điều phối bằng Airflow và file Power BI bốn trang. Quy mô quan sát hiện tại là 357.000 đơn hàng, với các chỉ tiêu Gold có thể truy nguyên về dòng chi tiết đơn.

Thiết kế xác định rõ grain, phân biệt payment attempt với doanh số và sử dụng hash để xử lý incremental trên snapshot đầy đủ. Việc tách DAG theo tầng và nghiệp vụ giúp người vận hành nhìn được lệnh SQL tương ứng. Báo cáo cũng chỉ ra giới hạn của Dataset, thời gian nghiệp vụ và sự khác nhau giữa kiểm tra khai báo với kiểm tra đã chạy.

Kết quả phù hợp một đồ án tích hợp dữ liệu và mô hình hóa phân tích. Để hoàn tất nghiệm thu theo tiêu chí học thuật, cần bổ sung hồ sơ thực nghiệm có kiểm soát cho các ca thay đổi và lỗi, cùng số đo hiệu năng nếu muốn đưa ra kết luận so sánh. Không dùng sự tồn tại của giao diện hoặc bảng dữ liệu thay cho các bằng chứng đó.

## Hướng phát triển ưu tiên
Ưu tiên đầu tiên là kiểm soát batch và độ đầy đủ. Mỗi lượt đồng bộ nên có mã lô, số dòng, thời điểm nguồn và trạng thái dùng chung. Tầng sau chỉ xử lý bộ lô đã xác nhận. Một cơ chế publication hoặc version view giúp Power BI đọc nhất quán toàn bộ tập Gold.

Ưu tiên tiếp theo là kiểm thử chất lượng có tự động hóa và quan sát vận hành. Các kiểm tra khóa, quan hệ, đối chiếu tiền và biến động số dòng cần có ngưỡng rõ. Cảnh báo chỉ nên phát khi có hành động cần thiết, đồng thời tránh gửi bí mật hoặc dữ liệu nhạy cảm vào log. Kết quả test nên gắn với commit hoặc phiên bản cấu hình.

CDC, lịch sử dimension và fact thanh toán là các hướng mở rộng sau khi nền tảng hiện tại được nghiệm thu. CDC yêu cầu xử lý delete event và thứ tự thay đổi; SCD2 yêu cầu khóa phiên bản và khoảng hiệu lực; fact thanh toán cần định nghĩa rõ grain của giao dịch, hoàn tiền và phí. Các chức năng này không nên được thêm chỉ để tăng số công nghệ trong đồ án.
