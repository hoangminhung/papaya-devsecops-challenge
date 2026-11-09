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
- **2026-11-09, design:** wrote the framework (17 review rounds), 10 ADRs, the threat model and the
  problem-control map; the owner approved each and decided OD1–OD13.
- **2026-11-09, deliverable plan and examples:** fixed the deliverable plan; built and locally checked the
  examples in three steps (change workflow, identity and access, agent runtime/supply chain/policy pack),
  each with independent review rounds and mutation tests; owner decisions OD14–OD21.
- **2026-11-09, final pass:** moved the rollout plan out of the framework, added the compliance register,
  engineer guide, three diagrams and the README; synced the framework, ADR index, threat model and map
  with the examples' findings. Two independent final reviews (no HIGH except one: the README's claim
  about Manual permission mode was false, since most working sessions ran in auto mode; corrected).

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

## 2026-11-09 — Thiết kế mục 1: `docs/framework.md`

- Viết `docs/framework.md` (8 tầng). Review độc lập 6 vòng; mỗi vòng có HIGH/MEDIUM mới (trích dẫn
  📖 cho dòng suy luận, lệch quyết định owner, nói quá). Sau vòng 4 viết lại thành v3 cho gọn và nhất quán.
- Owner trả lời OQ1–OQ5 (nguyên văn):
  - OQ1 (ngoại lệ S2 cho k0s/Firebase): "Có, k0s với firebase có thể cần key để scale in scale out liên tục, nên có thể xem là ngoại lệ, chỉ cần có single source of truth là được."
  - OQ2 (L3 có cần người platform): "Không nhất thiết phải cần người của platform, quy trình sẽ được thống nhất cho engineer. Chỉ cần engineer on call là đủ."
  - OQ3 (`CLAUDE.md` L2 hay L3): "Xếp hạng L3, vì workflow cần thống nhất với cả team."
  - OQ4 (lùi baseline còn lại và kiểm chứng SSM): "Có, lùi sang phase 2."
  - OQ5 (agent không duyệt PR): "là rule luôn, người duyệt PR luôn là engineer, không phải agent."
  - Không cần rút gọn file; cập nhật và chạy review vòng 7.
- Cách hiểu OQ2: L3 vẫn cần 2 engineer khác nhau, không cần thuộc platform; trong sự cố là on-call
  primary + backup. Owner xác nhận (nguyên văn): "Đúng vậy, vẫn là 2 engineer nhưng 1 primary và 1 backup."
- Review vòng 7: 3 HIGH, 8 MEDIUM, đã sửa. Câu hỏi mới OD6, OD7. Owner trả lời (nguyên văn):
  - OD6: "Vậy là tôi hiểu nhầm, ở đây nói về credentials nào? giải thích cụ thể dùm với." → agent giải thích
    hai loại (credential deploy trong GitHub secrets; credential runtime để scale trong cluster). Owner chốt:
    "OK, chấp nhận ngoại lệ cho tới khi check được k0s và firebase áp dụng OIDC được." (chỉ credential deploy trong CI)
  - OD7a: "Không sao, khi làm nhiệm vụ on call thì không được sửa quy trình. Tóm lại trong lúc on call thì tuyệt đối không sửa quy trình."
    → agent hỏi lại hai cách hiểu; owner chọn (a): người on-call chỉ duyệt, không tự viết fix; fix do engineer khác viết.
  - Owner làm rõ lại OD2/OD7 (nguyên văn): "Mình hiểu nhầm ý này, ý của mình là chỉ cần 2 người, 1 người thực thi
    và 1 người approve thôi. Người backup chỉ là backup, không cần duyệt hoặc thực thi cùng lúc."
  - Agent hỏi L3 có còn khác L2 về số người duyệt không; owner chọn: "L3 = 1 người duyệt mọi lúc". L3 khác L2 ở chỗ
    người duyệt phải là owner của path đó, cộng risk stop.
- Review vòng 8 (2 HIGH: credential ngoại lệ trong repository secret thành quyền ghi prod thường trực → chuyển sang
  environment secret `production`; thiếu lịch trực responder ở phase 1) và vòng 9 (0 HIGH, 10 MEDIUM), đã sửa.
  Vòng 10 để xác nhận.
  - OD7b: "OK làm theo đề xuất." → allowlist chỉ đọc ở phase 1.
- Review vòng 10: 1 HIGH, 7 MEDIUM, 9 LOW, đã sửa hết.
  - HIGH: trước đây on-call approver được thêm tạm vào mọi team owner L3 trong ca trực, làm "owner" chỉ còn trên danh nghĩa.
    Agent chọn mặc định: lịch trực chỉ lấy người vốn là owner, và mỗi ca phủ đủ owner cho mọi path L2/L3 deploy được.
    Path nào thiếu owner trong ca thì page owner ngoài lịch; trường hợp này không mở JIT. Đây là cách agent hiểu OD2,
    cần owner xác nhận.
  - MEDIUM:
    - §1 và Layer 3 giờ nói cùng một trạng thái; ví dụ Lambda ghi rõ R là owner của `serverless.yml`.
    - Viết lại khác biệt L2/L3: khác ở team owner, không phải "any code owner".
    - Nói rõ trường hợp PR chạm nhiều team (lệch quy tắc "2 người").
    - Risk stop: khóa theo SHA của commit gốc; CODEOWNERS theo stack và team L3.
    - excludedCommands làm `pulumi`/`serverless` chạy code repo ngoài sandbox; giới hạn của SCP `aws:ResourceOrgID`.
    - Chi phí: engineer mất quyền đọc log và config thô trong giai đoạn chuyển tiếp.
    - JIT ở phase 1 không có cách dừng ngay; drift check làm tay là lệch tạm thời so với D2.
