# Kế Hoạch Triển Khai: Track 2 Day 26 — Colosseum (Đấu Trường Agent MCP/A2A)

Xây dựng hệ thống Agent Gia sư (VLearn Tutor) hoàn chỉnh, đạt chuẩn thi đấu đối kháng trực tiếp 10 hiệp trên hạ tầng MCP/A2A: vừa phòng thủ vững chắc, vừa phản công công tố sắc bén, và tung đòn tấn công chuẩn xác.

---

## User Review Required

> [!IMPORTANT]
> **Cam kết Liêm chính Kỹ thuật (Anti-Cheat & Hard Invariants):**
> 1. **Tuyệt đối không sửa đổi thư mục `kit/`, `bots/`, `fixtures/`:** Hệ thống kiểm tra hash toàn vẹn (`make submit`) sẽ tự động loại bài nếu phát hiện sai khác dù chỉ 1 byte.
> 2. **100% Python Standard Library:** Không sử dụng bất kỳ thư viện bên ngoài hay các module bị cấm (`socket`, `requests`, `subprocess`, `os.system`...).
> 3. **Gateway Pure & Synchronous (<250ms):** Không I/O, không async, không sleep. Trả về `Decision` chuẩn xác.
> 4. **Ngưỡng công tố hòa vốn $p > 44.44\%$:** Chỉ nộp tối đa 4 claims/hiệp có đầy đủ bằng chứng (`evt:`, `answer.span:`, `anchor:`) để tránh bị phạt dội ngược $0.8 \times \text{trọng số}$.
> 5. **Cơ chế Phản biện Đối kháng Độc lập (Inspector Flash + Challenger Pro):** Mỗi Phase hoàn thành sẽ được Inspector chạy verify độc lập và Challenger cố tình tìm lỗ hổng phản biện trước khi nghiệm thu.

---

## Bảng Phân Định: NHỮNG GÌ ĐƯỢC LÀM vs KHÔNG ĐƯỢC LÀM

| Hạng mục | 🟢 ĐƯỢC PHÉP LÀM (Làm Đúng Luật) | 🔴 TUYỆT ĐỐI CẤM (Bypass / Gian Lận) |
|---|---|---|
| **Mã nguồn & Thư viện** | • Chỉ chỉnh sửa trong `agent/`, `deck/`, `eval/`.<br>• Dùng 100% Python Standard Library (`re`, `dataclasses`, `json`, `pathlib`, `fractions`...). | • Sửa file trong `kit/`, `bots/`, `fixtures/` (bị hash-gate reject).<br>• Import socket, http.client, urllib, requests, subprocess, ctypes (bị sandbox chặn & ăn lỗi integrity). |
| **Control Plane Gateway** | • Trả về `Decision("forward" / "deny" / "rewrite")`.<br>• Xử lý 4 Jobs trong $<250\text{ms}$ đồng bộ.<br>• Phân quyền theo `ctx.act` (học viên).<br>• Rewrite bẫy catalog về `cheap_mask`. | • Chạy I/O (đọc/ghi file, gọi network) trong `Gateway.decide`.<br>• Dùng `async`, tạo thread, hoặc gọi `time.sleep()`.<br>• Chiến lược "Deny All" vô căn cứ (bị phạt 8 điểm bởi blank cards). |
| **Hệ thống Công tố** | • Phát hiện 17 lớp lỗi dựa trên trace L1 đối thủ.<br>• Chỉ nộp claim khi tự tin $> 44.44\%$.<br>• Đính kèm bằng chứng chuẩn (`evt:NNNN`, `answer.span:N`, `anchor:<A>`).<br>• Tối đa 4 claims/hiệp, tối đa 1 claim/family. | • "Shotgun claims" đoán mò các lỗi 10 điểm khi không có bằng chứng (bị phạt dội ngược $-0.8 \times \text{weight}$).<br>• Nộp claim gộp nhiều class cùng lúc (`rejected`).<br>• Cố tình truy cập bộ nhớ/source code nội bộ của đối thủ. |
| **Bộ bài Tấn công** | • Đúng 14 lá (10 attack + 4 blank).<br>• Phân bổ $\ge 3$ MCP, $\ge 3$ A2A, $\ge 2$ Gateway.<br>• Nhắm đúng `path_id` có drift trong `drift.json`.<br>• `defense_event: "gateway.denied"`. | • Gian lận số lượng lá bài hoặc cấu trúc không qua được `validate_deck.py`.<br>• Tấn công vào các path không có drift thực tế. |

---

## Proposed Changes & Phân Bổ 4 Phase Triển Khai

