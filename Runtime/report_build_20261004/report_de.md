# Giới thiệu
## Bối cảnh của bài toán
Hệ thống bán vé sự kiện tạo ra dữ liệu ở nhiều thời điểm khác nhau. Thông tin sự kiện và hạng vé xuất hiện trước khi mở bán; đơn hàng hình thành khi người mua lựa chọn vé; các lần thử thanh toán tiếp tục bổ sung dữ liệu sau đó. Một câu hỏi tưởng đơn giản như “sự kiện này đã bán được bao nhiêu vé” vì thế phụ thuộc vào cách nối các bảng, trạng thái được chấp nhận và thời điểm ghi nhận. Nếu những quy tắc này chỉ nằm trong từng báo cáo riêng lẻ, cùng một nguồn có thể tạo ra nhiều kết quả khác nhau.

Đề tài xuất phát từ nhu cầu tổ chức một tuyến xử lý dữ liệu bán vé có thể theo dõi và giải thích được. Hệ thống nguồn cần phục vụ giao dịch, trong khi môi trường phân tích cần dữ liệu ổn định để nhóm theo ngày, sự kiện hoặc kênh bán. Việc tách hai nhiệm vụ giúp đặt quy tắc biến đổi ở một vị trí xác định và hạn chế việc mỗi công cụ báo cáo tự xử lý lại dữ liệu nguồn theo cách riêng.

Trong phạm vi khóa luận, dữ liệu nghiệp vụ được tạo bằng chương trình Python và lưu trong SQL Server. Cách tiếp cận này tránh sử dụng thông tin giao dịch nội bộ của doanh nghiệp, đồng thời cho phép điều chỉnh số lượng đơn và tái lập lô dữ liệu. Những tên sự kiện, địa điểm hoặc mức giá có vẻ gần thực tế không làm cho bộ dữ liệu trở thành dữ liệu giao dịch thật. Các kết luận trong báo cáo liên quan đến hệ thống xử lý, không đại diện cho thị trường bán vé.

## Vấn đề kỹ thuật cần giải quyết
Vấn đề thứ nhất là sự khác nhau về mức chi tiết giữa các bảng. Một đơn có thể chứa nhiều dòng vé và có nhiều lần thử thanh toán. Nếu nối hai tập này trực tiếp theo mã đơn, số dòng kết quả có thể bằng tích số dòng vé và số lần thử. Phép cộng tiền trên kết quả đó sẽ lớn hơn giá trị thực của đơn. Sai lệch xuất hiện từ thiết kế mô hình, dù câu lệnh SQL chạy thành công và báo cáo không hiển thị lỗi.

Vấn đề thứ hai là dữ liệu cũ vẫn thay đổi. Một đơn được tạo từ ngày trước có thể chuyển trạng thái sau lần đồng bộ gần nhất. Chỉ đọc các dòng chi tiết đơn có thời gian cập nhật mới sẽ không đủ nếu thay đổi chỉ xảy ra ở bảng đơn hàng. Quy trình biến đổi cần xem xét quan hệ giữa các bảng và xác định lại các đại lượng phụ thuộc vào trạng thái đơn.

Vấn đề thứ ba là xác nhận một bước thực sự hoàn thành. Lệnh yêu cầu Airbyte đồng bộ chỉ khởi tạo công việc, không chứng minh dữ liệu đã sẵn sàng. Tầng chuẩn hóa phải chờ kết quả đồng bộ, còn tầng phân tích phải chờ các đầu vào cần thiết. Thiết kế điều phối vì vậy cần phân biệt thời điểm gửi yêu cầu, trạng thái đang chạy và trạng thái hoàn tất thành công.

Các vấn đề trên tạo ra khoảng cách giữa việc kết nối thành công vài công cụ và việc xây dựng một hệ thống dữ liệu có quy tắc nhất quán. Đây là khoảng cách triển khai trong bài toán cụ thể, không phải tuyên bố rằng các kỹ thuật khử trùng hay cập nhật tăng dần chưa được nghiên cứu. Giá trị của đề tài nằm ở cách lựa chọn, kết hợp và kiểm chứng những kỹ thuật phù hợp với dữ liệu bán vé.

## Mục tiêu và câu hỏi nghiên cứu
Mục tiêu chung là thiết kế và xây dựng hệ thống tích hợp dữ liệu bán vé theo ba tầng Bronze, Silver và Gold. Hệ thống phải thể hiện được nguồn gốc dữ liệu, cách chuẩn hóa, quy tắc cập nhật và phụ thuộc thực thi. Sản phẩm phân tích cuối cùng được sử dụng trong Power BI để minh họa khả năng khai thác, nhưng trọng tâm của khóa luận là kiến trúc và xử lý dữ liệu.

Câu hỏi thứ nhất là cách phân chia trách nhiệm giữa công cụ đồng bộ, cơ sở dữ liệu đích, mã biến đổi và bộ điều phối. Câu trả lời cần chỉ rõ thành phần nào đọc dữ liệu, thành phần nào ghi bảng và thành phần nào chỉ phát tín hiệu. Việc phân chia này giúp tránh nhầm rằng Airflow lưu dữ liệu phân tích hoặc dbt tự đảm nhận toàn bộ quá trình trích xuất.

Câu hỏi thứ hai là cách nhận diện bản ghi mới, thay đổi, biến mất và xuất hiện trở lại khi đầu vào là một bản chụp đầy đủ. Câu hỏi này gắn với quy tắc so sánh khóa, dấu vân tay nội dung và cơ chế xóa mềm. Phương pháp phải nêu cả trường hợp hợp lệ lẫn điều kiện có thể gây sai, đặc biệt khi bản chụp đầu vào không đầy đủ.

Câu hỏi thứ ba là cách mô hình hóa dữ liệu để chỉ tiêu bán vé không bị nhân bản. Câu hỏi thứ tư là bằng chứng nào đủ để đánh giá hệ thống: số lượng bản ghi, đối chiếu khóa, kịch bản thay đổi, hành vi khi lỗi và thời gian xử lý. Báo cáo phân biệt câu trả lời rút ra từ mã nguồn với câu trả lời đã có quan sát thực nghiệm.

## Đối tượng và phạm vi
Đối tượng xử lý gồm năm nhóm dữ liệu: sự kiện, hạng vé, đơn hàng, chi tiết đơn và lần thử thanh toán. Khóa luận không thu thập hồ sơ khách hàng, thông tin định danh người mua hoặc dữ liệu thẻ thanh toán. Bảng thanh toán hỗ trợ mô tả nghiệp vụ nguồn; đề tài không triển khai đối soát với tệp do đối tác cung cấp.

Phạm vi công nghệ gồm SQL Server, Airbyte, PostgreSQL, dbt-postgres, Apache Airflow và Power BI Desktop. Hệ thống chạy trong môi trường cục bộ có sử dụng Docker. Kiến trúc không bao gồm Kafka, Spark, Iceberg hoặc kho lưu trữ đối tượng. Ba tầng dữ liệu là các lược đồ trong PostgreSQL, không phải một triển khai Lakehouse.

Phạm vi thời gian của dữ liệu tổng hợp bao gồm nhiều năm, nhưng số lượng mỗi năm do tham số sinh và các lô đã nạp quyết định. Năm 2026 trong bộ dữ liệu không được coi là một năm quan sát hoàn chỉnh. Khi so sánh theo năm, báo cáo chỉ minh họa chức năng lọc và tổng hợp, không suy luận xu thế kinh tế hoặc hành vi khách hàng.

## Phương pháp thực hiện và đóng góp
Phương pháp thực hiện bắt đầu bằng phân tích thực thể và quan hệ nguồn. Từ đó xác định mức chi tiết của bảng phân tích, định nghĩa chỉ tiêu và xây dựng quy tắc biến đổi. Mã nguồn được chia theo tầng và nghiệp vụ để có thể truy vết từ một tác vụ Airflow đến mô hình SQL tương ứng. Các lựa chọn được giải thích theo yêu cầu, không theo số lượng công nghệ sử dụng.

Đóng góp triển khai gồm bộ sinh dữ liệu có tham số, cấu trúc kho ba tầng, các mô hình chuẩn hóa và cập nhật theo khóa, mô hình phân tích bán vé, cùng cơ chế điều phối dựa trên kết quả xử lý. Đây là sản phẩm kỹ thuật ứng dụng. Đề tài không đưa ra thuật toán mới về mặt lý thuyết và không khẳng định đạt mức sẵn sàng vận hành sản xuất chỉ dựa trên việc các dịch vụ đã khởi động.

Báo cáo gồm năm chương. Chương đầu xác định bài toán; chương hai trình bày cơ sở lựa chọn; chương ba mô tả phương pháp và thiết kế; chương bốn giải thích triển khai, bằng chứng quan sát và kế hoạch đánh giá; chương cuối tổng hợp kết quả và giới hạn. Các phụ lục cung cấp từ điển dữ liệu, truy vấn đối chiếu và hướng dẫn vận hành, thay cho việc đưa toàn bộ mã nguồn vào phần nội dung chính.

# Cơ sở lý thuyết và các cách tiếp cận
## Hệ thống giao dịch và hệ thống phân tích
Trong hệ thống giao dịch, một thao tác đặt vé cần ghi nhận đơn, chi tiết và trạng thái liên quan một cách hợp lệ. Cấu trúc dữ liệu thường phản ánh các thực thể nghiệp vụ riêng để hạn chế lặp thông tin. Khi phân tích, người dùng lại cần nhìn nhiều giao dịch cùng lúc, nhóm theo thuộc tính sự kiện hoặc thời gian và tính các đại lượng tổng hợp. Hai loại công việc đặt ra cách tổ chức truy vấn khác nhau.

Với bài toán này, giữ nguyên năm bảng nguồn cho mọi biểu đồ sẽ buộc báo cáo lặp lại các phép nối và quy tắc trạng thái. Một thay đổi trong định nghĩa đơn đã thanh toán có thể phải sửa ở nhiều nơi. Kho phân tích đưa quy tắc đó vào mô hình dùng chung, giúp các biểu đồ cùng đọc một tập đại lượng đã xác định ý nghĩa.

Tách hệ thống không tự bảo đảm dữ liệu đúng. Kho dữ liệu vẫn có thể nhận bản chụp thiếu, sai kiểu hoặc số liệu bị nhân bản. Lợi ích thiết kế nằm ở việc có vị trí kiểm soát rõ: lỗi trích xuất được tìm ở tầng nạp; lỗi chuẩn hóa ở Silver; sai mức tổng hợp hoặc điều kiện trạng thái ở Gold. Việc truy vết này là một yêu cầu kỹ thuật quan trọng của đồ án.

## Trích xuất nạp và biến đổi dữ liệu
Trích xuất là đọc dữ liệu từ hệ thống nguồn; nạp là chuyển dữ liệu vào môi trường đích; biến đổi là áp dụng quy tắc để tạo cấu trúc sử dụng được. Trong cách tổ chức ELT của đề tài, dữ liệu được nạp vào PostgreSQL trước, sau đó các truy vấn SQL thực hiện chuẩn hóa và mô hình hóa. Airbyte phụ trách đường nạp, còn dbt tổ chức mã SQL tại đích.

