# Phân tích 3 version (v0 → v3)

Mỗi version sửa **một** nhóm lỗi, đặt **một** giả thuyết, rồi chạy lại **cùng bộ 30 case** (`data/eval_base.json`) để so sánh. Metric chính là `case_accuracy` (tỉ lệ case PASS).

## Bảng tổng quan

| Version | Sửa file nào | case_accuracy | Kết luận |
|---|---|---:|---|
| v0 | (baseline, chưa sửa) | 0.6667 (20/30) | Điểm khởi đầu |
| v1 | `system_prompt.md` | 0.7667 (23/30) | Giả thuyết đúng (+3 case) |
| v2 | `system_prompt.md` | 0.8333 (25/30) | Giả thuyết đúng (+2 case) |
| v3 | `tools.yaml` + `system_prompt.md` | 0.9667 (29/30) | Giả thuyết đúng (+4 case) |

---

## v0 — Baseline: 20/30, phát hiện 3 nhóm lỗi

Chạy bản gốc trước khi sửa bất cứ gì. 10 case fail chia thành 3 nhóm nguyên nhân rõ ràng:

1. **Đoán thay vì hỏi (3 case)** — user nói "laptop của mình" thì agent tự bịa `asset_id: "laptop"`; "nhân viên bên Sales" thì bịa `employee_id: "Sales"`; "môi trường demo QA" thì tự chọn `staging`. Cả 3 đều gây tool error `not_found`.
2. **Tạo ticket không xác nhận (3 case)** — user vừa yêu cầu là agent gọi `create_ticket` luôn, thậm chí **tự gán `confirmed: true`** — bịa xác nhận. Có case user đổi priority sau khi xác nhận mà agent vẫn dùng confirmation cũ.
3. **Sai/thiếu tham số (4 case)** — gọi đúng tool nhưng bỏ trống `check` của `inspect_device`, thiếu `category` của `search_kb`, hoặc tự gọi thêm `inspect_device` với employee ID làm asset ID.

## v1 — Sửa nhóm 1: thêm quy tắc "hỏi trước khi đoán" (system_prompt.md)

**Giả thuyết:** nếu prompt cấm đoán ID và bắt buộc hỏi lại khi thiếu thông tin thì 3 case `missing_info` sẽ PASS.

**Thay đổi:**
- Rule: *Never guess, construct, or transform identifiers* — chỉ dùng ID user nói rõ hoặc tool trả về.
- Mục **Missing information**: thiếu asset ID / employee ID → `clarify`; môi trường ngoài production/staging (demo, QA, dev...) → `clarify` kiểu `choice` với 2 lựa chọn.
- Cấm chạy tool khác với tham số đoán khi còn thiếu thông tin.

**Kết quả:** 23/30 (+3). `missing_info` 3 → 0, extra_tool_call ở H04 cũng giảm. Giả thuyết xác nhận.

## v2 — Sửa nhóm 2: thêm ranh giới xác nhận cho write action (system_prompt.md)

**Giả thuyết:** nếu bắt buộc hiện payload và hỏi yes/no trước khi tạo ticket thì 3 case `wrong_boundary` sẽ PASS.

**Thay đổi:** mục **Write actions and confirmation**:
- `create_ticket` là write action, không được tự gọi trong cùng lượt với yêu cầu.
- Phải hiện đúng payload (summary, priority, asset_id) và hỏi `clarify` kiểu `yes_no`.
- `confirmed: true` chỉ khi user trả lời yes cho đúng payload đó.
- Payload đổi sau khi xác nhận → confirmation cũ vô hiệu, phải hỏi lại.

**Kết quả:** 25/30 (+2), multiturn_accuracy lên 1.0. H12 vẫn fail (agent hỏi bổ sung summary thay vì hỏi yes/no) — chuyển sang v3 xử lý.

## v3 — Sửa nhóm 3: làm rõ mô tả tool (tools.yaml) + 3 rule nhỏ (system_prompt.md)

**Giả thuyết:** nếu mô tả tool nói rõ quy ước tham số và ranh giới write action thì các case sai tham số sẽ PASS.

**Thay đổi trong `tools.yaml`** (giữ nguyên tên tool và schema, chỉ sửa description):
- `inspect_device`: bắt buộc set `check` theo vấn đề (VPN→vpn, mạng/Wi-Fi→network, "tổng thể"→all), không bỏ trống.
- `search_kb`: bắt buộc set `category` theo chủ đề (Outlook/email→email, VPN→vpn...).
- `lookup_user`: nếu cần kiểm tra thiết bị, lấy asset ID **từ kết quả tra cứu**, không dùng employee ID.
- `create_ticket`: nhắc lại ranh giới — không gọi trước khi user xác nhận.

**Bổ sung 3 rule nhỏ trong `system_prompt.md`** (từ phân tích run v2):
- Quy ước `response_type` của `clarify`: hỏi thông tin tự do → `text`; xác nhận → `yes_no`; lựa chọn cố định → `choice` (sửa H11).
- Request đã đủ mô tả sự cố + priority + asset thì dùng chính mô tả đó làm summary, hỏi yes/no luôn, không hỏi lại (sửa H12).
- Request cần nhiều nguồn → gọi đủ các tool trong cùng lượt (giữ H13, H17).

**Kết quả:** 29/30 (+4). Chỉ còn H06 fail do noise: user nói rõ "Email staging" nhưng agent vẫn hỏi lại — over-clarify, không phải lỗi rule (đã chạy lại nhiều lần, kết quả dao động 28–29/30).

---

## Tổng kết

- **0.6667 → 0.9667** sau 3 vòng, mỗi vòng nhắm đúng 1 nhóm lỗi đã định hướng từ phân tích v0.
- Học được: lỗi agent không nằm ở code mà ở **prompt thiếu quy tắc** và **mô tả tool mơ hồ**; sửa artifact đúng chỗ thì hành vi đổi ngay mà không đụng code.