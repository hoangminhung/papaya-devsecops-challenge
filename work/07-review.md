# 07 — Review độc lập theo 4 vai

## English summary

- Independent review of the submission (`README.md`, `docs/`, `examples/`, `diagrams/`) against
  `work/00-challenge.md`, from four roles: Engineering lead, Compliance officer, attacker, grader.
- Reviewer: Claude Code in a fresh session that had not seen the work. It is the same model family
  that wrote the work, so this is not a fully independent review; a human review is still needed.
- **Verdict:** the design answers the question and is unusually honest about its limits. Its core
  (IAM + merge gate, not agent settings) is sound. The serious weaknesses are where the "two named
  people" control can be emptied: (1) approved code runs with the prod deploy role before any risk
  check; (2) a GitHub approval proves an account, not a named person; (3) a compromise of something
  every laptop runs (MCP server, internal plugin) gives an attacker many GitHub identities at once,
  so author ≠ approver no longer means two independent people.
- **Missing for Engineering:** no path for DB migrations and data fixes; Serverless IAM must move to
  the Pulumi IAM stack (only stated in `examples/`); the `incident` label is an easy way around
  domain review. **Missing for Compliance:** no evidence retention or JIT approval store in phase 1;
  Identity Center / management-account paths are not covered.
- **Grader view:** strong, Papaya-specific reasoning in many places, but very dense (11.1k-word
  framework full of internal codes). "Owner decisions" read as if Papaya had decided. The *use* of
  agents for DevSecOps work gets little space compared with *restricting* them.
- Top 10 fixes ranked by impact are at the end. Verified non-issue: `uses: $/...` is valid GitHub syntax.

> Working note. Updated: 2026-11-09 · Status: draft review, chưa sửa gì trong deliverable
>
> Ký hiệu: ✅ kiểm trong session này · 📖 có nguồn (link) · ⚠️ từ trí nhớ hoặc suy luận, chưa kiểm.
> Mức độ: **critical** = làm rỗng một lời hứa chính của framework (hai người có tên duyệt, hoặc
> không có standing prod write / PHI) · **major** = kỹ sư sẽ né, auditor sẽ ghi finding, hoặc thiếu
> một phần đề bài · **minor** = sửa cho rõ hoặc cho gọn.

---

## 0. Phạm vi và cách kiểm

- Đã đọc toàn bộ: `README.md`, `docs/01`–`06`, `docs/adr/README.md` + ADR-0003, `diagrams/*.mmd`,
  các example chính (workflows, CODEOWNERS, ruleset, environment, managed settings phase 1/2,
  marketplace, OIDC trust, SCP, permission set, risk-stop approval, đoạn `RISKY_KEY` của
  `classify.py`), `examples/README.md` mục findings 5–17.
- ✅ `examples/validate.sh`: 108 unit test pass, JSON/YAML/policy pack/`claude plugin validate`
  pass; **actionlint và zizmor bị SKIP** (chưa cài), nên các workflow chưa được lint trong session này.