- Review vòng 11: 1 HIGH, 7 MEDIUM, 6 LOW.
  - HIGH: risk stop do L3 team duyệt có thể thành người thứ ba.
  - MEDIUM: CODEOWNERS không đổi owner theo loại trigger được; cơ chế "re-run commit gốc" khác Options §1; cách xếp
    lịch đêm của vòng 10 mâu thuẫn với mô hình 1 primary + 1 backup.
  - Agent hỏi owner hai câu, owner chọn cả hai phương án khuyến nghị:
    - OD8: risk stop do owner của stack duyệt (có thể chính là người đã duyệt PR đầu), nên luôn chỉ 2 người.
      L3 owner team chỉ giữ các path L3 thật; Access Analyzer và policy pack bù lại.
    - OD9: nhóm on-call approvers làm co-owner mọi path deploy được, vẫn 1 primary + 1 backup. Domain review ngày thường
      thành quy tắc quy trình, kiểm tra hàng tháng.
  - Đã sửa thêm:
    - Risk stop quay về cơ chế của Options §1 (preview lại trên HEAD mới, so hash).
    - Thêm `sandbox.autoAllowBashIfSandboxed`.
    - Self-hosted runner: gắn ⚠️, thêm G15.
    - L3-data lúc đêm: on-call duyệt, data owner xem lại hôm sau [design].
    - Trích dẫn GĐ-14; phạm vi SCP `aws:ResourceOrgID`.
- Review vòng 12: 1 HIGH, 4 MEDIUM, 9 LOW, đã sửa hết.
  - HIGH: path-based required reviewers (R3.2.4) mâu thuẫn với OD9 → bỏ rule đó, L3 chỉ dùng CODEOWNERS + code-owner review.
  - MEDIUM:
    - Risk stop do chính người duyệt đầu duyệt; nếu đổi người thì là 3 người, ghi lại như một độ lệch.
    - PR liên domain: GitHub chấp nhận một approval → câu hỏi mở OQ-A cho owner.
    - Biến thể L3-data ban đêm được đưa vào Layer 6, Roles và bảng mức.
    - Allowlist không chứa `aws`/`pulumi`/`serverless`.
- Review vòng 13: 0 HIGH, 5 MEDIUM, 6 LOW. Agent tự chọn mặc định và gắn nhãn "agent's reading". Đã sửa:
  - Nhóm on-call chỉ co-own path deploy được. Path định nghĩa quy trình (`.github/**`, CODEOWNERS, agent config,
    catalogue) chỉ L3 team duyệt; nếu workflow hỏng ban đêm thì dùng JIT.
  - Team membership quản lý ngoài PR, chưa research (G16). Thêm G17 (thành phần của L3 owner team).
  - Risk stop: author gốc mở PR approval, người duyệt đầu duyệt. Trường hợp người duyệt đầu vắng là câu hỏi mở OQ-B.
  - S10 chia theo phase. Access Analyzer/policy pack có từ phase 2; trước đó OD8 chỉ dựa vào risk stop.
  - Floor version phase 1 ≥ 2.1.248 và ≥ bản sửa advisory high mới nhất.
- Review vòng 14: 0 HIGH, 4 MEDIUM, 9 LOW, đã sửa hết.
  - MEDIUM:
    - Rule OD9 có kẽ hở ban ngày trong ca trực → chỉ được duyệt PR có nhãn `incident`; report đếm mọi approval
      cross-domain trên PR không có nhãn đó.
    - Managed settings: bản thật nằm ở console, git là bản kỳ vọng, so sánh hàng tháng.
    - `autoAllowBashIfSandboxed` là lựa chọn của agent → câu hỏi mở OQ-C.
    - Phase 1 quá tải → thêm danh sách điều kiện cứng và những việc được phép trượt.
  - Thêm dòng AR vào bảng owner decisions: gom các cách hiểu của agent đang chờ owner xác nhận.
- Review vòng 15: 0 HIGH, 3 MEDIUM, 12 LOW. Đã sửa hết MEDIUM và phần lớn LOW. Riêng việc tách đoạn Principle ở Layer 3 chưa làm.
  - MEDIUM:
    - `/status` không in giá trị key → Owner export console hàng tháng để diff; thêm G18.
    - Phase 1 thêm luồng đọc dữ liệu thật tối thiểu; chỉ gỡ broad read roles sau khi luồng này chạy được.
    - Đưa OTel exporter vào phase-1 subset.
  - LOW:
    - Một danh sách L3 path chuẩn ở Layer 5.
    - Ghi rõ catalogue v1 được trượt khỏi phase 1 là lệch so với framing Q8, cần owner đồng ý.
- Review vòng 16: 0 HIGH, 2 MEDIUM, 15 LOW. Đã sửa hết MEDIUM và phần lớn LOW.
  - MEDIUM:
    - JIT chỉ dùng trong sự cố, đúng như owner chấp nhận ở Options §9 Q2.
    - Required check do một GitHub App riêng đặt. Phương án dùng workflow chỉ ghi kèm ⚠️; thêm G19.
  - LOW:
    - Thêm G1/G2: break-glass cho k0s/Firebase.
    - Thêm vai trò "L3 owner team" vào bảng Roles.
    - Ghi mốc phase cho các mục liên quan.
- Review vòng 17: 0 HIGH, 4 MEDIUM, 6 LOW. Đã sửa:
  - Không cho trượt `defaultMode`, allowlist và OTel (D1, OD7b).
  - `deploy-approvals/` ra khỏi danh sách L3 (OD8).
  - Rủi ro phụ thuộc hai GitHub App: key, hosting, sự cố app; mở rộng G19.
  - Thu hồi khẩn cấp ban đêm chưa có người làm (G20).
  - k0s/Firebase thêm vào mục "falls short".
  - Bổ sung review của agent độc lập (GĐ-11).
  - Chưa tách đoạn Principle Layer 3. Chưa đưa `stackPolicy` vào.
