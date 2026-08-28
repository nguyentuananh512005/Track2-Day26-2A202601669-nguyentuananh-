# Project Memory — Track2 Day 26 Colosseum Agent Arena

## Kiến trúc & Module
- **Dự án:** Track2 Day 26 Colosseum Agent Arena (Defend, Prosecute, Attack & Integration Phase)
- **Files chính:**
  - `agent/gateway.py`: Control plane chính (`Gateway.decide`), thực thi 4 jobs: ROUTE, ADMIT, AUTHORIZE, BUDGET.
  - `agent/guardrails.py`: Bộ kiểm tra an toàn câu trả lời (`scan_for_injected_instructions`, `redact`, `verify_arithmetic`, `check_grounding`, `abstention_policy`).
  - `agent/strategy.py`: Quản lý ngân sách (`BudgetPacer`), bộ nhớ đệm kết quả (`ResultCache`), bẫy catalog (`is_catalog_trap`, `cheap_mask`), replica (`pick_replica`).
  - `agent/telemetry.py`: Ghi nhận sự kiện (`Telemetry`, `RecordingGatewayContext`).
  - `eval/prosecute.py`: Hệ thống công tố viên 17 Detectors, bộ lọc Confidence Gate > 44.44%, quản lý ngân sách 4 claims/hiệp (`ProsecutionBudget`). Đạt F1 = 1.000 trên 40 labelled fixtures.
  - `deck/deck.json`: Bộ bài 14 lá (10 attack + 4 blank), phân bổ chuẩn (4 MCP, 4 A2A, 2 Gateway), 9 classes độc lập, mọi `replica_flip` và `drift` trỏ đúng vào path_id có drift thực tế (`8c5bf8f6`, `62fa4da7`).
  - `deck/lineup.json`: Lộ trình ra đòn 10 hiệp tối ưu hóa đòn đánh.

## Bản vá bảo mật & hoàn thiện (2026-08-28)
1. **Confused Deputy (`_act_owns_target`):** Quét đệ quy toàn bộ `cmd.args` (nested dict/list/scalar), kiểm tra chuỗi có tiền tố `learner:` hoặc định dạng `sv-`, và kiểm tra mọi key chứa từ khóa danh tính (`learner`, `student`, `user`, `target`, `account`, `act`, `subject`, `client`, `recipient`).
2. **Safe Fields Sanitization:** Chuẩn hóa an toàn `safe_fields = tuple(str(f) for f in fields if f is not None)` trước khi sort/lookup tại `cheap_mask`, `ResultCache`, `is_catalog_trap`, `Command.from_action_dict`, `Gateway.decide`.
3. **Chống lọt lease (`slides.get_frame`):** Kiểm tra `not cmd.lease_id or cmd.lease_id not in live_leases`, chặn đứng trường hợp `live_leases` rỗng.
4. **Guardrails Normalization & Regex Enhancement:** Loại bỏ zero-width unicode chars (`\u200b`, `\u200c`, `\u200d`, `\ufeff`, `\u00ad`...), chuẩn hóa khoảng trắng `re.sub(r'\s+', ' ', text)`, bổ sung các biến thể regex chống obfuscation.
5. **Anti-Forged Server & Card Signature (`Gateway._card_admitted`):** Chặn các server counterfeit (`x-server-fingerprint: unvouched`), card signature invalid (`x-card-signature: invalid`), và `peer_unverified: True`.
6. **Detector Calibration (`eval/prosecute.py`):** Bỏ qua các lệnh đã bị Gateway từ chối (`verdict_applied == "deny"`) trong `_hook_write_violation` và `_hook_protocol_misuse` để tránh bị phạt recoil dội ngược khi Gateway của đối thủ phòng thủ đúng.

## Kết quả Đấu tập Sparring
- **vs Rookie:** Thắng 100 - 0 (KO hiệp 6/8 across all seeds).
- **vs Operator:** Thắng 100 - 0 (KO hiệp 6/7 across all seeds, bắt gọn Confused Deputy).
- **vs Adversary:** Thắng 72 - 0 (seed 1 KO hiệp 9), Thắng 48 - 19 (seed 2), Thắng 72 - 13 (seed 3).
- **Bundle nộp bài:** `submissions/2A202601669_Nguyễn_Tuấn_Anh.bundle` (78,243 bytes, 13 files, 39 kit hashes).