Sự lựa chọn này phù hợp với dữ liệu quan hệ và mục tiêu thể hiện rõ logic biến đổi. Khi cần kiểm tra một công thức, người thực hiện có thể đọc mô hình SQL và truy vấn bảng trung gian. Một chương trình Python tự thực hiện toàn bộ tuyến cũng khả thi, nhưng phải tự quản lý nhiều trách nhiệm như kết nối, ghi lô, lập lịch và theo dõi trạng thái. Phương án đó được xem như lựa chọn thay thế, chưa được cài đặt để so sánh hiệu năng.

ELT không có nghĩa mọi phép xử lý đều đẩy xuống cơ sở dữ liệu bằng mọi giá. Bộ sinh vẫn dùng Python, các yêu cầu API vẫn cần mã điều phối, và việc đóng gói môi trường thuộc Docker. Ranh giới sử dụng được chọn theo bản chất công việc: xử lý tập bản ghi ở SQL; tương tác dịch vụ và kiểm soát thực thi ở mã điều phối.

## Phân tầng dữ liệu theo Medallion
Medallion mô tả cách nâng dần mức chuẩn hóa và khả năng sử dụng dữ liệu qua các tầng Bronze, Silver và Gold [1]. Khóa luận vận dụng nguyên tắc phân tầng này để tổ chức lược đồ PostgreSQL. Sự vận dụng không đồng nghĩa hệ thống có đầy đủ đặc tính của những nền tảng Lakehouse thường sử dụng tên gọi đó.

Trong thiết kế cụ thể, Bronze giữ dữ liệu gần với kết quả đồng bộ. Silver chịu trách nhiệm kiểu dữ liệu, định dạng, chọn bản ghi đại diện và trạng thái xóa. Gold chuyển dữ liệu hiện tại thành các bảng phục vụ câu hỏi phân tích. Một thay đổi tên cột kỹ thuật của Airbyte chủ yếu ảnh hưởng đầu đọc Silver, trong khi tên và ý nghĩa các chỉ tiêu công bố ở Gold có thể giữ ổn định.

Ba tầng không phải ba bản sao giống nhau. Silver thêm quy tắc chất lượng và trạng thái; Gold thay đổi mức chi tiết và cách tổ chức quan hệ. Cũng không nên coi Bronze mặc nhiên là kho lịch sử đầy đủ: chế độ ghi đè của đề tài thay thế tập dữ liệu sau đồng bộ. Muốn truy lại mọi phiên bản nguồn cần bổ sung cơ chế lưu bản chụp hoặc nhật ký thay đổi riêng.

## Bản chụp đầy đủ và cập nhật tăng dần
### Ý nghĩa của chế độ đồng bộ
Chế độ Full Refresh Overwrite đọc lại phạm vi dữ liệu đã cấu hình và thay thế tập tương ứng tại đích [2]. Trong đề tài, phạm vi đó là năm bảng được chọn. Đây là cơ sở để so sánh tập khóa hiện tại với tập khóa đã lưu, nhưng chỉ có ý nghĩa khi phạm vi đồng bộ giữ ổn định và công việc hoàn tất thành công.

Một bản chụp đầy đủ của từng bảng chưa chắc là bản chụp đồng thời của mọi bảng. Ví dụ, Airbyte có thể đọc đơn hàng trước khi một giao dịch mới xuất hiện, rồi đọc chi tiết sau thời điểm đó. Trường hợp này tạo quan hệ tạm thời không khớp dù mỗi bảng riêng lẻ đã đọc hết. Báo cáo vì vậy phân biệt độ đầy đủ của một bảng với tính nhất quán xuyên bảng.

### Cập nhật tại tầng biến đổi
Cập nhật tăng dần trong dbt cho phép mô hình chọn tập dòng cần xử lý khi bảng đích đã tồn tại; khóa duy nhất và chiến lược cập nhật phải phù hợp với cấu trúc dữ liệu [3]. Khóa luận sử dụng cơ chế này sau bước nạp đầy đủ. Do đó, “nguồn đồng bộ đầy đủ” và “đích cập nhật tăng dần” mô tả hai giai đoạn khác nhau, không mâu thuẫn nhau.

Trong mô hình hiện tại, tập ứng viên vẫn được tạo từ toàn bộ dữ liệu đang hoạt động. So sánh khóa và nội dung loại bỏ những dòng không cần ghi lại. Cách làm nhắm đến giảm thao tác ghi, không loại bỏ toàn bộ chi phí đọc và kết nối. Khi tập dữ liệu tăng mạnh, chi phí quét, xếp hạng và tính dấu vân tay có thể trở thành phần chiếm ưu thế.

### So sánh với mốc thời gian và nhật ký thay đổi
Một phương án thường dễ hình dung là chỉ chọn dòng có thời gian cập nhật lớn hơn mốc lớn nhất đã xử lý. Trong dữ liệu bán vé, mốc toàn cục có thể bỏ sót bản ghi đến muộn hoặc thay đổi ở bảng cha. Đề tài chọn so sánh toàn bản chụp để tránh phụ thuộc hoàn toàn vào mốc này. Đổi lại, thời gian xử lý không chỉ phụ thuộc số dòng mới.

Thu thập dữ liệu thay đổi từ nhật ký, thường gọi là CDC, là hướng khác để truyền các thao tác thêm, sửa và xóa. Tuyến hiện tại không triển khai CDC. Nếu chuyển sang CDC, không thể giữ nguyên giả định rằng khóa vắng mặt ở một lô đồng nghĩa với bị xóa; một lô thay đổi chỉ chứa phần phát sinh. Cơ chế xóa khi đó phải dựa vào sự kiện hoặc quy ước khác.

## Chuẩn hóa và khử trùng
Chuẩn hóa bắt đầu từ ý nghĩa trường dữ liệu, không chỉ từ thao tác đổi kiểu. Với mã trạng thái, khoảng trắng thừa và khác biệt chữ hoa chữ thường có thể tạo các nhóm không mong muốn. Với số tiền, hệ thống cần một đơn vị thống nhất và kiểu số tránh sai lệch do làm tròn ngoài chủ ý. Với thời gian, cần phân biệt thời điểm nghiệp vụ và thời điểm hệ thống nạp dữ liệu.

Khử trùng theo khóa đòi hỏi quy tắc chọn bản ghi. “Giữ bản ghi đầu tiên” không đủ nếu thứ tự đọc có thể thay đổi. Các mô hình Silver xếp hạng theo thời gian cập nhật nghiệp vụ, tiếp theo là thời điểm trích xuất và định danh dòng nguồn. Dấu vân tay nội dung là tiêu chí cuối để ổn định việc lựa chọn khi các tiêu chí trước trùng nhau.

Quy tắc xếp hạng không thay thế việc tìm nguyên nhân trùng. Nếu hai dòng cùng khóa mang nội dung khác nhau nhưng không có thông tin phiên bản đáng tin cậy, chương trình chỉ có thể chọn theo quy ước đã định. Vì vậy, dữ liệu trùng bất thường vẫn cần được ghi nhận trong đánh giá chất lượng. Kết quả chỉ còn một dòng không tự chứng minh đó là phiên bản đúng về nghiệp vụ.

## Dấu vân tay nội dung và phép hợp nhất
Dấu vân tay nội dung là giá trị rút gọn được tính từ một tập trường đã chọn. Trong mã của đề tài, các trường nghiệp vụ được đưa vào một cấu trúc có thứ tự trước khi tính MD5. Mục đích là phát hiện sự khác nhau giữa ứng viên và dòng đích, không phải mã hóa thông tin hay bảo đảm an toàn mật khẩu.

Việc chọn trường quyết định ý nghĩa so sánh. Nếu đưa thời điểm trích xuất vào dấu vân tay, một lần Airbyte đọc lại có thể làm mọi dòng trông như đã thay đổi. Nếu bỏ trường trạng thái đơn, hệ thống có thể không cập nhật giá trị vé khi đơn chuyển sang PAID. Vì vậy, danh sách trường phải gắn với nội dung công bố của từng mô hình.

MERGE trong PostgreSQL thực hiện các hành động có điều kiện dựa trên sự khớp giữa nguồn và đích [4]. Trong đồ án, dbt sử dụng khóa đã khai báo để đưa tập thay đổi vào bảng. Một điều kiện quan trọng là ứng viên không có nhiều dòng cạnh tranh cho cùng khóa đích. Bước khử trùng và chỉ mục duy nhất hỗ trợ kiểm soát điều kiện này.

## Mô hình chiều và mức chi tiết
Mô hình sao phân biệt bảng đo lường với các bảng thuộc tính dùng để lọc và nhóm dữ liệu [5]. Ở bài toán bán vé, bảng đo lường cần xác định trước một dòng đại diện cho đơn, dòng đơn hay lần thử thanh toán. Quyết định này chi phối cách tính số lượng, tiền và quan hệ với các bảng chiều.

Đề tài chọn dòng đơn làm mức chi tiết của bảng fact_ticket_sales. Một dòng lưu một hạng vé trong một đơn, kèm số lượng và giá trị đã chốt. Bảng chiều sự kiện, hạng vé, ngày, kênh và trạng thái cung cấp ngữ cảnh phân tích. Các lần thử thanh toán không ghép trực tiếp vào bảng đo lường này.

Một số đại lượng có thể cộng theo nhiều chiều, như số vé hoặc giá trị vé của các dòng hợp lệ. Số đơn lại cần đếm phân biệt vì một đơn xuất hiện ở nhiều dòng chi tiết. Khi tổng hợp trước, phải ghi rõ các chiều còn giữ lại. Bảng tổng hợp ngày của đề tài không có hạng vé, nên không thể dùng nó để giải thích cơ cấu bán theo hạng.

## Điều phối và tín hiệu hoàn thành
Airflow biểu diễn công việc dưới dạng đồ thị tác vụ có hướng không chu trình. Với cơ chế Dataset, một tác vụ có thể phát tín hiệu cập nhật khi hoàn tất thành công; đồ thị khác có thể lấy tín hiệu đó làm điều kiện lập lịch. Danh sách nhiều Dataset yêu cầu các đầu vào cập nhật theo quy tắc của bộ lập lịch [6].

Trong bài toán cụ thể, tác vụ gửi yêu cầu Airbyte và tác vụ chờ kết quả phải tách ý nghĩa. Nếu phát tín hiệu ngay sau khi gửi yêu cầu, Silver có thể đọc dữ liệu trước khi đồng bộ xong. Đặt tín hiệu tại tác vụ chờ thành công làm điều kiện chuyển tầng sát với trạng thái thực hơn.

Tín hiệu thành công cũng có giới hạn. Nó xác nhận tác vụ tương ứng kết thúc theo điều kiện lập trình, không tự chứng minh dữ liệu đúng nghiệp vụ hoặc thuộc cùng một lô với các đầu vào khác. Thiết kế cần thêm mã lô nếu muốn kiểm soát đồng nhất phiên bản xuyên bảng. Đây là một hướng nâng cấp, không phải tính năng đã hoàn thành trong bản triển khai.

