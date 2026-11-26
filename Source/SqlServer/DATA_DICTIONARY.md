# Từ điển dữ liệu nguồn

Tất cả tên, số tiền, ngày và mã trong dataset là giả lập. Giá trị tiền là VND nguyên đồng.
Mốc snapshot: 01/09/2026 00:00:00, múi giờ UTC+07. Không lưu khách hàng.

## events — một sự kiện, một suất diễn

| Cột | Ý nghĩa |
|---|---|
| event_id / event_code | Khóa số / mã nghiệp vụ SYN-E... duy nhất |
| event_name | Tên chương trình mô phỏng |
| category | CONCERT, ACOUSTIC, THEATRE, WORKSHOP |
| organizer_name | Ban tổ chức giả lập; gộp vào sự kiện trong phạm vi đơn giản |
| venue_name / province | Địa điểm giả lập / tỉnh thành |
| capacity | Sức chứa bán vé mô phỏng, bằng tổng quota ba hạng vé |
| starts_at / ends_at | Bắt đầu và kết thúc diễn |
| sales_start_at / sales_end_at | Cửa sổ bán vé |
| event_status | COMPLETED hoặc ON_SALE tại mốc snapshot |
| created_at / updated_at | Mốc tạo và lần cập nhật cuối của bản ghi |

## ticket_types — hạng vé theo sự kiện

| Cột | Ý nghĩa |
|---|---|
| ticket_type_id | Khóa chính |
| event_id | Sự kiện sở hữu hạng vé |
| ticket_type_code / ticket_type_name | STANDARD, PREMIUM, VIP / tên tiếng Việt |
| list_price | Giá niêm yết; không thay cho giá đã chốt ở order_items |
| sale_quota | Số vé thương mại cho phép bán |
| created_at / updated_at | Phục vụ truy vết và trích xuất thay đổi |

## orders — đơn đặt vé

| Cột | Ý nghĩa |
|---|---|
| order_id / order_code | Khóa chính / mã nghiệp vụ duy nhất |
| event_id | Mỗi đơn chỉ mua vé một sự kiện |
| ordered_at / expires_at | Thời điểm đặt / hết thời hạn thanh toán (15 phút) |
| sales_channel | WEB hoặc APP |
| order_status | PAID, EXPIRED, CANCELLED, PENDING |
| subtotal_amount | Tổng quantity × unit_price của các dòng |
| discount_amount | Tổng giảm giá của các dòng |
| total_amount | subtotal_amount − discount_amount |
| currency | VND |
| created_at / updated_at | Tạo đơn / thời điểm ghi nhận trạng thái hiện tại |

## order_items — chi tiết loại vé được đặt

| Cột | Ý nghĩa |
|---|---|
| order_item_id | Khóa chính; một dòng cho một hạng vé trong đơn |
| order_id | Đơn sở hữu dòng |
| event_id | Dùng khóa ngoại ghép để bảo đảm đơn và hạng vé cùng sự kiện |
| ticket_type_id | Hạng vé |
| quantity | Số vé, 1–6 mỗi dòng |
| unit_price | Đơn giá niêm yết tại thời điểm mua |
| discount_amount | Tổng giảm giá của cả dòng, không phải giảm trên một vé |
| line_amount | quantity × unit_price − discount_amount |
| created_at / updated_at | Dòng không thay đổi trong snapshot này; hai mốc bằng nhau |

## payments — từng lần thử thanh toán

| Cột | Ý nghĩa |
|---|---|
| payment_id | Khóa chính |
| order_id | Đơn cần thanh toán; một đơn có thể có nhiều lần thử |
| merchant_transaction_id | Mã giao dịch nội bộ duy nhất; khóa đối chiếu với đối tác |
| partner_transaction_id | Mã đối tác; có thể NULL khi đang chờ |
| payment_partner | PARTNER_SIM; chỉ một đối tác giả lập |
| payment_method | WALLET, DOMESTIC_CARD, QR_BANK |
| payment_amount | Số tiền yêu cầu cho lần thử, bằng total_amount của đơn |
| currency | VND |
| payment_status | SUCCESS, FAILED, PENDING |
| failure_reason | TIMEOUT, USER_ABORT, BANK_DECLINED hoặc NULL |
| initiated_at | Lúc bắt đầu thử thanh toán |
| completed_at | Lúc nhận kết quả, NULL nếu đang chờ |
| paid_at | Lúc thành công; FAILED/PENDING phải NULL |
| created_at / updated_at | Tạo bản ghi / ghi nhận kết quả sau độ trễ callback mô phỏng |

## Các phép tính để tránh sai báo cáo

- Giá trị vé bán thành công: SUM(total_amount) từ orders WHERE order_status='PAID'.
- Số đơn: COUNT(*) trên orders; nếu từ order_items thì COUNT(DISTINCT order_id).
- Số vé đã bán: SUM(quantity) từ order_items của các đơn PAID.
- Tỷ lệ thành công theo lần thử: số payments SUCCESS / tổng số payments trong tập xét.
- Tỷ lệ đơn thành công: số orders PAID / tổng số orders trong tập xét. Khác mẫu số phía trên.
- Giá trị đơn trung bình: tổng tiền của đơn PAID / số đơn PAID.
- Tỷ lệ bán quota theo hạng vé: số vé bán thành công / sale_quota, không phải tỷ lệ check-in.
- Không nối toàn bộ payments với order_items rồi cộng line_amount: sẽ nhân đôi khi có retry.
- Một dòng thanh toán thành công có thể cập nhật trạng thái đơn vào ngày tiếp theo;
  khi ELT cần phân biệt ordered_at, paid_at và updated_at.
