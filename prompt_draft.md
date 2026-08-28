# Teamwork Project Prompt — Final Draft

> Status: Ready for launch — awaiting user approval
> Goal: Triển khai toàn diện 3 nhiệm vụ (Defend, Prosecute, Attack) cho Lab Day 26 Colosseum với cơ chế phản biện đối kháng độc lập.
> Requested team: Full Multi-Agent Engineering Team (Multi-PM, Workers, Inspector & Challenger)

## Project Overview
Xây dựng và hoàn thiện trọn vẹn 3 trụ cột của hệ thống Agent Đấu trường Colosseum (Track 2 - Day 26) cho học viên Nguyễn Tuấn Anh (2A202601669):
- **Phòng thủ (Defend - `agent/`):** Control Plane Gateway đồng bộ <250ms (Route, Admit, Authorize check `ctx.act`, Budget) + Guardrails + System Prompt 4 bước.
- **Công tố (Prosecute - `eval/`):** Bộ phát hiện 17 lớp lỗi với ngưỡng tự tin >44.44% và đính kèm bằng chứng chuẩn xác.
- **Tấn công (Attack - `deck/`):** Bộ bài 14 lá (10 attack + 4 blank) phân bổ 3 tầng (MCP, A2A, Gateway) và lịch ra đòn 10 hiệp.

Working directory: `c:\Users\Admin\Desktop\lab\Track2-Day26-2A202601669-nguyentuananh-`
Integrity mode: `benchmark` (Tuân thủ nghiêm ngặt RULES.md, không bypass sandbox, không sửa `kit/`, không gian lận).

## Requirements

### R1. Triển khai Task 3 (Phòng thủ - `agent/`)
- Hoàn thiện `Gateway.decide` thuần túy đồng bộ (Pure, <250ms, zero I/O) giải quyết triệt để 4 Jobs: ROUTE (ép header `Mcp-Replica`, rewrite tool cũ), ADMIT (chặn thiếu lease/etag/injection), AUTHORIZE (chống lỗ hổng Confused Deputy dựa trên `ctx.act`), BUDGET (rewrite bẫy catalog `list_servers`/`list_terms`).
- Cài đặt `agent/guardrails.py` (check_grounding, scan_injection, redact PII, abstention) và `agent/prompt.md`.

### R2. Triển khai Task 2 (Công tố - `eval/prosecute.py`)
- Xây dựng đầy đủ detectors cho 17 lớp lỗi (5 nhóm: Hạ tầng, Sự thật, An toàn, Chất lượng, Kinh tế).
- Cài đặt cơ chế Confidence Gate ($p > 44.44\%$) để đảm bảo kỳ vọng dương ($E > 0$), tối đa 4 claims/hiệp (tối đa 1 claim/nhóm Family) đính kèm bằng chứng `evt:`, `answer.span:`, `anchor:`.

### R3. Triển khai Task 1 (Tấn công - `deck/`)
- Thiết kế 14 lá bài hợp lệ (10 attack + 4 blank) đạt chuẩn về phân bổ Layer, Class, drift target trong `drift.json`, và `defense_event: "gateway.denied"`.

### R4. Quy chuẩn Chống Gian lận (Anti-Cheat & Hard Invariants)
- Tuyệt đối không sửa đổi `kit/`, `bots/`, `fixtures/` (bảo đảm hash-check `make submit`).
- 100% Python Standard Library (không dùng socket, requests, subprocess...).
- Mọi logic phải vượt qua 13 test suites (`make test`) và thắng áp đảo khi spar với `rookie`, `operator`, `adversary`.

### R5. Quy trình Phản biện Đối kháng Độc lập (Inspector + Challenger Pair)
- Mỗi Phase sau khi Worker (Flash) hoàn thành sẽ được Inspector (Flash) chạy test độc lập và Challenger (Pro) phân tích tìm lỗ hổng/edge-case trước khi nghiệm thu.

## Acceptance Criteria

### [Defend & Gateway Standards]
- [ ] Vượt qua toàn bộ unit test gateway, guardrails, strategy.
- [ ] Không có bất kỳ timeout (>250ms) hay integrity exception nào trong suốt 10 hiệp đấu.
- [ ] Khắc phục 100% lỗ hổng Confused Deputy và không bị nuốt credits từ bẫy catalog.

### [Prosecution Standards]
- [ ] Tỷ lệ F1 score của bộ detectors đạt >= 85% trên 40 fixture traces mẫu.
- [ ] Tỷ lệ false claim = 0% trên các clean traces để tránh bị phạt dội ngược 0.8x.

### [Deck & Submission Standards]
- [ ] `make validate` báo PASS 100% cho 14 lá bài và lineup 10 rounds.
- [ ] `make test` PASS toàn bộ 13 test suites.
- [ ] Đấu tập thắng 10-0 trước `rookie`, thắng áp đảo trước `operator`, và hòa/thắng trước `adversary`.
- [ ] `make submit` đóng gói thành công bundle hợp lệ `submissions/2A202601669_Nguyễn_Tuấn_Anh.bundle`.

---
*Next: Nhận xác nhận của Sếp → Kích hoạt phân công Teamwork Multi-Agent.*