## Tổng hợp lựa chọn cho đề tài
Các khái niệm trên dẫn đến lựa chọn xử lý theo lô, dùng bản chụp đầy đủ ở đầu nạp và cập nhật theo nội dung ở tầng chuẩn hóa. PostgreSQL thực thi các phép xử lý tập hợp; dbt quản lý mô hình và phụ thuộc SQL; Airflow quản lý thứ tự và trạng thái công việc. Power BI là bên tiêu thụ cấu trúc đã công bố.

Lựa chọn ưu tiên khả năng đọc mã, truy vết và tái lập trong phạm vi khóa luận. Nó chấp nhận chi phí quét bản chụp và giới hạn nhất quán hiện tại. Đánh giá phù hợp nhất không phải đếm số công nghệ sử dụng, mà kiểm tra các giả định, chứng minh quy tắc mô hình và đo hành vi của hệ thống trong những tình huống đã xác định.

# Phương pháp và thiết kế hệ thống
## Quy trình thiết kế
Quy trình thiết kế đi từ nghiệp vụ đến mức chi tiết, sau đó mới chọn công cụ và lịch chạy. Trước hết cần xác định một đơn hợp lệ gồm những dữ liệu nào, trạng thái nào được coi là đã bán và thời điểm nào dùng để phân tích. Nếu những câu hỏi này chưa rõ, thay công nghệ không giải quyết được sự khác nhau giữa các báo cáo.

Tiếp theo, mỗi yêu cầu được ánh xạ vào một thành phần. Quy tắc liên bảng nằm ở cấu trúc nguồn; quy tắc chuẩn hóa nằm ở Silver; công thức đo lường nằm ở Gold; phụ thuộc thực thi nằm ở Airflow. Sự phân công này cho phép kiểm tra từng trách nhiệm riêng, đồng thời giữ được tuyến truy vết từ dữ liệu nguồn đến chỉ tiêu.

Cuối cùng, thiết kế đánh giá được lập cùng với thiết kế xử lý. Mỗi nhánh thêm, sửa, xóa hoặc khôi phục cần một tình huống đầu vào và kết quả mong đợi. Mỗi giới hạn điều phối cần một tình huống thất bại tương ứng. Cách làm này tránh chỉ kiểm tra đường chạy thuận lợi rồi suy ra hệ thống đã đáp ứng mọi điều kiện.

## Yêu cầu chức năng và yêu cầu vận hành
Hệ thống phải đọc được năm bảng nguồn và đưa dữ liệu vào các bảng Bronze đã cấu hình. Với mỗi bảng, Silver cần chuẩn hóa kiểu, chọn tối đa một bản ghi hiện tại theo khóa và phản ánh những thay đổi so với đích. Gold cần tạo cấu trúc phân tích mà một dòng chi tiết đơn không bị nhân bản bởi số lần thanh toán.

Ở mức điều phối, người vận hành cần nhìn thấy công việc theo tầng và nghiệp vụ. Lịch đồng bộ phải sửa được trong tệp DAG tương ứng; thông tin định danh kết nối được tách khỏi lịch. Khi công việc thất bại, nhật ký phải đủ để phân biệt lỗi kết nối, lỗi truy vấn và lỗi điều kiện chờ, nhưng không ghi bí mật đăng nhập vào nội dung công bố.

Khả năng chạy lại là yêu cầu quan trọng. Khi đầu vào không đổi, tập khóa và chỉ tiêu không được tăng chỉ vì chạy thêm một lần. Khi cấu trúc mô hình thay đổi, người vận hành phải biết trường hợp nào cần tạo lại bảng thay vì áp dụng cập nhật thường lệ. Việc khôi phục môi trường cũng phải phân biệt khởi động lại dịch vụ với xóa dữ liệu lưu trong ổ đĩa dùng chung.

@TABLE requirements

## Thiết kế bộ dữ liệu nguồn
### Các thực thể và quan hệ
Bảng events mô tả sự kiện, khoảng mở bán, thời điểm tổ chức và sức chứa. Bảng ticket_types mô tả các hạng vé thuộc một sự kiện, gồm tên hạng, giá niêm yết và hạn mức bán. Mã hạng có ý nghĩa trong sự kiện, trong khi khóa ticket_type_id dùng để tham chiếu chính xác một bản ghi.

Bảng orders mô tả giao dịch đặt vé ở mức đơn, gồm thời điểm đặt, kênh bán, trạng thái và tổng tiền. Bảng order_items lưu từng hạng vé được chọn, số lượng, đơn giá đã chốt và giảm giá của dòng. Tách hai bảng cho phép một đơn chứa nhiều hạng vé mà không lặp lại toàn bộ thông tin đơn.

Bảng payments ghi từng lần thử thanh toán. Một đơn có thể có lần thất bại trước lần thành công. Số bản ghi thanh toán vì vậy không phải số đơn đã thanh toán. Nguồn có các ràng buộc để hạn chế tổ hợp không hợp lệ, nhưng các quy tắc tổng tiền xuyên nhiều dòng vẫn cần đối chiếu riêng.

@TABLE relations

### Sinh dữ liệu và bảo đảm tính tái lập
Chương trình sinh dữ liệu tiếp nhận số đơn, năm và giá trị khởi tạo ngẫu nhiên. Các thực thể được tạo theo thứ tự bảo đảm có khóa tham chiếu trước khi tạo bảng phụ thuộc. Thời gian đặt đơn, trạng thái và giá trị tiền được tạo theo những quy tắc nghiệp vụ định trước, thay vì chọn độc lập từng cột rồi ghép lại.

Giá trị khởi tạo ngẫu nhiên giúp lặp lại lựa chọn trong cùng phiên bản bộ sinh. Nó không tự bảo đảm kết quả giống nhau sau khi thuật toán hoặc danh mục đầu vào thay đổi. Hồ sơ lô vì vậy cần lưu cả tham số, phiên bản chương trình và số lượng đầu ra. Tệp mô tả lô hiện tại là điểm bắt đầu cho khả năng truy vết này.

Khi nạp thêm lịch sử, chương trình dịch các khóa theo khoảng đã tồn tại và điều chỉnh khóa ngoại tương ứng. Mã nghiệp vụ có tiền tố theo năm và giá trị khởi tạo để nhận diện lô. Cách đánh dấu này giúp phân biệt các lô mô phỏng, không có ý nghĩa như một định dạng mã giao dịch thật của doanh nghiệp.

### Giới hạn của dữ liệu tổng hợp
Phân bố trạng thái, mùa vụ và kênh bán phụ thuộc bộ sinh. Nếu tỷ lệ đơn thanh toán của một năm cao hơn năm khác, đó có thể chỉ là hệ quả của tham số. Dữ liệu phù hợp để kiểm tra cấu trúc, phép nối, cập nhật và giao diện phân tích, nhưng chưa phù hợp để đánh giá hành vi người mua hay dự báo thị trường.

Việc thêm nhiều lô cùng năm cũng làm thay đổi số sự kiện và cơ cấu dữ liệu. Vì thế, báo cáo sử dụng số lượng gắn với ngày khảo sát thay vì coi chúng là hằng số cố định của dự án. Khi người thực hiện nạp thêm dữ liệu, cần chạy lại truy vấn thống kê và cập nhật bằng chứng nếu muốn đưa con số mới vào kết luận.

## Kiến trúc tổng thể
### Luồng dữ liệu
Luồng dữ liệu bắt đầu tại TicketingDB trên SQL Server. Airbyte đọc các bảng được chọn và nạp vào lược đồ bronze trong cơ sở dữ liệu ticketing_analytics. Các mô hình dbt đọc Bronze, tạo Silver rồi xây dựng Gold. Power BI kết nối đến Gold để khai thác số liệu phân tích.

Ở thiết kế này, database là đơn vị cơ sở dữ liệu, còn schema là nhóm đối tượng bên trong database. Bronze, Silver và Gold là ba schema trong cùng kho đích, không phải ba database độc lập. Cơ sở dữ liệu phục vụ nhật ký và bộ lập lịch Airflow có trách nhiệm khác với kho phân tích, dù cùng dùng PostgreSQL.

@FIG architecture

### Luồng điều khiển
Airflow khởi động đồng bộ theo lịch trong DAG Bronze. Sau khi nhận mã công việc từ Airbyte, bộ cảm biến theo dõi công việc đó cho đến trạng thái kết thúc. Chỉ nhánh thành công mới phát Dataset mà Silver đăng ký. Dữ liệu bản ghi không đi qua Dataset; tín hiệu chỉ biểu diễn điều kiện cho bước kế tiếp.

Trong tầng biến đổi, dbt đọc cấu hình nguồn và liên kết các mô hình bằng source() và ref(). Airflow chọn mô hình cần chạy bằng đường dẫn hoặc nhãn. Hai đồ thị phụ thuộc có liên quan nhưng không đồng nhất: đồ thị dbt nói về phụ thuộc dữ liệu SQL, còn đồ thị Airflow nói về công việc, lịch và trạng thái thực thi.

### Lựa chọn và đánh đổi
Airbyte giúp giảm phần mã phải tự viết cho kết nối nguồn và đích. Đổi lại, hệ thống cần tích hợp API, theo dõi trạng thái và hiểu chế độ đồng bộ. dbt giúp tách truy vấn thành mô hình có cấu hình, nhưng người thiết kế vẫn chịu trách nhiệm về khóa, điều kiện tăng dần và công thức nghiệp vụ. Airflow điều phối được các bước, nhưng không tự phát hiện mọi dữ liệu sai.

PostgreSQL phù hợp với việc kiểm tra bằng SQL và vận hành một kho cục bộ. Khóa luận chưa chứng minh khả năng đáp ứng tải lớn hay nhiều người dùng đồng thời. Việc không dùng Spark là một giới hạn phạm vi có chủ ý, không phải kết luận rằng xử lý phân tán không có giá trị. Nếu quy mô và yêu cầu độ trễ thay đổi, cần đánh giá lại lựa chọn bằng số đo.

## Thiết kế tầng Bronze
Bronze giữ các trường nghiệp vụ và thông tin kỹ thuật do công cụ nạp bổ sung. Silver đọc những trường cần thiết bằng tên rõ ràng thay vì chọn tất cả một cách không kiểm soát. Cách này giảm khả năng một cột kỹ thuật mới tự xuất hiện trong hợp đồng của tầng sau và làm thay đổi dấu vân tay nội dung.

Nguồn đang dùng chế độ Full Refresh Overwrite. Điều kiện xử lý là lô đồng bộ kết thúc thành công trên cùng phạm vi bảng đã thống nhất. Nếu người vận hành thay bộ lọc nguồn để chỉ lấy một năm, tập Bronze không còn là toàn bộ dữ liệu mà Silver từng biết. Khi đó, cơ chế phát hiện khóa biến mất có thể hiểu sai dữ liệu ngoài năm đã chọn thành dữ liệu bị xóa.