- Owner trả lời (chọn qua câu hỏi trắc nghiệm, nguyên văn lựa chọn):
  - Bước tiếp: "Dừng, duyệt mục 1". Owner chấp nhận dừng review sau vòng 17: 0 HIGH. Các MEDIUM của vòng 17 đã sửa
    nhưng chưa có vòng kiểm lại. **Mục 1 được duyệt.**
  - OQ-A → OD10: "1 approval là đủ".
  - OQ-B → OD11: "Được, ghi là lệch".
  - OQ-C → OD12: "Giữ true".
  - Dòng AR (cách hiểu OD8/OD9/L3-JIT của agent) vẫn chờ owner xác nhận.
- Owner xác nhận dòng AR (nguyên văn): "OK, tôi đồng ý." → ghi thành OD13 với 3 điểm:
  - OD8: author gốc mở PR approval, người duyệt đầu duyệt tiếp.
  - OD9: nhóm on-call không co-own các path định nghĩa quy trình và stack SCP.
  - L3-JIT: on-call approver được tính là owner của service.

## 2026-11-09 — Thiết kế mục 2: `docs/adr/`

- Viết 9 ADR, mỗi cái khoảng 420–480 từ, theo template ADR của skill `infra-docs` (bằng tiếng Anh, theo Rule 3), kèm `README.md` làm mục lục:
  - 0001: chỉ thay đổi prod qua PR + CI;
  - 0002: không ai có quyền ghi prod thường trực, agent chỉ đọc metadata;
  - 0003: merge vào `main` là cổng duyệt;
  - 0004: risk stop;
  - 0005: break-glass bằng JIT có thời hạn;
  - 0006: MCP/plugin theo allowlist;
  - 0007: settings của agent là lớp hygiene, không phải ranh giới bảo mật;
  - 0008: OIDC;
  - 0009: agent đứng ngoài PHI.
- Chỉ tóm tắt các quyết định đã có trong framework, không thêm quyết định mới.
- Review ADR vòng 1: 0 HIGH, 5 MEDIUM, 17 LOW, đã sửa.
  - ADR-0006 viết như thể đã biết Papaya dùng MCP cho Linear/Slack → giờ ghi là giả định (⚠️ G9).
  - ADR-0009 bổ sung luồng duyệt ban ngày.
  - ADR-0007 bổ sung rủi ro phase 1 và rủi ro của các lệnh bị loại khỏi sandbox.
  - Thêm ADR-0010 cho mô hình mức rủi ro.
  - Thêm ví dụ vào 0001, 0005, 0006.
- Review ADR vòng 2: 0 HIGH, 2 MEDIUM, 17 LOW. Đã sửa:
  - `--restricted` không thuộc managed settings: trong CI nó là flag, trên laptop là quy tắc quy trình.
  - Ranh giới PHI là mục tiêu, không phải bảo đảm.
  - Phần lớn LOW: sửa trích dẫn (R1.7.10), attribution (GĐ-5/6/8), các chi tiết còn thiếu.
- Review ADR vòng 3: 0 HIGH, 2 MEDIUM, 12 LOW. Đã sửa:
  - ADR-0007 nói quá: trước đây viết "không ghi prod, không đọc PHI".
  - ADR-0003 thêm điều kiện để duyệt lúc merge cũng là duyệt deploy (merge = deploy approval).
  - Sửa các LOW.
  - Rút gọn ADR-0003.
- Review ADR vòng 4: 0 HIGH, 2 MEDIUM, 12 LOW. Đã sửa:
  - ADR-0002 nói quá về "không đọc customer data".
  - ADR-0006 thiếu ý: allowlist thật nằm ở console.
  - Phần lớn LOW.
- Owner duyệt mục 2 (nguyên văn): "sang làm mục 3 nhé." Dừng ở review vòng 4; các sửa của vòng 4 chưa có vòng kiểm lại.

## 2026-11-09 — Thiết kế mục 3: `docs/threat-model.md`
- Viết `docs/threat-model.md`:
  - Có mục assets / actors / trust boundaries.
  - Bảng 16 threat theo cột threat → control (prevent/detect) → evidence → residual risk.
  - Đủ 6 threat bắt buộc (T1–T6, đánh dấu ★), cộng 10 threat lấy từ framework.
  - Cuối file có mục "What the controls do not cover".
- Review threat model vòng 1: 1 HIGH, 8 MEDIUM, 7 LOW. Đã viết lại bảng.
  - HIGH: hook của plugin chạy ngoài sandbox, nên sandbox allowlist không chặn được T3.
  - MEDIUM:
    - Ghi phase cho các control.
    - Chỉ `.claude/` và `.mcp.json` là protected path.
    - Sửa ví dụ T6 sang dữ liệu không phải PHI.
    - Tách phạm vi policy pack (Pulumi) và Access Analyzer (Serverless chưa research).
  - Thêm T9 (CI agent bị nội dung không tin cậy điều khiển). Tổng 17 threat.
- Review threat model vòng 2: 0 HIGH, 5 MEDIUM, 8 LOW. Đã sửa:
  - Allow rule ở user scope trong phase 1.
  - Không có audit event cho branch policy.
  - Ghi phase cho các control còn thiếu.
  - Thêm T18 (code do agent viết làm hỏng tenant isolation) và T19 (injection qua log/ticket trong session sự cố).
- Review threat model vòng 3: 0 HIGH, 4 MEDIUM, 11 LOW. Đã sửa:
  - Caveat cho fresh sign-in.
  - T7: nói rõ control kỹ thuật nào không áp dụng.
  - GitHub token dài hạn: phần PAT chưa research.
  - Thêm T20 (đường ghi prod đi vòng ngoài cổng GitHub).
  - Sửa các LOW. Tổng 20 threat.
