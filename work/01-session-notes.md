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

## Câu hỏi mở cho người dùng

Xem phần cuối tin nhắn của session 1.