Thiết kế hiện tại chưa giữ một vùng bản chụp bất biến riêng cho mỗi lô. Vì vậy, cần tránh đồng bộ mới ghi đè Bronze trong lúc dbt đang xử lý. Giới hạn số lượt chạy trong từng DAG chỉ hỗ trợ một phần; nó không tạo khóa toàn cục giữa nhiều DAG và nhiều kết nối khác nhau. Quy tắc vận hành và hướng bổ sung mã lô phải được nêu rõ.

## Thiết kế tầng Silver
### Hợp đồng dữ liệu
Hợp đồng dữ liệu xác định tên cột, kiểu và ý nghĩa mà mô hình công bố. Các khóa được chuẩn hóa sang bigint, giá trị tiền sang numeric(18,0), chuỗi mã được xử lý khoảng trắng và chữ hoa khi phù hợp. Bảng Silver còn lưu dấu vân tay, trạng thái xóa và thời điểm ghi để hỗ trợ cập nhật và truy vết.

Thời điểm cập nhật nghiệp vụ không đồng nghĩa thời điểm nạp vào kho. Một đơn cũ có thể được đồng bộ hôm nay nhưng vẫn giữ ngày đặt từ nhiều năm trước. Trường _loaded_at chỉ mô tả lần ghi tại kho theo logic mô hình, không được dùng thay cho ngày bán hoặc ngày thu tiền trong báo cáo.

### Thuật toán chọn bản ghi đại diện
Với mỗi bảng, mô hình tạo tập dữ liệu đã chuẩn hóa rồi tính dấu vân tay trên các trường nghiệp vụ. Sau đó ROW_NUMBER chia nhóm theo khóa chính và xếp thứ tự giảm dần theo các tiêu chí đã định. Chỉ dòng có hạng bằng một được đưa vào tập ứng viên. Các bước được tách thành biểu thức bảng chung để đọc và kiểm tra riêng.

Ví dụ minh họa, hai dòng cùng event_id có thời điểm updated_at khác nhau thì dòng mới hơn được chọn. Nếu thời điểm này bằng nhau, thời điểm trích xuất được dùng tiếp. Khi cả hai bằng nhau, định danh dòng và dấu vân tay giúp ổn định lựa chọn. Ví dụ này giải thích quy tắc, không phải kết quả kiểm thử đã thực hiện trên cơ sở dữ liệu đang chạy.

### Thuật toán tạo tập thay đổi
Tập ứng viên được nối với bảng đích theo khóa chính. Khóa chưa có được đưa vào tập thêm mới. Khóa đã có nhưng dấu vân tay khác được đưa vào tập cập nhật. Một dòng đích đang đánh dấu xóa cũng được đưa vào cập nhật khi khóa xuất hiện trở lại. Những dòng không thay đổi bị loại khỏi tập ghi.

Nhánh phát hiện xóa đọc các khóa đang hoạt động ở đích nhưng không có trong ứng viên. Các dòng này được giữ nội dung cũ và chuyển cờ xóa sang đúng. Hai tập kết hợp lại tạo đầu vào cho cơ chế hợp nhất. Việc giữ nội dung ở Silver giúp quan sát một khóa từng tồn tại, nhưng không lưu đầy đủ mọi phiên bản thay đổi của khóa đó.

@TABLE change_cases

### Chi phí và điều kiện đúng
Xếp hạng đòi hỏi tổ chức dữ liệu theo khóa và tiêu chí thứ tự; việc nối cần đọc ứng viên và tra cứu đích. Chi phí thực tế phụ thuộc kế hoạch thực thi, chỉ mục, bộ nhớ và kích thước dữ liệu. Không thể lấy số dòng ghi ít hơn để suy ra tổng thời gian giảm theo cùng tỷ lệ. Phân tích hiệu năng phải tách thời gian tạo ứng viên khỏi thời gian ghi đích.

Điều kiện đúng gồm khóa phù hợp, quy tắc chuẩn hóa ổn định, tập trường dấu vân tay đầy đủ và bản chụp đầu vào đủ phạm vi. Thay đổi quy tắc chuẩn hóa có thể làm nhiều dấu vân tay đổi dù nghiệp vụ nguồn không đổi. Đây là cập nhật do phiên bản xử lý, cần ghi nhận khi so sánh kết quả giữa hai lần chạy.

### Các bất biến của thuật toán
Bất biến thứ nhất là tập ứng viên có nhiều nhất một dòng trên mỗi khóa. Bước xếp hạng tạo điều kiện này trước khi hợp nhất. Nếu thay đổi mã làm nhánh cuối trả lại nhiều dòng cùng khóa, điều kiện của bước hợp nhất không còn được bảo đảm. Vì vậy, kiểm tra tính duy nhất nên đặt tại ranh giới ứng viên và tại bảng công bố, không chỉ dựa vào khóa của nguồn.

Bất biến thứ hai là mọi khóa đang hoạt động trong bản chụp phải có một dòng hoạt động ở đích sau khi xử lý thành công, với các trường nghiệp vụ tương ứng theo quy tắc chuẩn hóa. Khóa mới đi qua nhánh thêm; khóa thay đổi đi qua nhánh cập nhật; khóa giống nhau giữ nguyên; khóa từng xóa đi qua nhánh khôi phục. Phân chia này bao phủ các trạng thái đích của một khóa có trong ứng viên, với giả thiết phép ghi hoàn tất và không có tiến trình khác thay đổi đích đồng thời.

Bất biến thứ ba là khóa đang hoạt động ở đích nhưng vắng trong bản chụp đầy đủ phải chuyển sang trạng thái xóa mềm. Nhánh chống nối kiểm tra sự vắng mặt theo khóa. Sau một lần xử lý đúng, chạy lại cùng bản chụp không tiếp tục tạo thay đổi cho khóa đó vì điều kiện chỉ chọn dòng đích chưa đánh dấu xóa. Điều này giải thích cơ chế hội tụ về trạng thái hiện tại, thay vì chỉ mô tả một câu lệnh cập nhật.

Những lập luận trên phụ thuộc giả thiết dấu vân tay phân biệt được nội dung cần theo dõi. Hàm băm có khả năng va chạm về mặt lý thuyết; quy tắc chuẩn hóa cũng có thể làm hai đầu vào khác nhau trở thành cùng giá trị. Với yêu cầu kiểm chứng chặt hơn, cần đối chiếu trực tiếp các trường quan trọng hoặc bổ sung kiểm tra nội dung. Dấu vân tay là công cụ hỗ trợ so sánh hiệu quả, không phải chứng minh toán học rằng hai bản ghi luôn giống nhau.

### Minh họa chuyển trạng thái của một khóa
Xét một khóa minh họa K chưa có ở Silver. Ở lượt đầu, bản chụp chứa K với nội dung A; thuật toán thêm K và đánh dấu đang hoạt động. Ở lượt hai, bản chụp vẫn chứa A; khóa và dấu vân tay giống đích nên không phát sinh dòng ghi. Ở lượt ba, bản chụp chứa nội dung B; nhánh cập nhật thay A bằng B. Chuỗi này minh họa khác biệt giữa số lần chạy và số lần thực sự thay đổi bản ghi.

Ở lượt bốn, K vắng trong một bản chụp đầy đủ; dòng đích giữ nội dung B nhưng chuyển sang xóa mềm. Ở lượt năm, K xuất hiện lại với chính B. Dù dấu vân tay giống giá trị cũ, điều kiện cờ xóa làm dòng được cập nhật và trở lại hoạt động. Nếu thuật toán chỉ kiểm tra khác biệt dấu vân tay, bước thứ năm sẽ bị bỏ qua và dữ liệu hợp lệ vẫn bị xem là đã xóa.

Chuỗi trên là phân tích tình huống, chưa được ghi nhận như ca thực nghiệm đã chạy. Để kiểm chứng, cần lưu trạng thái trước và sau từng lượt, đồng thời giữ nguyên phạm vi bản chụp. Nếu giữa các lượt có tiến trình khác ghi cùng bảng, kết quả phải được phân tích cùng hoạt động đó. Việc công bố rõ giả thiết giúp tránh diễn giải một kết quả không ổn định thành lỗi ngẫu nhiên của công cụ.

## Thiết kế tầng Gold
### Bảng đo lường bán vé
fact_ticket_sales có khóa order_item_id. Mô hình kết hợp chi tiết đang hoạt động với đơn đang hoạt động, sau đó tra bảng chiều kênh và trạng thái. Giá trị trước giảm giá lấy từ số lượng nhân đơn giá trên dòng; giá trị sau giảm giá lấy từ số tiền dòng đã xác định ở nguồn. Giá niêm yết hiện hành của hạng vé không dùng để tính lại giao dịch quá khứ.

Trường sold_quantity và sales_amount chỉ nhận số lượng và tiền khi đơn ở trạng thái PAID, các trạng thái còn lại đóng góp bằng không. Cách thiết kế giữ được các dòng đơn chưa thanh toán để phân tích trạng thái, đồng thời không cộng chúng vào chỉ tiêu vé đã bán. Vì vậy, số dòng fact không bằng số vé bán và cũng không bằng số đơn.

Một đơn cũ chuyển sang PAID làm thay đổi nhiều dòng fact liên quan dù chi tiết không đổi. Mô hình tạo lại ứng viên từ các quan hệ hiện hành rồi so sánh nội dung, thay vì chỉ kiểm tra thời gian cập nhật của order_items. Đây là điểm quan trọng khi áp dụng tăng dần cho dữ liệu có phụ thuộc liên bảng.

### Các bảng chiều
dim_event lưu thuộc tính hiện hành của sự kiện; dim_ticket_type lưu thông tin hiện hành của hạng vé. dim_channel và dim_status chuẩn hóa các nhóm giá trị phục vụ lọc. dim_date tạo lịch theo khoảng ngày đơn đang có. Năm bảng này dùng kiểu tạo bảng lại theo cấu hình hiện tại.

Các bảng chiều chưa áp dụng cơ chế lịch sử loại hai. Nếu tên hoặc nhóm sự kiện thay đổi, báo cáo sẽ dùng thuộc tính hiện hành cho những giao dịch liên quan. Thiết kế phù hợp câu hỏi đang xét, nhưng không trả lời chính xác câu hỏi “tại thời điểm mua, sự kiện được phân loại thế nào” nếu thuộc tính đó đã thay đổi và không còn lịch sử.

### Bảng tổng hợp và công bố kết quả
agg_daily_sales nhóm theo ngày đặt đơn, sự kiện và kênh. Bảng này tổng hợp số vé, giá trị và số đơn phân biệt trong từng nhóm. Không có chiều hạng vé hoặc trạng thái trong khóa nhóm, nên việc dùng bảng tổng hợp cho câu hỏi chi tiết cần được giới hạn theo đúng cấu trúc.

Gold cập nhật theo từng mô hình, chưa công bố toàn bộ như một phiên bản nguyên tử. Trong một khoảng ngắn, bảng chiều có thể đã mới còn fact chưa xong. Báo cáo nên làm mới sau khi công việc cuối hoàn thành và tránh trùng cửa sổ ghi mới. Một phiên bản công bố chung là hướng cải tiến cần thiết nếu mở rộng số người dùng hoặc lịch chạy.