- Owner duyệt mục 3 (nguyên văn): "Duyệt, sang mục 4 nhé." Đã chạy 3 vòng review; các sửa của vòng 3 chưa có vòng kiểm lại.
  Chưa quyết việc thêm G21 (GitHub PAT).

## 2026-11-09 — Thiết kế mục 4: bảng đối chiếu problem → control
- Viết `docs/problem-control-map.md`: 40 dòng (P1a–P9c, A1–A13), cột Controls / Evidence / Coverage.
  - Kết quả: Covered 12, Partial 24, Gap 4. Bốn gap: P5b (PAT), P9c (chất lượng review PR lớn), A7a (ngoài phạm vi),
    A12b (data residency); ô control ghi rõ "none".
- Review bảng đối chiếu vòng 1: 0 HIGH, 6 MEDIUM, 9 LOW. Đã sửa:
  - Bốn dòng gắn Covered quá tay (P4c, P7b, A2, A9) hạ xuống Partial.
  - Đổi định nghĩa Gap: phần lõi chưa có control.
  - P1b: cửa sổ grant thực tế có thể tới khoảng 2 h.
  - Số đếm mới: Covered 8, Partial 28, Gap 4.
- Review bảng đối chiếu vòng 2: 0 HIGH, 6 MEDIUM, 9 LOW. Đã sửa: nhãn được áp đúng theo định nghĩa của chính tài liệu (dòng hỗn hợp tính là Partial; control chỉ là quy trình tính là Partial).
  Số đếm mới: Covered 3, Partial 34, Gap 3 (P9c, A7a, A12b).
- Review bảng đối chiếu vòng 3: 2 HIGH (P9b, P5d gắn Covered nhưng còn phần hở), 2 MEDIUM, 9 LOW. Đã sửa.
  - Định nghĩa Covered thêm vế "nothing named left open".
  - Gắn nhãn "[map finding]" cho các gap mới mà framework chưa có.
  - Số đếm mới: Covered 1, Partial 36, Gap 3.
- Review bảng đối chiếu vòng 4: 0 HIGH, 3 MEDIUM, 9 LOW. Đã sửa:
  - P5a hạ xuống Partial, vì không có gì chặn việc thêm lại key.
  - P7b: chưa có định nghĩa ai được tuyên bố incident, đánh dấu [map finding].
  - P8b: lý giải vì sao là Partial.
  - Số đếm cuối: Covered 0, Partial 37, Gap 3.
  - Các sửa của vòng 4 chưa có vòng kiểm lại; trình owner.
- Owner chọn (nguyên văn): "Làm theo hướng (b) nhé". Chia lại thành 4 mức: Covered (phần lõi được ép, có liệt kê residual)
  / Partial / Gap / Out of scope. Kết quả: Covered 11, Partial 26, Gap 2, Out of scope 1.
- Review bảng 4 mức: 1 HIGH (A9 phải là Partial), 3 MEDIUM, 5 LOW. Đã sửa:
  - Ghi ngày có hiệu lực cho các dòng Covered.
  - P3a thêm rủi ro trong cửa sổ JIT.
  - P6b thêm việc chưa có nơi lưu bản ghi phê duyệt JIT.
  - Số đếm cuối: Covered 10, Partial 27, Gap 2, Out of scope 1. Chưa có vòng kiểm lại; trình owner.
- Owner chọn (nguyên văn) "commit đi" sau khi được trình mục 4. Commit gồm framework, ADR, threat model, bảng đối chiếu và
  transcript tới thời điểm này. Trước khi commit đã quét mẫu secret: 0 kết quả.

## 2026-11-09 — Plan deliverable (`work/05-deliverable-plan.md`)
- Đọc docs/ và work/, viết plan: danh sách file nộp (người đọc, độ dài, nguồn), thứ tự viết, examples E1–E10 kèm cách kiểm
  cục bộ và giới hạn của từng kiểm tra, danh sách không đưa vào, 7 câu hỏi cho owner.
- Kiểm cục bộ ✅: schemastore settings schema thiếu `allowedProviders`, `managedSourcesBehavior`; `claude plugin validate` có trong 2.1.319;
  có `mmdc`, `yamllint`, `jq`, `jsonschema`; thiếu `actionlint`, `zizmor`, `checkov`, `pulumi`, `tsc`, `pytest`.
- Phản biện gợi ý của owner: không có environment approval trên Team/private (R3.1.2) → cổng là ruleset `main`; thêm OIDC trust
  (immutable `sub`), SCP, risk stop, catalogue; CrossGuard = Pulumi Policies, tier B.
- Review độc lập vòng 1: 1 HIGH, 9 MEDIUM; vòng 2: 0 HIGH, 3 MEDIUM, 8 LOW; đã sửa hết. Các sửa vòng 2 chưa có vòng kiểm lại. Chờ owner trả lời Q1–Q7.
- Owner trả lời Q1–Q7 của plan: "OK" cho cả 7 đề xuất. **Plan deliverable được duyệt.** Đổi status của `docs/problem-control-map.md`
  thành approved (Q7). Dừng ở review vòng 2; các sửa vòng 2 chưa có vòng kiểm lại.

## 2026-11-09 — Viết bản cuối, bước 0–1
- Commit plan (`21b4b52`). Cài vào scratch (Q5): `actionlint` 1.7.12 (checksum OK), `zizmor` 1.30.1 (`pip --target`, máy không có
  `python3-venv`; 1.31.1 không có wheel tương thích).
- Đổi tên (Q3): `docs/framework.md` → `docs/01-framework.md`, `threat-model.md` → `05-threat-model.md`,
  `problem-control-map.md` → `06-problem-control-map.md`; sửa link trong `docs/`. Các mục cũ trong `work/` giữ tên cũ (lịch sử).
