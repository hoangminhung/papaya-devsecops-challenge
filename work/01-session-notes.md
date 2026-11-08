# Ghi chú làm việc (Vietnamese)

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