## Thiết kế đánh giá
Đánh giá được chia thành kiểm tra cấu trúc, đối chiếu nội dung, thử hành vi cập nhật và đo hiệu năng. Kiểm tra cấu trúc xác nhận khóa, cột và quan hệ. Đối chiếu nội dung kiểm tra từng khóa và các giá trị quan trọng. Thử hành vi cập nhật quan sát trước và sau một thay đổi có kiểm soát. Đo hiệu năng ghi thời gian và tài nguyên trong điều kiện xác định.

Một số lượng bằng nhau giữa nguồn và đích chỉ là bằng chứng bước đầu. Một dòng bị thiếu có thể được bù bởi một dòng trùng. Tổng tiền bằng nhau cũng có thể che hai sai số trái dấu. Vì vậy, nghiệm thu cần kết hợp nhiều lớp kiểm tra, không dùng một phép đếm duy nhất làm kết luận toàn bộ hệ thống.

Đối với dữ liệu mô phỏng, có thể thiết kế một tập nhỏ với kết quả tính tay để đối chiếu thuật toán, sau đó dùng tập lớn để đo khả năng xử lý. Hai tập phục vụ hai mục đích khác nhau. Báo cáo không tự gán trạng thái đạt cho những ca chưa có nhật ký và kết quả truy vấn tương ứng.

# Triển khai và đánh giá
## Môi trường và cấu trúc mã nguồn
### Thành phần triển khai
Kho đích trong cấu hình sử dụng PostgreSQL 17.9; Airflow sử dụng bộ thực thi LocalExecutor và múi giờ Asia/Ho_Chi_Minh. Các dịch vụ web, lập lịch và cơ sở dữ liệu siêu dữ liệu của Airflow có trách nhiệm riêng. Airbyte cục bộ được quản lý bằng abctl, nên vòng đời của nó không đồng nhất với nhóm dịch vụ trong tệp compose của dự án.

Docker Compose mô tả các dịch vụ, mạng và vùng lưu trữ để tổ chức ứng dụng nhiều thành phần [7]. Trong dự án, các thư mục mã nguồn được gắn vào vùng thực thi và các ổ dữ liệu được giữ tách khỏi vòng đời một container. Khởi động lại container vì thế khác với xóa volume: thao tác thứ hai có thể làm mất trạng thái và dữ liệu đã lưu.

Từ máy Windows, cổng kho phân tích là 5433, giao diện Airflow là 8080 và giao diện Airbyte là 8000 theo cấu hình cục bộ. Bên trong mạng container, dịch vụ kho dùng cổng PostgreSQL nội bộ. Sự khác nhau giữa địa chỉ từ máy chủ và từ container cần được hiểu rõ để tránh cho rằng mọi nơi đều truy cập cùng một localhost.

### Tổ chức thư mục
Thư mục Source/SqlServer chứa cấu trúc nguồn và mã sinh, nạp dữ liệu. Airflow/dags chia công việc theo Bronze, Silver và Gold; Airflow/plugins chứa phần dùng chung như bộ cảm biến và thao tác chạy dbt. Dbt/Dbt-Postgres chứa mô hình SQL, khai báo nguồn, macro và cấu hình. Cách tổ chức này đặt mã gần với trách nhiệm nghiệp vụ tương ứng.

PowerBI chứa tệp báo cáo tiêu thụ Gold. Reports chứa tài liệu thuyết trình và báo cáo. Runtime phục vụ nhật ký hoặc sản phẩm thực thi, không phải nơi nên sửa mô hình gốc. Khi đọc một câu SQL đã biên dịch trong Runtime, người thực hiện cần lần ngược về tệp mô hình để chỉnh sửa lâu dài.

@TABLE folders

### Cấu hình và thông tin nhạy cảm
Thông tin máy chủ, tài khoản và bí mật kết nối cần được tách khỏi đoạn SQL hoặc nội dung slide. Tài liệu chỉ ghi tên biến cần cấu hình và vị trí sử dụng, không đưa mật khẩu thực tế vào phụ lục. Khi chia sẻ kho mã hoặc ảnh nhật ký, phải kiểm tra cả chuỗi kết nối và phản hồi API, vì chúng có thể chứa thông tin nhạy cảm ngoài dự kiến.

Tài khoản đọc báo cáo chỉ cần quyền phù hợp với dữ liệu công bố. Tài khoản nạp Bronze và tài khoản biến đổi có trách nhiệm khác, nên việc phân quyền cần theo phạm vi ghi thực tế. Đây là nguyên tắc vận hành cần duy trì; báo cáo không coi sự tồn tại của các tên tài khoản trong tệp cấu hình là bằng chứng đã kiểm toán đầy đủ quyền truy cập.

## Triển khai bộ sinh và nạp dữ liệu
### Sinh theo năm và giá trị khởi tạo
append_history.py nhận khoảng năm, số đơn mỗi năm, giá trị khởi tạo, máy chủ và tên cơ sở dữ liệu. Khi không có --load, chương trình sinh dữ liệu và lưu thông tin lô mà chưa ghi vào SQL Server. Khi có --load, chương trình gọi hàm nạp. Tách hai chế độ giúp kiểm tra tham số trước khi thực hiện thay đổi dữ liệu.

Trong phiên bản khảo sát, chương trình hỗ trợ các năm lịch sử từ 2020 đến 2025. Tham số --orders-per-year ghi đè số lượng mặc định của từng năm. Giá trị khởi tạo được kết hợp với năm khi gọi bộ sinh để tạo những tập khác nhau. Người vận hành cần giữ lại cùng bộ tham số nếu muốn tái hiện tình huống, thay vì đổi giá trị khởi tạo mỗi lần gặp lỗi.

### Cấp khóa và giao dịch nạp
Trước khi ghi, chương trình lấy khóa ứng dụng và khóa bảng trong giao dịch để tính khoảng khóa hiện có. Mỗi khóa mới được dịch theo khoảng của đúng bảng, còn các khóa tham chiếu dịch theo bảng đích tương ứng. Nếu chỉ dịch khóa chính mà quên khóa ngoại, cấu trúc liên bảng sẽ sai hoặc ràng buộc nguồn sẽ chặn lô nạp.

Chương trình ghi theo các nhóm bản ghi và chỉ xác nhận giao dịch sau khi hoàn thành năm bảng của năm đang xử lý. Khi có ngoại lệ, giao dịch được hoàn tác. Phạm vi nguyên tử là một năm trong một lần gọi hàm nạp, không phải toàn bộ nhiều năm truyền trong một lệnh. Nếu năm đầu thành công còn năm sau lỗi, kết quả năm đầu vẫn có thể đã lưu.

Khóa ứng dụng và khóa bảng giúp hạn chế hai tiến trình tự cấp cùng khoảng định danh, nhưng cũng có thể làm tiến trình khác chờ. Vì đây là bộ nạp phục vụ môi trường thử, cách khóa mạnh dễ kiểm soát hơn. Không nên suy ra đây là cơ chế nhập liệu phù hợp cho hệ thống bán vé đang phục vụ người mua đồng thời mà chưa đánh giá tác động.

### Phát hiện lô đã có
Mã lô sử dụng năm và giá trị khởi tạo trong tiền tố. Nếu phát hiện lô tồn tại, chương trình so sánh số sự kiện và số đơn với tập vừa sinh. Khi số lượng khác, nó dừng bằng lỗi để tránh dùng lại cùng định danh với cấu hình khác. Khi số lượng phù hợp, trạng thái already_loaded cho biết chương trình bỏ qua nạp lại theo điều kiện kiểm tra hiện tại.

Kiểm tra số lượng này chưa so sánh toàn bộ nội dung của lô. Hai tập có cùng số sự kiện và số đơn vẫn có thể khác dữ liệu nếu bộ sinh đã sửa. Vì vậy, “đã có” trong chương trình có ý nghĩa giới hạn, không phải chứng minh hai tập giống nhau theo từng cột. Hướng cải tiến là lưu phiên bản bộ sinh và dấu kiểm tra nội dung hoặc một hồ sơ lô có ràng buộc rõ hơn.

### Nhật ký lô và khả năng truy vết
Tệp thông tin lô ghi năm, tham số, số dòng từng bảng và một số tổng hợp kiểm tra. Trạng thái loaded thể hiện hàm nạp đã xác nhận giao dịch, generated_only thể hiện chưa nạp, còn already_loaded thể hiện nhánh bỏ qua. Việc nhìn thấy dòng “đang sinh dữ liệu” chưa đủ để kết luận đã ghi thành công.

Tệp thông tin được ghi sau bước xử lý lô. Do đó, nếu ghi cơ sở dữ liệu thành công nhưng quá trình lưu tệp gặp lỗi, không nên nạp một lô mới chỉ vì không thấy tệp. Cần kiểm tra dữ liệu nguồn theo định danh lô. Đây là ví dụ cho sự khác nhau giữa xác nhận dữ liệu và xác nhận nhật ký ngoài cơ sở dữ liệu.

## Triển khai đồng bộ Bronze
### Định danh kết nối và công việc
Airbyte phân biệt không gian làm việc, kết nối và từng lần chạy. Định danh kết nối xác định tuyến nguồn tới đích; mã công việc xác định một lần thực thi cụ thể. Liên kết giao diện chứa mã không gian làm việc không thể dùng thay cho mã kết nối khi gửi yêu cầu đồng bộ.

Dự án lưu các định danh kết nối trong phần cấu hình dùng chung, còn mỗi DAG chọn một giá trị theo tên nghiệp vụ. Lịch và dag_id nằm trong tệp DAG để người vận hành dễ sửa. Thiết kế này giảm việc phải mở một tệp cấu hình lớn chỉ để thay giờ chạy, đồng thời tránh sao chép cùng một định danh ở quá nhiều vị trí.

### Gửi yêu cầu và theo dõi trạng thái
Tác vụ đầu gọi chức năng khởi tạo đồng bộ và trả lại mã công việc. Tác vụ thứ hai nhận mã đó để kiểm tra trạng thái. Nếu công việc đang chạy, tác vụ chờ tiếp; nếu thành công, nó kết thúc thành công; nếu thất bại hoặc vượt giới hạn, luồng không phát tín hiệu hoàn thành tương ứng.

Chế độ reschedule cho phép tác vụ chờ nhường tài nguyên thực thi giữa các lần kiểm tra. Khoảng kiểm tra là sự đánh đổi giữa độ trễ nhận biết và số lần gọi API. Việc giảm khoảng kiểm tra không làm Airbyte đồng bộ nhanh hơn, mà chỉ có thể rút ngắn thời gian từ lúc công việc xong đến lúc Airflow nhận biết.

### Lịch và rủi ro gửi lặp
Lịch cron được khai báo tại từng DAG Bronze với múi giờ kinh doanh đã chọn. DAG Silver và Gold không cần đoán giờ kết thúc của Bronze bằng cách chạy chậm hơn một số phút cố định. Chúng dùng tín hiệu phụ thuộc để tránh giả định thời lượng đồng bộ luôn ổn định.