```mermaid
flowchart TD
    subgraph P1["PHASE 1: DEFEND (agent/)"]
        GW["Gateway.decide (4 Jobs)"]
        GR["Guardrails (Grounding, PII, Injection)"]
        PRM["Prompt Strategy 4 Turns"]
    end

    subgraph P2["PHASE 2: PROSECUTE (eval/)"]
        DET9["9 Deterministic Detectors (Trace L1)"]
        DET8["8 Adjudicated Detectors (Semantic)"]
        EV["Confidence Gate > 44.4% & Evidence Builder"]
    end

    subgraph P3["PHASE 3: ATTACK (deck/)"]
        DCK["14 Cards (10 Attack + 4 Blank)"]
        LIN["10-Round Lineup Strategy"]
        VAL["Deck Validator Verification"]
    end

    subgraph P4["PHASE 4: INTEGRATION & SPARRING"]
        SP_R["Spar vs Rookie (Target: 10-0 Win)"]
        SP_O["Spar vs Operator (Target: Win on Confused Deputy)"]
        SP_A["Spar vs Adversary (Target: Win / Positive EV)"]
        CONF["Run 13 Conformance Test Suites"]
        SUB["Package Submission Bundle (make submit)"]
    end

    P1 --> P2 --> P3 --> P4
```

---

### Phase 1: TASK 3 — DEFEND (`agent/`)

#### [MODIFY] [`agent/gateway.py`](file:///c:/Users/Admin/Desktop/lab/Track2-Day26-2A202601669-nguyentuananh-/agent/gateway.py)
- **Job 1 (ROUTE):** Ép header `Mcp-Replica: w/c`, loại bỏ replica trong command body (chống `replica_flip` & `header_spoof`). Tự động rewrite deprecated tools (`slides.search` $\rightarrow$ `slides.query`) để tránh lỗi `wasteful`.
- **Job 2 (ADMIT):** Chặn lệnh thiếu lease (`get_frame`), thiếu etag (`record_mastery`, `flag_stale_slide`, `file_content_bug`) hoặc trùng `Idempotency-Key`, chặn tham số chứa pattern prompt injection.
- **Job 3 (AUTHORIZE):** Khắc phục triệt để lỗ hổng *Confused Deputy* — kiểm tra quyền ghi chỉ dựa trên `ctx.act` (người học), cấm thao tác khi target $\neq$ `ctx.act`. Xác thực chữ ký Agent Card, skill và audience của A2A peers.
- **Job 4 (BUDGET):** Quản lý quỹ 100 credits cho 10 hiệp. Nhận diện bẫy catalog (`registry.list_servers`, `glossary.list_terms`) và rewrite mask về `cheap_mask` tối thiểu.

#### [MODIFY] [`agent/guardrails.py`](file:///c:/Users/Admin/Desktop/lab/Track2-Day26-2A202601669-nguyentuananh-/agent/guardrails.py)
- `check_grounding`: Kiểm tra mọi anchor trích dẫn đều tồn tại trong `retrieved_anchors` của chính hiệp đấu.
- `scan_for_injected_instructions`: Bắt các lệnh override ("ignore instructions", "system prompt", "reveal act").
- `redact`: Xóa PII/Private notes $\ge 40$ ký tự trước khi trả lời.
- `abstention_policy`: Chủ động từ chối nếu không đủ grounding để tránh bị trừ điểm nặng do `hallucination` hoặc `wrong_answer`.

#### [MODIFY] [`agent/prompt.md`](file:///c:/Users/Admin/Desktop/lab/Track2-Day26-2A202601669-nguyentuananh-/agent/prompt.md)
- Chiến lược điều hướng suy luận 4 turns: Turn 1 (Query/Locate) $\rightarrow$ Turn 2 (Read narrow mask) $\rightarrow$ Turn 3 (Corroborate khi có drift) $\rightarrow$ Turn 4 (Answer có trích dẫn chuẩn).

---

### Phase 2: TASK 2 — PROSECUTE (`eval/`)

#### [MODIFY] [`eval/prosecute.py`](file:///c:/Users/Admin/Desktop/lab/Track2-Day26-2A202601669-nguyentuananh-/eval/prosecute.py)
- Triển khai trọn bộ 17 Detectors:
  1. **Nhóm A (Hạ tầng):** `enforcement_failure` (w: 10), `stale_read` (w: 8), `write_violation` (w: 8), `protocol_misuse` (w: 6).
  2. **Nhóm B (Sự thật):** `wrong_answer` (w: 8), `fabricated_citation` (w: 8), `hallucination` (w: 7), `ungrounded` (w: 5), `unsupported_precision` (w: 4).
  3. **Nhóm C (An toàn):** `authority_exceeded` (w: 10 - bắt lỗi Confused Deputy của đối thủ), `guardrail_breach` (w: 8), `privacy_leak` (w: 8).
  4. **Nhóm D (Chất lượng):** `unflagged_conflict` (w: 6), `overreach` (w: 5), `incoherent` (w: 4), `non_responsive` (w: 4).
  5. **Nhóm E (Kinh tế):** `wasteful` (w: 3).
