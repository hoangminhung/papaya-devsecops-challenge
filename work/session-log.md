# Ghi chú làm việc (Vietnamese)

## English summary

Running log of the working sessions, not part of the reading order.
- **Session 1 (2026-11-08):** fetched the challenge text and set up the repo skeleton. Transcript location and retention
  were checked. The transcript also contains the employer account's skill and connector names; this was accepted.
- **Session 2 (2026-11-08):** set a repo-local git identity and rewrote unpushed commits; wrote the problem framing.
  The session ran through the VS Code extension in auto mode on the default profile; this was accepted.
- **Session 3 (2026-11-08):** ran on the clean profile (`~/.claude-papaya`); the problem framing was reviewed in
  two question rounds, and the owner confirmed the scope and assumptions.
- **2026-11-09:** wrote `03-options.md` (4 options, 2 combinations) and took it through 5 independent review rounds.
  The owner chose A + D2' and set the incident target to ≤ 30 min.

## 2026-11-08 — Session 1: dựng khung repo

- Đã tải đề từ GitHub về `work/00-challenge.md` ✅.
- Dựng thư mục `docs/ examples/ diagrams/ work/ transcripts/`, viết `CLAUDE.md` và `README.md` khung.
- Transcript:
  - Vị trí ✅: `~/.claude/projects/-home-do-hoang-minh-hung-papaya-devsecops-challenge/<session-id>.jsonl`
    (session này: `6cd4c971-cfc4-49e3-a503-538be8f11bcd.jsonl`). Thư mục `memory/` cùng cấp là auto-memory, không phải transcript.
  - Cơ chế xóa 📖 (https://code.claude.com/docs/en/claude-directory#cleaned-up-automatically):
    xóa file cũ hơn `cleanupPeriodDays`; mặc định 30 ngày, tối thiểu 1, giá trị 0 bị từ chối → không tắt hẳn được, chỉ kéo dài.
    Subagent transcripts nằm ở `<session-id>/subagents/`, bị xóa cùng session cha.
  - Máy này ✅: `~/.claude/settings.json` có `"cleanupPeriodDays": 365`.
  - Lưu ý 📖: transcript là plaintext và chứa cả system prompt, tool definitions, CLAUDE.md và các rule toàn cục
    (`~/.claude/CLAUDE.md`, `~/.claude/rules/**`) đã được nạp. Nộp nguyên bản nghĩa là người chấm đọc được các rule đó.
- Chưa viết nội dung bài. Chưa commit (chờ người dùng).

## Quyết định sau khi trao đổi (cùng ngày)

- Branch nộp bài: `master`. Đã commit khung (`4d02c11`).
- Từ session 2: chạy permission mode mặc định (không auto mode).
- Rà soát rò rỉ ✅: `~/.claude/CLAUDE.md` và `rules/devops-kit/**` không chứa tên tổ chức, khách hàng, secret.
  Nguồn rò rỉ nằm ở **tài khoản claude.ai**: email người dùng (trong system prompt và đường dẫn home),
  tên sản phẩm AI nội bộ của công ty hiện tại (từ skill/plugin được sync), tên MCP connector của công ty.
  Những thứ này đã nằm trong transcript session 1 và không gỡ được; chấp nhận.
- Giải pháp cho các session sau: profile sạch `~/.claude-papaya` chỉ cài devops kit, tắt
  `syncClaudeAiSkills`, `syncClaudeAiPlugins`, bật `disableClaudeAiConnectors` 📖 (settings-reference index).
  Email tài khoản vẫn xuất hiện (là identity đăng nhập), đường dẫn home vẫn chứa tên người dùng.
- Agent không được phép chạy installer của kit vào profile mới (auto-mode classifier: "Security Weaken",
  vì cài hook và permission rule). Người dùng tự chạy `work/setup-clean-config.sh`.
- Git author email khác domain với tài khoản Claude; cả hai sẽ lộ trong repo/transcript. Người dùng quyết.

## 2026-11-08 — Session 2: git identity, transcripts, problem framing

- Git author: đặt `user.email` local cho repo, viết lại 2 commit chưa push sang email cá nhân;
  xoá `user.email` global theo yêu cầu người dùng. Tag `backup/pre-email-rewrite` giữ commit cũ (không push).
- Transcript commit nguyên bản; chấp nhận việc chứa email công việc của chính tác giả (ghi trong `CLAUDE.md`).
- Viết `work/01-problem-framing.md`; người dùng xác nhận giả định (mục 6 của file đó).
- Đổi `work/01-session-notes.md` → `work/session-log.md` (nhật ký không thuộc thứ tự đọc).
- Phát hiện ✅ (`ps`, biến môi trường): phiên này chạy qua **VSCode extension**, `CLAUDE_CONFIG_DIR` không được đặt
  → dùng `~/.claude` (profile mặc định, có sync skill/connector từ claude.ai), và extension khởi động với
  `--permission-mode=auto`. Cả hai trái với quyết định "từ session 2" trong `CLAUDE.md`.
  Profile sạch không cần tài khoản khác; chỉ cần chạy CLI: `CLAUDE_CONFIG_DIR=~/.claude-papaya claude`.
  Người dùng chấp nhận giữ nguyên transcript phiên này.

## 2026-11-08 — Session 3: rà soát problem framing (grill-me)

- Chạy qua VSCode extension, lần này với `CLAUDE_CONFIG_DIR=~/.claude-papaya` ✅ (biến môi trường).
  Transcript lưu ở `~/.claude-papaya/projects/…/28544ac2-2bc6-4da2-845a-d8dfd0339f26.jsonl` ✅.
- Các session ngắn `a95ee902` và `2e7942e6` (profile sạch, khởi động/thử extension) cũng được copy vào `transcripts/`.
- Rà `work/01-problem-framing.md` so với đề. Chỗ hở: dữ liệu ở non-prod, bảo mật code do agent viết,
  phạm vi prod AI agents, GĐ-2 chưa xác nhận, mục tiêu S7, hình thức và người đọc của deliverable.
- Hỏi 2 vòng; người dùng chọn đề xuất ở cả 7 câu. Kết quả ghi ở §6 "Vòng 2" của framing:
  thêm P9, nhóm 7, mục 1.4 (out of scope), GĐ-14, S10, S11; xác nhận GĐ-2 và S7.
- Bước tiếp theo: thiết kế (docs/ + examples/). Tra docs cho GĐ-5 (GitHub environment protection)
  và GĐ-6 (managed settings trên gói Team).

## 2026-11-09 — Brainstorm phương án (`work/03-options.md`)

- Viết `work/03-options.md`: 4 phương án (A PR-only, B runbook SSM có `aws:approve`, C JIT trực tiếp, D agent hosted)
  và 2 tổ hợp (A + D2 hiện tại, A + D2' đề xuất); ma trận 5 tiêu chí; kịch bản Lambda lúc 2 giờ sáng; khuyến nghị.
- Kiểm docs AWS mới ✅ (bản `.md`): Change Manager đóng với khách hàng mới từ 2025-11-07; SSM Automation `aws:approve`
  có approver dạng role ARN, tối đa 10, không hỗ trợ automation multi-account/Region.
- Review độc lập 5 vòng. Vòng 1–3 có HIGH/MEDIUM, nên file được viết lại thành v4. Vòng 4–5 còn MEDIUM nhỏ (bẫy SQS
  visibility timeout chưa được xử lý ở mọi kịch bản; nói thẳng C nhanh hơn ở đâu). Đã sửa; lần sửa cuối là sửa một
  dòng, chỉ kiểm bằng grep, không chạy thêm vòng review.
- Khuyến nghị: A + D2'. Chờ owner trả lời Q1–Q3 ở mục 9 của file.
- Owner trả lời (2026-11-09): Q1 chọn A + D2' (cách đọc D2 = "IaC trước"); Q2 chấp nhận JIT dự phòng đạt một phần,
  chỉ dùng khi đường chính không dùng được và đã được approve; Q3 mục tiêu ≤ 30 phút. Ghi ở mục 9 của `03-options.md`.
- Sửa một câu bị gãy ở mục 7 của `03-options.md` (đoạn "A + D2 như đang có").