Tác vụ gửi yêu cầu không tự thử lại POST theo cấu hình đang dùng. Nếu máy chủ đã nhận yêu cầu nhưng đường mạng mất phản hồi, gửi lại có thể tạo thêm công việc. Khi gặp lỗi loại này, người vận hành cần xem lịch sử Airbyte trước khi kích hoạt thủ công. Thiết kế chưa có cơ chế chống gửi lặp bằng khóa yêu cầu ở cấp ứng dụng.

## Triển khai biến đổi Silver
### Khai báo nguồn và ánh xạ bảng
Tệp sources.yml mô tả các bảng Bronze để mô hình gọi qua source(). Mô hình silver_events.sql có thể tạo bảng đích mang tên events trong schema silver nhờ cấu hình tên xuất bản. Tên tệp mô hình và tên bảng cuối vì vậy không nhất thiết giống nhau. Phụ lục ánh xạ giúp tra cứu đường dẫn, đầu vào và đầu ra tương ứng.

Các mô hình dùng ref() khi phụ thuộc một mô hình dbt khác. Cơ chế tham chiếu này cho phép dbt biết quan hệ giữa các mô hình, nhưng câu lệnh chọn một mô hình không mặc nhiên có nghĩa mọi công việc ngoài dbt đã chạy. Điều kiện Airbyte hoàn tất vẫn thuộc phần điều phối trước đó.

### Quy tắc kiểu và giá trị rỗng
Các cột số định danh được ép về kiểu khóa thống nhất; chuỗi rỗng sau khi loại khoảng trắng được chuyển thành giá trị rỗng phù hợp. Trạng thái được chuẩn hóa chữ hoa để so sánh với tập giá trị cho phép. Cách xử lý được viết rõ trên từng trường, tránh một phép chuyển đổi tổng quát làm thay đổi những chuỗi vốn phân biệt chữ hoa chữ thường.

Một giá trị không chuyển được sang kiểu số có thể làm câu lệnh thất bại. Đây là hành vi cần xem xét theo yêu cầu: dừng cả lô để bảo vệ tính đúng, hay tách bản ghi lỗi vào vùng cách ly. Bản triển khai hiện tại ưu tiên khai báo hợp đồng và phát hiện lỗi, chưa có luồng cách ly dữ liệu hoàn chỉnh để tiếp tục nạp phần hợp lệ.

### Mã lõi khử trùng
Đoạn mã rút gọn dưới đây thể hiện thứ tự chọn dòng của mô hình sự kiện. Tập hashed đã có dữ liệu chuẩn hóa và dấu vân tay. Các mô hình còn lại áp dụng cùng nguyên tắc với khóa nghiệp vụ tương ứng. Giữ đoạn mã ngắn giúp nhìn rõ quyết định thuật toán thay vì đọc toàn bộ danh sách cột.

@CODE dedup

Điểm cần kiểm tra là khóa chia nhóm và cách xử lý thời gian rỗng. Cấu hình nulls last làm bản ghi có thời gian xác định được ưu tiên trong thứ tự giảm dần. Tuy nhiên, một thời gian nguồn sai nhưng có giá trị vẫn có thể được chọn. Vì thế, kiểm tra miền thời gian hợp lệ là vấn đề chất lượng riêng, không tự được giải quyết bởi hàm xếp hạng.

### Mã lõi phát hiện thay đổi
Macro incremental_changes tạo nhánh chọn các dòng mới, khác nội dung hoặc cần khôi phục. Điều kiện is distinct from giúp so sánh theo cách có xét giá trị rỗng trong SQL. Đoạn dưới minh họa logic sau khi thay tham số bằng khóa sự kiện; đó là diễn giải ngắn của macro, không phải một tệp hoàn chỉnh để chạy độc lập.

@CODE changed

Sau nhánh này, macro thêm các dòng đang hoạt động ở đích nhưng không xuất hiện trong ứng viên và gắn cờ xóa. Khi bảng đích chưa tồn tại, mô hình đi theo đường nạp ban đầu. Khi cần thay cấu trúc lớn, cờ tạo lại toàn bộ có thể được dùng có chủ ý; nó không phải chế độ mặc định cho mọi lần chạy.

### Hợp đồng và kiểm tra khai báo
Khai báo YAML mô tả kiểu cột và các kiểm tra dữ liệu. Hợp đồng cấu trúc và kiểm tra dữ liệu phục vụ mục tiêu khác nhau: hợp đồng kiểm soát hình dạng đầu ra, còn kiểm tra dữ liệu đánh giá các điều kiện trên bản ghi. Chạy dbt run không đồng nghĩa mọi kiểm tra bằng dbt test đã được thực hiện.

Một khóa unique_key dùng cho cập nhật cũng không tự thay thế mọi phép kiểm tra tính duy nhất của đầu vào. Dữ liệu ứng viên vẫn cần khử trùng và đối chiếu. Khi trình bày kết quả, phải phân biệt “đã khai báo kiểm tra” với “đã chạy và có kết quả đạt”. Báo cáo chỉ sử dụng loại kết luận thứ hai khi có bằng chứng tương ứng.

## Triển khai mô hình Gold
### Phép nối và tránh nhân bản
Ứng viên fact được hình thành từ chi tiết và đơn đang hoạt động. Các khóa chiều bổ sung cách phân loại kênh và trạng thái. Không có phép nối trực tiếp với từng dòng payments trong phép tính doanh số. Điều này loại bỏ một nguồn nhân bản phổ biến do quan hệ một đơn có nhiều lần thử thanh toán.

Ví dụ minh họa, một đơn có hai dòng với giá trị sau giảm lần lượt 200.000 và 300.000 đồng. Nếu đơn có ba lần thử thanh toán, phép nối không phù hợp có thể tạo sáu dòng và tổng 1.500.000 đồng. Mô hình ở mức dòng đơn phải giữ tổng 500.000 đồng khi trạng thái đáp ứng quy tắc bán. Các số trong ví dụ dùng để giải thích phép nối, không phải giao dịch được quan sát.

### Định nghĩa đại lượng
quantity mô tả số vé được đặt trên dòng, còn sold_quantity chỉ ghi nhận số đó khi đơn PAID. Tương tự, net_amount mô tả giá trị dòng và sales_amount mô tả phần đóng góp vào giá trị vé đã thanh toán theo trạng thái đơn. Việc giữ hai nhóm trường giúp phân biệt lượng đặt với lượng đã bán theo định nghĩa hiện tại.

Ngày phân tích lấy từ ordered_at. Nếu đơn được thanh toán sau ngày đặt, kết quả vẫn quy về ngày đặt. Đây là lựa chọn mô hình, không phải dữ liệu tiền về đúng ngày thanh toán. Một báo cáo dòng tiền cần bảng đo lường và quy tắc thời gian khác, có xét hoàn tiền hoặc quyết toán nếu những nghiệp vụ đó được bổ sung.

### Xóa tại Gold và cập nhật bảng chiều
Các dòng fact đánh dấu xóa được loại bằng bước xử lý sau mô hình. Trong khi Silver giữ dấu vết khóa đã biến mất, Gold công bố tập phục vụ phân tích hiện hành. Hai hành vi không mâu thuẫn vì chúng phục vụ trách nhiệm khác nhau. Muốn phân tích đầy đủ lịch sử xóa phải thiết kế thêm dữ liệu lịch sử riêng.

Bảng chiều và bảng tổng hợp tạo lại theo cấu hình table. Vì vậy, cách mô tả chính xác là năm mô hình Silver và fact dùng cập nhật tăng dần, còn các đối tượng Gold khác được xây lại. Gọi toàn bộ dự án “tăng dần hoàn toàn” sẽ che mất một phần chi phí và hành vi thực thi.

## Điều phối các tầng
### Phụ thuộc theo nghiệp vụ
Mỗi DAG Silver đăng ký Dataset Bronze của bảng tương ứng. Sau khi lệnh dbt thành công, tác vụ phát Dataset Silver. Các DAG chiều Gold chờ tập Dataset Silver theo khai báo; fact chờ các bảng chiều; bảng tổng hợp ngày chờ fact. Cấu trúc này giúp giao diện điều phối thể hiện những điểm chờ rõ ràng.

Một DAG tổng hợp và DAG riêng lẻ có thể cùng tác động lên các mô hình tương tự. Người vận hành phải chọn đường chạy phù hợp cho một lượt thay vì kích hoạt đồng thời mọi DAG có tên liên quan. Giới hạn số lượt chạy trong một DAG không ngăn hai DAG khác nhau ghi cùng bảng.

### Liên kết đến mã biến đổi
Tệp DAG ghi đường dẫn mô hình trong mô tả và trong câu lệnh chọn dbt. Nhờ đó, khi tác vụ lỗi, người đọc có thể mở đúng tệp SQL thay vì tìm trong một hàm chung quá lớn. Các phần dùng chung vẫn được tách ở lớp thao tác để tránh lặp cơ chế môi trường và xử lý kết quả.

@CODE dag

Đoạn mã rút gọn cho thấy lịch dựa vào đầu vào, lệnh chọn mô hình và tín hiệu đầu ra. Tham số lịch nằm ở tầng điều phối; phép ref() trong SQL vẫn xác định quan hệ dữ liệu. Hai cơ chế cần khớp với nhau, đặc biệt khi thêm mô hình mới hoặc đổi một phụ thuộc hiện có.

### Giới hạn của tín hiệu nhiều đầu vào
Giả sử bảng sự kiện hoàn thành ở lượt trước còn bảng đơn hoàn thành ở lượt mới. Bộ lập lịch có thể có đủ tín hiệu để chạy một DAG tiêu thụ nhiều đầu vào, nhưng các dữ liệu đó chưa chắc thuộc một bản chụp nghiệp vụ chung. Tình huống này không thể được giải quyết chỉ bằng cách đổi tên Dataset cho giống tên tầng.

Một thiết kế mở rộng cần gắn mã lô hoặc phiên bản công bố và kiểm tra sự tương thích trước khi chạy tầng sau. Các dấu thời gian đơn lẻ chỉ hỗ trợ quan sát; chúng chưa chắc xác định ranh giới giao dịch nguồn. Do vậy, hướng nâng cấp phải bắt đầu từ định nghĩa “cùng lô” chứ không chỉ bổ sung một cột batch_id mà không có quy tắc.

## Minh họa đầu ra bằng Power BI
Power BI sử dụng các bảng Gold với quan hệ từ bảng chiều đến bảng đo lường. Các khóa định danh được dùng để nối và lọc, không phải đại lượng cần cộng. Những cột kỹ thuật như dấu vân tay và thời điểm nạp có thể ẩn khỏi giao diện người xem thông thường, trong khi vẫn giữ để kiểm tra khi cần.

Tệp báo cáo có bốn trang: Tổng quan, Hiệu quả các sự kiện, Chi tiết sự kiện, Kênh bán và trạng thái đơn. Vai trò của chúng là chứng minh cấu trúc Gold sử dụng được cho các câu hỏi khác nhau. Đồ án không coi số trang hoặc số biểu đồ là chỉ tiêu chính để đánh giá chất lượng hệ thống dữ liệu.