- Bước 1 (layer 3): viết E1 ruleset, E2 CODEOWNERS, E3 workflows, E3b environment, E7 risk stop, `validate.sh`, `examples/README.md`.
  `validate.sh`: 43 test + actionlint + zizmor (auditor) + yamllint + jq đều đạt ✅.
- Phát hiện khi viết example (chưa đưa vào framework):
  - classifier của risk stop phải là path L3 → thêm `/tools/risk-stop/` vào CODEOWNERS [design], **cần owner xác nhận**;
  - hash duyệt phải gồm digest giá trị;
  - `AWS::Lambda::Version` bị thay ở mọi lần đổi code;
  - cú pháp `$/` cho reusable workflow (📖 GitHub docs) mà actionlint chưa biết;
  - `runner.temp` không dùng được trong `env` cấp job.
- Review độc lập bước 1, vòng 1: 1 HIGH, 5 MEDIUM, 8 LOW. Đã sửa:
  - HIGH: `deploy-approvals/claims-api/` không có owner. Sửa: thêm dòng owner, thêm default fail-safe `*` [design],
    thêm test lấy stack từ `deploy-on-main.yml`.
  - MEDIUM:
    - test không chứng minh risk stop chặn được apply → thêm test, có mutation kèm theo;
    - danh sách type để lọt → thêm luật theo tên thuộc tính, ghép danh sách Pulumi/CFN theo cặp;
    - bản duyệt gắn với git: tổ tiên, commit chỉ chạm `deploy-approvals/<stack>/`, tối đa 7 ngày [design];
    - hash Serverless không ổn định → bỏ `Code`/`Lambda::Version` khỏi hash (⚠️ theo trí nhớ).
  - M2 (code của stack chạy với deploy role nên có thể vô hiệu hoá risk stop): chỉ ghi giới hạn trong README,
    phương án mạnh hơn (role preview riêng + tách job) **chờ owner**.
  - LOW:
    - flag được tách token và kiểm theo allowlist;
    - ghi giới hạn của concurrency (không dùng `queue: max` vì thứ tự không bảo đảm, 📖);
    - ghi khoảng hở giữa hai lần preview;
    - `npm ci` chạy trước khi có credential;
    - biến prod chuyển sang environment;
    - bỏ `require_extra_approval_for_unattributed_changes`;
    - xoá code chết;
    - thêm marker nguồn;
    - ghi `$GITHUB_STEP_SUMMARY`;
    - thêm `.gitignore`.
  - Kết quả: `validate.sh` đạt, 54 test ✅.
- Review bước 1, vòng 2: 3 HIGH, 3 MEDIUM, 9 LOW. Agent tự tái hiện H1 trước khi sửa ✅. Đã sửa:
  - H1: approval bị sửa sau khi thêm vẫn được chấp nhận → đọc từ git object, từ chối file đã bị sửa.
  - H2: merge commit cho phép PR tự duyệt → ruleset chỉ cho squash [design], kiểm theo first-parent.
  - H3: re-run deploy cũ làm prod quay lui mà không ai duyệt → bước chỉ deploy đỉnh `main` [design],
    là điều kiện mới cho layer 3.
  - M1: approval merge trước thay đổi rủi ro → thư mục stack và classifier phải không đổi từ stopped commit.
  - M2: luật tên thuộc tính áp cho cả create (tập hẹp), thêm nhóm audit, prefix `aws-native:`.
  - M3: `pulumi install` (📖), policy pack, `serverless --version` (⚠️) chạy trước credential.
  - LOW:
    - test apply theo lệnh, không theo tên step;
    - kiểm tên file và stack;
    - ghi rõ việc dùng lại trong 7 ngày là cố ý;
    - sửa comment, parse URN;
    - link "planned";
    - bảng ánh xạ path;
    - "co-owned";
    - liệt kê các luật [design] mới.
  - Kết quả: `validate.sh` đạt, 60 test ✅.
- Review bước 1, vòng 3: 0 HIGH, 3 MEDIUM, 6 LOW. Các bản sửa trước giữ được; luồng hợp lệ của layer 3 vẫn qua.
  - M1 (approval merge sớm + thay đổi ngoài thư mục stack): **chưa đóng**. Ghi trong README Limits, có test ghi nhận.
    Cách đóng là approval-gate app kiểm hash của run đã dừng (G19) [design], chờ owner.
  - M2: guard dùng `git/ref/heads/main` (✅ endpoint chỉ nhận branch), tag tên `main` không còn lừa được.
  - M3: người duyệt chỉ thấy resource/thuộc tính đổi, không thấy giá trị → sửa câu chữ trong framework ở bản cuối
    (ADR-0004 không sửa được vì đã accepted; cần ghi chú hoặc ADR mới).
  - LOW:
    - tuổi approval tính theo đồng hồ thật;
    - ghi rõ `[skip ci]`, việc mất approval khi stack đổi, và script của `npm ci`;
    - test guard và mainline giờ bắt được mutation;
    - ghi nguồn License Key.
  - Kết quả: `validate.sh` đạt, 62 test ✅. Các sửa của vòng 3 chưa có vòng kiểm lại.
- Owner trả lời (nguyên văn rút gọn: "Đồng ý" cho cả 5 câu, "Không cần chạy vòng 4"). Ghi vào framework thành OD14–OD18:
  - `/tools/risk-stop/` vào danh sách L3;
  - risk stop giữ phạm vi hiện tại, role preview + tách job đưa vào roadmap phase 2;
  - chỉ cho squash merge;
  - chỉ deploy đỉnh `main`;
  - lỗ hở "bản duyệt merge sớm" là giới hạn được chấp nhận, giao G19.
  - Dừng review bước 1 ở vòng 3.
- Commit bước 1 (`b0881c7`).

