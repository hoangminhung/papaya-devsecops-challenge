# 03 — Các phương án (brainstorm)

## English summary

- **Question:** how can a coding agent touch production so that Engineering ships fast while Compliance keeps a named
  human approval for every change?
- **Options considered:** **A** every change is a PR, applied by the CI pipeline; **B** pre-approved operations run as
  SSM Automation runbooks with an `aws:approve` step; **C** time-boxed JIT permission window, agent calls AWS directly
  (Engineering's proposal); **D** the agent as a separate principal hosted on Papaya infrastructure. Two combinations
  were also scored: A + D2 (JIT for incidents) and A + D2' (IaC first, JIT only as a fallback).
- **Comparison:** five criteria scored 1–5 (§5) and a step-by-step 2 a.m. Lambda-config incident for each option (§6).
  C is fastest in incidents but fails the "approved before apply" constraint and carries the highest residual risk.
- **Owner decision (2026-11-09, §9):** **A + D2'**, because it balances process and incident speed. The PR pipeline is
  the default for every prod change, incidents included; a JIT window is used only when that path is unavailable and
  after approval, accepted as meeting the approval constraint only partially. Incident target: ≤ 30 min, decision to apply.
- **Follow-ups:** measure the incident PR lane on a real service (estimated up to ~46 min, unmeasured); verify B early;
  14 open checks in §8.

> Working note (Vietnamese). Mục đích: có các phương án **khác nhau về bản chất** cho câu hỏi trung tâm, so sánh
> chúng, rồi để owner chọn. File này **không** viết framework đầy đủ.
>
> Updated: 2026-11-09 · Status: draft v4 (viết lại sau 3 vòng review độc lập), owner đã chọn A + D2' (mục 9)

Ký hiệu (theo Rule 1 trong `CLAUDE.md`):
- ✅ / 📖 / ⚠️ như trong `CLAUDE.md`. Một tham chiếu kiểu "(02-research 3.1.2)" nghĩa là dòng đó trong research
  đã có nguồn và marker riêng; ở đây tôi chỉ dùng lại, và giữ marker gốc khi nó là ⚠️.
- **[TK]**: ý thiết kế của tôi, chưa ai kiểm chứng (một dạng ⚠️). Mọi con số thời gian trong file là ⚠️ ước lượng.
- GĐ-n: giả định trong `work/01-problem-framing.md` §4. D1–D3: quyết định của owner trong `02-research.md` 6.6.
- Hai trang AWS mới được đọc trong phiên này (bản `.md`, 2026-11-09, ✅):
  [automation-action-approve](https://docs.aws.amazon.com/systems-manager/latest/userguide/automation-action-approve.html),
  [change-manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/change-manager.html).

---

## 0. Câu hỏi, ràng buộc, phần chung

### 0.1 Câu hỏi trung tâm và các phương án khác nhau ở đâu

> Coding agent được chạm vào production như thế nào để Engineering vẫn ship nhanh, mà Compliance vẫn có
> "một người có tên đã review và approve" cho mọi thay đổi?

Theo framing §3.1, mâu thuẫn thật chỉ nằm ở **ghi vào prod**. Các phương án khác nhau ở bốn điểm của con đường ghi:

1. **Cái được duyệt là gì:** một diff code (A), một thao tác cụ thể (B), một cửa sổ quyền (C), hay một lượt chạy của agent (D).
2. **Ai thực thi:** pipeline CI, một runbook tất định (deterministic), agent/người trên laptop, hay agent trên hạ tầng Papaya.
3. **Identity nào mang quyền ghi prod:** role của pipeline, role của runbook, role JIT của người, hay role riêng của agent.
4. **Agent chạy ở đâu** khi chạm prod: laptop hay môi trường do Papaya kiểm soát.

Nói thẳng về mức khác biệt:
- **A, B và D dùng chung luồng PR + pipeline cho thay đổi code/IaC thường ngày.** Ba phương án này khác nhau chủ yếu
  ở **đường sự cố và thao tác ngoài IaC**.
- Chỉ **C** khác cả ở luồng thường: C là đúng đề xuất của Engineering, agent gọi AWS trực tiếp cho cả thay đổi thường.
- Ma trận (mục 5) vì vậy tách tốc độ thành hai hàng.

**Thao tác nào là IaC, thao tác nào không** (cách chia dùng trong cả file, [TK]):
- **Diễn đạt được bằng IaC:** timeout/memory/reserved concurrency của Lambda, desired count của ECS, kích thước và
  cấu hình tài nguyên. Điều kiện là chúng đang được khai báo trong Pulumi/Serverless.
- **Ngoài IaC:** restart một ECS service (force new deployment), redrive DLQ, purge queue, xoá cache.
- Tỉ lệ sự cố cần thao tác ngoài IaC ở Papaya **không biết** (⚠️). Tỉ lệ này ảnh hưởng trực tiếp tới khuyến nghị (mục 7).

### 0.2 Ràng buộc và đầu vào (D2 được so sánh lại ở mục 5 và 7)

| Ràng buộc | Nguồn |
|---|---|
| Mọi thay đổi prod được duyệt **trước** khi áp dụng, kể cả trong sự cố | GĐ-8 |
| Thời gian **chờ duyệt** trong sự cố ≤ 15 phút, 24/7. S7 đo thời gian chờ duyệt, **không** đo end-to-end; framing chưa có mục tiêu end-to-end (mục 9 Q3) | S7 |
| Người duyệt khác người làm (tác giả và agent tạo thay đổi); agent không được tính là người duyệt | GĐ-11 |
| Không còn quyền ghi prod thường trực gán cho người | S1 |
| GitHub **Team**, không merge queue: không có required reviewers ở environment cho repo private; cổng duyệt là merge PR vào `main` qua rulesets | GĐ-5; 02-research 3.1.2, 3.6 #1, 3.7 |
| Agent không chạm PHI; mặc định chỉ đọc metadata; đọc dữ liệu thật là ngoại lệ có duyệt | GĐ-9; 02-research 1.9, 5.8 |
| Non-prod chỉ có dữ liệu synthetic, nên vòng lặp non-prod tự do | GĐ-14 |
| 100% PR vào nhánh deploy chạy secret scan, kiểm tra dependency và SAST | S10 |
| Không thay Pulumi, Serverless, GitHub Actions | `CLAUDE.md` |
| Đội 20–60 engineer, DevSecOps 1–2 người | GĐ-1 ✔ |
| Managed settings mặc định Manual; `--restricted` cho session phân tích và CI; nguyên tắc "ma sát tỉ lệ với thiệt hại" | D1, D3, 02-research 6.8 |
| **Sự cố (D2):** agent phân tích bằng identity read-only; người trực chạy lệnh ghi trong terminal riêng có quyền JIT hẹp, TTL ngắn; mọi thay đổi tay được codify bằng PR, có drift detection; đây là kiểm soát bằng quy trình; giai đoạn sau: break-glass từ môi trường không cài agent | D2 |

**Giả định chưa xác nhận nhưng ảnh hưởng tới khuyến nghị:** GĐ-12 (lộ trình ~90 ngày, ngân sách công cụ nhỏ) vẫn là [GĐ].

### 0.3 Phần chung cho mọi phương án (không phải điểm khác biệt)

- **Không ai có quyền ghi prod thường trực**, người hay agent (02-research 2.9 #2).
- **Không còn credential dài hạn trong CI**: GitHub OIDC sang AWS/GCP (02-research 3.4, 3.6 #2).
- **Agent đọc prod** bằng một identity read-only chỉ thấy metadata. SCP chặn data plane trên bucket/queue chứa PHI
  (02-research 2.9 #4).
- **Claude Code managed settings là lớp vệ sinh, không phải kiểm soát chính** (02-research 1.1.7 ✅, 1.8 #1).
- **Audit nền:**
  - Organization CloudTrail đổ về log-archive account, có integrity validation (02-research 2.9 #5).
  - GitHub org audit log giữ 180 ngày, nên phải export (02-research 3.5.6, 3.6 #6).
  - Bản ghi phê duyệt và thay đổi giữ ≥ 6 năm (02-research 5.7 #2).
- **Chặn đường vòng của Lambda, và ngoại lệ của nó.**
  - 02-research 4.6 #3 đề xuất deny `lambda:UpdateFunctionCode` và `lambda:UpdateFunctionConfiguration` với mọi
    principal trừ CloudFormation `deploymentRole` (SCP hay IAM: ⚠️ chưa chọn).
  - Mọi đường ghi ngoài pipeline (runbook của B, JIT của C/D2, role của D) phải là một **ngoại lệ có tên** trong lệnh deny đó.
  - Mỗi ngoại lệ phải có alert khi được dùng, và mỗi lần dùng là một tín hiệu drift [TK].

### 0.4 Các hướng đã loại trước khi so sánh

| Hướng | Lý do loại |
|---|---|
| Làm trước, duyệt sau (break-glass không duyệt) | Trái GĐ-8. Owner đã bác ở vòng 1 của framing. |
| Dùng permission prompt, hook hoặc managed settings của Claude Code làm cổng duyệt | Chạy phía client, bypass được (02-research 1.1.7, 1.1.8). Bash rule không phải ranh giới bảo mật (1.2.6 ✅). Người bấm "approve" trong prompt cũng là người làm (GĐ-11). |
| Agent có permission set riêng trên laptop, còn người vẫn giữ quyền ghi prod | Agent dùng chung SSO cache với người và với mọi role của người, nên không tách được (02-research 2.9 #1). |
| Cổng duyệt ở GitHub Environment (required reviewers) | Không có trên Team cho repo private (02-research 3.1.2 ✅). Chỉ là biến thể của A nếu Papaya lên Enterprise Cloud. |
| AWS Systems Manager **Change Manager** | "will no longer be open to new customers starting November 7, 2025" ✅. Chỉ dùng được nếu Papaya đã đăng ký trước ngày đó (⚠️ không biết). |

---

## 1. Phương án A — "Mọi thay đổi là một PR" (pipeline-only)

**Một câu:** agent chỉ viết code; thay đổi prod duy nhất là merge một PR đã được người khác duyệt, sau đó pipeline
áp dụng. Không có đường ghi nào khác, kể cả trong sự cố.

A có hai mức, chấm riêng ở mục 5:
- **A lõi:** PR + pipeline cho mọi thứ diễn đạt được bằng IaC.
- **A đầy đủ:** A lõi cộng "ops-as-code" cho thao tác ngoài IaC.

- **Identity agent dùng:**
  - Laptop: identity của engineer cho git/PR. AWS chỉ có quyền non-prod và role read-only metadata cho prod.
  - Chỉ role deploy của pipeline ghi được prod. Role này trust qua OIDC `sub` = `environment:production`, nên ghim
    thêm reusable workflow (02-research 3.6 #2).
- **Luồng thay đổi thường:**
  1. Agent sửa Pulumi / `serverless.yml` / code, chạy preview trên **non-prod**. PR không được cầm credential prod,
     vì preview chạy code của PR và đọc được secret (02-research 4.6 #2).
  2. Mở PR bằng identity của engineer. GitHub không cho tác giả tự duyệt (02-research 3.3.1 ✅).
  3. Rulesets: cần approval, code owner, dismiss stale "when the diff changes", "require an approval from someone
     other than the last person to push", bypass list rỗng (02-research 3.2.3 ✅, 3.6 #1). Yêu cầu branch phải up-to-date là suy luận trong 02-research 4.6 #1.
  4. Merge xong, workflow deploy trên `main` chạy prod preview rồi apply.
- **Diff rủi ro cần lần duyệt thứ hai (A lõi) [TK]:**
  - Nếu prod preview cho thấy replace/delete tài nguyên stateful, đổi IAM hoặc vi phạm policy, workflow **tự dừng**
    (02-research 4.6 #1 (b)).
  - Workflow đăng prod preview (đã lọc stack output/secret, 02-research 4.6 #2) vào job summary hoặc artifact.
  - **Engineer** mở PR thứ hai bằng identity của mình, thêm `deploy-approvals/<sha>.yaml` chứa SHA và hash của
    preview. Workflow không tự mở PR, vì "Allow GitHub Actions to create and approve pull requests" phải để tắt
    (02-research 3.3.3, 3.6 #3).
  - CODEOWNERS của thư mục này là platform team. Merge xong thì workflow chạy lại preview trên HEAD mới, và chỉ tiếp
    tục nếu hash trùng. Nếu có PR khác merge chen vào, hash lệch và workflow dừng.
  - Preview có cho output tất định để hash không (timestamp, giá trị unknown) là ⚠️ (mục 8). Nếu không, phải so một
    bản tóm tắt có cấu trúc (danh sách tài nguyên và thao tác).
- **Thao tác ngoài IaC (A đầy đủ) = "ops-as-code" [TK]:**
  - Một PR sửa file khai báo (ví dụ `ops/requests/…yaml`); sau khi merge, workflow chạy thao tác trong allowlist.
  - Về bản chất đây là **một broker dựng trên GitHub**. Khác với B ở chỗ cổng duyệt nằm ở GitHub, không có dịch vụ
    riêng, và phụ thuộc uptime của GitHub. Thao tác ngoài allowlist vẫn không có đường đi.
- **Luồng sự cố:** "làn sự cố" của chính con đường này.
  - PR gắn nhãn `incident`; on-call approver được page.
  - **Security checks (secret scan, dependency, SAST) luôn chạy** (S10); chỉ bớt test chậm không liên quan [TK].
  - Một required check bị path filter bỏ qua có thể kẹt ở trạng thái pending và chặn merge (⚠️, mục 8).
- **Ai duyệt được lúc 2 giờ sáng (trade-off chưa giải) [TK]:**
  - Cách đơn giản: nhóm on-call approver là code owner của mọi path deploy được (CODEOWNERS chỉ cần **một** owner
    bất kỳ, 02-research 3.2.7 ✅).
  - Cái giá: mọi PR thường cũng được thoả code-owner review chỉ với một người on-call, nên mất chuyên môn theo domain.
    Nếu có path-based required reviewers (3.2.4), người on-call vẫn chưa đủ. Lần duyệt thứ hai cho diff rủi ro cần
    platform team, nên rota phải có người của platform team, có cả primary và backup (S7). Nếu platform team chính là
    nhóm DevSecOps 1–2 người thì không đủ người theo GĐ-1. Khi đó cần chỉ định thêm người duyệt thay thế (⚠️ quy mô
    platform team chưa biết).
  - Cách khác: ruleset riêng cho nhánh sự cố (⚠️ chưa kiểm), hoặc rota on-call phủ đủ domain.
- **Bằng chứng audit:**
  - PR (diff, người duyệt, check) + log và artifact của run (prod preview, kết quả deploy) + CloudTrail của role
    deploy, nối với nhau qua commit SHA và run ID.
  - Log và artifact của run có thời hạn lưu (⚠️ con số chưa kiểm), nên phải export sang log archive.
- **Người duyệt thực sự thấy gì:** diff code và preview **non-prod**. Trên Team, không ai thấy prod diff trước khi
  apply (02-research 4.6 #1), trừ trường hợp diff rủi ro.
- **Điểm yếu, phụ thuộc:**
  - GitHub hoặc Actions ngừng thì không thay đổi được gì, kể cả trong sự cố.
  - Admin sửa được rulesets; việc đó chỉ được log (02-research 3.6 #1).
  - PR do agent viết dễ bị duyệt hời hợt (P9c), nhất là lúc 2 giờ sáng.
  - Nội dung PR có thể mang injection từ log mà agent đã đọc (A7b); người duyệt là lớp chặn duy nhất.
- **Quan hệ với D2:** không mâu thuẫn. A thêm một đường sự cố **không cần quyền JIT** cho thay đổi IaC.

## 2. Phương án B — "Thao tác đã duyệt, chạy bằng runbook"

**Một câu:** agent soạn **một thao tác cụ thể** (loại thao tác + tham số); người khác duyệt đúng thao tác đó; một
runbook tất định thực thi bằng role riêng. Không người hay agent nào cầm credential ghi.

- **Có sẵn trên AWS, không phải tự xây từ đầu:**
  - SSM Automation có bước `aws:approve`: "pauses an automation until designated principals either approve or reject the action" ✅.
  - `Approvers` nhận "An IAM role ARN" hoặc "An IAM assume role ARN", tối đa 10; có `MinRequiredApprovals` ✅.
  - "This action doesn't support multi-account and Region automations" ✅.
  - Runbook chạy bằng một `assumeRole`: điều này suy ra từ ví dụ trên trang doc, không phải câu khẳng định (⚠️ diễn giải).
  - 02-research 2.4.1 chỉ nói AWS không có tính năng gốc để request/approve **quyền truy cập**; nó không nói gì về
    phê duyệt thao tác.
- **Ba điều kiện để B đạt ràng buộc cứng (tất cả ⚠️, mục 8):**
  1. **Chặn tự duyệt:** người khởi chạy không duyệt được chính execution của mình.
  2. **Ghi đúng người duyệt:** bản ghi lưu identity của từng người, không chỉ role dùng chung. Lưu ý: ARN của role
     permission set đổi suffix khi bị tạo lại (02-research 2.1.3 ✅), nên danh sách `Approvers` có thể gãy âm thầm.
  3. **Đóng đường vòng IAM:**
     - Người khởi chạy cần quyền start automation, có thể cả `iam:PassRole` trên role của runbook (⚠️ theo trí nhớ).
     - Nếu IAM không giới hạn đúng document ARN, và không cấm con người tạo/sửa document trên prod, thì người khởi
       chạy, hoặc agent dùng chung SSO cache, có thể chạy một document **không có** `aws:approve` với cùng role ghi.
     - Vì vậy cần: chỉ document đã duyệt dùng được role runbook; document do pipeline deploy; PassRole giới hạn theo
       resource và service [TK].
- **Có thể cần quyền approve thường trực trong prod.** Câu "doesn't support multi-account" ✅ nói về automation
  chạy multi-account. Việc approver phải là principal trong cùng account là **suy luận** (⚠️). Nếu đúng, người duyệt
  cần một permission set thường trực trong prod, chỉ đủ để approve/reject. Quyền này có thuộc mức "Write" của IAM hay
  không thì chưa kiểm (⚠️), và điều đó quyết định S1 có còn giữ hay không.
- **Identity agent dùng:** laptop có read-only metadata cho prod, cộng quyền khởi chạy đúng các runbook đã duyệt.
  Quyền ghi nằm ở role của từng runbook, mỗi role chỉ đủ cho loại thao tác của runbook đó [TK].
- **Luồng thay đổi thường:** code/IaC vẫn qua PR + pipeline như A lõi. Bản thân runbook là code trong monorepo, đi
  qua PR và CODEOWNERS [TK].
- **Luồng sự cố:**
  1. Agent chọn runbook và điền tham số, kèm lý do.
  2. Runbook kiểm tra tham số, tới bước `aws:approve`, SNS báo người duyệt. Bước này có `NotificationArn` trỏ tới
     một SNS topic để báo người duyệt ✅ (trang automation-action-approve).
  3. Người duyệt xem tham số bằng identity SSO và approve.
  4. Runbook thực thi, sau đó mở ticket/PR codify vào IaC [TK].
- **Bằng chứng audit:** lịch sử execution của Automation (tham số, bước duyệt, kết quả) + CloudTrail của role
  runbook, export sang log archive [TK]. Evidence nằm ở hai nơi: AWS và GitHub.
- **Người duyệt thực sự thấy gì:** đúng tham số của thao tác sẽ chạy. Đây là mức chặt nhất, với điều kiện thao tác
  nằm trong một runbook đã viết sẵn.
- **Điểm yếu, phụ thuộc:**
  - Thao tác không có runbook vẫn cần đường khác.
  - Drift với IaC cho tới khi codify.
  - Nếu ba điều kiện không đạt được trên SSM, B quay về dạng tự xây: một dịch vụ giữ quyền ghi, vận hành 24/7.
- **Quan hệ với D2:** **thay** D2 cho những thao tác có runbook.

## 3. Phương án C — "Cửa sổ quyền JIT, agent gọi AWS trực tiếp" (đúng đề xuất của Engineering)

**Một câu:** engineer xin một cửa sổ quyền ghi hẹp, có thời hạn; người khác duyệt **cửa sổ đó**; trong cửa sổ, Claude
Code gọi AWS trực tiếp, cho cả thay đổi thường lẫn sự cố.

- **Identity agent dùng:**
  - Identity của engineer, mang thêm một permission set JIT qua assignment tạm thời (ví dụ `InfraOperator-<service>`, 1–4 giờ).
  - Có thể đi qua AWS MCP Server để có `aws:ViaAWSMCPService`. Nhưng key này chỉ là kiểm soát khi agent không gọi
    trực tiếp được (02-research 2.2.5, 2.9 #1).
- **Luồng thay đổi thường:**
  1. Xin cửa sổ JIT cho service cần sửa; người khác duyệt (≤ 1 giờ trong giờ làm việc, S4b).
  2. Agent áp dụng trực tiếp (`pulumi up` / `serverless deploy` từ laptop, hoặc AWS CLI), rồi commit code.
  3. PR sau đó chỉ để đồng bộ code, không còn là cổng duyệt.
  - Pipeline vẫn còn cho deploy ứng dụng.
- **Luồng sự cố:** giống luồng thường, với on-call approver.
- **Công cụ JIT:** sản phẩm của partner, sample TEAM, hoặc tự xây trên `CreateAccountAssignment` (02-research 2.4.1, 2.4.1b, 2.4.2).
- **Bằng chứng audit:** bản ghi phê duyệt trong công cụ JIT + CloudTrail của grant và của các lệnh trong cửa sổ, export
  sang log archive. Khi audit phải tái dựng "lệnh nào thuộc yêu cầu nào" theo khoảng thời gian (⚠️, 02-research 2.9 #2).
- **Người duyệt thực sự thấy gì:** phạm vi và lý do, không phải thay đổi.
- **Điểm yếu, phụ thuộc:**
  - Agent đọc log/tài liệu không tin cậy **trong khi** cầm quyền ghi (02-research 6.5 #1, #8).
  - CloudTrail ghi identity của engineer cho cả lệnh của agent (02-research 2.9 #1).
  - **Thu hồi:**
    - Xoá assignment chỉ chặn session **mới** (02-research 2.4.2, ⚠️ inference).
    - Session đang chạy sống tới hết thời hạn, tối đa bằng session duration (tối thiểu cấu hình được 1 giờ, 2.1.4 ✅).
    - Muốn chặn ngay phải có SCP Deny theo `identitystore:userId` dựng sẵn (2.4.4 ✅).
  - Thay đổi từ laptop bỏ qua prod preview và policy của pipeline.
- **Quan hệ với D2/D3:** **trái** D2 (D2 cấm agent dùng quyền JIT). Session cầm quyền JIT phải chạy `--restricted`
  theo D3, nên agent chỉ có những tool được khai báo trong `--tools`. Điều này làm giảm chính lợi thế tốc độ của C.

## 4. Phương án D — "Agent là một principal riêng, chạy trên hạ tầng Papaya"

**Một câu:** việc chạm prod không bao giờ chạy trên laptop. Một agent chạy trong runtime do Papaya kiểm soát, với
identity riêng; người duyệt **một lượt chạy** (nhiệm vụ + kế hoạch + giới hạn công cụ); cả phiên được ghi lại tập trung.

- **Identity agent dùng [TK]:**
  - Một role workload riêng (ví dụ task role trên ECS/k0s) trong account "agent-runtime", là một principal tách khỏi
    mọi người trong CloudTrail (giải quyết P1a/P1b).
  - Role read-only của nó cũng chỉ thấy metadata (GĐ-9, 02-research 2.9 #4).
  - Laptop không còn credential prod nào.
- **Luồng thay đổi thường:**
  - Engineer vẫn dùng Claude Code trên laptop cho non-prod và cho PR.
  - Nếu agent hosted mở PR dưới danh nghĩa app thì cần 2 approval hoặc một check có nguồn được ghim (02-research 3.3.4, 3.7 A3).
- **Luồng sự cố:**
  1. Người trực khởi động một lượt chạy "incident". Agent hosted phân tích và đề xuất kế hoạch, theo một trong hai
     nhánh: (a) PR làn sự cố như A, hoặc (b) thao tác trực tiếp có giới hạn.
  2. Người duyệt phê duyệt kế hoạch.
  3. Với nhánh (b), runtime nhận role ghi hẹp có TTL cho đúng lượt chạy [TK].
  - Có thể tách agent lập kế hoạch khỏi agent thực thi (02-research 6.5 #2).
- **Bằng chứng audit:** phê duyệt + transcript/OTel của lượt chạy trong kho tập trung + CloudTrail với principal của
  agent. Bằng chứng đầy đủ nhất về **agent đã làm gì**.
- **Người duyệt thực sự thấy gì:** kế hoạch, chưa phải lệnh chính xác. LLM thực thi có thể lệch; IAM scope giới hạn độ lệch.
- **Điểm yếu, phụ thuộc:**
  - Chi phí dựng runtime lớn nhất.
  - Server-managed settings không tới job chạy bằng API key/OIDC (02-research 1.7.10 ✅). Trên image do Papaya kiểm
    soát có thể bake file endpoint `managed-settings.json` (02-research 1.8 #3), miễn là agent không có root trong container [TK].
  - GitHub-hosted runner có sudo, nên không phù hợp (02-research 3.5.1).
  - Vẫn cần một chỗ phê duyệt ngoài GitHub Environment: `aws:approve` của B, hoặc cơ chế PR của A.
    `aws:approve` "doesn't support multi-account and Region automations" ✅. Runtime lại nằm ở account
    "agent-runtime" riêng, nên automation có lẽ phải chạy trong account prod (⚠️). Nếu không làm được thì D dùng cơ
    chế PR của A.
  - LLM cầm quyền ghi sau khi đọc log (02-research 6.5 #1), trừ khi tách planner/executor.
  - Transcript tập trung là kho dữ liệu nhạy cảm mới (02-research 6.5 #9).
- **Quan hệ với D2:** **khác hướng.** Giai đoạn sau của D2 là break-glass từ môi trường **không có** agent; D đặt agent
  **vào** môi trường cầm quyền ghi, đổi lại được tách identity bằng kỹ thuật.

## 4b. Tổ hợp hiện có và tổ hợp được đề xuất

- **A + D2 (hiện tại):**
  - Thay đổi thường đi A lõi.
  - Sự cố: agent read-only đề xuất lệnh; người trực xin JIT, tự gõ lệnh trong terminal riêng; người duyệt duyệt **yêu cầu JIT**.
  - Văn bản D2 không nói thứ tự IaC hay JIT. Có hai cách đọc:
    - **JIT cho sự cố.** 02-research 2.9 #2 đặt "Incidents: … the same flow with a fast approver" ngay sau gạch JIT
      ("manual operations, incidents"). Mục 5 chấm A + D2 theo cách đọc này.
    - **IaC trước, JIT chỉ cho thay đổi tay.** Câu "Mọi thay đổi tay phải có PR codify" của D2 tương thích với cách
      đọc này.
- **A + D2' (đề xuất, mục 7):**
  - A lõi (không ops-as-code) là mặc định, cả trong sự cố.
  - JIT chỉ dùng khi A lõi không dùng được: thao tác ngoài IaC chưa có runbook, GitHub/Actions ngừng, hoặc pipeline hỏng.
  - Yêu cầu JIT chứa **đúng danh sách lệnh**; R duyệt danh sách đó; sau cửa sổ, job đối chiếu sự kiện ghi trong
    CloudTrail với danh sách [TK].
  - **R gác cổng:** R từ chối JIT nếu thay đổi diễn đạt được bằng IaC và pipeline đang chạy, và ghi lý do.
  - **Codify:** mọi thay đổi qua JIT có PR codify trong thời hạn cố định, và có drift detection (giữ nguyên từ D2).
    Nếu GitHub ngừng, PR được mở ngay khi GitHub hoạt động lại.
  - Giữ lộ trình "break-glass từ môi trường không cài agent" của D2.
  - Thao tác lặp lại chuyển dần sang runbook B, khi B đạt ba điều kiện.
  - **Bằng chứng audit:** bản ghi yêu cầu JIT (danh sách lệnh, người yêu cầu, người duyệt, thời điểm, lý do nếu bị
    từ chối); CloudTrail của grant và của các lệnh; kết quả job đối chiếu; PR codify. Tất cả nối bằng request ID và
    export sang log archive, giữ ≥ 6 năm. Cách nối request ID với CloudTrail còn là ⚠️ (02-research 2.9 #2). Chuỗi này
    phục vụ S3 và S8.
- **Nếu owner đọc D2 theo cách thứ hai** (IaC trước), thì D2' = D2 + danh sách lệnh + job đối chiếu + R gác cổng.
  Khi đó phần lớn khoảng cách điểm giữa hai cột ở mục 5 đến từ **cách đọc**, không phải từ thiết kế. Q1 ở mục 9 thực
  chất một phần là xác nhận cách đọc này.

---

## 5. Ma trận so sánh

### 5.1 Kiểm tra ràng buộc cứng

"Người có tên đã review **thay đổi** và approve **trước** khi áp dụng, người duyệt khác người làm" (GĐ-8, GĐ-11).
Quy ước: "đạt một phần" thì điểm Compliance ở 5.2 không quá 3; "không đạt" thì không quá 2.

| A | B | C | D | A + D2 | A + D2' |
|---|---|---|---|---|---|
| **Đạt.** Duyệt diff trước merge; thiếu prod preview trên Team. | **Đạt nếu** cả ba điều kiện ⚠️ đúng (mục 2), và quyền approve không phá S1 (⚠️). | **Không đạt.** Duyệt quyền, không duyệt thay đổi, cho mọi thay đổi. | **Một phần.** Duyệt kế hoạch; LLM thực thi. | **Một phần, rộng.** Phần lớn sự cố đi JIT, duyệt quyền chứ không duyệt lệnh. | **Một phần, hẹp.** Sự cố IaC đạt; ngoại lệ đi JIT, duyệt danh sách lệnh, đối chiếu sau. "Hẹp" phụ thuộc tỉ lệ thao tác ngoài IaC (⚠️, 0.1). |

Vì sao "một phần" chấp nhận được cho D2' mà không cho C:
- Ở C, khoảng hở áp dụng cho mọi thay đổi, và agent tự chạy lệnh.
- Ở D2', khoảng hở chỉ cho ngoại lệ đo được; người gõ từng lệnh đã duyệt; lệch bị phát hiện sau.
- Đây là lập luận, không phải bảo đảm kỹ thuật. Owner cần chấp nhận rõ ràng (mục 9 Q2).

### 5.2 Chấm điểm

Thang 1–5, **5 luôn là tốt nhất cho Papaya**: nhanh nhất / đáp ứng tốt nhất / đơn giản nhất / rẻ nhất / rủi ro còn
lại thấp nhất. Không cộng tổng: các tiêu chí không cùng trọng số, và Compliance là ràng buộc (5.1).

Quy ước cho độ phức tạp và chi phí: một tổ hợp chứa toàn bộ thành phần của phương án khác thì không được điểm cao
hơn phương án đó. Cột A chấm **A đầy đủ**; A lõi được ghi trong ngoặc. Các tổ hợp dùng A lõi.

| Tiêu chí | A — PR-only | B — Runbook | C — JIT trực tiếp | D — Agent hosted | A + D2 | A + D2' |
|---|---|---|---|---|---|---|
| **Tốc độ — thay đổi thường** | **4** — như luồng PR hiện nay; ship trong ngày (S4a); chờ duyệt ≤ 1 giờ. | **4** — giống A cho code/IaC. | **5** — không chờ CI; một lần duyệt cửa sổ phủ cả chuỗi thay đổi nhỏ liên tiếp. | **4** — giống A. | **4** — giống A. | **4** — giống A. |
| **Tốc độ — sự cố / ngoài IaC** | **2** — ~11–46 phút ⚠️ (mục 6); thao tác ngoài allowlist của ops-as-code không có đường. | **4** — ~2–17 phút ⚠️ nếu một runbook phủ đủ thao tác; ~4–34 nếu cần hai runbook và hai lần duyệt (mục 6 B); chỉ với thao tác có runbook. | **4** — ~2–20 phút ⚠️ cộng thời gian provisioning (⚠️, mục 8); ngang B và D2: vẫn chờ duyệt ≤ 15. | **2–3** — nhánh PR ~14–56, nhánh trực tiếp ~5–30 phút ⚠️. | **4** — như C (~2–20 + provisioning ⚠️). | **2 / 4** — sự cố IaC đi A (2); ngoài IaC đi JIT (4). |
| **Compliance / ISO / HIPAA** | **4** — four-eyes ép bằng rulesets; chuỗi PR → run → CloudTrail; trừ điểm vì không ai thấy prod diff thường ngày, và admin chỉ bị log. | **5** nếu đủ ba điều kiện ⚠️ và không phá S1; **3** nếu tự duyệt chỉ chặn bằng quy trình; **≤ 2** nếu tự duyệt được. | **2** — duyệt quyền chứ không duyệt thay đổi; không tách lệnh agent với lệnh người. | **3** — identity agent riêng, transcript đầy đủ; duyệt kế hoạch, LLM thực thi. | **2** — theo cách đọc "JIT cho sự cố": phần lớn thay đổi sự cố chỉ duyệt ở mức quyền. (Cách đọc IaC trước: 3.) | **3** — sự cố IaC đạt đầy đủ; JIT cho ngoại lệ, duyệt danh sách lệnh, đối chiếu sau; vẫn là quy trình. |
| **Độ phức tạp triển khai** | **2** — A lõi (OIDC, rulesets, deploy workflow, lần duyệt thứ hai cho diff rủi ro) cộng ops-as-code. (A lõi: **3**.) | **2** — A lõi cộng runbook SSM và khoá IAM cho document/PassRole; nếu SSM không đạt, tự xây: **1**. | **3** — công cụ JIT, thu hồi, SCP; không cần lần duyệt thứ hai của A. | **1** — runtime, identity riêng, image có policy, kho transcript, cộng thành phần duyệt. | **2** — A lõi cộng công cụ JIT. | **2** — như A + D2; job đối chiếu nhỏ, không đáng một bậc. |
| **Chi phí** | **4** — không công cụ mới; công xây ops-as-code. (A lõi: **5**.) | **4** — A lõi cộng SSM Automation (giá ⚠️) và công viết runbook. | **3** — TEAM miễn phí nhưng phải vận hành; partner tốn license (⚠️ chưa tra giá). | **2** — compute cho runtime, kho transcript, công xây lớn nhất. | **3** — A lõi cộng đúng công cụ JIT của C. | **3** — như A + D2. |
| **Rủi ro còn lại** (5 = thấp nhất) | **4** — không ai cầm quyền ghi prod; còn: chuỗi cung ứng CI, admin sửa rulesets, duyệt hời hợt lúc 2 giờ sáng, injection qua nội dung PR, GitHub ngừng là kẹt. | **4** — role runbook hẹp theo thao tác; còn: tham số do agent điền, thao tác ngoài runbook, drift, có thể có quyền approve thường trực (⚠️). | **1** — injection trong lúc cầm quyền ghi cho mọi thay đổi; bỏ qua prod preview và policy; thu hồi cần SCP dựng sẵn. | **3** — identity tách bạch, không credential trên laptop; nhưng LLM cầm quyền ghi sau khi đọc log; runtime là bề mặt tấn công mới. | **2** — mỗi sự cố mở một cửa sổ JIT, trong đó agent trên cùng laptop vẫn dùng được quyền; drift sau mỗi sự cố. | **3** — cùng loại rủi ro với A + D2, nhưng chỉ khi có ngoại lệ; sự cố IaC không để drift. Điểm này phụ thuộc tỉ lệ thao tác ngoài IaC (⚠️). |

### 5.3 Đọc ma trận

- **C nhanh nhất, và đó là lý do Engineering muốn nó.**
  - C nhanh hơn A + D2' ở sự cố IaC (4 so với 2), và ở chuỗi thay đổi nhỏ liên tiếp (5 so với 4).
  - So với B và A + D2 ở sự cố, C ngang nhau, vì cả ba đều phải chờ duyệt ≤ 15 phút.
  - Cái giá: C không đạt ràng buộc cứng, Compliance 2, rủi ro 1. Đây là trade-off cần nói thẳng với Engineering, chứ
    không phải "C không nhanh hơn".
- Với **thay đổi thường**, mọi phương án **trừ C** ngang nhau (4). C nhỉnh hơn một bậc nhờ một lần duyệt cửa sổ phủ
  cả chuỗi thay đổi. Lựa chọn thật nằm ở **đường sự cố / ngoài IaC**.
- **A** đủ chặt cho Compliance, nhưng cùng với nhánh PR của D thuộc nhóm chậm nhất khi có sự cố, và kẹt hoàn toàn
  khi GitHub ngừng.
- **B** cho người duyệt thấy đúng tham số, với rủi ro thấp. Toàn bộ lợi thế này phụ thuộc vào **ba** điều kiện ⚠️ ở mục 2.
- **D** tách identity triệt để nhất, nhưng đắt và phức tạp nhất, và chỉ đạt một phần.
- **A + D2' so với A + D2:** D2' chậm hơn với sự cố IaC (2 so với 4). Đổi lại, D2' hơn một bậc ở Compliance và rủi ro,
  vì phần lớn sự cố không còn mở cửa sổ quyền. Khoảng cách này giả định cách đọc "JIT cho sự cố" của D2, và giả định
  phần lớn sự cố là IaC (⚠️).
  - Theo cách đọc "IaC trước", cột A + D2 sẽ thành khoảng: tốc độ 4 / 2–4, Compliance 3, độ phức tạp 2, chi phí 3,
    rủi ro 3. Tức là gần như trùng với A + D2'.
- **A + D2' so với A:** A chặt hơn (Đạt, 4) và phủ thao tác ngoài IaC bằng ops-as-code. Mục 7 giải thích vì sao vẫn
  cần đường dự phòng.

---

## 6. Kịch bản: sửa cấu hình Lambda trên prod lúc 2 giờ sáng

**Bối cảnh chung (giả định để so sánh):**
- Function `claims-doc-extract` (tên giả định) xử lý message từ SQS.
- Một partner bắt đầu gửi file lớn hơn, nên function timeout hàng loạt, message quay lại queue, backlog tăng. Alarm kêu.
- Bản sửa: tăng `timeout` 30s → 90s, `memorySize` 1024 → 2048. Cả hai được khai báo rõ trong `serverless.yml`.
  Giả định queue nguồn cũng được khai báo trong cùng `serverless.yml`. Nếu queue nằm ở stack khác (ví dụ Pulumi), A
  phải sửa hai stack và lo thứ tự deploy; lợi thế "một PR, một lần deploy" của A yếu đi.
- Bẫy có thật: visibility timeout của queue nguồn phải đủ lớn so với timeout của function (AWS khuyến nghị ≥ 6 lần;
  ⚠️ nhớ từ docs, chưa mở trang). Agent có thể bỏ sót; đây là chỗ người duyệt có giá trị.
- Người trực: engineer E. Người duyệt trực: R (người khác).
- **Thời gian chẩn đoán không tính** ở mọi phương án, kể cả D (ở D, chẩn đoán chạy trên agent hosted). Thời gian khởi
  động runtime của D được tính, vì đó là chi phí riêng của D.

### A — PR-only

1. E nhận page. E mở **session phân tích**: `--restricted`, `--tools "Bash,Read,Grep,Glob"`, identity read-only
   metadata (D3, 02-research 6.9.4 Q2). Agent chạy `aws lambda get-function-configuration`, đọc metric và log đã che, rồi chẩn đoán.
2. E mở **session thứ hai** có Edit và git/gh, không có identity prod. Session này nhận bản tóm tắt chẩn đoán, không
   đọc lại log thô [TK]. Agent sửa `serverless.yml` (timeout, memory, kèm visibility timeout nếu cùng stack) và chạy
   `serverless diff` trên non-prod.
   - Lệnh này cần sf-core ≥ 4.37.0, và khác biệt không làm exit code khác 0, nên CI phải tự parse `--json` (02-research 4.4.2 ✅).
3. Agent mở PR bằng identity của E, nhãn `incident`. Security checks chạy đủ.
4. R được page, xem diff (GitHub Mobile duyệt được PR là ⚠️ chưa kiểm) và approve.
5. E merge. Workflow deploy: `serverless package`, prod preview, diff không thuộc loại rủi ro, rồi
   `serverless deploy --package` bằng role OIDC `production` (02-research 4.4.3).
6. E theo dõi metric để xác nhận.
- **Thời gian (quyết định sửa → áp dụng):** ~11–46 phút ⚠️ = PR 2–3 + checks 5–15 + chờ duyệt 0–15 (S7) + package và
  prod preview 1–3 + CloudFormation 3–10. Nếu phải sửa bản fix sau khi đã duyệt thì cộng thêm một vòng duyệt.
- **Còn lại:** không drift, không cần PR codify; bằng chứng nằm sẵn trong PR, run và CloudTrail.

### B — Runbook (SSM Automation)

1. Chẩn đoán như A bước 1.
2. Agent chọn runbook `Papaya-LambdaSetTimeoutMemory` (tên giả định), điền function, 90, 2048 và lý do. E khởi chạy.
3. Runbook kiểm tra: function thuộc prod, giá trị trong khoảng cho phép, visibility timeout (VT) của queue nguồn đủ
   lớn so với timeout mới [TK].
   - Queue đang đặt theo function 30s, nên tăng lên 90s gần như chắc chắn **làm kiểm tra VT thất bại**.
   - Khi đó có hai nhánh:
     - **(a)** Nếu có runbook gộp "Lambda + SQS" (đổi cả `SetQueueAttributes`), dùng runbook đó với một lần duyệt.
     - **(b)** Nếu không có, cần runbook SQS thứ hai và **lần duyệt thứ hai**, hoặc rơi về JIT cho phần SQS.
4. Runbook tới `aws:approve`; SNS page R. R đăng nhập console bằng SSO, xem tham số và approve.
5. Runbook thực thi bằng role của nó (ngoại lệ có tên trong lệnh deny Lambda, 0.3), rồi mở PR codify.
6. E theo dõi metric. Sáng hôm sau, PR codify đi luồng thường.
- **Thời gian:** nhánh (a) ~2–17 phút ⚠️ = điền tham số ~2 + chờ duyệt 0–15 (gồm page và đăng nhập, như mọi phương
  án) + thực thi vài giây. Nhánh (b) ~4–34 phút ⚠️ (hai lượt).
- **Còn lại:** drift trên **cả function lẫn queue** cho tới khi PR codify merge. Đây là chỗ A có lợi thế thật: một PR
  sửa cả hai trong `serverless.yml`, người duyệt thấy cả hai, không có drift.
  - Với `deploy function`, docs nói "A later `serverless deploy` does not undo a configuration change made this way"
    (02-research 4.4.4 ✅). Áp dụng câu này cho `UpdateFunctionConfiguration` gọi trực tiếp là suy luận (⚠️).
  - Drift detection của CloudFormation (job bắt buộc theo D2) **có thể** bắt được, vì hai property được đặt rõ
    (02-research 4.4.6 ✅ chỉ kiểm property "explicitly set"). `AWS::Lambda::Function` có hỗ trợ drift detection
    không là ⚠️ (mục 8).

### C — JIT trực tiếp

1. Chẩn đoán như A, nhưng trên cùng session mà lát nữa sẽ cầm quyền ghi.
2. E gửi yêu cầu JIT: `InfraOperator-claims`, prod, 1 giờ, lý do.
3. R duyệt trong công cụ JIT: thấy phạm vi và lý do, **không thấy lệnh**.
4. Công cụ tạo assignment; E đăng nhập lại profile (provisioning ⚠️).
5. Agent tự chạy `aws lambda update-function-configuration …` và `aws sqs set-queue-attributes …` cho VT (permission
   set này là ngoại lệ trong lệnh deny Lambda, và phải có quyền SQS). Agent cũng có thể chạy thêm lệnh khác trong phạm
   vi mà không ai xem trước. Nếu agent quên VT thì không ai bắt được.
6. Hết giờ, assignment bị xoá. Session đang có sống tới hết hạn, trừ khi bật SCP Deny dựng sẵn (02-research 2.4.4).
7. Sau đó: PR codify; audit đối chiếu CloudTrail với yêu cầu.
- **Thời gian:** ~2–20 phút ⚠️ = yêu cầu 1–2 + chờ duyệt 0–15 + E đăng nhập lại ~1–3 + lệnh vài giây, chưa tính provisioning.
- **Còn lại:** drift trên function và queue; không tách được lệnh của agent với lệnh của người.

### D — Agent hosted

1. E khởi động lượt chạy "incident" (Slack hoặc CLI) kèm link alarm; runtime khởi động (~3–10 phút ⚠️).
2. Agent hosted chẩn đoán bằng role read-only metadata của chính nó, rồi đề xuất kế hoạch theo một trong hai nhánh.
3. **Nhánh (a), PR:** agent sửa `serverless.yml` và mở PR làn sự cố; từ đây giống A bước 3–6.
   Thời gian ~14–56 phút ⚠️ = khởi động + A.
4. **Nhánh (b), trực tiếp:** kế hoạch phải gồm cả Lambda và VT, và role ghi hẹp phải có quyền SQS. R duyệt kế hoạch (`aws:approve` hoặc cơ chế PR); runtime cấp role ghi hẹp có TTL; agent
   thực thi; transcript được lưu tập trung; PR codify sau.
   Thời gian ~5–30 phút ⚠️ = khởi động 3–10 + lập kế hoạch 2–5 + chờ duyệt 0–15 + thực thi.
- **Còn lại:** nhánh (a) không drift; nhánh (b) drift như B. Bằng chứng đầy đủ nhất ở cả hai nhánh.

### A + D2 / A + D2' (để đối chiếu)

- **A + D2 (đọc "JIT cho sự cố"):**
  - Agent read-only đề xuất hai lệnh (Lambda và SQS VT); E xin JIT; R duyệt yêu cầu; E **tự gõ** lệnh trong terminal riêng.
  - CloudTrail ghi E, **giống hệt C**: ở C agent cũng chạy bằng identity của E (02-research 2.9 #1). Khác biệt duy
    nhất là bảo đảm bằng quy trình rằng E đã đọc từng lệnh.
  - Thu hồi có cùng điểm yếu với C. Còn lại: drift trên function và queue, PR codify. Thời gian ~2–20 phút cộng provisioning ⚠️.
- **A + D2':**
  - Thay đổi này **là** IaC, nên đi đường A ở trên (~11–46 phút ⚠️). R sẽ từ chối một yêu cầu JIT cho thay đổi này.
  - Nếu GitHub Actions đang ngừng: yêu cầu JIT liệt kê đúng hai lệnh (`update-function-configuration` và
    `set-queue-attributes` cho VT); R duyệt danh sách đó. Nếu danh sách thiếu lệnh VT, R là người bắt lỗi. Sau đó E
    gõ; job đối chiếu CloudTrail chạy sau cửa sổ; PR codify được mở ngay khi GitHub hoạt động lại; drift detection
    theo dõi cả function lẫn queue tới khi PR merge.

---

## 7. Khuyến nghị

**Chọn A + D2':**
- A lõi là xương sống, cả trong sự cố.
- Giữ D2 làm đường dự phòng hẹp, có chỉnh.
- Ngay giai đoạn đầu, kiểm chứng ba điều kiện của B (SSM `aws:approve`). Nếu đạt, thao tác ngoài IaC lặp lại chuyển
  sang runbook và đường JIT co lại thêm.
- Chưa xây ops-as-code; chỉ xây nếu B không đạt và số liệu cho thấy cần.
- D để dành, có điều kiện kích hoạt.

1. **A lõi cho mọi thay đổi diễn đạt được bằng IaC, kể cả trong sự cố.**
   - A đạt ràng buộc cứng, và dựng trên công cụ Papaya đã có, phù hợp đội DevSecOps 1–2 người (GĐ-1). Lập luận mạnh
     hơn nếu GĐ-12 đúng; GĐ-12 chưa xác nhận.
   - A đặt ranh giới ở IAM và cổng CI, đúng nguyên tắc 6.8.
   - Trong kịch bản 2 giờ sáng, thay đổi cấu hình Lambda là IaC, nên đi A thì không drift và không cần cửa sổ quyền.
2. **Chốt thứ tự: IaC trước, JIT sau; R gác cổng** (mục 4b).
   - Theo cách đọc "JIT cho sự cố" của 02-research 2.9 #2, đây là một thay đổi so với D2.
   - Theo cách đọc "IaC trước", đây chỉ là làm rõ D2.
   - Owner quyết (mục 9 Q1).
3. **Thu hẹp khoảng hở "duyệt quyền, không duyệt lệnh":** yêu cầu JIT chứa đúng danh sách lệnh, R duyệt danh sách
   đó, và job đối chiếu CloudTrail sau cửa sổ [TK]. Đây vẫn là quy trình cộng phát hiện, không phải chặn trước (5.1).
4. **Kiểm chứng B sớm, vì kết quả có thể đổi khuyến nghị.**
   - Nếu đủ **ba** điều kiện (chặn tự duyệt, ghi đúng người duyệt, đóng đường vòng IAM), và quyền approve không phá S1,
     thì thao tác vận hành lặp lại (restart, redrive, scale ngoài IaC) chuyển sang runbook.
   - Nếu không đạt, giữ A + D2'. Chỉ xây ops-as-code của A nếu metric cho thấy JIT ngoài IaC quá nhiều.
5. **Không chọn C.**
   - C không đạt ràng buộc cứng, và rủi ro nằm đúng chỗ đặc thù của Papaya: agent đọc tài liệu và log có thể bị cài
     cắm (A7b) trong khi cầm quyền ghi.
   - Với Engineering, nói thẳng: C nhanh hơn khuyến nghị này ở sự cố IaC (~2–20 so với ~11–46 phút) và ở chuỗi thay
     đổi nhỏ. Đổi lại, khuyến nghị giữ được ràng buộc cứng. "Tự ship" vẫn đúng với A cộng vòng lặp non-prod tự do;
     chỉ bước vào prod cần thêm một người.
6. **D: có điều kiện kích hoạt.** Làm D khi cần tách identity agent bằng kỹ thuật (auditor/partner yêu cầu), hoặc khi
   có cách lưu transcript tập trung đáp ứng yêu cầu dữ liệu.

**Vì sao không chọn A (đầy đủ), và vì sao không giữ A + D2 như đang có:**
- **A đầy đủ** chặt nhất và phủ thao tác ngoài IaC bằng ops-as-code. Nhưng còn hai trường hợp nó không có đường đi:
  (a) GitHub/Actions ngừng; (b) thao tác nằm ngoài allowlist của ops-as-code.
  - Khi đó chỉ còn hai lựa chọn: chờ, hoặc phá luật. Theo 6.8 và bài học P3b, luật không có lối thoát sẽ bị phá ở sự
    cố đầu tiên, và việc đó không để lại bằng chứng.
  - Một lối thoát có khai báo, có duyệt, có đo và có đối chiếu thì tốt hơn cho cả Compliance lẫn vận hành.
  - Thêm nữa, ops-as-code tốn công xây (độ phức tạp 2) mà vẫn chậm; B có thể phủ cùng nhu cầu rẻ hơn nếu đạt ba điều kiện.
- **A + D2 như đang có (đọc "JIT cho sự cố"):**
  - Mỗi sự cố mở một cửa sổ quyền, trong đó agent trên cùng laptop dùng được quyền; mỗi sự cố để lại drift.
  - D2' đổi khoảng 6–29 phút ⚠️ trong mỗi sự cố IaC. Cách tính: thời gian chờ duyệt của R như nhau ở hai bên nên trừ
    ra, còn A 11–31 so với JIT 2–5, chưa tính provisioning JIT. Đổi lại, D2' bỏ được cả hai điều trên (cửa sổ quyền
    và drift), đúng hướng "ma sát ở nơi thiệt hại lớn" của 6.8.
  - Nếu owner coi tốc độ sự cố quan trọng hơn, A + D2 là lựa chọn hợp lý tiếp theo, với cái giá trong ma trận:
    Compliance 2, rủi ro 2.

**Chỗ khuyến nghị lệch khỏi framing (nói rõ):**
- Framing §3.3 đòi "một con đường duy nhất, ép bằng kỹ thuật". Khuyến nghị có **hai** con đường, trong đó đường dự
  phòng là kiểm soát bằng quy trình. Lệch này có chủ ý, vì lý do ở trên.
- 6.8 cảnh báo đường an toàn chậm hơn đường tắt thì người ta đi đường tắt. Ở đây đường mặc định A (~11–46 phút) chậm
  hơn đường dự phòng JIT (~2–20 phút). Ba điều giữ cho đường tắt không thành đường chính:
  - R từ chối JIT khi A dùng được;
  - metric "JIT dùng cho thay đổi lẽ ra đi A" và metric "số cửa sổ JIT cho thao tác ngoài IaC", mỗi cái có ngưỡng xem lại;
  - khi vượt ngưỡng, làm A nhanh hơn hoặc chuyển thao tác sang runbook B, chứ không nới JIT.

**Rủi ro của chính khuyến nghị này:**
- **Tốc độ sự cố của A chưa đo, và framing chưa có mục tiêu end-to-end.** Cận trên ~46 phút vượt mục tiêu ≤ 30 phút
  đề xuất ở Q3. Việc đầu tiên trong rollout phải là đo một PR làn sự cố trên service thật.
- **"Đường dự phòng hẹp" là giả định.** Nếu phần lớn sự cố ở Papaya cần thao tác ngoài IaC (⚠️, 0.1), A + D2' trôi về
  A + D2 cho tới khi B sẵn sàng.
- **Đường dự phòng chỉ đạt ràng buộc một phần** (5.1). Owner phải chấp nhận rõ ràng, kèm số liệu theo dõi.
- **Trên Team, không ai thấy prod diff thường ngày trước khi apply.** Lớp bù "tự dừng khi diff rủi ro" là [TK], dựa
  vào việc parse prod preview. `--save-plan` ([PREVIEW]) và `up --plan` ([EXPERIMENTAL]) của Pulumi chỉ là bổ sung
  (02-research 4.1.1–4.1.3 ✅).
- **Code owner cho on-call** có thể làm yếu review của luồng thường (mục 1). Chưa có cách giải được kiểm chứng.

## 8. Việc cần kiểm chứng trước khi viết framework

- [ ] ⚠️ B, điều kiện 1–2: `aws:approve` có chặn người khởi chạy tự duyệt không; bản ghi lưu identity nào khi approver
      là role Identity Center; lịch sử execution giữ bao lâu; giá SSM Automation.
- [ ] ⚠️ B, điều kiện 3: IAM cho SSM Automation (giới hạn theo document ARN, `iam:PassRole`, chặn tạo/sửa document trên prod).
- [ ] ⚠️ B: approver có được ở account khác không; action dùng để approve tên gì và có access level "Write" không (ảnh hưởng S1).
- [ ] ⚠️ D: `aws:approve` dùng được cho runtime ở account riêng không (giới hạn multi-account).
- [ ] ⚠️ Tỉ lệ sự cố ở Papaya cần thao tác ngoài IaC (hỏi Papaya, hoặc đo sau rollout).
- [ ] ⚠️ Thời gian end-to-end của làn sự cố A trên một service thật.
- [ ] ⚠️ Prod preview (Pulumi, Serverless) có output tất định để hash không.
- [ ] ⚠️ Required check bị path filter bỏ qua có chặn merge (pending) không; update branch không đổi diff có làm mất approval không.
- [ ] ⚠️ Có tách được quy tắc duyệt cho PR sự cố (ruleset riêng cho nhánh) mà không làm yếu code-owner review thường ngày không.
- [ ] ⚠️ GitHub Mobile có duyệt PR được không, và có thoả các rule của ruleset không.
- [ ] ⚠️ Thời hạn lưu log và artifact của workflow run; cách export sang log archive.
- [ ] ⚠️ "Deploy sau không hoàn tác thay đổi config" (02-research 4.4.4) có đúng với `UpdateFunctionConfiguration` gọi
      trực tiếp không; `AWS::Lambda::Function` có hỗ trợ CloudFormation drift detection không.
- [ ] ⚠️ Thời gian provisioning của account assignment Identity Center.
- [ ] ⚠️ Lambda/SQS: khuyến nghị visibility timeout so với function timeout (mở docs trước khi trích).

## 9. Quyết định của owner

Câu hỏi cần owner trả lời:
- **Q1.** Chọn phương án/tổ hợp nào? (Đề xuất: A + D2', kèm kiểm chứng B ở giai đoạn đầu.) Câu hỏi này cũng là xác
  nhận cách đọc D2: "JIT cho sự cố" hay "IaC trước" (mục 4b).
- **Q2.** Có chấp nhận rằng đường dự phòng JIT chỉ đạt ràng buộc "duyệt thay đổi" **một phần** (5.1) không, với điều
  kiện tần suất được đo và lệch được phát hiện sau?
- **Q3.** Mục tiêu end-to-end cho thay đổi trong sự cố, từ lúc quyết định sửa tới lúc áp dụng? (Đề xuất ⚠️: ≤ 30
  phút, đo ở rollout.)

### Trả lời của owner (2026-11-09)

- **Q1 → A + D2'.** Lý do của owner: cân bằng giữa quy trình và tốc độ xử lý sự cố. Đồng thời chốt cách đọc D2 là
  **"IaC trước"**: JIT không phải đường mặc định cho sự cố.
- **Q2 → Chấp nhận.** Khi có sự cố mà đường chính (A) không dùng được, JIT được dùng sau khi được approve. Owner chấp
  nhận rằng đường này chỉ đạt ràng buộc "duyệt thay đổi" một phần (5.1).
- **Q3 → ≤ 30 phút** từ lúc quyết định sửa tới lúc áp dụng, đo ở rollout.

**Hệ quả cần mang sang bước framework** (ghi chú của agent, không phải lý do của owner):
- Cận trên ước lượng của A trong sự cố (~46 phút ⚠️, mục 6) vượt mục tiêu 30 phút. Đo làn sự cố A trên một service
  thật là việc đầu tiên của rollout. Nếu không đạt, làm A nhanh hơn trước, chứ không nới JIT (mục 7).
- Kiểm chứng B (mục 8) vẫn ở giai đoạn đầu, vì kết quả có thể thu hẹp thêm đường JIT.
- Metric và ngưỡng xem lại cho việc dùng JIT (mục 7) trở thành một phần của bằng chứng cho Q2.
