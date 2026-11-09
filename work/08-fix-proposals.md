# 08 — Đề xuất sửa cho top 10 của review

## English summary

- Proposes a fix for each of the ten top findings in `work/07-review.md` §5, with the reason, the cost to
  engineers, the value to Compliance, the files touched and what must be verified first.
- For each item the owner chooses **Fix**, **Accept risk** (the risk is written into the deliverable as a
  stated limit; no design change) or **Reject** (no change; the reason is recorded here).
- Proposed order: content fixes F1–F9 first, presentation F10 last, because F10 rewrites text that F1–F9 change.
- Per fix: verify the tool facts it relies on (📖 or ⚠️), edit docs and examples, run `examples/validate.sh`,
  then a fresh subagent re-runs the grader role with the challenge text and the grader questions only (not
  this note's conclusions); findings are fixed before moving to the next item.
- Several fixes revise earlier owner decisions (OD2, OD9, OD20); accepted changes are recorded as new
  owner decisions OD22+ in the framework, and as new ADRs where an accepted ADR's decision changes.

> Working note. Updated: 2026-11-09 · Status: chờ owner duyệt
>
> Ký hiệu: ✅ đã kiểm · 📖 có nguồn · ⚠️ chưa kiểm, **phải kiểm trước khi đưa vào deliverable**.

---

## Cách quyết định

| Lựa chọn | Nghĩa là |
|---|---|
| **Sửa** | Làm theo đề xuất (hoặc theo phương án bạn chọn trong mục đó) |
| **Chấp nhận rủi ro** | Không đổi thiết kế; ghi rủi ro vào §1 "Where the design falls short", threat model và compliance register như một giới hạn đã biết, kèm người chấp nhận và ngày |
| **Bác bỏ** | Không đổi gì; ghi lý do bác bỏ vào note này |

---

## F1 · Code đã approve chạy với prod deploy role (A-1) · critical

**Đề xuất (phase 1):**
1. `npm ci --ignore-scripts` trong `deploy-prod.yml` và `pr-preview-nonprod.yml`. Package nào thật
   sự cần install script thì chạy `npm rebuild <pkg>` riêng, và danh sách đó là một L3 path.
2. Đưa OD20 từ phase 2 lên phase 1: mỗi nhóm stack một OIDC subject và một role.
   - IAM stack có environment `production-iam` và role riêng, là role **duy nhất** được tạo hoặc sửa
     các role tên được miễn SCP.
   - Role của domain stack chỉ được tạo role khi gắn kèm một permissions boundary (điều kiện
     `iam:PermissionsBoundary`), và không được đụng tới các tên được miễn.
3. (Tuỳ chọn) Agent review trong CI chạy trên mọi PR chạm `infra/**`. Nó chỉ post review, không phải
   approval (GĐ-11).

**Lý do:** role deploy Pulumi là tài sản quan trọng nhất: được miễn SCP và tạo được role đọc claim
data. Hiện tại, bất kỳ code nào chạy trong deploy job (install script, chương trình Pulumi lúc
preview) đều dùng được role này, trước khi risk stop kịp nhìn thấy. (1) rất rẻ. (2) không chặn được
code độc **trong** stack, nhưng giới hạn thiệt hại từ "cả prod" xuống "một stack". Đây là kết quả lớn
nhất trên mỗi đơn vị công sức trong cả danh sách.

**Chi phí cho kỹ sư:** một số package hỏng khi tắt install script (phải thêm vào allowlist). Thêm
environment và role nên item 1.3 nặng hơn. Lambda role của domain stack phải có boundary.
**Giá trị cho Compliance:** blast radius của một approval sai bị giới hạn theo từng stack; quyền IAM
nhạy cảm có một nơi kiểm soát duy nhất.

**Cần kiểm trước:** `--ignore-scripts` với `npm ci` (📖 npm docs); khoá điều kiện
`iam:PermissionsBoundary` (📖 IAM docs); OIDC subject theo environment (đã có 📖 R3.4.3).
**File:** 2 workflow, `aws/` (trust mới + policy boundary, SCP sửa), tests, framework layer 1/3/5, OD
table (OD22 thay OD20), rollout 1.3/2.9, threat model, ADR README refinement, register C-07.
**Nếu chấp nhận rủi ro:** thêm một gạch ở §1 framework: "approved code runs with the prod deploy role
during preview; fix scheduled for phase 2 (OD20)".

---

## F2 · "Người có tên" chỉ là tài khoản GitHub (C-1) · critical

**Đề xuất:**
1. Thêm mục "GitHub identity" vào layer 1:
   - Org bắt buộc 2FA.
   - Có sổ login GitHub ↔ nhân viên, cập nhật theo joiner/leaver của HR, review hằng quý (mở rộng C-03).
   - Remove khỏi org ngay ngày nghỉ việc; outside collaborator không có quyền write vào monorepo.
2. Thêm vào managed settings phase 1: deny `Bash(gh pr review *)` và `Bash(gh api *reviews*)`. Nếu
   catalogue có GitHub MCP, bỏ tool review của nó. Ghi rõ: đây là hygiene, gọi `curl` thẳng vào API vẫn
   vượt qua được.
3. Register C-04: thêm evidence "sổ login ↔ nhân viên tại thời điểm approve".
4. ADR-0003 option A (Enterprise Cloud): liệt kê những gì nó đóng được (SAML, environment reviewers
   tức là thấy prod diff trước apply, audit-log streaming, G8) và giá theo seat. Để Papaya quyết (đưa
   vào F10, mục "Decisions Papaya must take").

**Lý do:** đây đúng nguyên văn câu của Compliance. Hiện tại chuỗi bằng chứng dừng ở một login. (1)–(3)
gần như không tốn gì. (4) là cách trung thực để nói phần còn lại cần tiền.

**Chi phí cho kỹ sư:** gần như bằng 0; agent không còn approve được qua `gh`.
**Giá trị cho Compliance:** "named person" truy được tới HR record; có control (dù yếu) cho OD5.
**Cần kiểm trước:** yêu cầu 2FA có trên plan Team không, SAML có trên Team không (📖 GitHub docs);
cú pháp của deny rule Bash (📖 permissions doc); giá Enterprise (📖 trang pricing, ghi ngày).
**File:** framework layer 1/3, `managed-settings.phase1.json` (và phase2), tests, register C-03/C-04,
threat model T7, ADR-0003 (thêm phần refinement, không sửa quyết định).
**Nếu chấp nhận rủi ro:** §1 ghi rõ "named = a GitHub account, mapped to a person by process".

---

## F3 · Supply chain chạy trên mọi laptop phá tính độc lập của hai người (A-2, A-3) · critical

**Đề xuất:**
1. Threat model thêm T21: "nhiều danh tính bị chiếm cùng lúc qua một thành phần chạy trên mọi laptop
   (MCP server, plugin, hook, bản Claude Code)". Nối T2, T3, T7 lại với nhau.
2. Layer 4: MCP server cục bộ chỉ được vào catalogue dưới dạng không đổi được: bản build một file
   đóng gói trong một plugin đã pin sha, hoặc image theo digest. Không nhận `npx -y pkg@x`.
3. Repo marketplace: thêm ví dụ ruleset (2 approval từ L3 owners), CODEOWNERS và owner có tên; item
   1.17 "done when" phải gồm những thứ này; pin marketplace vào một ref nếu settings hỗ trợ.
4. Token GitHub trên laptop chỉ lưu trong OS keychain (không lưu plaintext trong file).
5. Approval-gate app cảnh báo khi: approve chưa tới N giây sau push; một approver duyệt PR của nhiều
   author trong vài phút; approve ngoài giờ mà không có incident.
6. **Cần bạn quyết riêng:** 2 approval cho các L3 **process path** (workflow, CODEOWNERS, agent
   config, catalogue, SCP), tức là đảo một phần OD2. Mình đề xuất **có**: các path này đổi luật cho cả
   công ty, ít khi thay đổi, và không bao giờ là việc gấp lúc 2 giờ sáng (on-call vốn không co-own chúng).

**Lý do:** quy tắc bốn mắt giả định hai người độc lập. Một thành phần bị chiếm trên mọi máy cho kẻ
tấn công nhiều login cùng lúc. Threat model hiện tại không thấy điều này vì xét từng threat riêng lẻ.

**Chi phí cho kỹ sư:** onboard một MCP server chậm hơn (phải đóng gói), nên SLA 5 ngày khó giữ hơn;
nếu nhận (6) thì PR process path cần 2 người.
**Giá trị cho Compliance:** tính độc lập của approval có căn cứ; repo nhạy cảm nhất được kiểm soát ở
mức tương xứng.
**Cần kiểm trước:** `allowedMcpServers` có khớp MCP server do plugin cung cấp không; plugin có kèm
MCP server được không; `strictKnownMarketplaces` có hỗ trợ `ref` không (📖 Claude Code docs); `gh`
có lưu token trong keychain không (📖 gh docs).
**File:** threat model, framework layer 4/5, `examples/claude/` (settings, marketplace, ruleset mới
cho repo marketplace), tests, rollout 1.17, ADR-0006 refinement; nếu nhận (6) thì ADR mới thay một
phần ADR-0010/0003 và OD23.
**Nếu chấp nhận rủi ro:** thêm T21 với phần "residual: accepted"; §1 thêm một gạch.

---

## F4 · PHI vào agent qua log "đã redact" (A-1b) · critical

**Đề xuất:**
1. Layer 6: gắn CloudWatch Logs data protection policy (masking) cho mọi log group mà
   `ProdReadMetadata` đọc được, gồm managed identifier và custom identifier (regex số CCCD/ID quốc
   gia, số tài khoản ngân hàng). `ProdReadMetadata` **không** có `logs:Unmask`.
2. Thêm vào SAST (S10): một rule cấm log nguyên event/payload trong handler của các service claims.
3. Điều kiện để mở log group cho `ProdReadMetadata` (item 1.11) gồm cả (1) và (2), không chỉ "redacted
   at source".
4. Layer 3: ghi lý do đổi log level là risky (log debug có thể mang PHI).

**Lý do:** ADR-0009 nói agent đứng ngoài PHI, và IAM chặn đúng là kho dữ liệu, nhưng log group thì
mở. Việc redact nằm trong code ứng dụng, chỉ cần một PR là gãy. Masking ở phía AWS biến ranh giới từ
"code review" thành "code review + một lớp kỹ thuật".

**Chi phí cho kỹ sư:** log bị che một phần khi debug; muốn xem bản gốc phải xin L3-data. Có chi phí
AWS theo GB được quét (⚠️ cần số liệu).
**Giá trị cho Compliance:** "minimum necessary" có control kỹ thuật cho kênh log.
**Cần kiểm trước:** tính năng, quyền `logs:Unmask`, danh sách managed identifier (có loại nào cho dữ
liệu y tế hay ID của VN/TH/HK không), giá (📖 AWS docs). Nếu độ phủ kém, nói rõ masking chỉ là một lớp
phụ.
**File:** framework layer 6/3, permission set E6 (+ test kiểm `logs:Unmask` không có), register C-16,
threat model T17, ADR-0009 refinement, rollout 1.11.
**Nếu chấp nhận rủi ro:** ADR-0009 và §1 ghi "for logs the PHI boundary is code review".

---

## F5 · Không có đường cho DB migration và data fix (E-1) · critical

**Đề xuất:** layer 3 thêm mục "Database changes" và một mức mới **L3-data-write**.
1. **Schema migration:** file migration trong monorepo (của công cụ Papaya đang dùng, không đoán
   tên); job trong deploy workflow chạy sau approval, bằng một DB role cho migration; risk stop có
   thêm luật SQL: `DROP`, `TRUNCATE`, `ALTER ... TYPE`, `DELETE`/`UPDATE` không có `WHERE` thì dừng.
   Khuyến nghị dùng expand/contract.
2. **Data fix:** file `data-fixes/<tenant>/<ticket>.sql` qua PR, được duyệt bởi code owner **và**
   data owner của tenant đó; job chạy trong một transaction với `--expected-rows N`, sai số dòng thì
   rollback; job summary chỉ ghi số dòng, không ghi giá trị.
3. Credential DB của CI: IAM database authentication hoặc Secrets Manager; không có credential DB cho
   người.
4. Incident: đi cùng làn PR.
5. **Bạn chọn mức:** (a) chỉ tài liệu; (b) tài liệu + luật SQL trong `classify.py` có test (mình đề
   xuất phương án này); (c) như (b) + một workflow data-fix mẫu.

**Lý do:** đây là hai loại thay đổi prod phổ biến nhất của một nền tảng claim trên Aurora/Hasura.
Sau item 1.16, hai loại này không còn đường hợp lệ nào, nên chắc chắn sẽ sinh lối tắt (tài khoản DB
dùng chung, admin endpoint), đúng loại mà framework muốn xoá.

**Chi phí cho kỹ sư:** data fix cần PR + 2 người duyệt, chậm hơn `psql`. Đổi lại họ có một đường
hợp lệ, thay vì không có đường nào.
**Giá trị cho Compliance:** SQL thay đổi dữ liệu prod có approval trước khi chạy; A1/A3 chuyển từ
Partial sang Covered.
**Cần kiểm trước:** IAM auth cho Aurora PostgreSQL (📖 AWS docs). Kỹ thuật chặn bằng `WHERE` chỉ là
heuristic, ghi ⚠️.
**File:** framework layer 3/6, ADR mới (0011), engineer guide, register (dòng mới), problem map
A1/A3, threat model; với (b)/(c) thêm `risk-stop/` + tests (+ workflow).
**Nếu chấp nhận rủi ro:** §1 ghi "DB changes have no designed path; until one exists standing DB
access stays" (đây là một câu khó bảo vệ trước hội đồng).

---

## F6 · Kho bằng chứng và thời gian lưu từ phase 1 (C-2, C-3) · major

**Đề xuất:**
1. Thêm item phase 1 (tách khỏi 2.4): một job hằng đêm export những PR đã merge (author, review kèm
   thời gian, check, SHA), log deploy và `risk-summary` vào S3 bật Object Lock trong log-archive account.
2. Kho cho request JIT và data-read từ phase 1: issue Linear theo template bắt buộc (command list,
   scope, tenant, lý do, incident). Approval là hành động của approver trên issue đó. Export hằng đêm
   vào cùng bucket. Nếu sau này chọn TEAM thì kho của TEAM thay thế. Request ID được đưa vào session
   name của grant.
3. Chốt retention: bằng chứng approval và change record 6 năm, Object Lock compliance mode. Log thô
   giao cho compliance owner quyết (O-2 thu hẹp lại).
4. Đóng O-1, O-4; register cập nhật cột "Kept".

**Lý do:** nếu audit rơi vào tháng 4–6, các thay đổi của 60 ngày đầu có thể đã mất bằng chứng (audit
log 180 ngày, log Actions ngắn hơn). Break-glass là luồng auditor sẽ chọn mẫu đầu tiên, nhưng hiện
lại có nguy cơ nằm trong Slack.

**Chi phí cho kỹ sư:** request JIT phải điền form (vài phút). DevSecOps tốn khoảng vài ngày để làm job
(⚠️ ước lượng).
**Giá trị cho Compliance:** S8 khả thi từ phase 1; bằng chứng không sửa được.
**Cần kiểm trước:** trên plan Team có API cho audit log không, hay chỉ export qua UI (📖 GitHub docs).
Nếu chỉ qua UI, export tay hằng tháng là một deviation. Retention mặc định của log Actions (📖).
Linear có lịch sử thay đổi và export được không (📖).
**File:** rollout (item mới), framework layer 7, register (Kept, O-1/O-2/O-4), engineer guide §4/§5.
**Nếu chấp nhận rủi ro:** register ghi "evidence before phase 2 may expire; accepted by …".

---

## F7 · Đường quản trị: Identity Center, management account (C-4) · major

**Đề xuất:** layer 1 thêm mục "Who administers the administrators".
1. Permission set và account assignment quản lý bằng code trong một stack ở management account (L3
   path, chỉ L3 owners). Assignment của automation JIT là ngoại lệ duy nhất.
2. Alert (EventBridge trên CloudTrail của management account) khi có `CreateAccountAssignment` hoặc
   thay đổi permission set mà không đến từ role IaC hoặc role JIT.
3. `OrganizationAccountAccessRole`: kiểm kê; xoá trong prod account, hoặc dùng SCP chặn việc dùng nó
   trừ khi có break-glass đã duyệt.
4. Root của member account: quản lý root tập trung (nếu tính năng có), không giữ credential root.
5. Nêu tên nhóm admin (Identity Center, management account): tối thiểu 2 người, MFA phần cứng, review
   hằng quý (C-03).

**Lý do:** ai quản trị Identity Center thì người đó tự cấp được quyền ghi prod cho mình. Đây là gốc
của lời hứa "không có standing prod write", nhưng tài liệu chưa nhắc tới (✅ grep).

**Chi phí cho kỹ sư:** gần như bằng 0. Admin chậm hơn khi đổi quyền.
**Giá trị cho Compliance:** đóng "privileged access to the access system" (gần ISO 8.2, ⚠️ ID).
**Cần kiểm trước:** tên event của Identity Center; `OrganizationAccountAccessRole` có được tạo mặc
định không; tính năng quản lý root tập trung (📖 AWS docs).
**File:** framework layer 1/7, SCP (+ test), register C-01/C-03, threat model (T22), rollout.
**Nếu chấp nhận rủi ro:** threat model thêm T22 với phần "accepted; detected monthly by assignment export".

---

## F8 · Kubeconfig k0s (A-4) · major

**Đề xuất, phase 1, không chờ G1:**
1. Credential deploy là token của một ServiceAccount, RBAC chỉ trong các namespace deploy, không có
   `secrets`, `pods/exec`, `pods/log`, không đổi được RBAC. Thay đổi RBAC đi L3 path bằng một credential khác.
2. Token có hạn (ví dụ 30 ngày), xoay vòng thủ công theo register; environment `production-k0s` là
   **bắt buộc**, không còn tuỳ chọn.
3. Bật audit log của kube-apiserver trên k0s, đưa về log-archive.
4. Đích dài hạn (thu hẹp G1): kube-apiserver tin trực tiếp OIDC của GitHub, nên không còn credential
   lưu trữ nào.

**Lý do:** ngoại lệ S2 duy nhất rơi đúng vào cluster chạy AI agent đọc tài liệu partner. Nếu lộ thì
không ai phát hiện, và có quyền ghi prod lâu dài. (1)–(3) không phụ thuộc vào việc G1 được giải xong.

**Chi phí cho kỹ sư:** PL phải cấu hình k0s; mỗi tháng xoay token một lần.
**Giá trị cho Compliance:** k0s có dấu vết; blast radius của credential lộ được giới hạn.
**Cần kiểm trước:** khoá cấu hình audit của k0s, cách k0s truyền flag cho API server; xác thực OIDC
dạng structured của Kubernetes và phiên bản tối thiểu; độ dài tối đa của token (📖 k0s/Kubernetes docs).
Tất cả phải dựa trên docs, không đoán phiên bản k0s Papaya đang chạy.
**File:** framework layer 1/5, `environment-production/secrets.md`, G1, register C-14, threat model
T5, rollout 1.15, problem map A5.
**Nếu chấp nhận rủi ro:** register ghi rõ "leaked k0s token undetectable, accepted until G1".

---

## F9 · Nhãn `incident` là lối tắt (E-2) · major

**Đề xuất:** biến OD9 từ process thành control kỹ thuật trong approval-gate app (G19, vốn đã là
required check). Approval của một thành viên on-call trên domain mà họ không thuộc chỉ được tính khi:
1. PR có nhãn `incident`;
2. PR liên kết tới một incident đang mở (phase 1: issue incident trên Linear; phase 2: công cụ paging);
3. người approve là primary/backup đang trực (phase 1: file lịch trong repo, owner là EM; phase 2: API
   của công cụ paging).

Báo cáo hằng tháng liệt kê **mọi** PR có nhãn `incident`, kèm incident ID.

**Lý do:** hiện ai cũng gắn được nhãn, và báo cáo bỏ qua PR có nhãn, nên lối tắt hoàn toàn vô hình.
App đã có trong kế hoạch, nên thêm logic này gần như không tốn thêm hạ tầng.

**Chi phí cho kỹ sư:** lúc 2 giờ sáng phải tạo issue incident trước (vài chục giây). Nếu file lịch cũ
thì approval bị từ chối; khi đó dự phòng là domain owner hoặc backup. App thêm logic nên rủi ro single
point of failure tăng nhẹ.
**Giá trị cho Compliance:** domain review ngày thường được ép bằng kỹ thuật; mỗi lần approve chéo
domain gắn với một incident có thật.
**Cần kiểm trước:** API của GitHub cho review và label (📖); API của Linear (📖). Đây là [design],
chưa có code.
**File:** framework layer 3 (OD9 → OD mới), ADR mới thay phần OD9 của ADR-0003, engineer guide §4/§7,
register C-06/C-10, problem map P7b/A8, G19, rollout 1.6/1.12.
**Nếu chấp nhận rủi ro:** problem map P7b và register C-06 ghi rõ lối tắt này và việc chấp nhận nó.

---

## F10 · Trình bày cho hội đồng (G-1, G-2, G-3) · major

**Đề xuất (làm cuối cùng):**
1. Viết lại §1 framework thành đúng một trang, không dùng mã nội bộ. Nguồn dồn vào một dòng
   "Sources" ở cuối mục.
2. "Owner": **giữ** các ID `OD-n` và `GĐ-n` (đổi tên sẽ làm xáo hàng trăm tham chiếu và test), nhưng
   (a) đổi tiêu đề bảng thành "Author's design decisions", (b) thêm câu "owner = the author of this
   submission, not Papaya", (c) ghi trong chú giải rằng GĐ = giả định (assumption).
3. Thêm bảng **"Decisions Papaya must take"** (README + §1), khoảng 7 mục, mỗi mục có khuyến nghị:
   plan GitHub (F2), số approver cho L3 (OD2/F3), ngoại lệ k0s/Firebase, quy mô rota, HIPAA
   applicability, nhân sự DevSecOps, danh sách coding agent được phép.
4. Thêm mục **"Agent-assisted DevSecOps workflows"** (framework, khoảng 1–1.5 trang, + engineer guide):
   triage incident; agent review bảo mật cho PR; soạn command list JIT và PR codify; giải thích
   risk-summary cho approver; triage finding drift/reconciliation; soạn review record cho catalogue;
   vá dependency. Mỗi workflow ghi: session type, identity, output, người chịu trách nhiệm.

**Lý do:** hội đồng đọc §1 và README trước. Hiện tại hai phần này cần tra cứu file research mới hiểu
được. Đề hỏi Papaya "dùng" agent thế nào, nhưng bài chủ yếu trả lời agent "bị giới hạn" thế nào.
**Chi phí:** chỉ là viết. Rủi ro là tạo mâu thuẫn mới, nên vòng chấm sau mục này sẽ kiểm tính nhất quán.
**File:** README, framework §1 + mục mới, engineer guide, chú giải.
**Nếu chấp nhận rủi ro / bác bỏ:** giữ nguyên trình bày; người chấm phải tự đọc vượt qua mật độ mã.

---

## Quy trình sau khi duyệt

Với mỗi mục được chọn "Sửa", theo thứ tự F1 → F9, F10 cuối:
1. Kiểm các ý "Cần kiểm trước" (WebFetch docs). Ý nào không kiểm được thì ghi ⚠️, hoặc thiết kế vòng
   qua nó.
2. Sửa docs và examples; ghi OD mới vào bảng owner decisions; thêm dòng vào `work/session-log.md`.
3. Chạy `examples/validate.sh`.
4. **Chạy lại vai người chấm** bằng một subagent mới. Nó chỉ được nhận: đề bài, bộ câu hỏi của vai 4,
   và danh sách file. Nó không nhận note này hay kết luận của mình (đúng Rule 4 trong `CLAUDE.md`).
   Mình báo lại kết quả. Finding critical/major mới về **chính mục vừa sửa** thì sửa luôn rồi chấm
   lại; finding ngoài phạm vi thì ghi lại để bạn quyết.
5. Mỗi mục một commit (chỉ khi bạn bảo commit).

## Quyết định của owner

Owner duyệt 2026-11-09 (nguyên văn trong chat: "Đồng ý sửa theo đề xuất" cho cả 10 mục).

| # | Quyết định | Phương án con | Ghi chú |
|---|---|---|---|
| F1 | Sửa | (3) có, theo đề xuất (advisory, không phải approval) | |
| F2 | Sửa | | |
| F3 | Sửa | (6) có: 2 approval cho process path | đảo một phần OD2 |
| F4 | Sửa | | |
| F5 | Sửa | (b) tài liệu + luật SQL trong `classify.py` có test | owner chọn rõ |
| F6 | Sửa | | |
| F7 | Sửa | | |
| F8 | Sửa | | |
| F9 | Sửa | | đổi OD9 từ process sang kỹ thuật |
| F10 | Sửa | | làm cuối |

**Cách chạy (owner cho phép gộp hoặc chạy song song; agent chọn 2026-11-09):**

- **Song song:** bước 1 (kiểm docs). Bước này chỉ đọc, các chủ đề độc lập nhau: 4 subagent
  nghiên cứu (AWS, GitHub, Claude Code, Kubernetes/k0s).
- **Tuần tự, theo nhóm:** bước 2 (sửa). Gần như mọi mục đều sửa cùng các file `01-framework.md`,
  `04`, `05`, `03`, cùng bảng OD và danh sách T-n. Sửa song song sẽ xung đột, và sự nhất quán chính
  là thứ người chấm soi. Bốn nhóm, mỗi nhóm một vòng chấm:
  - **G1** identity & credentials: F1, F7, F8;
  - **G2** approval integrity: F2, F3, F9;
  - **G3** data & evidence: F4, F5, F6;
  - **G4** presentation: F10.

---

## Kết quả các vòng chấm

### Vòng chấm sau G1 (F1, F7, F8) — 2026-11-09

Subagent mới, chỉ nhận đề, câu hỏi vai 4 và danh sách file. Nó tự chạy 132 test (OK), kiểm 9 hàng
research mà docs trích (đều khớp) và kiểm cú pháp `$/` (đúng). 15 finding: 1 critical, 11 major, 3 minor.

| # | Mức | Nội dung (tóm tắt) | Xử lý |
|---|---|---|---|
| 1 | critical | Không có đường cho DB; code SQL trỏ tới mục layer 3 và ADR-0011 chưa tồn tại | Thuộc F5 (G3): đúng như dự kiến, docs của F5 chưa viết |
| 2 | major | Bài nói cách giới hạn agent, ít về cách dùng agent | Thuộc F10 (G4) |
| 3 | major | Chi phí lớn nhất cho Engineering (phase 2: agent không `git push`/`gh`, Docker lỗi, mọi lệnh `aws` hỏi) không có trên README | **Mới, ngoài top 10** → hỏi owner |
| 4 | major | Nhãn `incident` không ai kiểm soát | Thuộc F9 (G2) |
| 5 | major | "Người có tên": phase 1 không deny `Read(~/.config/gh/**)` | Thuộc F2 (G2); nhận gợi ý deny ngay phase 1 |
| 6 | major | Approval-gate app là required check từ E1 nhưng app chỉ có ở 1.6, không phải prerequisite | Liên quan F9 (G2 mở rộng app) → xử lý trong G2 |
| 7 | major | Phase 1 có 20 item, không có ước lượng công sức | Review G-7, ngoài top 10 → hỏi owner |
| 8 | major | GCP, Firebase, quyền người vào k0s chỉ là "same principles" | Review G-4, ngoài top 10 → hỏi owner |
| 9 | major | Thái Lan (PDPA), Hồng Kông (PDPO) không được nhắc | **Mới, ngoài top 10** → hỏi owner |
| 10 | major | Giám sát phân mảnh: chưa có kiến trúc đích | Review G-4, ngoài top 10 → hỏi owner |
| 11 | major | Mật độ mã, "approved by the owner" | Thuộc F10 (G4) |
| 12 | major | Check S10 chỉ có tên; không scan/ký image; không giới hạn cỡ PR agent | **Mới, ngoài top 10** → hỏi owner |
| 13 | minor | k0s secret ghi `production` ở vài nơi, `production-k0s` ở nơi khác; guide §7 thiếu "and you are on shift" | Phần k0s **đã sửa** (framework, T5, A6, P5d); phần OD9 thuộc F9 (G2) |
| 14 | minor | Tham chiếu cũ: OD1–OD21, E1–E10, "25 unit tests", "Ran 108"; ADR-0007/0004 thiếu con trỏ refinement | OD và E range **đã sửa**; số test cập nhật sau G3 (còn đổi); con trỏ ADR thuộc F10 |
| 15 | minor | SKILL `prod-change` tự mâu thuẫn (agent mở PR hay kỹ sư mở PR) | Liên quan F2 (G2) |

### Quyết định của owner sau vòng chấm G1 (2026-11-09)

- **OD27 và OD10:** owner xác nhận: "khi có incident mới được vượt quyền, còn lại ngày thường thì vẫn cần
  owner của từng team". Hệ quả ghi trong OD27 và ADR-0012 là đúng ý owner.
- **Finding mới ngoài top 10 (#3, #7, #8, #9, #10, #12):** owner "chấp nhận sửa hết". Gom thành nhóm
  **G5**, làm sau G3, trước G4 (trình bày làm cuối):
  - F11 (#3): chi phí phase 2 cho Engineering lên README/§1, kèm giảm nhẹ cho `git push`/`gh`;
  - F12 (#7): ước lượng công sức phase 1 và critical path;
  - F13 (#8): mô hình truy cập interim cho GCP, Firebase, người vào k0s; sơ đồ 02;
  - F14 (#9): Thái Lan (PDPA), Hồng Kông (PDPO): chuyển dữ liệu ra nước ngoài, báo cáo vi phạm; slot hồ sơ theo tenant;
  - F15 (#10): kiến trúc đích cho alert và khai báo incident;
  - F16 (#12): check bảo mật cụ thể theo stack, scan/ký image, giới hạn cỡ PR agent.

### Vòng chấm sau G2 (F2, F3, F9) — 2026-11-09

Subagent mới, cùng điều kiện. Nó tự chạy 146 test (OK), kiểm 11 hàng research (đều khớp). 15 finding:
1 critical, 9 major, 5 minor.

| # | Mức | Nội dung (tóm tắt) | Xử lý |
|---|---|---|---|
| 1 | critical | Không có đường cho DB; ADR index nhắc ADR-0011 chưa tồn tại | Thuộc F5 (G3), làm ngay sau |
| 2 | major | Quy tắc đếm approval tự mâu thuẫn (layer 3 "two people, no more", "cross-team: one approval"; sơ đồ 01 node AR, sơ đồ 03 thiếu incident link) | **Đã sửa**: nguyên tắc layer 3, Cost/value, 2 sơ đồ (render lại; sơ đồ 03 lỗi parse vì `;`, đã sửa) |
| 3 | major | Mật độ mã | F10 (G4) |
| 4 | major | Engineering mất log thô và config prod không có hạn; thiếu đường debug prod an toàn cho agent | **Mới** → gộp vào F11 (chi phí Engineering) nếu owner đồng ý |
| 5 | major | Không chứng minh khả thi, không có headcount tối thiểu | F12 (G5) |
| 6 | major | Approval-gate app chưa thiết kế; key không có trong S2 inventory | **Đã sửa** (thiết kế tối thiểu): tài khoản tooling riêng, key trong secrets store và inventory (C-14), fail closed, quy trình gỡ check có kiểm soát |
| 7 | major | Ít workflow agent làm DevSecOps | F10 (G4) |
| 8 | major | GCP chưa có mô hình truy cập; **Expo/EAS và OTA update không được nhắc** | GCP: F13 (G5). Expo/EAS: **mới** → hỏi owner |
| 9 | major | Giám sát/on-call bị hoãn | F15 (G5) |
| 10 | major | Không có store cho approval JIT/data-read | F6 (G3) |
| 11 | minor | C-01 owner "L3 + on-call" trái với OD23 | **Đã sửa** |
| 12 | minor | ADR-0006 còn ví dụ `npx` | **Đã sửa** (refinement) |
| 13 | minor | E-range thiếu E9b, E12; finding 1 còn "needs owner confirmation" | **Đã sửa**; số test cập nhật ở cuối |
| 14 | minor | `gate.py` dùng UTC+7, Hồng Kông là UTC+8 | **Đã sửa**: múi giờ theo approver, thêm test |
| 15 | minor | README: claim `cleanupPeriodDays` không có marker | **Đã sửa** (⚠️) |

### Quyết định của owner sau vòng chấm G2 (2026-11-09)

- G2 #4 (đường debug prod an toàn cho agent; log thô và config prod bị giới hạn không có hạn):
  **gộp vào F11**.
- G2 #8, phần Expo/EAS (release mobile và OTA update có thể đi vòng merge gate): **sửa, thành F17
  trong G5**.
- Hai bản tải docs mà subagent nghiên cứu lưu trong `~/.claude-papaya/projects/`: giữ, không xoá.

### Vòng chấm sau G3 (F4, F5, F6) — 2026-11-09

Subagent mới, cùng điều kiện (chỉ đề bài, bộ câu hỏi vai 4, danh sách file). Nó tự chạy 157 test
(OK), mở 14 hàng research (đều khớp). 15 finding: 1 critical, 10 major, 4 minor. Không finding nào
về masking (F4) hay kho bằng chứng (F6); một finding major về F5.

| # | Mức | Nội dung (tóm tắt) | Xử lý |
|---|---|---|---|
| 1 | critical | Lời hứa "non-prod loop tự do" mâu thuẫn với managed settings phase 2 (`ask` cho mọi `aws`/`pulumi`, sandbox giấu credential git/`gh`) | F11 (G5) |
| 2 | major | Thiếu thiết kế agent được *dùng* cho DevSecOps | F10 (G4) |
| 3 | major | Job `sql` chạy trên runner GitHub không tới được Aurora trong VPC; Hasura metadata cần admin secret, không phải DB role; claim không có marker | **Đã sửa** (F5): job chỉ khởi một ECS task Fargate trong VPC (E15: CI role chỉ `RunTask` một family, một cluster, `PassRole` hai role, một S3 prefix, deny `ExecuteCommand`; task role `rds-db:connect` một user); task kiểm SHA-256 bundle đã phân loại; metadata qua `hasura metadata apply` với admin secret từ Secrets Manager (📖 Hasura CLI, 📖 ECS RunTask); `iam:PassRole` ⚠️; ADR-0011 thêm phương án B'; rollout 1.23; 6 test mới |
| 4 | major | Strict up-to-date + gate chỉ đếm approval trên head commit → mỗi merge làm mọi PR khác stale, phải approve lại | **Mới** → hỏi owner |
| 5 | major | Stack IAM (đổi được role `app-claims-*` và boundary) chỉ cần 1 approver, on-call đồng sở hữu; process paths lại cần 2 | **Mới** → hỏi owner |
| 6 | major | Nhiều đường ghi prod chưa có workflow: GCP (WIF chỉ ở mức org), Firebase, Expo, EC2, SNS, ML model deploy | GCP/Firebase/k0s: F13; Expo: F17. EC2/SNS/ML deploy + bảng kiểm kê đường ghi prod: **mới** → hỏi owner |
| 7 | major | JIT: không thành phần nào kiểm "approver ≠ requester" trước `CreateAccountAssignment` | **Mới** → hỏi owner |
| 8 | major | Rủi ro còn lại ghi "owner chấp nhận", owner là người làm bài | F10 (G4) |
| 9 | major | Phase 1 không ước lượng công sức | F12 (G5) |
| 10 | major | Monitoring/alert chỉ có nguyên tắc | F15 (G5) |
| 11 | major | Đường đọc 15 phút không khả thi; mật độ mã | F10 (G4) |
| 12 | minor | Incident: PR approval của risk stop cũng cần nhãn `incident` và link issue | **Đã sửa**: guide §4 bước 4, sơ đồ 03 (render lại) |
| 13 | minor | README "một ngoại lệ" credential dài hạn (thiếu key của GitHub App); guide nói managed settings "chặn" `gh pr review` | **Đã sửa** |
| 14 | minor | ADR-0003/0010 vẫn "Accepted", còn quy tắc cũ; thiếu L3-data-write; README thiếu data fix cần 2 | **Đã sửa**: status "superseded in part", ghi chú tại chỗ, hàng L3-data-write |
| 15 | minor | examples README: "Ran 108 tests", finding 16 còn `github-prod-deploy-pulumi`, dải E1–E12 | **Đã sửa**: chạy lại `validate.sh` đủ actionlint/zizmor (163 test OK), finding 16, dải E1–E15 |

### Quyết định của owner sau vòng chấm G3 (2026-11-09)

| # | Quyết định | Mục |
|---|---|---|
| 4 | Gate so diff: approval cũ vẫn đếm khi diff của PR so với merge base không đổi | F18 |
| 5 | Stack IAM thành process path: 2 thành viên L3, on-call không đồng sở hữu | F19 |
| 7 | Automation kiểm approver ≠ requester và đang trực rồi mới `CreateAccountAssignment` | F20 |
| 6 (phần còn lại) | Bảng kiểm kê đường ghi prod theo nền tảng, gate chặn từng đường; gộp vào F13 | F13 |

Làm F18–F20 ngay (cùng chủ đề approval), rồi G5 (F11–F17); một vòng chấm chung cho G5 và F18–F20.

**F18–F20 đã làm (2026-11-09):**

- **F18 / OD31:** GitHub tự gỡ approval khi diff của PR đổi (📖 "About protected branches"); gate làm
  theo cùng quy tắc: approval trên commit cũ vẫn đếm nếu patch ID (diff so với merge base,
  `git patch-id --stable`, ✅ có trong git 2.34.1) bằng head; last pusher = người cuối cùng đổi diff.
  Thiếu ID thì không khớp (fail closed). 1 test mới. Ý nghĩa "most recent reviewable push" khi
  "Update branch" chưa có trong docs (⚠️); tần suất phải approve lại đo trong rollout (S4).
- **F19 / OD32:** `infra/pulumi/iam/` và `deploy-approvals/iam/` vào mục L3-only của CODEOWNERS;
  gate áp R3 (2 thành viên L3). Test CODEOWNERS cập nhật. ADR-0003 ghi chú superseded; framework, guide,
  register C-01, danh sách L3 path chuẩn ở layer 5.
- **F20 / OD33:** receiver webhook Linear trong tài khoản tooling (E16 `jit-grant/check.py`, 8 test):
  chữ ký HMAC-SHA256 `Linear-Signature` và tuổi ≤ 60 s (📖 Linear webhooks), người (không phải
  integration) chuyển sang Approved, approver ≠ requester theo user Identity Center, đang trực, incident
  mở, permission set trong allowlist → `CreateAccountAssignment` cho requester 60 phút. Chế độ suy
  giảm: L3 cấp tay theo checklist, alert Identity Center bắt. Shape payload Linear giả định (⚠️).
- ✅ `validate.sh` đủ actionlint/zizmor: 172 test OK.

### G5 đã làm (F11–F17) — 2026-11-09

| Mục | OD | Thay đổi chính |
|---|---|---|
| F11 (+ G2 #4, G3 #1) | OD34 | Bảng "Engineering mất gì ở phase 2 và cái gì bù lại" (layer 2): push/PR ở `!` prompt, cloud CLI chạy thật trong CI, Docker test trong CI, token npm read-only (⚠️ chưa test với sandbox), hạn chót masking log từng service (claims hết phase 2, còn lại day 90) + Logs Insights qua masking (📖 R9.2.7) làm đường debug prod an toàn cho agent; per-group settings cần Claude apps gateway (📖 R1.1.6) → phase 3. README cost row, §1, S4, guide §1 |
| F12 | OD35 | Ước lượng ≈ 75–110 pd (⚠️), critical path qua gate app, phase 1 tối thiểu ≈ 55–80 pd (2 DevSecOps + 1 platform ~45 ngày, hoặc 1–2 người ~60 ngày), chế độ suy giảm (detective) nếu gate app trễ, chỉ khi Compliance chấp nhận bằng văn bản |
| F13 (+ G3 #6) | OD36 | GCP: WIF theo repo + subject `production` (📖 docs WIF; dạng grant theo subject ⚠️), PAM có approval (📖 R9.6.1), Data Access logs (📖 R9.6.3), xác nhận BAA bằng văn bản; Firebase: spike WIF, rollback, preview chỉ từ non-prod; k0s: OIDC cho người, 1 cert break-glass niêm phong; bảng mọi đường ghi prod + gate (layer 3); sơ đồ 02 (+ evidence bucket thay node audit-log cũ); rollout 2.13 |
| F14 | OD37 | Register C-18 (chuyển dữ liệu theo nước), C-26 (báo cáo vi phạm: TH 72 h, VN 72 h, HK tự nguyện), hồ sơ tuân thủ theo tenant, O-10 (OIC), O-11 (IA GL14, PCPD checklist); standards cross-reference thêm TH/HK |
| F15 | OD38 | Định tuyến alert đích: CloudWatch → SNS → paging tool + Slack (Amazon Q Developer), GCP + email/Pub/Sub; không Incident Manager (📖 R9.6.7); 3 mức SEV, escalation, khai báo incident = Linear issue; rollout 2.8 |
| F16 | OD39 | Bảng check S10 cụ thể (license GitHub là quyết định có giá cho Papaya, ≈ $1,470/tháng cho 30 committer ⚠️ số người), Trivy, actionlint/zizmor, `pr-size`; ECR enhanced scanning + managed signing; ruleset E1 thêm 3 check (test cập nhật); rollout 1.8, 2.11 |
| F17 | OD40 | Mobile/Expo trong layer 5: protected channel, robot Release Manager chỉ ở environment `production`, ký update, không EAS Workflows cho prod, đối chiếu hằng đêm; CODEOWNERS `apps/mobile/certs/` (L3); T25; A14; rollout 1.16, 2.12 |

Đồng bộ: problem map (P6a, P7a, P9c, A4–A6, A12a, A12b, A14; Covered 12 / Partial 28 / Gap 0 /
Out of scope 1), threat model (T25, phần không bao phủ), register C-09, C-14, C-22, guide §1, §3.
✅ `validate.sh` đủ actionlint/zizmor: 172 test OK. Tiếp theo: một vòng chấm chung cho G5 và F18–F20.

### Quyết định của owner về phần còn hở của F18–F20 (2026-11-09)

- **F18:** chỉ ghi rủi ro còn lại (cùng patch ID vẫn có thể va chạm ngữ nghĩa với code mới trên
  `main`; CI và risk stop chạy lại trên commit mới) và chấp nhận. Không có điều kiện thử repo thật;
  hành vi của GitHub khi "Update branch" được test khi triển khai thật.
- **F19:** (1) nói rõ thay đổi IAM ban đêm trong stack IAM là hiếm (stack chỉ chứa role miễn SCP và
  boundary; quyền thường ngày của service nằm trong domain stack, role `svc-*`, on-call approve
  được); (2) thêm chỉ số JIT "số lần JIT vì cần đổi stack IAM"; luật incident riêng (on-call + 1 L3)
  chỉ xét khi chỉ số vượt ngưỡng.
- **F20:** đồng ý cả 5: kiểm payload thật khi triển khai; permission set từ label, incident từ quan hệ
  issue; mỗi request ID chỉ cấp một lần (thêm test); Linear qua SSO và vào register danh tính; so sánh
  với mẫu AWS TEAM.

### Vòng chấm sau G5 và F18–F20 — 2026-11-09

Subagent mới, cùng điều kiện. Nó tự chạy 172 test (OK), mở ~35 hàng research (đều khớp, không trích
sai). 13 finding: 0 critical, 8 major, 5 minor.

| # | Mức | Nội dung (tóm tắt) | Xử lý |
|---|---|---|---|
| 1 | major | Role DB lấy được từ mọi job `production`; hash do chính caller chọn | **Đã sửa** (OD42): environment `production-db` + trust riêng (E15, test); job này không cài package, không chạy Pulumi; hash chỉ chứng minh toàn vẹn, approval đến từ việc chỉ code L3 trên `main` chạy được |
| 2 | major | DML trong migration không dừng; tenant không có dòng CODEOWNERS thì mở | **Đã sửa**: kind `dml_in_migration` dừng (test); gate R4 đọc tenant từ path, thiếu team `data-owners-<tenant>` thì fail (test) |
| 3 | major | `secrets.md`, ADR-0008, sơ đồ 02 còn mô tả k0s/Firebase cũ | **Đã sửa**: `secrets.md` liệt kê 5 environment, test `EnvironmentSecretsTest`; ADR-0008; sơ đồ 02 |
| 4 | major | Token Expo và key ký ở `production`, ngoài danh sách ngoại lệ | **Đã sửa**: environment `production-mobile`; README, S2, ADR-0008, C-14, T25 |
| 5 | major | Threat model thiếu tài khoản tooling, key gate app, JIT receiver, webhook secret | **Đã sửa**: T26; policy role receiver (E16) chỉ gán permission set có tag `jit-grant`, deny sửa/tag permission set; resource types ✅ AWS Service Reference (`sso.json`); catalogue thêm `sso`, `rds-db` |
| 6 | major | 45–60 ngày đầu: auto mode + SSO còn quyền ghi prod, không có biện pháp tạm | **Mới** → hỏi owner (đụng D1) |
| 7 | major | Không có so sánh TCO với GitHub Enterprise | **Mới** → hỏi owner |
| 8 | major | Khó đọc; "owner decision" là của người làm bài | F10 (G4) |
| 9 | minor | S1 = 0 không đạt được trong phase 1 tối thiểu (1.7, 1.20) | **Đã sửa**: 1.7 thành prerequisite thứ 8 và vào phase 1 tối thiểu (57–83 pd); S1 ghi rõ ngoại lệ management account đến khi 1.20 xong |
| 10 | minor | Data owner phải có quyền write repo | **Đã sửa** (cùng #2): data owner không là code owner, chỉ cần read |
| 11 | minor | Thay đổi prompt/model/tool của AI agent production không có risk class | **Mới** → hỏi owner (A7a đang out of scope) |
| 12 | minor | Sơ đồ 01 lệch text | **Đã sửa**, render lại |
| 13 | minor | Câu lặp, dải E1–E15, số deny rule | **Đã sửa** |

Cùng lượt: các điểm owner duyệt cho F18–F20 (OD41): rủi ro va chạm ngữ nghĩa ghi lại; F19 nói rõ hiếm
+ chỉ số JIT cho stack IAM; F20 một grant mỗi request (J6, test), label/relation, SSO Linear, so TEAM,
bắt payload thật ở 1.13. ✅ `validate.sh` đủ actionlint/zizmor: 178 test OK (yamllint bắt dòng dài ở
`environment`, đã gập dòng).

**Quyết định của owner cho #6, #7, #11 (2026-11-09), đã làm:**

- **#6 → OD43:** 3 rule `ask` cho `aws`/`pulumi`/`serverless` vào subset phase 1 (may not slip);
  auto mode vẫn cho phép (D1). E8 phase 1 + test; framework layer 2, README, guide §1, rollout 1.18.
- **#7 → OD44:** bảng Team vs Enterprise Cloud (cái gì Enterprise thay: register danh tính, export
  audit log tay, prod diff trước apply; cái gì vẫn tự xây: gate R1–R4/W1, JIT receiver, risk stop,
  đường DB, evidence bucket). Khuyến nghị: lên Enterprise ở phase 2, trước evidence pack đầu tiên,
  nếu ≤ ~100 user (ngưỡng [design], số tiền ⚠️).
- **#11 → OD45:** prompt và model của agent production do team AI sở hữu (không on-call) + required
  check `agent-eval` theo tenant; `tools.yaml` là process path (2 L3). Bảo mật runtime vẫn out of
  scope (A7a ghi rõ). CODEOWNERS, ruleset, 2 test mới; bảng đường ghi prod; C-09.
- ✅ `validate.sh` đủ actionlint/zizmor: 180 test OK.

Còn lại: G4 (F10, trình bày; gồm #8 vòng này) và vòng chấm cuối.

### G4 đã làm (F10, trình bày) — 2026-11-09 → OD46

- `docs/00-executive-brief.md` (mới): ~10 phút, ngôn ngữ thường, không mã; "một ngày làm việc" 5
  tình huống; agent dùng cho DevSecOps; chi phí; điều không giải quyết; bảng giải nghĩa mã.
- Framework §1 viết lại thành một trang: "Who decided" (owner = người làm bài), câu trả lời, bảng
  Engineering/Compliance không mã, bảng **Decisions Papaya must take** (9 mục, có khuyến nghị). Chi
  tiết giới hạn cũ (giữ mã) chuyển xuống §1a.
- Framework §2 (mới): 8 workflow agent cho DevSecOps (session, identity, skill, output, người chịu
  trách nhiệm, metric). Plugin nội bộ thêm 3 skill (`incident-triage`, `risk-summary-explainer`,
  `dependency-fix`), version 0.2.0, pin và review record cập nhật; template `CLAUDE.md` monorepo và PR
  template (E17); guide §8–§9; test cho skill và template.
- "Owner": status line các docs, README, bảng quyết định đổi thành "the author (owner of this
  submission, not Papaya)"; chấp nhận rủi ro JIT ghi "cần Compliance của Papaya ký".
- ADR-0004, ADR-0007 có con trỏ refinement; ADR index thêm refinement cho 0004, 0005, 0007, 0008.
- ✅ `validate.sh` đủ actionlint/zizmor: 183 test OK; kiểm link/anchor nội bộ: 0 lỗi.
- Tiếp: vòng chấm cuối (subagent mới, cùng điều kiện).

### Vòng chấm cuối (sau G4) — 2026-11-09

Subagent mới, cùng điều kiện, thêm câu hỏi kết luận. Kết luận: **"Hire, close to strong hire"**. Nó tự
chạy 183 test (OK), kiểm ~12 hàng research (đều khớp). 12 finding: 5 major, 7 minor. Lưu ý repo: nhiều
file mới đang untracked; cần commit trước khi push (chỉ khi owner bảo).

| # | Mức | Nội dung (tóm tắt) | Xử lý |
|---|---|---|---|
| 1 | major | Quá dày; mã chỉ giải được trong `work/` | **Đã sửa một phần** (G4): brief định nghĩa GĐ dùng trong docs, D1–D3, các tham chiếu "Options §n"; framework trỏ về glossary. Cắt framework/đưa OD ra phụ lục: chưa làm |
| 2 | major | Engineering mất push/PR ở phase 2 vì kiểm soát mà chính bài gọi là hygiene | **Mới** → hỏi owner |
| 3 | major | Công cụ tự xây trên critical path; tiêu đề phase vẫn "0–30" | **Mới** → hỏi owner |
| 4 | major | File SQL data fix đưa dữ liệu cá nhân của tenant vào monorepo | **Mới** → hỏi owner |
| 5 | major | Nửa "dùng agent" còn mỏng | **Đã sửa** (G4): workflow CI review `agent-security-review.yml` + `ci-managed-settings.json` (E18; SHA thật qua `git ls-remote`: claude-code-action v1.0.269, create-github-app-token v3.3.0; input đọc từ `action.yml`), bảng baseline/target cho §2 |
| 6 | minor | Blast radius của code domain stack bị nói nhẹ (role dùng chung trong `production`) | **Mới** → hỏi owner |
| 7 | minor | Session incident vẫn có MCP | **Đã sửa**: `--strict-mcp-config` (✅ `claude --help` 2.1.319) ở framework, T19, guide §4, skill |
| 8 | minor | Plugin nội bộ không force-enable, skill không tải dưới `--restricted` | **Đã sửa**: managed `enabledPlugins` (📖 R1.4.2, R9.4.7) ở 2 phase + test (OD47) |
| 9 | minor | Required check bị path filter có thể treo | **Đã sửa**: mọi required check chạy trên mọi PR, quyết định trong job |
| 10 | minor | Rota on-call chưa định cỡ | **Mới** → hỏi owner |
| 11 | minor | Không nhất quán (T-model phase 2, prerequisite 8 lặp, số ngoại lệ, P8b) | **Đã sửa** |
| 12 | minor | ⚠️ cho `--tools` có thể thành ✅ | **Đã sửa** (✅ `claude --help` 2.1.319) |

✅ `validate.sh` đủ actionlint/zizmor: 186 test OK (zizmor bắt secret ngoài environment → environment
`ci-agent`; job thiếu tên → đã đặt); link/anchor nội bộ: 0 lỗi.

**Quyết định của owner cho #2, #3, #4, #6, #10 (2026-11-09), đã làm:**

- **#4 → OD48:** data fix chỉ dùng ID nội bộ; giá trị nhạy cảm nạp lúc chạy từ values file chỉ task
  trong VPC đọc; required check `data-fix-scan` (E19, 5 test) chặn identifier của E14 và dãy ≥ 9 chữ số.
- **#3 → OD49:** phase 0–45 / 45–75 / 75–100; gate app chạy report-only 2 tuần rồi mới required;
  availability 99.5 % giờ làm việc, alert sau 5 phút, runbook gỡ check được diễn tập.
- **#2 → OD50:** sandbox phase 2 thử trên một team pilot trước; cả công ty chỉ khi S4 đạt; đánh giá
  credential hẹp push/PR cho agent. Pilot cần file endpoint + `managedSourcesBehavior: "merge"`
  (📖 R1.1.4, R1.1.6; cách hoạt động ⚠️ kiểm trong pilot).
- **#6 → OD51:** nói rõ blast radius (role domain dùng chung trong `production`), tách environment theo
  domain là bước tiếp theo; T21 cập nhật. **#10:** không sửa (owner chọn), ghi trong OD51.
- ✅ `validate.sh` đủ actionlint/zizmor: 191 test OK; link/anchor: 0 lỗi.

### #1 (phần còn lại) → OD52 (owner đồng ý 2026-11-09)

- 16 khối chi tiết (§1a, SCP, quản trị Identity Center, GCP/Firebase/k0s, AWS credentials trên
  laptop, vận hành gate app, phê duyệt ban đêm, GitHub plan, risk stop, database, pinning, điều kiện
  credential lưu trữ, Expo, audit stores, drift, alert routing) cùng Gaps và bảng OD chuyển nguyên văn
  sang `docs/07-framework-appendix.md` (mục A–R); framework giữ tên mục và tóm tắt có link, nên các
  tham chiếu theo tên vẫn đúng. Framework 1.309 → 937 dòng.
- ✅ `validate.sh` đủ actionlint/zizmor: 191 test OK; link/anchor: 0 lỗi.

## Vòng chấm sau OD52 (2026-11-09): Hire, 11 finding

| # | Mức | Finding (tóm tắt) | Xử lý |
|---|---|---|---|
| 1 | major | "Minimum safe phase 1" hoãn 1.4 (deploy từ laptop) và 1.8 (check S10) nhưng vẫn gỡ quyền ghi ở phase 1 và ruleset vẫn bắt các check đó; S9–S11, C-09/15/17 lệch | hỏi owner |
| 2 | major | JIT ban đêm cho IAM stack bị chính SCP chặn (chỉ `github-prod-deploy-iam` được miễn) | hỏi owner |
| 3 | major | MDM là điều kiện then chốt nhưng không nằm trong quyết định của Papaya | hỏi owner |
| 4 | major | Khó đọc: chuỗi mã OD/Options; meta-text quá trình review | meta-text đã bỏ; viết lại: hỏi owner |
| 5 | major | Chi phí vận hành tooling tự xây, rota 24/7 chưa định cỡ | hỏi owner |
| 6 | major | Không có runtime riêng cho agent; attribution vẫn Partial | hỏi owner |
| 7 | minor | `--restricted` bỏ Bash (✅ help) nên không hợp cho daily; `Skill` thiếu trong `--tools` | đã sửa |
| 8 | minor | `sls`, `npx …` lọt rule `ask` | đã sửa |
| 9 | minor | Brief "data owner informed" lệch với co-approve; vai trò data owner chưa định nghĩa | câu chữ đã sửa; vai trò: hỏi owner |
| 10 | minor | ★ "named in the task" không chính xác | đã sửa |
| 11 | minor | Tham chiếu cũ sau OD52 | đã sửa (tên `production-k0s` giữ nguyên) |