## 2026-11-09 — Bước 2: identity & access (E4–E6)
- Danh mục IAM action: tải từ Service Authorization Reference dạng máy đọc của AWS ✅ (`servicereference.us-east-1.amazonaws.com`,
  19 service), lưu `examples/schemas/aws-actions.json`. Dùng để mở rộng wildcard, bắt tên action sai, kiểm `IsWrite`.
- Viết:
  - E4: trust OIDC prod (`environment:production`, `sub` dạng immutable) + non-prod (`pull_request`). Không cần `sts:TagSession`
    vì action không gắn tag khi dùng OIDC (📖 README của action).
  - E5: SCP prod OU, phase 2.
  - E6: permission set `ProdReadMetadata`, bỏ các lệnh "metadata" làm lộ config/dữ liệu.
- 14 test mới, 8 mutation đều bị bắt. `validate.sh`: 76 test đạt ✅.
- Phát hiện:
  - SCP "bảo vệ org trail" phần lớn thừa (R2.6.2);
  - một số lệnh đọc metadata làm lộ config;
  - nhãn `IsDataPlane` của AWS không có nghĩa là dữ liệu khách hàng.
- Review độc lập bước 2: đang chạy.
- Review bước 2, vòng 1: 1 HIGH, 4 MEDIUM, 6 LOW. Agent tự kiểm H1 trong docs AWS ✅ trước khi sửa. Đã sửa:
  - H1: ARN role Identity Center không có đoạn region khi identity source ở us-east-1 (📖 referencingpermissionsets)
    → liệt kê cả hai dạng.
  - M1: test lọt các mutation → ghim chính xác principal được miễn, action bị chặn, ARN theo service; `Resource: "*"`
    chỉ cho action `IsList` hoặc allowlist đã xem xét. 9 mutation của reviewer đều bị bắt.
  - M2: điều kiện tiên quyết là opt-in định dạng `sub` mới (R3.4.4) cho repo cũ.
  - M3: tách deploy role Pulumi / Serverless; SCP chỉ miễn role Pulumi (đúng framework layer 1).
  - M4: luật đặt tên của SCP chặn đọc dữ liệu là [design]; điều kiện phase 2 là kiểm kê caller thật.
  - LOW: tên [design]; bỏ `StopQuery`; sửa finding 11; thêm torrent/`StartSyncExecution`, CloudTrail Lake;
    thêm EC2/ELB/`ecs:ListTasks`, cố ý bỏ `ecs:DescribeTasks`.
  - Kết quả: `validate.sh` đạt, 78 test ✅.
- Review bước 2, vòng 2: 1 HIGH, 4 MEDIUM, 7 LOW. Đã sửa:
  - H1 và M4 (code trong job deploy, kể cả install script, xin được OIDC token cho cả hai role): cùng loại với OD15.
    Sửa câu chữ: tách role chỉ chặn drift, không chặn code độc hại. Ghi vào Limits; đưa build job không `id-token`
    và environment riêng cho từng role vào roadmap phase 2 cùng OD15.
  - M1: `Resource: "*"` chỉ cho allowlist tường minh; bỏ tin nhãn `IsList` (nhiều action `IsList` trả dữ liệu).
  - M2: SCP chặn tạo/sửa role có tên được miễn, trừ deploy role của IAM stack [design]; ghi rủi ro còn lại của JIT.
  - M3: sửa finding về trail.
  - LOW:
    - một bước credential cho mỗi tool, không fallback;
    - số service;
    - câu chữ "pinned";
    - placeholder;
    - `secrets.md`;
    - thêm `sqs:StartMessageMoveTask`, `cloudtrail:UpdateEventDataStore`;
    - thêm action metadata cho phân tích sự cố;
    - ghi lỗ hở access point/KMS vào G13.
  - Thêm IAM vào catalogue (22 service). 7 mutation mới đều bị bắt. `validate.sh`: 80 test đạt ✅.
- Owner: "đồng ý" cho OD19 (SCP bảo vệ tên role được miễn) và OD20 (OIDC token toàn job → roadmap phase 2 cùng OD15);
  đồng ý chạy vòng 3 ngắn rồi commit.
- Review bước 2, vòng 3 (ngắn, chỉ phần vừa sửa): 2 HIGH, 2 MEDIUM, 5 LOW. Agent tự kiểm H2 trong API reference ✅ trước khi sửa.
  - H2: `DescribeStackEvents` trả `ResourceProperties` (📖 StackEvent), có thể chứa biến môi trường → bỏ khỏi permission set.
  - H1: "chỉ IAM stack" trong OD19 chưa đúng: role Pulumi deploy mọi stack Pulumi, và theo OD20 job nào cũng lấy được.
    Ghi rõ trong finding 16. Cách hiểu của agent về OD19 (cần owner xác nhận): chỉ đúng sau OD20; trước đó là
    "chỉ một lần deploy Pulumi prod đã duyệt".
  - M1/M2: rủi ro còn lại từ `PassRole` + `CreateFunction`; ràng buộc phase 2 (role `app-claims-*` nằm ở IAM stack,
    tạo trước khi gắn SCP, sửa trust của role Pulumi chỉ bằng cách đổi SCP) → finding 16.
  - LOW:
    - bỏ `StopQuery`/`DescribeQueries`;
    - ghim đủ 10 action IAM;
    - comment `StartMessageMoveTask` và chi phí redrive DLQ;
    - điều kiện cho `states:ListExecutions`.
  - `validate.sh` đạt, 80 test ✅. Theo đồng ý của owner: commit sau vòng 3, không chạy vòng 4; các sửa vòng 3 chưa có vòng kiểm lại.
- Owner xác nhận cách hiểu OD19 ("Đúng"); ghi vào framework và README. Bắt đầu bước 3 (E8–E10).

## 2026-11-09 — Bước 3: agent runtime, supply chain, policy pack (E8–E10)
- Nguồn: template `settings-hipaa.json` của Anthropic ✅ (commit `9196319`); schema settings của schemastore (cộng đồng);
  marketplace reference 📖, xác nhận `sha` cho nguồn plugin (R1.4.1b từ "link only" lên 📖).