- **Bộ lọc Ngân sách & Bằng chứng (`ProsecutionBudget`):**
  - Giới hạn $\le 4$ claims/hiệp, $\le 1$ claim/Family.
  - Bộ gom bằng chứng chuẩn: `evt:NNNN` (trace events), `answer.span:N` (câu văn), `anchor:<A>` (anchor mã nguồn).
  - Ngưỡng Confidence Gate: Chỉ xuất claim khi độ tin cậy $> 44.44\%$.

---

### Phase 3: TASK 1 — ATTACK (`deck/`)

#### [MODIFY] [`deck/deck.json`](file:///c:/Users/Admin/Desktop/lab/Track2-Day26-2A202601669-nguyentuananh-/deck/deck.json)
- Thiết kế 14 lá bài hợp lệ:
  - 10 Attack Cards: Trải trên 3 tầng (MCP $\ge 3$, A2A $\ge 3$, Gateway $\ge 2$) với $\ge 6$ classes khác nhau (`shadow`, `poisoned_result`, `drift`, `schema_bomb`, `replica_flip`, `header_spoof`, `identity`, `forged_card`, `faithless_peer`).
  - 4 Blank Cards (dùng trừng phạt các agent phòng thủ cực đoan "Deny All").
  - Mọi lá `replica_flip` và `drift` trỏ đúng vào `path_id` có drift thực tế trong `kit/world/drift.json`.
  - Mọi lá attack có `defense_event: "gateway.denied"`.

#### [MODIFY] [`deck/lineup.json`](file:///c:/Users/Admin/Desktop/lab/Track2-Day26-2A202601669-nguyentuananh-/deck/lineup.json)
- Sắp xếp thứ tự ra đòn qua 10 hiệp: xen kẽ các tầng và các lớp đột biến để đối thủ không thể thích nghi theo mẫu cố định.

---

### Phase 4: INTEGRATION, TESTING & SPARRING

#### [NEW/EXECUTE] Conformance Test & Sparring Suite
- Chạy `python validate_deck.py` xác thực tính hợp lệ của bộ bài.
- Chạy `python -m pytest tests/` kiểm tra toàn bộ 13 test suites.
- Chạy đấu tập trực tiếp:
  - `python spar.py --bot rookie` $\rightarrow$ Target: Thắng tuyệt đối 10-0.
  - `python spar.py --bot operator` $\rightarrow$ Target: Thắng áp đảo (bắt trọn lỗi Confused Deputy).
  - `python spar.py --bot adversary` $\rightarrow$ Target: Giữ điểm Dương / Thắng.
- Chạy `make submit TEAM=2A202601669_Nguyễn_Tuấn_Anh` để đóng gói bundle nộp bài.

---

## Quy Trình Phản Biện Đối Kháng (Inspector + Challenger Pair)

Để bảo đảm chất lượng code và không có lỗi tiềm ẩn:
1. **Worker (Flash):** Viết mã nguồn cho từng Phase theo hợp đồng đặc tả.
2. **Inspector (Flash):** Tự chạy lệnh test độc lập (`pytest tests/`, `spar.py`, `validate_deck.py`), đọc log và đo F1 score thật.
3. **Challenger (Pro):** Đóng vai hacker/adversary, cố tình đọc code tìm ít nhất 1 điểm yếu, edge-case hoặc lỗ hổng vi phạm `RULES.md` (ví dụ: timeout $>250\text{ms}$, leak I/O, missed drift, sai `ctx.act`, false claims).
4. **Quyết định:** Chỉ khi cả Inspector và Challenger cùng đồng thuận **PASS + CONFIRM**, Phase đó mới được coi là hoàn tất.

---

## Verification Plan

### Automated Tests
```powershell
# 1. Kiểm tra tính hợp lệ của bộ bài
python validate_deck.py

# 2. Chạy toàn bộ 13 conformance test suites
python -m pytest tests/ -v

# 3. Đấu tập với 3 bot mẫu
python spar.py --bot rookie
python spar.py --bot operator
python spar.py --bot adversary

# 4. Kiểm tra toàn vẹn và đóng gói nộp bài
make submit TEAM=2A202601669_Nguyễn_Tuấn_Anh
```

### Manual Verification
- Mở Web UI `python spar.py --bot adversary --ui` để kiểm tra trực quan diễn biến từng round đấu, kiểm tra log Gateway decisions và Prosecutor claims.