- ✅ Nghi vấn đã loại: `uses: $/.github/workflows/deploy-prod.yml` trong
  [deploy-on-main.yml:15](../examples/github/workflows/deploy-on-main.yml#L15) là hợp lệ. Nguồn
  GitHub docs ghi đây là "the recommended syntax for referencing a reusable workflow in the same
  repository" (📖 [reusable-workflow-calling-syntax.md](https://raw.githubusercontent.com/github/docs/main/data/reusables/actions/reusable-workflow-calling-syntax.md), đọc 2026-11-09).
- Không đọc hết `work/02-research.md` (283 KB). Những chỗ deliverable trỏ vào R*x.y* được coi là đúng
  như nó ghi, trừ khi có lý do nghi ngờ.

---

## 1. Vai Engineering lead

> Câu hỏi: có làm tôi chậm vô lý không? Kỹ sư sẽ tạo lối tắt ở đâu? 2 giờ sáng có thực tế không?

Nhận định chung: luồng hằng ngày (non-prod tự do, một approval, CI deploy) hợp lý và rẻ. Vấn đề nằm ở
những loại thay đổi mà framework **không có đường đi**, và ở các quy tắc process mà người ta né dễ dàng.

### E-1 · critical · Không có đường cho DB migration và data fix

- **Vị trí:** [06-problem-control-map.md:61](../docs/06-problem-control-map.md#L61) (A1: "Database
  schema and data changes have no designed CI path"), [:63](../docs/06-problem-control-map.md#L63)
  (A3); framework layer 3 không nhắc tới; engineer guide không có mục nào.
- **Vấn đề:** Papaya chạy Aurora PostgreSQL + Hasura. Schema migration là thay đổi prod thường gặp
  nhất sau code. Còn data fix (sửa một claim bị kẹt, chạy lại một payout) là việc vận hành hằng tuần
  của một nền tảng bảo hiểm. Sau item 1.16 (bỏ standing prod write), cả hai không còn đường hợp lệ:
  JIT chỉ dùng khi có incident, còn L3-data chỉ cho đọc. Kết quả dễ đoán là một "tài khoản DB dùng
  chung" hoặc một admin endpoint trong app, tức là đúng loại lối tắt mà framework muốn xoá.
- **Đề xuất:** thêm một làn riêng ở layer 3:
  1. Migration là file trong monorepo, chạy bằng job trong deploy workflow (cùng gate, cùng risk
     stop, coi `DROP`/`ALTER ... TYPE`/`DELETE` không có `WHERE` là risky).
  2. Data fix là một script/SQL được review qua PR, rồi một job "data-fix" chạy với role riêng, có
     giới hạn một tenant, ghi output vào change record.
  3. Ghi rõ trong engineer guide. Thêm một dòng ở compliance register (C-04 mở rộng sang SQL).

### E-2 · major · Nhãn `incident` là lối tắt để né domain review

- **Vị trí:** [01-framework.md:329-344](../docs/01-framework.md#L329-L344) (OD9);
  [02-engineer-guide.md:132](../docs/02-engineer-guide.md#L132); P7b ở
  [06-problem-control-map.md:50](../docs/06-problem-control-map.md#L50) tự ghi "who may declare an
  incident or apply the `incident` label: **none**".
- **Vấn đề:** nhóm on-call co-own mọi đường dẫn deployable, và báo cáo hằng tháng chỉ đếm những
  approval chéo domain trên PR **không có** nhãn `incident`. Ai có quyền triage đều gắn được nhãn.
  Lối tắt hiển nhiên là: gắn `incident`, nhờ một người quen trong nhóm on-call approve. Không có báo
  cáo nào bắt được, vì PR có nhãn được coi là hợp lệ. Nhóm on-call sẽ dần thành "nhóm approve nhanh"
  cho mọi thứ.
- **Đề xuất:** cho approval-gate app (vốn đã là required check, G19) kiểm tra luôn quy tắc OD9:
  approval của thành viên on-call trên domain mà họ không sở hữu chỉ được tính khi PR liên kết với
  một incident ID đang mở trong công cụ paging **và** người approve đang trực theo lịch. Báo cáo hằng
  tháng phải liệt kê **mọi** PR có nhãn `incident`, kèm incident ID. Làm vậy, OD9 chuyển từ process
  sang technical với chi phí gần như bằng 0.

### E-3 · major · Chi phí ẩn: IAM của Lambda Serverless phải chuyển sang Pulumi IAM stack

- **Vị trí:** [examples/README.md:294-296](../examples/README.md#L294-L296) (finding 16:
  "Serverless services cannot create their own `app-claims-*` execution roles ... those roles live in
  the Pulumi IAM stack"); trái ngược với [01-framework.md:299](../docs/01-framework.md#L299), nơi
  framework vẫn coi "an IAM statement in `serverless.yml`" là L3 content trong file domain.
- **Vấn đề:** từ phase 2, mọi thay đổi quyền cho Lambda đọc claim data sẽ thành thay đổi xuyên hai
  stack: một PR vào `/infra/pulumi/iam/` (L3 owners + on-call), deploy xong rồi mới tới
  `serverless.yml`. Đây là thay đổi lớn trong cách làm hằng ngày của team claims, nhưng nó chỉ nằm
  trong examples, không có trong framework, engineer guide hay rollout plan. Framework và examples
  đang mâu thuẫn với nhau.
- **Đề xuất:** đưa ràng buộc này vào layer 1/3 và engineer guide §3. Thêm một item phase 2 "chuyển
  execution role của các service claims sang IAM stack" trước 2.2. Sửa dòng L3 ở layer 3.

### E-4 · major · Kịch bản 2 giờ sáng: thực tế ở dạng "best case", chưa phải trường hợp điển hình

- **Vị trí:** [01-framework.md:392-405](../docs/01-framework.md#L392-L405);
  [classify.py:133-137](../examples/risk-stop/classify.py#L133-L137);
  [01-framework.md:249](../docs/01-framework.md#L249).
- **Vấn đề:** kịch bản được chọn (timeout, memory, visibility timeout) né đúng risk stop. Nhưng các
  thao tác incident rất thường gặp lại khớp `RISKY_KEY`: đổi `LoggingConfig`/log level
  (`logging`), đổi DLQ `RedrivePolicy` (`polic`), đổi subnet/security group. Khi đó cần thêm PR
  `deploy-approvals/` và thêm một vòng approve, nên 11–46 phút dễ vượt mốc 30 phút. Ngoài ra, session
  phân tích bị đặt trong "empty scratch directory, not the repo", tức là agent không đọc được
  `serverless.yml` khi chẩn đoán. Kỹ sư sẽ bỏ quy tắc này và chạy một session duy nhất trong repo.
  (Ghi chú: tăng log level lên debug cũng là rủi ro PHI thật, xem A-1b, nên dừng ở đây là đúng; điều
  thiếu là framework không nói ra.)
- **Đề xuất:** (1) thêm một ví dụ incident thứ hai có risk stop, kèm thời gian ước tính; (2) item 1.1
  đo cả trường hợp có risk stop; (3) cho phép session phân tích đọc repo ở chế độ chỉ đọc (repo là
  non-sensitive), chỉ giữ ràng buộc "không có prod write role"; (4) ghi vào layer 3 lý do log-level là
  risky.

### E-5 · major · Tổng ma sát phase 2 đẩy người dùng sang công cụ khác

- **Vị trí:** [02-engineer-guide.md:30-34](../docs/02-engineer-guide.md#L30-L34);
  [01-framework.md:260-264](../docs/01-framework.md#L260-L264) (G11).
- **Vấn đề:** cùng lúc: mỗi lệnh `aws`/`pulumi`/`serverless` đều hỏi (kể cả auto mode), mỗi WebFetch
  hỏi, rule riêng của user/project bị bỏ qua, `git push`/`gh`/Docker/`npm ci` private hỏng trong
  sandbox. Với một công ty "agent-first", lối tắt rẻ nhất là chạy agent **khác** (Cursor, Codex, `claude`
  với API key trên máy không có MDM). Framework chỉ quản Claude Code. Ranh giới IAM vẫn giữ, nhưng S5,
  OTel và mọi bằng chứng về việc dùng agent sẽ mất.
- **Đề xuất:** (1) thêm chính sách "approved coding agents" ở layer 8: ranh giới IAM/merge áp dụng
  cho mọi agent; (2) đặt ngân sách ma sát đo được, ví dụ số prompt mỗi kỹ sư mỗi ngày và tỷ lệ
  `blocked_on_user`, kèm tiêu chí tự động nới một rule khi vượt ngưỡng; (3) bật từng nhóm key phase 2
  một, không bật cả gói một lần.

### E-6 · minor · Hai rota 24/7 cho một tổ chức hiện "on-call informal"

- **Vị trí:** [01-framework.md:636-641](../docs/01-framework.md#L636-L641), OD7.
- **Vấn đề:** mỗi incident đêm cần hai người thức (responder + approver), từ hai lịch riêng, gọi
  bằng điện thoại ở phase 1. Framework thừa nhận "whether Papaya's team size allows full coverage is
  unknown" nhưng không cho con số tối thiểu.
- **Đề xuất:** ghi rõ số người tối thiểu cho mỗi rota bền vững (⚠️ thường được nêu khoảng 5–8 người
  cho rota tuần), và một phương án dự phòng: responder là on-call của service, approver là bất kỳ ai
  trong nhóm on-call trả lời đầu tiên (app kiểm tra ≠ author).

---

## 2. Vai Compliance officer (ISO 27001, HIPAA)

> Câu hỏi: bằng chứng của mỗi control nằm đâu? "Người có tên đã review và approve" truy được bằng
> cách nào? Có đường nào đổi prod mà không để lại dấu vết?

Nhận định chung: register [04-compliance-mapping.md](../docs/04-compliance-mapping.md) tốt hơn mức
thường gặp. Mỗi control có evidence, owner, tần suất; chuỗi S8 đi ngược từ CloudTrail là cách làm
đúng. Lỗ hổng nằm ở ba chỗ: danh tính người approve, nơi lưu và thời gian lưu bằng chứng, và vài đường
quản trị không có trong mô hình.

### C-1 · critical · Approval chứng minh một **tài khoản GitHub**, chưa chứng minh một **người có tên**

- **Vị trí:** [04-compliance-mapping.md:100](../docs/04-compliance-mapping.md#L100) (bước 5);
  [05-threat-model.md:42](../docs/05-threat-model.md#L42) (T7). Không có chỗ nào nói cách gắn GitHub
  login với một nhân viên (✅ grep `SAML`, `personal account`, `GitHub login`: chỉ có câu về agent
  dùng login của kỹ sư).
- **Vấn đề:** đây chính là câu của Compliance. Trên GitHub Team, login thường là tài khoản cá nhân, và
  ⚠️ (theo trí nhớ, cần kiểm) SAML SSO cho org chỉ có ở Enterprise Cloud. Không có quy định bắt buộc
  2FA cho org, không có sổ đăng ký login ↔ nhân viên, không có quy trình joiner/leaver cho GitHub.
  Thêm nữa, agent có thể approve bằng chính login đó (T7), mà không có control kỹ thuật nào. Auditor
  sẽ hỏi: "làm sao biết account `x` là ông A, và chính ông A bấm approve?". Hiện tại câu trả lời là
  "tin vào training".
- **Đề xuất:**
  1. Phase 1: bật "require 2FA" cho org; có một sổ login ↔ nhân viên lấy từ HR, review hằng quý
     (mở rộng C-03).
  2. Managed deny rules cho `Bash(gh pr review *)` và `Bash(gh api *reviews*)` ngay từ phase 1. Rule
     này không phải ranh giới, nhưng nâng rào cản với agent và là bằng chứng rằng policy được áp dụng.
  3. Đưa GitHub Enterprise Cloud (SAML/EMU, environment reviewers, audit-log streaming) thành một
     phương án **có giá** trong ADR-0003, vì nó đóng cùng lúc C-1, G8, "prod diff unseen" và một
     phần C-2 (xem G-5).

### C-2 · major · Bằng chứng phase 1 không có nơi lưu bền và thời gian lưu

- **Vị trí:** cột "Kept" của [04-compliance-mapping.md:35-83](../docs/04-compliance-mapping.md#L35-L83)
  (phần lớn là "O-2", "⚠️ not researched"); [:104-106](../docs/04-compliance-mapping.md#L104-L106);
  G7.
- **Vấn đề:** GitHub audit log giữ 180 ngày (📖 R3.5.6). Log và artifact Actions (gồm
  `risk-summary`) có retention ngắn (⚠️ mặc định khoảng 90 ngày, G7). Export, change record và
  reconciliation chỉ có từ phase 2. Nếu audit ISO rơi vào khoảng tháng 4–6, các thay đổi của 60 ngày
  đầu có thể đã mất bằng chứng. Yêu cầu 6 năm của HIPAA đang dựa vào việc GitHub giữ PR mãi mãi.
- **Đề xuất:** đưa một item lên phase 1: export hằng đêm metadata PR đã merge (author, reviews +
  thời gian, checks, SHA), log deploy và `risk-summary` vào S3 có Object Lock trong log-archive
  account. Quyết định ngay retention cho O-2/O-4 thay vì để mở.

### C-3 · major · Bản ghi approval của JIT và data-read không có chỗ lưu

- **Vị trí:** O-1 ở [04-compliance-mapping.md:151](../docs/04-compliance-mapping.md#L151); A11 ở
  [06-problem-control-map.md:72](../docs/06-problem-control-map.md#L72) tự ghi "it could end up in
  Slack"; JIT có từ phase 1 (item 1.13).
- **Vấn đề:** break-glass và đọc dữ liệu thật là đúng hai luồng auditor sẽ chọn mẫu đầu tiên, vì đó
  là nơi approval-before-apply yếu nhất. Ngay từ phase 1, request và approval của hai luồng này nằm
  "trong một channel không phụ thuộc GitHub", nghĩa là Slack, loại bằng chứng mà chính tài liệu chê.
- **Đề xuất:** chọn ngay một store: issue Linear theo template bắt buộc (command list, scope, tenant,
  approver), approval là một trường hoặc comment của approver, export vào cùng bucket Object Lock như
  C-2. Khoá request ID vào session name của grant để CloudTrail join được.

### C-4 · major · Các đường đổi prod không nằm trong mô hình (hoặc chỉ để lại dấu vết yếu)

- **Vị trí:** layer 1 [01-framework.md:148-164](../docs/01-framework.md#L148-L164); G1, G2; R2.7.1.
- **Vấn đề:** liệt kê đầy đủ:

  | Đường | Dấu vết | Trong tài liệu? |
  |---|---|---|
  | Admin Identity Center tự gán permission set có quyền ghi prod | CloudTrail management event; chỉ thấy ở lần export assignment hằng tháng | **Không**. Không ai được nêu là admin Identity Center; ✅ grep `OrganizationAccountAccessRole`: 0 kết quả |
  | Management account assume `OrganizationAccountAccessRole` (⚠️ được tạo mặc định cho account tạo qua Organizations) | CloudTrail | **Không** |
  | Kubeconfig deploy k0s trong environment secret | **Không có** (k0s chưa có audit, G1) | Có, chấp nhận (OD1) |
  | Token Firebase | Không | Có (G2) |
  | SQL trực tiếp vào Aurora | Không, cho tới khi có activity streams ở phase 2 | Có (⚠️ R2.7.1) |
  | Admin sửa branch policy của `production` qua UI | Có thể không có event | Có (⚠️ R3.1.4, G8) |

  Hai dòng đầu là "gốc" của lời hứa "không có standing prod write": ai quản trị Identity Center thì
  người đó tự cấp được quyền cho mình.
- **Đề xuất:** permission set và assignment quản lý bằng code (L3 path); alert khi có
  `CreateAccountAssignment`/`AttachManagedPolicyToPermissionSet` không đến từ automation của JIT; một
  SCP giới hạn `OrganizationAccountAccessRole` trong prod OU, chỉ cho phép break-glass (⚠️ cần kiểm
  tác dụng phụ); nêu tên nhóm admin Identity Center và management account trong layer 1 và C-03.

### C-5 · major · Chuỗi S8 chưa được chứng minh cho loại thay đổi phổ biến nhất (Lambda/Serverless)

- **Vị trí:** [04-compliance-mapping.md:108-110](../docs/04-compliance-mapping.md#L108-L110).
- **Vấn đề:** khoá join chính là session name `deploy-<run_id>-<attempt>`. Nhưng với Serverless,
  CloudFormation thay đổi tài nguyên bằng `deploymentRole`, nên event "may not carry the run's session
  name (⚠️ not researched)". Lambda là nền tảng chính trong Appendix A, nên điểm yếu này rơi đúng vào
  phần lớn các thay đổi.
- **Đề xuất:** gắn run ID và commit SHA làm stack tag (`provider.stackTags`) và nhúng vào
  description của deployment; kiểm tra cách CloudTrail ghi các call do CloudFormation thực hiện;
  thêm bước này vào item 1.1 (đo trên một service thật).

### C-6 · minor · Register thiếu cách kiểm, và ID ISO chưa đối chiếu

- **Vị trí:** cột "Checked" trong register (chỉ có tần suất); [04-compliance-mapping.md:163-164](../docs/04-compliance-mapping.md#L163-L164).
- **Vấn đề:** auditor cần biết cách chọn mẫu (ví dụ: 25 thay đổi prod ngẫu nhiên mỗi quý, đi ngược
  từ CloudTrail) và tiêu chí pass/fail. ID Annex A "recalled, not read". (Những ID mình đọc thấy đều
  khớp trí nhớ của mình, ví dụ 8.32 change management, 8.31 tách môi trường, nhưng đó cũng chỉ là trí
  nhớ ⚠️.)
- **Đề xuất:** thêm cột "Test procedure" cho C-04, C-08, C-15, C-23; đối chiếu ID với bản ISO có
  license hoặc NIST crosswalk trước khi nộp cho auditor.

---

## 3. Vai kẻ tấn công

> Đi từ (a) tài liệu claim có prompt injection, (b) MCP server độc, (c) plugin nội bộ, (d) token CI
> bị lộ, tới dữ liệu prod hoặc thay đổi prod. Control nào chặn, chặn ở bước nào.

Nhận định chung: đường **trực tiếp** (lấy SSO token rồi ghi prod) bị IAM chặn tốt từ cuối phase 1;
framework đã đúng khi coi settings là hygiene. Các đường thực tế còn lại đều đi **xuyên qua gate**:
code được approve, nhiều danh tính bị chiếm cùng lúc, hoặc credential dài hạn ngoài AWS.

### Bảng đường tấn công

| # | Điểm vào → đích | Các bước | Chặn ở đâu | Kết quả |
|---|---|---|---|---|
| a1 | Claim doc → SSO token → prod | Kỹ sư dán tài liệu vào session → agent `cat ~/.aws/sso/cache/*` → `curl` ra ngoài (phase 1 mạng mở) | Bước đọc: deny `Read(~/.aws/**)` (một phần), prompt/classifier. Bước dùng: **IAM**, token chỉ mở `ProdReadMetadata` + non-prod | Bị chặn ở IAM, **trừ** khi đang có grant JIT/DataRead (T10) |
| a2 | Claim doc → code độc trong PR → deploy job | Injection bảo agent sửa Pulumi program / plugin Serverless / dependency, trộn vào PR lớn → domain owner approve → `pulumi preview` chạy program **với prod role trước risk stop** → gọi SDK lúc runtime (không hiện trong preview) để tạo role `app-claims-*` tin một account ngoài | Chỉ có **review của người** (P9c: "none"); risk stop không thấy gì vì call SDK không phải resource | **Thông**: thay đổi prod + đọc claim data. Xem A-1 |
| a1b | Claim doc → PHI chảy vào log "đã redact" | Agent thêm `console.log(event)` vào handler → PR được approve ("debug log") → PHI vào log group mà `ProdReadMetadata` đọc được → mọi agent và mọi token bị đánh cắp đều đọc được | Chỉ có review | **Thông**: ranh giới "agent không thấy PHI" bị phá. Xem A-1b |
| b | MCP server → nhiều danh tính | Entry đã duyệt `npx -y @example-org/mcp-runbooks@1.4.2` chỉ pin gói gốc; dependency bắc cầu resolve theo semver (⚠️ hành vi npx, cần kiểm) → một dependency bị chiếm → chạy **ngoài sandbox trên mọi laptop** → lấy token `gh` của nhiều kỹ sư | Catalogue (chỉ chặn server chưa duyệt); không có gì ngăn bắc cầu | Kẻ tấn công có author **và** approver. Xem A-2 |
| c | Plugin nội bộ → mọi laptop | `devsecops-guardrails` có `source: "./plugins/..."` (đi theo HEAD của repo marketplace, **không pin**); marketplace trong `strictKnownMarketplaces` cũng không có ref; ruleset của repo marketplace chỉ là "[design]", không có ví dụ, không có item rollout | Chỉ có branch protection (chưa định nghĩa) của repo marketplace | Ai merge được vào repo marketplace thì chạy code trên mọi laptop. Xem A-3 |
| d1 | Dependency trong deploy job → prod deploy role | `npm ci` trong deploy job **có chạy install scripts**, `id-token: write` áp cho cả job ([deploy-prod.yml:89-91](../examples/github/workflows/deploy-prod.yml#L89-L91)) → script xin OIDC token cho `github-prod-deploy-pulumi` (được miễn SCP và được tạo role `app-claims-*`) | Dependency check (sản phẩm chưa chọn, G4); OD20 để sang phase 2 | **Thông**. Xem A-1 |
| d2 | Kubeconfig k0s bị lộ | Lộ qua code chạy trong job deploy k0s, hoặc qua runner self-hosted (G15) → ghi prod k0s, nơi chạy **AI agent đọc tài liệu partner** (PHI) | Không có: không audit, không phát hiện, hạn dùng chỉ ghi trong register | **Thông, im lặng, lâu dài**. Xem A-4 |
| d3 | Lộ khoá GitHub App (approval-gate, CI agent) | Đặt check `approval-gate` thành success, hoặc mở PR | Code-owner review + dòng fail-safe `*` trong CODEOWNERS: approval của app không đủ | Bị chặn ✅ (thiết kế tốt) |
| d4 | Lộ một token GitHub của kỹ sư | Push hoặc mở PR | `require_last_push_approval`, author ≠ approver: cần **danh tính thứ hai** | Bị chặn nếu chỉ lộ một token. Xem b/c: giả định này gãy |

### A-1 · critical · Code đã được approve chạy với prod deploy role trước mọi kiểm tra rủi ro

- **Vị trí:** [deploy-prod.yml:86-91, 139-144](../examples/github/workflows/deploy-prod.yml#L86-L144);
  OD15, OD20 ([01-framework.md:764, 769](../docs/01-framework.md#L764)); P9c
  ([06-problem-control-map.md:55](../docs/06-problem-control-map.md#L55)).
- **Vấn đề:** với Compliance, cả framework dựa trên câu "một người có tên đã approve". Đường a2/d1 cho
  thấy approval chỉ là một lần đọc diff code: approver không thấy prod diff (GitHub Team), PR do agent
  viết thường dài (P9c, không có control), và mã Pulumi/dependency chạy **trong lúc preview**, với role
  được miễn SCP. Tài liệu có nêu giới hạn này (tốt), nhưng xếp cách sửa vào phase 2, dù role này là tài
  sản quan trọng nhất của hệ thống.
- **Đề xuất (đưa lên phase 1, đều rẻ):**
  1. `npm ci --ignore-scripts` trong deploy job (và trong PR preview); chỉ cho phép install script
     cho những package có trong allowlist.
  2. Tách role: preview chạy với role chỉ đọc + ghi state; role apply riêng. OD20 (environment hoặc
     `job_workflow_ref` riêng cho IAM stack) làm luôn ở phase 1.
  3. Dependency của chương trình IaC (`infra/**/package-lock.json`) và `policy-packs/` là L3 path.
  4. Hỗ trợ reviewer: PR do agent viết mang nhãn `agent-authored`; review bằng một agent độc lập là
     **bắt buộc** (vẫn không tính là approval) với PR chạm `infra/**`; đặt giới hạn kích thước PR
     cho path deployable.

### A-1b · critical · PHI có thể vào agent qua kênh log "đã redact"

- **Vị trí:** layer 6 [01-framework.md:554](../docs/01-framework.md#L554) ("logs redacted at
  source"); [permission-set-prod-read-metadata.json:48-59](../examples/aws/permission-set-prod-read-metadata.json#L48-L59).
- **Vấn đề:** việc redact nằm trong code ứng dụng. Bất kỳ PR L2 nào cũng có thể thêm một dòng log
  in ra payload, và log group đó vẫn được `ProdReadMetadata` đọc. Ranh giới "agent stays outside
  PHI" (ADR-0009) vì vậy chỉ được giữ bằng code review, không phải bằng IAM như tài liệu ngụ ý.
- **Đề xuất:** thêm một lớp ở phía AWS: CloudWatch Logs data protection policy (masking bằng
  managed data identifiers; unmask cần một quyền riêng) trên những log group mà `ProdReadMetadata`
  đọc (⚠️ tính năng và độ phủ với dữ liệu y tế/CCCD Việt Nam cần kiểm); thêm một check SAST/lint
  cấm log nguyên payload trong handler claims; coi việc đổi log level là risky (đã có, cần ghi lý do).

### A-2 · critical · Bị chiếm một thứ chạy trên mọi laptop = phá tính độc lập của hai người

- **Vị trí:** [managed-settings.phase1.json:26-37](../examples/claude/managed-settings.phase1.json#L26-L37);
  T2/T3/T7 trong [05-threat-model.md](../docs/05-threat-model.md#L37-L42); layer 4 "[design] pins an
  exact package version in it".
- **Vấn đề:** quy tắc bốn mắt giả định author và approver là hai người **độc lập**. Một MCP server,
  plugin, hook hay bản Claude Code bị chiếm sẽ chạy cùng lúc trên mọi laptop, **ngoài sandbox**, có
  quyền đọc `~/.config/gh` (ví dụ phase 2 chỉ cấm đọc trong sandbox). Kẻ tấn công khi đó có nhiều token
  GitHub cùng lúc: một để làm author, một để approve (nhắm vào thành viên nhóm on-call, vốn co-own mọi
  thứ). Threat model xét T2, T3, T7 riêng lẻ, chưa nối chúng lại. Pin `pkg@1.4.2` trong argv không pin
  được dependency bắc cầu.
- **Đề xuất:**
  1. Thêm threat "nhiều danh tính bị chiếm qua supply chain trên laptop" vào threat model.
  2. Catalogue chỉ nhận MCP server cục bộ dưới dạng bản build có lockfile hoặc image digest, không
     nhận `npx -y pkg@x`.
  3. Token GitHub trên laptop: ngắn hạn, lưu trong OS keychain, không nằm trong file.
  4. Approval-gate app cảnh báo các mẫu bất thường: approve chưa tới N giây sau push, approve ngoài
     giờ mà không có incident, một approver duyệt PR của nhiều author trong vài phút.
  5. Cân nhắc 2 approval cho L3 path (đảo lại OD2 chỉ cho nhóm này). Ít nhất, ghi rõ đây là rủi ro
     còn lại của OD2.

### A-3 · major · Repo marketplace là repo nhạy cảm nhất nhưng được mô tả ít nhất

- **Vị trí:** [marketplace.json:12](../examples/claude/marketplace/.claude-plugin/marketplace.json#L12)
  (plugin nội bộ dùng đường dẫn tương đối, không pin); [managed-settings.phase1.json:17-22](../examples/claude/managed-settings.phase1.json#L17-L22)
  (marketplace không có ref); layer 5 "needs its own ruleset and CODEOWNERS [design]";
  [03-rollout-plan.md:45](../docs/03-rollout-plan.md#L45) (1.17 không nhắc ruleset).
- **Vấn đề:** merge vào nhánh mặc định của repo marketplace = chạy code (hook, MCP, skill) trên mọi
  laptop có token SSO và token GitHub. Repo này cần bảo vệ ít nhất bằng monorepo, nhưng không có ví
  dụ ruleset, không có item rollout, không nói ai là owner.
- **Đề xuất:** thêm vào E1 một ruleset cho repo marketplace (giống `main`, approver thuộc nhóm L3
  owners, 2 approval); item 1.17 "done when" gồm ruleset + CODEOWNERS; xem xét pin marketplace vào
  một ref/tag đã ký (⚠️ kiểm xem `strictKnownMarketplaces` có hỗ trợ ref không).

### A-4 · major · Kubeconfig k0s: credential dài hạn, không phát hiện được, gần PHI

- **Vị trí:** [secrets.md:8](../examples/github/environment-production/secrets.md#L8); OD1/OD6;
  G1, G15; Appendix A ("k0s: workloads for AI agents").
- **Vấn đề:** ngoại lệ S2 duy nhất rơi đúng vào cluster chạy các AI agent đọc tài liệu partner. Nếu lộ:
  có quyền ghi prod, không có audit log, không có cách phát hiện; hạn dùng chỉ là một dòng trong
  register.
- **Đề xuất:** ngay trong phase 1, kể cả khi G1 còn mở: RBAC của credential deploy chỉ cho
  apply/patch trong các namespace deploy, không có `get secrets`, `pods/exec`, `pods/log`; xoay vòng
  theo lịch ngắn bằng một job; bật audit log của kube-apiserver trên k0s (⚠️ cần kiểm cách cấu hình);
  dùng environment riêng `production-k0s` (đang là "optional", nên chuyển thành bắt buộc).

---

## 4. Vai người chấm bài

> Câu hỏi: có trả lời đúng "design the framework and workflow for how Papaya uses coding agents for
> DevSecOps" không? Chỗ nào là văn mẫu, chỗ nào là tư duy riêng, thiếu gì so với đề?

### Trả lời đúng câu hỏi chưa?

Phần lớn là có. Bài giải quyết đúng xung đột giữa hai giọng nói trong đề (§1 framework); có workflow
cụ thể (engineer guide, incident lane, risk stop); có rollout và evidence. Phần **"workflow"** tốt hơn
phần **"how Papaya uses coding agents"** (xem G-3).

### Chỗ thể hiện tư duy riêng (giữ lại, làm nổi bật hơn)

- "The engineer's access is the agent's access": không tạo identity riêng cho agent, mà kiểm soát
  cái kỹ sư nắm giữ ([01-framework.md:118-122](../docs/01-framework.md#L118-L122)). Đây là kết luận
  không hiển nhiên và đúng.
- Merge vào `main` làm gate vì GitHub Team không có environment reviewers cho private repo; các điều
  kiện để "merge approval = deploy approval" thật sự đúng (re-run một run cũ để rollback, chỉ deploy
  tip của main, squash-only).
- Risk stop có file approval gắn với lịch sử git và hash của preview; tự nêu ra những giới hạn của nó
  (OD15, OD18).
- SCP chặn `serverless deploy function` (đi vòng qua CloudFormation); examples finding 11 ("metadata"
  reads làm lộ secret qua `ListFunctions`/`DescribeStackEvents`).
- Phân tích `sandbox.excludedCommands`: `pulumi preview` chạy code trong repo ngoài sandbox.
- Mục "Where the design falls short" và register các gap: hiếm bài nào trung thực như vậy.
- Examples chạy được, có 108 test, và mỗi example ghi rõ nó **không** chứng minh điều gì.

### G-1 · major · Quá dày, mật độ mã nội bộ khiến hội đồng khó đọc

- **Vị trí:** [01-framework.md](../docs/01-framework.md) dài 11.1k từ (✅ `wc -w`; kế hoạch ở
  `05-deliverable-plan.md` là 9.5–10k); ✅ khoảng 384 tham chiếu dạng OD/GĐ/R*x.y* chỉ riêng trong
  framework; §1 "The decision in one page" dài khoảng 75 dòng; `GĐ-n` là chữ viết tắt tiếng Việt nằm
  trong tài liệu tiếng Anh.
- **Vấn đề:** hội đồng gồm Engineering và Compliance. Để hiểu một câu ở §1, họ phải tra
  `work/02-research.md` (283 KB) hoặc framing. Mật độ marker cho thấy sự cẩn thận, nhưng che mất
  quyết định chính.
- **Đề xuất:** §1 đúng một trang, không có mã nội bộ; chuyển mã nguồn xuống chú thích cuối mỗi layer
  hoặc một cột "Source"; đổi `GĐ-n` thành `AS-n` (assumption); một bảng chú giải duy nhất.

### G-2 · major · "Owner decisions" đọc như thể Papaya đã quyết

- **Vị trí:** [README.md:6](../README.md#L6) ("all documents approved by the owner"); bảng OD
  [01-framework.md:743-770](../docs/01-framework.md#L743-L770); ADR "Decided by: owner of this submission".
- **Vấn đề:** người đọc ở Papaya sẽ hiểu "owner decision OD9" là quyết định của một stakeholder bên
  họ. Thực tế đó là quyết định của chính ứng viên, trả lời câu hỏi của agent. Một số OD là những lựa
  chọn mà Papaya **phải** tự quyết (OD2: một approver cho L3; OD1: ngoại lệ k0s; OD12). Nếu trình bày
  như đã chốt, bài mất cơ hội cho thấy ứng viên biết đâu là quyết định của tổ chức.
- **Đề xuất:** đổi tên thành "Author decisions"; thêm một bảng ngắn "Decisions Papaya must take"
  (khoảng 5–7 mục: plan GitHub, OD2, OD1/OD6, quy mô rota on-call, HIPAA applicability, nhân sự
  DevSecOps), mỗi mục có khuyến nghị.

### G-3 · major · Phần "dùng agent cho DevSecOps" mỏng hơn nhiều so với phần "giới hạn agent"

- **Vị trí:** toàn bộ framework; layer 5 chỉ có hai gạch đầu dòng về "Agent review" và "Agents in CI"
  ([01-framework.md:506-514](../docs/01-framework.md#L506-L514)).
- **Vấn đề:** đề hỏi Papaya **dùng** agent thế nào cho DevSecOps. Bài gần như chỉ trả lời "agent bị
  giới hạn thế nào". Những cách dùng đem lại giá trị chỉ được nhắc qua: agent phân tích incident;
  agent review bảo mật cho PR (advisory); agent soạn command list cho JIT và PR codify sau JIT; agent
  giải thích risk-summary cho reviewer; agent phân loại finding drift và reconciliation; agent soạn
  review record cho catalogue; agent vá dependency. Engineering đọc bài sẽ thấy mình mất nhiều hơn
  được.
- **Đề xuất:** thêm một mục ngắn (1–1.5 trang) "Agent-assisted DevSecOps workflows": 5–6 workflow,
  mỗi cái có session type, identity, output và người chịu trách nhiệm. Phần lớn tái dùng các khái niệm
  đã có, nên chi phí viết thấp, nhưng nó cân lại toàn bộ thông điệp.

### G-4 · major · Thiếu so với đề và Appendix A

- k0s (nơi chạy AI agent), GCP (Vertex/Gemini xử lý tài liệu, tức là có PHI) và Firebase: ba trên năm
  nền tảng chỉ có "same principles, mechanism open" (G1–G3). Đây là gap lớn nhất về phạm vi; ít nhất
  cần một trang interim control cho mỗi nền tảng (xem A-4).
- DB migration và data fix: xem E-1.
- Giám sát phân mảnh và on-call informal là hai vấn đề có tên trong đề, nhưng chỉ được xử lý ở mức
  lịch trực; việc hợp nhất alert để sang G5/phase 2 (P6a "Partial"). Cần ít nhất một kiến trúc đích
  (CloudWatch + GCP → một kênh, có owner) dài nửa trang.
- Đa tenant, đa quốc gia: A12b "Gap"; chấp nhận được nếu nói rõ là cần pháp chế, nhưng nên có ít nhất
  một cơ chế (tag tenant trên dữ liệu và grant).

### G-5 · major · Phương án GitHub Enterprise bị loại mà không có con số

- **Vị trí:** ADR-0003 option A ("Cost; not assumed"); GĐ-5.
- **Vấn đề:** một phần đáng kể của độ phức tạp (risk-stop approval PR, approval-gate app tự xây, so
  sánh settings G8, "prod diff unseen", SAML cho C-1, audit-log streaming) tồn tại chỉ vì giả định
  Team. Không có bảng so sánh chi phí license với chi phí xây và vận hành các workaround cho 1–2
  người DevSecOps.
- **Đề xuất:** một bảng "What Enterprise Cloud would close / what it costs" trong ADR-0003; để Papaya
  quyết định (đưa vào G-2).

### G-6 · minor · Các đoạn văn mẫu có thể dán cho bất kỳ công ty nào

- Nguyên tắc layer 8 ("Every control has an owner, a metric and a review date…"); phần lớn layer 5
  (OIDC, pin action, không dùng `pull_request_target`, `GITHUB_TOKEN` restricted); T15/T16. Nội dung
  đúng nhưng là chuẩn chung của GitHub hardening.
- **Đề xuất:** gom thành một checklist có link, dành chỗ cho phần riêng của Papaya (G-3, G-4).

### G-7 · minor · Rollout phase 1 có khả năng không làm kịp, và điều đó làm trễ control chính

- **Vị trí:** [03-rollout-plan.md:124-125](../docs/03-rollout-plan.md#L124-L125) (18 item, 1–2
  người, "effort not estimated"); item 1.6 (một GitHub App tự xây) cộng với
  [ruleset-main.json:32](../examples/github/ruleset-main.json#L32), nơi `approval-gate` là required
  check cho **mọi** merge (single point of failure, kể cả với PR incident).
- **Vấn đề:** nếu phase 1 trễ, 1.16 (bỏ standing prod write, lời hứa chính của bài) trễ theo. Người
  chấm sẽ hỏi "30 ngày có làm nổi không?".
- **Đề xuất:** ước lượng theo person-day cho 6 hard prerequisite; chỉ bắt buộc `approval-gate` khi
  đã có workflow agent mở PR; nêu rõ cần mượn bao nhiêu kỹ sư từ các team.

---

## 5. Top 10 việc nên sửa (xếp theo tác động)

Tiêu chí xếp hạng: (1) có làm rỗng lời hứa chính với Compliance hay không; (2) Engineering có né
được hay không; (3) ảnh hưởng tới điểm chấm; (4) chi phí sửa thấp thì xếp cao hơn khi tác động ngang nhau.

| # | Việc | Từ finding | Mức | Chi phí sửa |
|---|---|---|---|---|
| 1 | Đưa OD20 lên phase 1: `npm ci --ignore-scripts`, tách role preview/apply, IaC deps và policy pack thành L3 path, agent review bắt buộc cho PR `infra/**` | A-1, a2, d1 | critical | thấp–vừa (sửa workflow + 2 role) |
| 2 | Chứng minh "người có tên": 2FA cho org, sổ login ↔ nhân viên, deny `gh pr review` trong managed settings; đưa Enterprise Cloud thành phương án có giá | C-1, G-5 | critical | thấp (tài liệu + settings) |
| 3 | Thêm threat "nhiều danh tính bị chiếm qua supply chain trên laptop"; MCP chỉ nhận bản build có lockfile hoặc digest; ruleset + owner cho repo marketplace; pin plugin nội bộ | A-2, A-3 | critical | vừa |
| 4 | Lớp bảo vệ phía AWS cho log mà `ProdReadMetadata` đọc (data protection policy), check cấm log nguyên payload | A-1b | critical | thấp–vừa |
| 5 | Làn cho DB migration và data fix qua PR + job, có tenant scope | E-1, G-4 | critical | vừa (tài liệu + một ví dụ) |
| 6 | Kho bằng chứng từ phase 1: export PR/run log/risk-summary + approval JIT/data-read vào S3 Object Lock; chốt retention O-2/O-4, store O-1 | C-2, C-3 | major | thấp–vừa |
| 7 | Đóng các đường quản trị: Identity Center as code + alert, giới hạn `OrganizationAccountAccessRole`, nêu tên admin | C-4 | major | thấp (tài liệu + SCP mẫu) |
| 8 | Siết k0s ngay phase 1: RBAC tối thiểu cho credential deploy, xoay vòng, audit log, `production-k0s` bắt buộc | A-4, d2 | major | thấp |
| 9 | Biến OD9 thành control kỹ thuật trong approval-gate app (incident ID + lịch trực); báo cáo mọi PR `incident` | E-2 | major | thấp (thêm logic cho app đã có kế hoạch) |
| 10 | Viết lại cho hội đồng: §1 một trang không mã nội bộ, đổi "owner decisions" thành "author decisions" + "Decisions Papaya must take", thêm mục "Agent-assisted DevSecOps workflows" | G-1, G-2, G-3 | major | vừa (chỉ là viết) |

Ngoài top 10 nhưng nên làm cùng đợt: đưa ràng buộc Serverless IAM vào framework và engineer guide
(E-3); ví dụ incident thứ hai có risk stop (E-4); chính sách "approved coding agents" và ngân sách ma
sát (E-5); con số tối thiểu cho rota (E-6); chuỗi S8 cho Serverless qua stack tags (C-5); chạy
actionlint + zizmor vì session này đã skip.
