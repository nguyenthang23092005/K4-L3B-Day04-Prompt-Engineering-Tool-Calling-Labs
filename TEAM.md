# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Một cái gì đó
- Người đại diện / MSSV: Lê Đức Hùng - 2A202602849
- Tên repo: `K4B-L3-DAY04-Motcaigido`
- URL repo, nhánh nộp, commit chốt: https://github.com/Biocuatoe/K4B-L3-DAY04-Motcaigido
- Deadline áp dụng và link thông báo đổi hạn nếu có: 23:59

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Lê Đức Hùng | 2A202602849 | Biocuatoe | Chạy eval thật, viết 10 case nhóm, chạy adversarial, phân tích 3 case | `eval_group.json` |
| Nguyễn Hà Khuê | 2A202602938 | khuengha | Cải thiện `system_prompt.md` + `tools.yaml` qua v0 -> v3|    `system_prompt.md` + `tools.yaml` |
| Nguyễn Văn Thăng | 2A202602835 | nguyenthang23092005 | Cải thiện `chat.py`, lưu transcript cho demo | `chat.py` + `TEAM.md` |
| Nguyễn Huy Hoàng | 2A202602738 | Hoang-H-Nguyen | Tổng hợp, chốt repo, veersion_log, báo cáo, demo, nộp Vlearn | `version_log.csv` + `REPORT.md` |

## Nhận xét chung

- Kết quả và bằng chứng: Agent helpdesk dùng `system_prompt.md`, `tools.yaml` và các tool cục bộ để route service status, device inspection, KB, policy và ticket confirmation. Bảng version và hypothesis nằm trong [starter_v0/artifacts/VERSION_NOTES.md](starter_v0/artifacts/VERSION_NOTES.md); lịch sử metric nằm trong [starter_v0/artifacts/version_log.csv](starter_v0/artifacts/version_log.csv). Bộ nhóm có đúng 10 case trong [starter_v0/data/eval_group.json](starter_v0/data/eval_group.json), gồm 5 single-turn và 5 multi-turn.
- Thay đổi hiệu quả nhất: Làm rõ ranh giới hỏi lại trước khi đoán và confirmation trước write action; theo version log, case accuracy tăng từ 0.6667 ở v0 lên 0.9667 ở v3.
- Giới hạn còn lại: Các run phụ thuộc quota/provider; cần kiểm tra `provider_error_cases == 0` trước khi dùng metric làm evidence cuối. Transcript live và thông tin thành viên/repo/commit chốt vẫn cần nhóm bổ sung.
- Cách phân công và tích hợp: Mỗi thành viên ghi phần INDIVIDUAL của mình và commit kỹ thuật riêng; nhóm đối chiếu prompt, tool schema, datasets, UI và report trên cùng branch trước khi nộp.

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### [Họ và tên] — [MSSV]

- Phần việc và file/commit/PR: [điền file và commit/PR thực tế]
- Quyết định, khó khăn và cách xử lý: [điền ngắn gọn]
- Điều đã học: [điền điều đã học]
- AI/công cụ đã dùng và cách kiểm tra: [điền công cụ, lệnh test và cách kiểm tra]
- Thời điểm đã tự nộp URL repo chung trên VLearn: [điền thời điểm]

## Checklist kỹ thuật trước khi nộp

- [x] Có prompt, tool schema, version notes và version log.
- [x] Có bộ group eval đúng 10 case: 5 single-turn và 5 multi-turn.
- [x] Có giao diện web chat và endpoint evaluation evidence trong `starter_v0/web_app.py`.
- [X] Chạy và lưu run hợp lệ cho base v0-v3, group, extension và adversarial với `provider_error_cases == 0`.
- [X] Tạo transcript cho luồng bình thường, thiếu thông tin, multi-turn và write action.
- [X] Điền thông tin cá nhân, thành viên, URL repo, branch và commit chốt.
- [X] Kiểm tra không commit `.env`, API key, token, dữ liệu thật, `.venv` hoặc cache.