@FIG bi

Các đại lượng cần định nghĩa nhất quán: giá trị vé là tổng sales_amount, số vé là tổng sold_quantity, số đơn là số order_id phân biệt. Tỷ lệ đơn thanh toán lấy số đơn PAID chia số đơn trong cùng ngữ cảnh lọc. Không gọi đại lượng này là tỷ lệ chuyển đổi người truy cập vì dữ liệu không có phiên truy cập hay lượt xem.

Nếu sử dụng cả fact chi tiết và bảng tổng hợp, mỗi biểu đồ phải chọn nguồn phù hợp. Cộng hai nguồn với nhau sẽ đếm cùng hoạt động ở hai mức. Phân tích theo hạng vé phải dùng nguồn giữ hạng vé. Việc thử một bộ lọc sự kiện rồi đối chiếu với SQL Gold là cách kiểm tra đầu ra có ý nghĩa hơn chỉ quan sát biểu đồ hiển thị đẹp.

## Kết quả quan sát có bằng chứng
### Phạm vi của lần khảo sát
Các số liệu trong mục này thuộc lần truy vấn đọc ngày 04 tháng 10 năm 2026. Chúng không được trình bày như số lượng trực tiếp của ngày biên soạn lại báo cáo, vì sau đó có thể đã nạp thêm lô lịch sử. Quan sát gồm số lượng ở nguồn, một số bảng đích và tổng hợp trạng thái tại Gold. Không có thao tác tạo lỗi hoặc thay đổi có kiểm soát được suy diễn thành kết quả đã chạy.

Đọc mã nguồn cho thấy cách xử lý được cài đặt; truy vấn số lượng cho thấy trạng thái dữ liệu tại một thời điểm. Hai loại bằng chứng bổ sung cho nhau nhưng không thay thế nhau. Một nhánh mã tồn tại chưa chứng minh đã đi qua nhánh đó trong thực nghiệm, còn một bảng có dữ liệu chưa chứng minh mọi trường hợp cập nhật đều đúng.

### Quy mô dữ liệu
Nguồn tại thời điểm khảo sát có 360 sự kiện, 1.080 hạng vé, 357.000 đơn, 399.696 chi tiết đơn và 420.792 lần thử thanh toán. Số thanh toán lớn hơn số đơn phù hợp với mô hình nhiều lần thử. Số chi tiết lớn hơn số đơn phản ánh việc có đơn chứa nhiều dòng, không có nghĩa mỗi dòng là một đơn độc lập.

@TABLE counts

Theo ngày đặt đơn, số đơn phân bố qua giai đoạn 2020–2026. Những con số này phản ánh các lô sinh và phạm vi ngày của nguồn. Chúng không được dùng để kết luận mức tăng trưởng kinh doanh, tác động của dịch bệnh hoặc thay đổi thị hiếu. Việc gắn rõ nguồn tổng hợp giúp giới hạn cách diễn giải số liệu.

@TABLE years

### Đối chiếu nguồn và đích
Trong lần đọc, Bronze orders và Silver orders cùng có 357.000 dòng; fact_ticket_sales có 399.696 dòng, bằng số chi tiết nguồn được ghi nhận. Sự tương ứng này phù hợp kỳ vọng của mô hình hiện tại trong phạm vi quan sát. Báo cáo không mở rộng kết luận thành “mọi dữ liệu đã đối chiếu chính xác” vì chưa có kết quả so sánh toàn bộ khóa và nội dung.

Đối chiếu sâu hơn cần loại rõ các dòng xóa mềm khi so sánh và xem xét các quy tắc lọc hợp lệ. Nếu nguồn có bản ghi không còn hoạt động, so sánh tổng số dòng vật lý của Silver với nguồn có thể sai ý nghĩa. Tập so sánh phải được định nghĩa trước, tránh thay điều kiện sau khi nhìn thấy chênh lệch để làm hai số bằng nhau.

### Các đại lượng tại Gold
Gold ghi nhận 293.274 đơn PAID, 47.059 đơn EXPIRED, 16.657 đơn CANCELLED và 10 đơn PENDING. Tổng các nhóm bằng 357.000 đơn. Chỉ nhóm PAID đóng góp 636.959 vé và giá trị 188.306.020.500 đồng trong truy vấn đã đọc. Tỷ lệ đơn PAID trên tổng số đơn xấp xỉ 82,15 phần trăm.

@TABLE status

Những giá trị này là chỉ tiêu của dữ liệu mô phỏng theo trạng thái hiện hành. Chúng chưa trừ hoàn tiền, phí đối tác hoặc chi phí tổ chức. Vì vậy, không gọi chúng là lợi nhuận hoặc số tiền doanh nghiệp đã quyết toán. Sự chính xác của thuật ngữ là một phần của chất lượng dữ liệu công bố.

## Kịch bản kiểm thử cần hoàn tất
### Chạy lại và thêm mới
Ca chạy lại sử dụng cùng một bản chụp ổn định. Trước và sau lượt chạy, cần lưu tập khóa, dấu vân tay và chỉ tiêu. Kết quả mong đợi là không phát sinh khóa dư, không tăng số vé hay giá trị vì chạy lặp. Việc DAG thành công hai lần chỉ xác nhận thực thi, chưa xác nhận tính lặp lại an toàn về dữ liệu.

Ca thêm mới dùng một đơn hợp lệ có các dòng chi tiết và tham chiếu danh mục tồn tại. Nếu đơn chưa PAID, số đơn có thể tăng nhưng chỉ tiêu vé đã bán chưa tăng. Nếu đơn PAID, mức tăng kỳ vọng được tính từ số lượng và giá trị của chính các dòng được thêm. Ca này cần ghi rõ trạng thái để không dùng một kỳ vọng cho mọi đơn.

### Sửa dữ liệu cũ
Ca quan trọng là đổi trạng thái một đơn cũ mà không sửa chi tiết. Sau đồng bộ và biến đổi, các dòng fact liên quan phải thay đổi phần số vé và giá trị theo quy tắc trạng thái. Ngày phân tích vẫn là ngày đặt đơn. Nếu kết quả chỉ thay khi sửa thêm thời gian của chi tiết, logic phụ thuộc đang bỏ sót thay đổi từ bảng đơn.

Ca sửa số tiền dòng cần kiểm tra cả dữ liệu chuẩn hóa và tổng hợp. Đồng thời phải giữ các ràng buộc nguồn hợp lệ, tránh tạo một đơn có tổng tiền không khớp rồi quy lỗi cho tầng đích. Mọi thay đổi thử nghiệm nên thực hiện trên môi trường sao chép hoặc có phương án hoàn tác rõ ràng.

### Xóa và khôi phục
Ca xóa cần lấy một khóa đã tồn tại, tạo bản chụp mới đầy đủ nhưng không còn khóa đó, rồi kiểm tra cờ xóa ở Silver và việc loại khỏi tập công bố Gold. Không dùng một lần đồng bộ chỉ lấy một phần dữ liệu để giả lập xóa, vì điều đó vi phạm giả thiết của thuật toán và có thể ảnh hưởng hàng loạt khóa khác.

Ca khôi phục đưa cùng khóa trở lại với dữ liệu hợp lệ. Kết quả mong đợi là khóa hoạt động lại mà không tạo bản sao. Nếu nội dung giống trước khi xóa, nhánh khôi phục vẫn cần chạy vì cờ đích đang ở trạng thái xóa. Đây là lý do điều kiện cập nhật không chỉ so sánh dấu vân tay.

### Lỗi đồng bộ và lỗi biến đổi
Khi Airbyte thất bại, cần xác nhận bộ cảm biến kết thúc theo nhánh lỗi và không phát tín hiệu thành công cho công việc đó. Khi dbt lỗi, cần kiểm tra tác vụ và các Dataset đầu ra tương ứng. Đồng thời phải xem tín hiệu cũ đang chờ, vì các sự kiện tồn đọng có thể ảnh hưởng lịch của tầng sau.

Một ca lỗi hữu ích cần lưu thời điểm, mã công việc, mã lượt chạy DAG và nhật ký liên quan. Ảnh giao diện chỉ có màu đỏ hoặc xanh chưa đủ để giải thích nguyên nhân và tác động. Hồ sơ ca thử nên gắn với phiên bản mã nguồn để tránh dùng bằng chứng của phiên bản cũ cho một logic đã thay đổi.

@TABLE tests

## Phương pháp đo hiệu năng
### Điều kiện so sánh
So sánh cần giữ cùng phần cứng, cấu hình cơ sở dữ liệu, số luồng dbt và phạm vi dữ liệu. Hai phương án phải tạo cùng kết quả nghiệp vụ. Nếu một phương án bỏ qua xóa hoặc không cập nhật đơn cũ, thời gian ngắn hơn không chứng minh nó tốt hơn cho yêu cầu đang xét.

Có thể chuẩn bị ba trạng thái đầu vào: không đổi, thay đổi một phần nhỏ và thay đổi nhiều. Với mỗi trạng thái, đo riêng nạp Bronze và biến đổi. Lượt khởi tạo bảng đầu tiên cũng nên tách khỏi lượt chạy tăng dần khi bảng đã tồn tại, vì chúng có công việc khác nhau. Không trộn các lượt này vào một con số trung bình mà không giải thích.

### Chỉ tiêu thu thập
Thời gian toàn tuyến bắt đầu từ lúc yêu cầu đồng bộ đến khi bảng công bố cuối hoàn thành. Thời gian dbt riêng không bao gồm chờ điều phối và nạp dữ liệu. Ngoài thời gian, số dòng thêm, sửa hoặc xóa là bằng chứng quan trọng để kiểm tra thuật toán đã chọn đúng tập thay đổi.

Nếu có điều kiện quan sát, cần ghi bộ nhớ, CPU và hoạt động đọc ghi. Mỗi cấu hình nên chạy lặp nhiều lần và báo trung vị cùng khoảng dao động, thay vì chỉ chọn lượt nhanh nhất. Trạng thái bộ nhớ đệm và tải nền của máy cũng cần ghi nhận để người đọc hiểu khác biệt giữa các lượt.

### Giới hạn kết luận hiện tại
Báo cáo chưa có bộ số đo hiệu năng đã nghiệm thu. Do đó, kết luận hiện tại chỉ là mã có cơ chế hạn chế ghi lại dòng không đổi và vẫn quét bản chụp để so sánh. Không đưa ra phần trăm tăng tốc, khả năng đáp ứng đồng thời hoặc thông lượng giả định. Bảng trong phụ lục mô tả cách ghi kết quả khi thực nghiệm hoàn tất.

Nếu đo được kết quả tăng dần chậm hơn tạo lại trong một tình huống, đó vẫn là thông tin có ích. Chi phí tính dấu vân tay, nối và cập nhật chỉ mục có thể vượt lợi ích giảm ghi. Phân tích cần giải thích bằng điều kiện dữ liệu và kế hoạch thực thi, thay vì loại bỏ kết quả không phù hợp kỳ vọng ban đầu.