- E8: managed settings phase 1 (đúng tập con của layer 8) và phase 2 (baseline đầy đủ).
  Lệch có chủ đích so với template: WebFetch `ask`, không tắt auto mode (D1), `autoAllowBashIfSandboxed: true` (OD12).
- E9: marketplace mẫu (đường dẫn tương đối, `github` và `git-subdir` pin `sha`) + 2 bản ghi review. `claude plugin validate` đạt ✅.
- E10: Pulumi policy pack với 3 policy mandatory.
  - TypeScript 7 không tương thích `@pulumi/pulumi` (peer `< 7`) → pin 6.0.3.
  - Test gọi trực tiếp hàm validate với đối số giả (`isType`), không cần Pulumi engine: 11/11 case đạt ✅.
- `validate.sh` thêm `claude plugin validate` và test policy pack; sửa lỗi `fail` bị mất trong subshell (kiểm bằng mutation).
  Kết quả: 102 test Python, plugin validate, 11 case policy, actionlint, zizmor, yamllint đều đạt ✅.
- 11 mutation cho E8–E10 đều bị bắt. Review độc lập bước 3: đang chạy.
- Review bước 3, vòng 1: 3 HIGH, 4 MEDIUM, 5 LOW. Agent tự tải lại docs (sandboxing, permissions, settings-reference,
  tools-reference, README-hipaa) và tự chạy lại `git log --output` ✅ trước khi sửa; mọi điểm đều đúng.
  - H1: `excludedCommands: ["aws"]` chỉ khớp lệnh `aws` không tham số (📖) → đổi thành `aws *`, `pulumi *`, `serverless *`.
    Docs trả lời luôn ⚠️ "cách khớp lệnh" của framework (finding 22).
  - H2: `Bash(git log|show|diff *)` khớp `--output=<path>` → ghi file tùy ý ✅. Bỏ hết rule git (đã có trong tập read-only
    built-in, 📖); allowlist còn 2 script chính xác. Phase 2 thêm `autoMode.classifyAllShell: true`.
  - H3: policy pack bỏ sót UserPolicy/GroupPolicy, attach AdministratorAccess, `managedPolicyArns`, `iam:Pass*` →
    thêm policy `iam-no-admin-managed-policies` và luật wildcard cho iam/sts/organizations/sso; 27 case ✅.
  - M1: giá trị unknown lúc preview → policy thành advisory ✅ (`server.js`) → ghi giới hạn (finding 23).
  - M2: phase 2 dựng lại từ template, giữ mọi khóa trừ các điểm lệch có lý do; bảng lệch trong README.
  - M3: finding 19 sai lý do (cat/grep chạy không hỏi trong mọi mode, 📖) → viết lại; cách đóng trong phase 1
    (`blockReadsOutsideWorkingDirectories` hoặc deny `Read(~/.aws/**)`, và `classifyAllShell`) đổi OD4 → hỏi owner.
  - M4: thêm `~/.config/gh` vào sandbox credentials, gcloud, Firebase (⚠️ đường dẫn), Docker, các đường dẫn của template.
  - LOW: sửa câu sai về `claude plugin validate` (nó fail khi entry sai ✅); sửa mâu thuẫn trong review `pulumi-helpers`
    và thêm dòng Authentication; ghi giới hạn MDM, `excludedCommands` ở user settings, pin `npx` chỉ top-level;
    test MCP entry đúng một khóa.
  - Còn lại cho bước 6: framework dòng 199/212 và ADR-0007 §3 còn mô tả `excludedCommands` theo cách cũ và gọi
    allowlist là "read-only".
  - 10 mutation mới đều bị bắt. `validate.sh` rc=0: 105 test Python, 27/27 case policy, plugin validate, linter ✅.
- Review bước 3, vòng 2: 0 HIGH, 5 MEDIUM, 8 LOW. Agent tự kiểm lại trên docs (auto-mode-config, sandboxing,
  settings-reference, iam, IAM Action element) trước khi sửa; tất cả đúng.
  - M1: khôi phục 3 pin `"$defaults"` của `autoMode` (thiếu thì danh sách của dev thay thế luật built-in, kể cả luật
    chống exfiltration) + test.
  - M2: thêm `ask` cho `Bash(aws *)`, `Bash(pulumi *)`, `Bash(serverless *)` (auto mode cũng phải hỏi); ghi giới hạn:
    CLI excluded chạy code của repo ngoài sandbox, mà code đó sandbox ghi được không cần hỏi.
  - M3: bỏ `allowManagedReadPathsOnly` (không tác dụng, và làm `blockReadsOutsideWorkingDirectories` không tới sandbox);
    ghi rõ đọc trong sandbox là denylist, egress qua domain được phép; thêm `~/.serverlessrc`,
    `SERVERLESS_ACCESS_KEY`, `PULUMI_CONFIG_PASSPHRASE`; test cấm `*` trong `allowedDomains`.
  - M4: liệt kê chi phí cho engineer (git/gh/npm private, Docker, localhost trên macOS, Windows native, `/goal`);
    skill `prod-change` sửa: engineer push và mở PR.
  - M5: luật wildcard bắt cả `?` (`s3:?*`, `*?`) theo 📖 IAM; 31 case ✅.
  - LOW: E10 nêu rõ phạm vi (ssoadmin, RDS instance, Serverless không có); test thêm các khóa còn lại, MCP package,
    npm `package`; bảng lệch dựng lại từ diff; sửa 2 câu nói quá về `forceLoginMethod` và `allowedHttpHookUrls`;
    template review thêm agents/monitors/LSP/bin; floor 2.1.310 (monitor); đường ngoại lệ khi gỡ cluster.
  - Test mới bắt thêm một lỗ thật: token Firebase chưa có trong `denyWrite` → đã thêm.
  - 12 mutation mới đều bị bắt. `validate.sh` rc=0: 106 test Python, 31/31 case policy, plugin validate, linter ✅.
  - Cho bước 6: framework nêu phase-2 floor 2.1.285 → nay 2.1.310; layer 2 cần thêm các giới hạn trên.