### Phân tích kế hoạch thực thi
Khi truy vấn biến đổi có thời gian lớn, bước tiếp theo là xem kế hoạch thực thi thay vì lập tức tăng tài nguyên. Cần xác định chi phí tập trung ở đọc bảng, sắp xếp cho hàm cửa sổ, nối với đích hay ghi kết quả. Một chỉ mục trên khóa có thể hỗ trợ tra cứu, nhưng không loại bỏ mọi chi phí sắp xếp hoặc bảo trì khi cập nhật hàng loạt.

Phép đo có thực thi truy vấn cần được thực hiện trên môi trường thử nếu câu lệnh có khả năng ghi. Với những bước đọc tạo ứng viên, có thể bắt đầu bằng kế hoạch của câu SELECT tương ứng. Nếu thống kê cơ sở dữ liệu không phản ánh quy mô mới sau khi nạp thêm nhiều lô, bộ tối ưu có thể chọn kế hoạch không phù hợp. Hồ sơ đo cần ghi tình trạng dữ liệu và cấu hình để việc so sánh có ý nghĩa.

Đối với cập nhật tăng dần, cần xem cả thời gian tạo tập thay đổi và thời gian hợp nhất. Một tập thay đổi rất nhỏ vẫn có thể tốn nhiều thời gian để phát hiện nếu mỗi lần phải đọc toàn bộ nguồn. Kết quả đo nên diễn giải theo hai phần này. Cách trình bày đó cho thấy vì sao tiết kiệm số dòng ghi không luôn tương đương tiết kiệm tổng thời gian theo cùng tỷ lệ.

### Độ tin cậy của kết quả đánh giá
Thử nghiệm trên cùng bộ dữ liệu do người thực hiện sinh có lợi về khả năng biết trước quy tắc, nhưng có thể thiếu những lỗi xuất hiện trong dữ liệu thật. Ví dụ, bộ sinh luôn tạo mã trạng thái hợp lệ thì không kiểm tra được hành vi khi nguồn có mã ngoài danh mục. Vì vậy, một tập thử chất lượng riêng cần chủ động bao gồm giá trị rỗng, trùng khóa và quan hệ không hợp lệ trong phạm vi an toàn.

Tính đại diện của hiệu năng cũng có giới hạn. Hai tập cùng số dòng có thể khác độ rộng chuỗi, tỷ lệ lặp khóa, số nhóm và phân bố thời gian, từ đó tạo chi phí khác nhau. Chỉ tăng số đơn mỗi năm chưa mô tả đầy đủ độ khó của dữ liệu. Báo cáo thực nghiệm cần nêu cả đặc điểm tập dữ liệu bên cạnh số lượng.

Khả năng tái lập đòi hỏi giữ được đầu vào và phiên bản chương trình. Nếu mỗi lượt nạp tạo thêm dữ liệu vào cùng cơ sở dữ liệu mà không ghi lại trạng thái, lượt sau không còn cùng điều kiện với lượt trước. Một cách tổ chức phù hợp là dùng các bản sao thử nghiệm có định danh rõ và giữ nguyên nguồn trong suốt một nhóm phép đo. Đây là thiết kế đánh giá đề xuất, chưa phải cam kết rằng môi trường hiện tại đã có đầy đủ tự động hóa đó.

## Thảo luận và giới hạn
### Tính đúng đắn và độ đầy đủ
Rủi ro đáng chú ý nhất là hiểu một bản chụp thiếu thành nhiều thao tác xóa. Trạng thái thành công kỹ thuật của Airbyte chưa đủ để xác nhận phạm vi nghiệp vụ không bị đổi do cấu hình. Cần bổ sung kiểm tra số lượng bất thường, phạm vi thời gian và danh sách bảng trước khi cho phép áp dụng nhánh phát hiện xóa trong môi trường mở rộng.

Các kiểm tra độ đầy đủ cũng cần tránh quy tắc cứng thiếu căn cứ. Ví dụ, số dòng giảm không phải lúc nào cũng sai nếu nghiệp vụ có xóa hợp lệ. Ngưỡng cảnh báo nên kết hợp lịch sử, quy mô và khả năng giải thích thay đổi. Mục tiêu là yêu cầu xem xét khi bất thường, không tự sửa dữ liệu để giữ số lượng cũ.

### Nhất quán và lịch sử
Tầng Bronze chưa cố định bản chụp xuyên bảng theo một mã lô. Gold chưa công bố nguyên tử toàn bộ mô hình. Các bảng chiều giữ thuộc tính hiện hành và fact không bao gồm đầy đủ lịch sử thanh toán, hoàn tiền hoặc kiểm soát vé vào cửa. Những giới hạn này xác định loại câu hỏi hệ thống hiện trả lời được.

Lưu một cờ xóa không biến Silver thành kho lịch sử phiên bản. Giữ nhiều năm đơn hàng cũng không đồng nghĩa lưu lịch sử thay đổi của một đơn. Hai loại thời gian phải được phân biệt: thời gian nghiệp vụ của giao dịch và thời gian hiệu lực của phiên bản dữ liệu. Thiết kế lịch sử cần xác định rõ cả hai trước khi bổ sung bảng.

### Giá trị đối với chuyên ngành Khoa học máy tính
Nội dung kỹ thuật của đề tài nằm ở mô hình quan hệ, thuật toán chọn bản ghi, so sánh tập dữ liệu, kiểm soát giao dịch và điều phối công việc. Các công cụ hỗ trợ thực thi, nhưng không quyết định thay người thiết kế về mức chi tiết, ý nghĩa xóa hoặc điều kiện hoàn thành. Vì vậy, chất lượng khóa luận cần thể hiện qua lập luận và bằng chứng của các quyết định này.

Power BI là minh họa cho khả năng sử dụng đầu ra. Một biểu đồ đúng không thay thế được kiểm thử thay đổi dữ liệu; một số lượng bảng lớn cũng không chứng minh kiến trúc tốt. Phạm vi hiện tại tập trung vào một hệ thống có thể đọc mã và giải thích toàn tuyến, đồng thời nêu rõ phần cần hoàn tất trước nghiệm thu.

# Kết luận và hướng phát triển
## Kết quả đạt được
Đề tài đã tổ chức được tuyến xử lý gồm dữ liệu nguồn SQL Server, nạp bằng Airbyte, chuẩn hóa và mô hình hóa bằng dbt-postgres, điều phối qua Airflow và khai thác bằng Power BI. Mã nguồn phân chia theo trách nhiệm, các mô hình có đầu vào và đầu ra xác định, còn công việc theo tầng có tín hiệu phụ thuộc thay cho việc chỉ ước lượng giờ kết thúc.

Thiết kế dữ liệu lựa chọn chi tiết đơn làm mức đo lường, tách số lần thử thanh toán khỏi phép tính giá trị vé. Tầng Silver chuẩn hóa, xếp hạng và so sánh nội dung theo khóa. Những bản ghi biến mất hoặc quay lại được xử lý theo giả thiết bản chụp đầy đủ. Các quyết định này tạo cơ sở để giải thích vì sao một chỉ tiêu thay đổi sau một lượt xử lý.

Quan sát ngày 04 tháng 10 năm 2026 cung cấp bằng chứng về quy mô nguồn và một số kết quả đích. Số lượng tương ứng giữa đơn nguồn, Silver và chi tiết fact phù hợp kỳ vọng tại thời điểm đó. Báo cáo không dùng kết quả này để thay thế kiểm thử theo khóa, tình huống lỗi hay đo hiệu năng chưa thực hiện.

## Trả lời các câu hỏi nghiên cứu
Về phân chia trách nhiệm, đường nạp thuộc Airbyte, lưu trữ và thực thi truy vấn thuộc PostgreSQL, tổ chức biến đổi thuộc dbt và điều phối thuộc Airflow. Sự phân chia được thể hiện trong cấu trúc thư mục, tệp cấu hình và cách gọi công việc. Power BI đọc kết quả công bố thay vì tự xây dựng lại toàn bộ quy tắc nguồn.

Về xử lý thay đổi, khóa xác định đối tượng, dấu vân tay xác định khác biệt nội dung và cờ xóa hỗ trợ trạng thái biến mất hoặc khôi phục. Cơ chế này phù hợp bản chụp đầy đủ nhưng cần kiểm soát độ đầy đủ và thời điểm đọc. Về mô hình phân tích, giữ mức dòng đơn và không nối các lần thanh toán giúp tránh một nguyên nhân nhân bản doanh số.

Về đánh giá, kết hợp kiểm tra cấu trúc, đối chiếu dòng, thử thay đổi và đo tài nguyên là phương pháp phù hợp hơn một phép đếm đơn lẻ. Phần quan sát đã có mới trả lời một phần câu hỏi đánh giá. Hồ sơ thực nghiệm có kiểm soát cần hoàn thiện để kết luận mạnh hơn về khả năng chạy lại và phản ứng khi lỗi.

## Hạn chế của đề tài
Hệ thống chạy cục bộ, chưa có đánh giá tải đồng thời hay độ sẵn sàng cao. Dữ liệu mô phỏng không đại diện cho phân bố giao dịch thật. Phương pháp so sánh quét bản chụp, bảng chiều chưa lưu lịch sử phiên bản và tầng Gold chưa có cơ chế công bố chung. Đây là những giới hạn cụ thể, có thể ánh xạ thành yêu cầu cho phiên bản tiếp theo.

Việc dùng công cụ nguồn mở hoặc mã SQL có thể đọc được không loại bỏ yêu cầu kiểm thử. Cấu hình thay đổi, nguồn thiếu hoặc thao tác chạy chồng vẫn có thể gây sai. Do đó, đánh giá cuối cùng của đồ án cần dựa trên bằng chứng gắn với một phiên bản triển khai và một bộ dữ liệu xác định.

## Hướng phát triển ưu tiên
Ưu tiên đầu tiên là quản lý lô và độ đầy đủ. Mỗi lần đồng bộ cần hồ sơ gồm phạm vi bảng, số lượng, thời điểm và trạng thái. Tầng sau chỉ xử lý tổ hợp đầu vào đã được xác nhận theo quy tắc cùng lô. Cơ chế công bố Gold theo phiên bản giúp người dùng đọc một tập nhất quán hơn khi nhiều mô hình cập nhật.

Ưu tiên tiếp theo là tự động hóa các ca kiểm tra đã thiết kế, đặc biệt đổi trạng thái đơn cũ, xóa và khôi phục. Kết quả cần lưu theo phiên bản mã cùng nhật ký. Sau khi có nền tảng kiểm chứng, mới tiến hành so sánh hiệu năng và xác định điểm nghẽn thực tế để lựa chọn cải tiến có căn cứ.

CDC, bảng chiều lưu lịch sử và bảng đo lường thanh toán có thể bổ sung khi yêu cầu nghiệp vụ cần đến. Mỗi hướng đòi hỏi thay đổi giả thiết: CDC cần sự kiện xóa và thứ tự; lịch sử chiều cần khoảng hiệu lực; thanh toán cần phân biệt lần thử, giao dịch thành công và hoàn tiền. Mở rộng nên xuất phát từ câu hỏi dữ liệu cụ thể thay vì chỉ tăng số thành phần công nghệ.