- Review bước 3, vòng 3 (ngắn, chỉ phần vừa sửa): 0 HIGH, 2 MEDIUM (chỉ là câu chữ), 6 LOW. Reviewer xác nhận rule `ask`
  hoạt động đúng ở mọi mode và bảng lệch khớp diff với template. Agent tự kiểm M1/L4 trên docs ✅.
  - M1: "mọi lệnh shell qua classifier" nói quá: lệnh trong sandbox vẫn tự duyệt (OD12) → sửa câu E8, tách
    "giữ từ template" / "lệch của Papaya", đổi tên test.
  - M2: pin `"$defaults"` không phải ranh giới: `autoMode.allow` của dev vẫn nới classifier (📖 "additive") → finding 25.
  - LOW: wildcard ở phần service (`*:*`) → chặn; test giữ đủ danh sách của template (env, deny, denyWrite,
    rule thư mục đúng dạng `/**`); cấm `allowRead`; `sha256` cho phép chữ hoa; bổ sung bảng lệch; `dontAsk`.
  - Mutation: 6 trường hợp reviewer báo lọt nay đều bị bắt (một trường hợp cần sửa test lần hai).
  - `validate.sh` rc=0: 107 test Python, 35/35 case policy, plugin validate, linter ✅.
- Owner: "Đồng ý" OD21 (thêm deny `Read(~/.aws/**)` và `autoMode.classifyAllShell: true` vào phase 1); commit luôn,
  không chạy vòng 4 (các sửa vòng 3 chưa có vòng kiểm lại); làm tiếp các bước còn lại và báo khi xong hết.
  - OD21 ghi vào bảng owner decisions của framework, layer 8 (phase 1), README E8 + finding 19; test mới.
  - `validate.sh` rc=0: 108 test Python, 35/35 case policy ✅.

## 2026-11-09 — Bước 4–8: rollout, register, sơ đồ, đồng bộ, guide, README, review cuối
- Commit bước 3 (`68e38e3`) sau OD21. Owner: làm tiếp đến hết các bước rồi báo.
- Bước 4: tách `docs/03-rollout-plan.md` từ layer 8 (thêm owner, "done when", cột "measured from", ghi rõ là
  phần thêm [design] chờ owner xem). `docs/04-compliance-mapping.md` (register C-01…C-24, walk-through S8,
  O-1…O-9) do một agent soạn, agent chính kiểm anchor, sửa link. Đoạn "Audit evidence" của 8 layer thành
  một câu + link; bảng standards chuyển sang register.
- Bước 5: ba sơ đồ Mermaid, render SVG bằng `mmdc` 11.12.0 ✅, xem PNG để kiểm nhãn bị cắt/đè.
- Bước 6: đồng bộ framework layer 1, 2, 3, 5 với findings của examples và OD14–OD21; sửa câu "Nothing here was
  checked locally"; ADR không sửa (quy tắc ADR), thêm mục "Refinements since acceptance" ở `adr/README.md`
  cho ADR-0003, 0004, 0007; threat model đổi status thành approved, sửa T4 và phase-1 window; map sửa P3b, P8a, P9c.
- Bước 7: `docs/02-engineer-guide.md`, README mới.
- Bước 8: hai review độc lập song song.
  - Review B (README, guide, sơ đồ, link, secret): 1 HIGH, 10 MEDIUM. HIGH: README nói "từ session 2 chạy Manual
    mode" là sai. Agent tự kiểm ✅ `permissionMode` trong transcript: các session làm việc chính đều `auto`, chỉ
    3 session ngắn là `default`. Đã viết lại README cho đúng và ghi là lệch so với `CLAUDE.md`; dòng quyết định
    trong `CLAUDE.md` cần owner đồng ý trước khi sửa. Các MEDIUM khác: README thiếu ngoại lệ k0s/Firebase, thiếu
    chi phí cho engineer và một số điểm "falls short"; guide thiếu phần on-call approver, thay đổi phase 2,
    bước đăng nhập lại trước JIT/data-read, quy tắc store chưa quét; sơ đồ 2 ghi "every API call". Đã sửa hết.
  - Review A (rollout, register, đồng bộ framework): 0 HIGH, 6 MEDIUM. Rollout ghi "không đổi nội dung" nhưng có
    thêm, kể cả một luật mới → bỏ luật đó, ghi rõ phần thêm; walk-through S8 giả định một run = một commit →
    sửa; mất câu về log MCP → thêm vào C-12; threat model/map còn câu cũ → sửa; ADR-0003 thiếu refinement →
    thêm; 📖 không có link → thêm link và một dòng legend. Các LOW chính cũng đã sửa.
  - Framework 10 974 → khoảng 11k từ, trên mục tiêu 9.5–10k (Q1). Reviewer gợi ý chuyển tiếp bảng owner decisions,
    gaps, bảng break-glass; chưa làm vì cần owner quyết.
  - Các sửa của vòng này chưa có vòng review lại.
- Vòng review lại (ngắn, chỉ phần sửa): 0 HIGH, 2 MEDIUM, 6 LOW. MEDIUM: README nói sai "các session ngày 11-08 dùng
  profile mặc định" (chỉ session 1–2); threat model T1 và đoạn "excluded commands" còn mô tả phase 1/auto mode cũ.
  Đã sửa cả 2 MEDIUM và 6 LOW. Không chạy thêm vòng nữa: phần còn lại chỉ là sửa một câu; các sửa này chưa có vòng kiểm lại.
