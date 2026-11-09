# 05 — Kế hoạch deliverable (chốt sẽ nộp gì)

## English summary

- Fixes what is submitted before the final writing pass; no new design decisions.
- **Docs:** one-page README; framework trimmed to ~9.5–10k words; new engineer guide; separate rollout plan;
  a compliance control-and-evidence register; existing threat model, problem→control map and 10 ADRs; three
  Mermaid diagrams.
- **Order:** change workflow (layer 3) and identity & access (layer 1) first, with their examples; README last.
- **Examples:** 7 core + 3 secondary, each tied to a framework claim and a local check with stated limits. Key
  pushback: GitHub Team has no environment reviewers on private repos (R3.1.2), so the gate example is a
  ruleset on `main`; OIDC trust policy and SCP added; the risk stop gets a runnable classifier.
- **Excluded:** invented facts (k0s, Firebase, GCP), live-infra runs, open-gap implementations, a hook example (owner agreed)
  (owner agreed). **Owner decisions:** §5, all seven proposals accepted. Two independent review rounds; log in §6.

> Working note. Updated: 2026-11-09 · Status: owner duyệt 2026-11-09 (§5)
>
> Ký hiệu: ✅ kiểm trong session này · 📖 R*x.y* = dòng trong `work/02-research.md` · ⚠️ chưa kiểm.

---

## 0. Hiện trạng (đầu vào của plan)

| Đã có | Kích thước ✅ (`wc -w`) | Trạng thái |
|---|---|---|
| `docs/framework.md` | 11 026 từ, 779 dòng | Owner duyệt (mục 1), 17 vòng review |
| `docs/adr/0001…0010` + `README.md` | 453–594 từ mỗi ADR | Owner duyệt (mục 2), 4 vòng review |
| `docs/threat-model.md` | 3 039 từ, 20 threat | Owner duyệt (mục 3), 3 vòng review |
| `docs/problem-control-map.md` | 3 194 từ, 40 dòng | Owner cho commit sau mục 4, nhưng file vẫn ghi "Status: draft for owner review" (dòng 3) → §5 Q7 |
| `README.md` | khung, ghi "skeleton only" | Phải viết lại |
| `examples/`, `diagrams/` | trống (`.gitkeep`) | Chưa làm |

Nhận xét dẫn tới plan này:

1. **Framework quá dài cho người đọc đầu tiên.** 11k từ ≈ 45–50 phút đọc. Panel lãnh đạo sẽ chỉ đọc §1.
   Layer 8 có một ô bảng (phase 1) dài khoảng 450 từ, khó đọc như một kế hoạch.
2. **Compliance chưa có tài liệu của riêng mình.** Evidence nằm rải ở đoạn "Audit evidence" của 8 layer;
   bảng ISO/HIPAA ở layer 8 chỉ có 4 dòng, mã ISO là nhớ lại chưa đọc (⚠️ R5.1).
3. **Engineering chưa có câu trả lời ngắn cho "ngày làm việc của tôi thay đổi thế nào".** Có, nhưng rải ở
   layer 2 (session types), layer 3 (ví dụ 2 giờ sáng), layer 4, 6, 7.
4. **Framework hứa "copy-paste detail belongs in `examples/`"** (`docs/framework.md:11`), README hứa "Claude
   Code settings and hooks, GitHub Actions, IAM/OIDC, plugin manifests", và framing Q14 cũng liệt kê như vậy;
   nhưng `examples/` trống. Đây là chỗ hở lớn nhất so với hình thức deliverable đã chốt.

---

## 1. Danh sách file sẽ nộp

Người đọc: **LĐ** = lãnh đạo / panel quyết định · **CO** = Compliance · **KS** = kỹ sư (engineer, DevSecOps).
Độ dài là mục tiêu, không phải giới hạn cứng. Tiền tố số là thứ tự đọc (quy ước `CLAUDE.md`).

| # | File | Mục đích | Người đọc chính | Độ dài mục tiêu | Lấy từ |
|---|---|---|---|---|---|
| 1 | `README.md` | Cổng vào: bài toán trong 3 câu, quyết định (A + D2'), mỗi bên được gì, chỗ chưa đạt, **đường đọc theo vai trò** (LĐ 15 phút / CO / KS), cách đọc marker, cách repo được làm bằng agent (CLAUDE.md, reviewer độc lập, permission mode mặc định), transcript | Tất cả, trước hết LĐ | 1 trang, ≤ 700 từ | `framework.md` §1 (rút gọn), `work/session-log.md`, README khung (phần transcript giữ nguyên) |
| 2 | `docs/01-framework.md` | Tài liệu tham chiếu: 8 layer, mỗi layer Principle / On Papaya's stack / Audit evidence / Cost-value; gaps; owner decisions | KS, CO | ~9 500–10 000 từ (từ 11 026) | `docs/framework.md`. Chuyển (không chép) bảng rollout + "Phase-1 load" (~750 từ ✅ reviewer đếm) sang #4; phần chi tiết của "Audit evidence" (~390 từ) và bảng standards (~130 từ) sang #5. **Mỗi layer giữ một câu tóm tắt evidence** + link (thêm lại ~150 từ, nên phần evidence chỉ bớt ròng ~230 từ), để cấu trúc 4 phần của layer vẫn đúng. Câu "full evidence live in the framework" của `docs/adr/README.md` nói về nguồn của quyết định, không phải audit evidence; bước 6 kiểm lại câu chữ. Rút thêm (biên tập câu chữ) chỉ khi owner chọn ở §5 Q1, vì đó là sửa tài liệu đã duyệt |
| 3 | `docs/02-engineer-guide.md` (mới) | "Làm việc với agent ở Papaya": vòng lặp non-prod, đọc prod, ship một thay đổi prod, sự cố lúc 2 giờ sáng, xin đọc dữ liệu thật, xin thêm plugin/MCP. Mỗi mục: làm gì, mất bao lâu, ai duyệt, link tới layer | KS | ~1 200 từ | Layer 2 (bảng session types), layer 3 (bảng mức + ví dụ Lambda), layer 4, 6, 7. Chỉ trình bày lại, không thêm luật |
| 4 | `docs/03-rollout-plan.md` | 30/60/90: mỗi phase có danh sách việc (owner, điều kiện xong), **điều kiện cứng** trước khi gỡ quyền ghi prod, việc được trượt / không được trượt, metric S1–S11 theo phase, rủi ro tải phase 1 | LĐ, KS (DevSecOps) | ~1 500 từ | Layer 8 (bảng phase, "Phase-1 load"), framing §5 (S1–S11), framing Q8 |
| 5 | `docs/04-compliance-mapping.md` | **Control & evidence register**: control → owner → bản ghi evidence (ở đâu, giữ bao lâu, ai lấy) → tần suất kiểm → metric S → tham chiếu ISO 27001 Annex A / HIPAA / luật VN (giữ marker). Kèm "auditor lấy evidence cho một thay đổi prod trong ≤ 30 phút" (S8) | CO | ~2 000 từ | Đoạn "Audit evidence" của 8 layer, bảng standards ở layer 8, research 5.1–5.7, framing §5 |
| 6 | `docs/05-threat-model.md` | Giữ nội dung; chỉ sửa link và số layer nếu đổi | KS, CO | ~3 000 từ | `docs/threat-model.md` |
| 7 | `docs/06-problem-control-map.md` | Truy vết đề bài → control, để người chấm kiểm có bỏ sót vấn đề nào không | CO, người chấm | ~3 200 từ | `docs/problem-control-map.md`; status theo §5 Q7 |
| 8 | `docs/adr/0001…0010`, `docs/adr/README.md` | Giữ nội dung ADR (quy tắc "accepted ADR is not edited"); chỉ sửa link. `README.md` của ADR cập nhật dòng "rollout plan (layer 8)" sau khi tách | KS, LĐ | ~500 từ mỗi ADR | Như hiện tại |
| 9 | `diagrams/01-change-workflow.mmd` (+ `.svg`) | Luồng thay đổi theo mức L0–L3: PR → ruleset → merge → deploy job → risk stop → PR `deploy-approvals/` → deploy. Thể hiện "2 người", ai duyệt ở mỗi mức | KS, CO | ≤ ~25 node | Layer 3 |
| 10 | `diagrams/02-identity-trust-boundaries.mmd` (+ `.svg`) | Laptop (engineer + agent, chung SSO cache) / GitHub (ruleset, environment `production`, OIDC) / AWS prod account (deploy role, `ProdReadMetadata`, JIT role, SCP) / audit store. Thể hiện "quyền của engineer = quyền của agent" và ranh giới thật nằm ở đâu | LĐ, CO | 1 sơ đồ | Layer 1, 2, 5, threat model "trust boundaries" |
| 11 | `diagrams/03-incident-lane.mmd` (+ `.svg`) | Sự cố: responder E + on-call approver R; nhánh chính (PR `incident`) và nhánh dự phòng JIT (điều kiện dùng, đối chiếu CloudTrail, codify PR) | LĐ, KS | 1 sequence | Layer 3 ví dụ 2 giờ sáng, layer 7 bảng break-glass, Options §6 |
| 12 | `examples/` + `examples/README.md` | Xem §3 | KS | xem §3 | xem §3 |

Ghi chú về các lựa chọn khác với gợi ý ban đầu:

- **Compliance mapping → control & evidence register.** Một bảng chỉ "control ↔ mã ISO" yếu ở chỗ mã ISO là nhớ
  lại (⚠️ R5.1). Điều Compliance cần trong audit là "bản ghi nào chứng minh control chạy, ở đâu, giữ bao lâu"
  (S8). Cột mã ISO/HIPAA vẫn giữ, với marker.
- **Thêm engineer guide.** Compliance có #5; Engineering hiện chỉ có §1 của framework. Câu của Engineering là
  "debug and ship my own infra changes without waiting" → guide trả lời: việc nào không chờ ai, việc nào chờ ai,
  bao lâu. Là mục đầu tiên cắt nếu thiếu thời gian (§5 Q2).
- **Rollout tách ra file riêng**, layer 8 giữ principle + link, để không có hai bản rollout lệch nhau.
- **Ba sơ đồ**: ba thứ khó nói bằng chữ nhất (luồng có nhánh, ranh giới tin cậy, trình tự theo thời gian).
  Không vẽ sơ đồ rollout (bảng là đủ).
- **Nguồn sơ đồ ở `diagrams/*.mmd`, render `.svg` bằng `mmdc`** (✅ 11.12.0; reviewer đã render thử một sơ đồ
  thành SVG). Một nguồn duy nhất; render thành công là bước kiểm.

---

## 2. Thứ tự viết và lý do

| Bước | Việc | Vì sao ở vị trí này |
|---|---|---|
| 0 | Đóng băng quyết định: OD1–OD13, D1–D3, Options §9. Lập danh sách thuật ngữ (L0–L3, risk stop, on-call approver, incident responder…) dùng thống nhất | Bản cuối là biên tập, không thiết kế lại. Thay đổi quyết định phải quay về owner |
| 1 | **Lõi A — Change workflow (layer 3)** + E1 ruleset, E2 CODEOWNERS, E3 workflows + environment, E7 risk stop | Câu trả lời trực tiếp cho câu của Compliance ("named person approved"). ADR 0001, 0003, 0004, 0010, threat model và điều kiện cứng của rollout đều tham chiếu nó. Viết example **cùng lúc** với văn bản để ép văn bản chính xác: nếu ruleset JSON không biểu diễn được điều văn bản nói thì văn bản sai |
| 2 | **Lõi B — Identity & access (layer 1)** + E4 OIDC trust, E5 SCP, E6 permission set | Câu trả lời cho câu của Engineering ("talk to AWS directly"): agent được gì, không được gì. Sau layer 3 vì layer 1 dựa vào "ghi prod chỉ qua pipeline role" mà layer 3 định nghĩa; E4 phụ thuộc tên environment ở E3 |
| 3 | Layer 2 (agent runtime), 4 (supply chain), 5 (CI hardening) + E8 managed settings, E9 marketplace, E10 policy pack | Lớp hỗ trợ / hygiene (ADR-0007). **Lưu ý phụ thuộc:** bước 1 dùng hai thứ định nghĩa ở layer 5 — danh sách L3 path chuẩn (cho E2) và quy tắc credential/pinning/trigger (cho E3). Trong bước 1–2, layer 5 được giữ nguyên làm đầu vào; nếu E2/E3 lộ ra chỗ sai trong layer 5 thì sửa layer 5 ngay trong bước 1 và ghi lại |
| 4 | Layer 6, 7, 8; tách `03-rollout-plan.md`; viết `04-compliance-mapping.md` | Rollout cần danh sách control cuối và điều kiện cứng từ bước 1–2. Register cần đoạn "Audit evidence" cuối của mọi layer |
| 5 | Ba sơ đồ | Vẽ khi văn bản đã ổn định, nếu không phải vẽ lại. Mỗi sơ đồ đối chiếu ngược với văn bản (sơ đồ không nói điều văn bản không nói) |
| 6 | Đồng bộ phụ thuộc bằng grep: threat model, problem-control map, `docs/adr/README.md` (dòng 3–4 về evidence, dòng "rollout plan (layer 8)"), `framework.md:20` ("Nothing here was checked locally (✅)" phải sửa khi examples có output ✅), link, số layer, mã G/OD | Grep có hệ thống, không đọc lại bằng mắt |
| 7 | Engineer guide, rồi README | Đều là bản tóm tắt; viết cuối để tóm đúng bản cuối |
| 8 | Review độc lập toàn bộ (Rule 4) → sửa → review lại tới khi hết HIGH/MEDIUM; quét secret/PII; kiểm link; chạy `examples/validate.sh`; copy transcript | Cổng chất lượng trước khi nộp |

Mỗi bước 1–4 có review độc lập riêng trên phần vừa viết (Rule 4).

---

## 3. Config mẫu trong `examples/`

Nguyên tắc chọn: mỗi file phải (1) chứng minh một claim cụ thể trong framework hoặc ADR, và (2) kiểm được
**cục bộ**, không chạm hạ tầng thật (Rule 4). Mỗi kiểm tra ghi rõ nó **không** chứng minh điều gì.

Quy ước chung:
- Placeholder (`<AWS_ACCOUNT_ID>`, `123456789012`, `<org>`, `<ORG_ID>`…); comment đầu file trỏ về layer/ADR,
  phase áp dụng, và marker cho trường/khóa chưa kiểm.
- Test viết bằng Python `unittest` (✅ có sẵn; `pytest` chưa cài ✅), đặt trong `examples/tests/`.
- `examples/validate.sh` chạy mọi kiểm tra, in phiên bản từng công cụ, và **bỏ qua có thông báo rõ** công cụ chưa
  cài (không âm thầm báo đạt); output thật dán vào `examples/README.md` (✅).

### 3.1 Tier A — lõi (phải có)

| # | File | Chứng minh điều gì | Kiểm bằng | Giới hạn của kiểm tra |
|---|---|---|---|---|
| E1 | `examples/github/ruleset-main.json` | ADR-0003: merge vào `main` là cổng duyệt. PR bắt buộc, 1 approval, code-owner review, dismiss stale, approval ≠ last pusher, required check có source app pin, **branch phải up to date trước khi merge** (`strict_required_status_checks_policy`, vì không có merge queue — layer 3, owner chốt bỏ merge queue), cấm force push, bypass list rỗng (📖 R3.2.2, R3.2.3, R3.2.5; riêng "up to date" là ⚠️ R4.6 #1 như framework ghi) | (1) `jq` + JSON Schema của request body "create a repository ruleset" trích từ GitHub REST OpenAPI description (`github/rest-api-description`). Reviewer vòng 2 đã trích thử được; khi viết sẽ chạy lại và ghi lệnh (✅). (2) Test khóa theo **đường dẫn**: mọi khóa phải nằm trong `properties` đã trích tại đúng vị trí (ví dụ `require_last_push_approval`, `dismiss_stale_reviews_on_push`, `strict_required_status_checks_policy`, `integration_id`). (3) Test: đủ các rule trên, `bypass_actors` rỗng | Schema không có `additionalProperties: false`, nên (1) không bắt được khóa viết sai — vì vậy cần (2). Spec là OpenAPI 3.0 (`nullable`, `$ref`), phải resolve/chuyển trước khi dùng Python `jsonschema`. Không chứng minh GitHub áp đúng như mô tả. `integration_id` là placeholder, phụ thuộc gap G19 |
| E2 | `examples/github/CODEOWNERS` | Layer 3/5: L3 path chuẩn chỉ thuộc L3 owner team; on-call group đồng sở hữu path deploy được nhưng **không** đồng sở hữu path định nghĩa quy trình (OD9, OD13); `deploy-approvals/<stack>/` thuộc owner stack + on-call (OD8) | Test resolve **owner thực tế** cho một danh sách path mẫu theo luật "dòng khớp cuối cùng thắng" của CODEOWNERS (⚠️: luật này chưa có dòng 📖 trong research, cần thêm khi viết), rồi kiểm: (a) mọi path L3 chuẩn ở layer 5 → chỉ L3 team; (b) path deploy được → domain team + on-call; (c) dòng đúng cú pháp | Không phát hiện được team không tồn tại hoặc thiếu quyền write (GitHub bỏ qua im lặng, 📖 R3.2.7); endpoint báo lỗi của GitHub cần repo thật → không dùng |
| E3 | `examples/github/workflows/deploy-prod.yml` (**reusable**, `on: workflow_call`, như framework dòng 359 yêu cầu), `deploy-on-main.yml` (caller, `push` lên `main`), `pr-preview-nonprod.yml` | Điều kiện "merge approval = deploy approval" (layer 3) và layer 5: OIDC (`id-token: write`), `permissions:` theo job, action pin SHA, PR chỉ preview non-prod | (1) `actionlint` + `zizmor` (chưa cài ✅, §5 Q5) và `yamllint` (✅ có): cú pháp và mẫu rủi ro đã biết. (2) Test riêng `test_workflow_policy.py` trên **mọi** file workflow, không phụ thuộc linter: chỉ workflow deploy reusable tham chiếu `environment: production`; không input ref/SHA; không `pull_request_target`/`workflow_run`/`issue_comment`; mỗi stack một concurrency group, không `cancel-in-progress`; mọi `uses:` pin SHA 40 ký tự; `permissions:` khai báo ở từng job; `id-token: write` chỉ ở job cần OIDC | Linter không hiểu các điều kiện thiết kế, nên mới cần test (2). Test chỉ thấy file trong `examples/`, không thấy cả monorepo |
| E3b | `examples/github/environment-production/`: `environment.json` (body `PUT …/environments/production`: `deployment_branch_policy` với `custom_branch_policies: true`, `protected_branches: false`, **không có `reviewers`**), `branch-policy.json` (body `POST …/deployment-branch-policies`: `{"name": "main", "type": "branch"}`), `secrets.md` (chỉ **tên** secret ngoại lệ k0s/Firebase, không giá trị; đặt qua secrets API; tùy chọn environment riêng `production-k0s` như layer 5) | Environment `production` chỉ cho `main`, không có required reviewers (Team, repo private, 📖 R3.1.2); chứa secret ngoại lệ k0s/Firebase (OD1, OD6). Đây là thứ giới hạn branch nào lấy được role prod, vì `sub` dạng environment không chứa branch (⚠️ suy luận R3.4.3) | `jq` + test trên cả hai body: `custom_branch_policies` bật, policy chỉ có `main`, không có `reviewers`; khóa đối chiếu với schema trích từ OpenAPI như E1 | Là ba lời gọi API riêng (reviewer vòng 2 kiểm trong OpenAPI description), không phải một file cấu hình; GitHub có thể khác mô tả |
| E4 | `examples/aws/oidc-trust-prod-deploy.json` | Layer 1/ADR-0008: role deploy prod chỉ tin `sub` = `repo:<org>@<ORG_ID>/<repo>@<REPO_ID>:environment:production` — **định dạng immutable** có owner ID và repo ID (định dạng 📖 R3.4.4, ví dụ của GitHub ở dạng `ref`; áp sang dạng `environment` là ⚠️ suy luận R3.7 A2, như framework ghi); `aud` = `sts.amazonaws.com` (📖 R3.4.1). Comment: repo cũ dùng định dạng không có ID trừ khi opt in; tùy chọn thêm `job_workflow_ref` (⚠️ G10) | `jq` + test: `StringEquals` (không `StringLike`/wildcard) trên `sub` đúng dạng immutable và trên `aud`. Access Analyzer `validate-policy` là API AWS → không dùng (Rule 4). Linter offline (`parliament`) ⚠️ chưa kiểm còn bảo trì và có hỗ trợ trust policy | Không chứng minh AWS chấp nhận policy |
| E5 | `examples/aws/scp-prod-ou.json` (phase 2) | Layer 1: deny đúng `lambda:UpdateFunctionCode` và `lambda:UpdateFunctionConfiguration` trừ deploy roles và JIT roles; revocation Deny theo `identitystore:UserId`; bảo vệ org trail; deny data-plane read trên claim store trừ role ứng dụng / data-read (danh sách action chưa đủ, ⚠️ G13). SCP deny ghi ra ngoài org (`aws:ResourceOrgID`, mọi OU) **không** nằm trong file này | `jq` + test: chỉ có `Deny`; kích thước ≤ 10 240 ký tự (📖 R2.3.4), đo cả bản minify và bản nguyên như sẽ deploy | Khoảng trắng có tính vào giới hạn hay không ⚠️, nên bản minify chỉ là cận dưới. Không chạy được policy simulator (cần AWS) |
| E6 | `examples/aws/permission-set-prod-read-metadata.json` | Layer 1/ADR-0002: `ProdReadMetadata` chỉ đọc metadata, session 1 h (📖 R2.1.4). Đọc log thô (`logs:GetLogEvents`) và `lambda:GetFunctionConfiguration` chỉ cho từng service đã redact/chuyển secret (layer 1) | File theo hình dạng của API Identity Center (inline policy + `SessionDuration`), ghi rõ trong comment. Test: (a) sau khi **mở rộng wildcard action** (ví dụ `logs:Get*`) theo một danh mục IAM action offline — AWS Service Authorization Reference dạng JSON tải một lần, hoặc dữ liệu đi kèm `policy_sentry`/`parliament` (§5 Q5; nguồn ⚠️ chưa kiểm) — không action nào thuộc danh sách data-plane đã biết (`s3:GetObject`, `sqs:ReceiveMessage`, `states:GetExecutionHistory`, `secretsmanager:GetSecretValue`, …); (b) mọi action đọc dữ liệu log hoặc cấu hình hàm (`logs:GetLogEvents`, `logs:FilterLogEvents`, `logs:StartQuery`/`GetQueryResults`, `lambda:GetFunctionConfiguration`, …) chỉ đi với ARN trong allowlist từng service, không `Resource: "*"`; (c) `Resource: "*"` chỉ được cho action đọc metric/metadata | Chỉ chứng minh các action **đã liệt kê** vắng mặt hoặc bị giới hạn; danh sách data-plane chưa đủ (G13) |
| E7 | `examples/risk-stop/`: `classify.py`, `adapters/pulumi.py`, `adapters/serverless.py`, `fixtures/`, `deploy-approvals/<stack>/<sha>.yaml`, test | Risk stop ([design], layer 3): phát hiện replace/delete stateful, thay đổi IAM, network/security group → dừng; tính hash preview để so khi deploy lại (Options §1) | Classifier chạy trên một **định dạng chuẩn hóa nhỏ** do repo này định nghĩa (danh sách thay đổi: loại resource, thao tác). Hai adapter đọc output `pulumi preview --json` và `serverless diff --json` sang định dạng đó; cấu trúc JSON thật của hai lệnh **chưa có trong research** (R4.1.1, R4.4.2 chỉ nêu flag) → adapter và fixture của adapter gắn ⚠️. `unittest` trên fixture chuẩn hóa | Fixture viết tay, không sinh từ Pulumi/Serverless thật (chưa cài ✅, Rule 4). **Không chứng minh hash ổn định giữa các lần preview** (⚠️ Options §8). Có thể research cấu trúc JSON trước khi viết để nâng adapter lên 📖 |

### 3.2 Tier B — hỗ trợ (nên có)

| # | File | Chứng minh điều gì | Kiểm bằng | Giới hạn |
|---|---|---|---|---|
| E8 | `examples/claude/managed-settings.phase1.json`, `managed-settings.phase2.json` | Layer 2/ADR-0007 và phân pha OD4: phase 1 chỉ các khóa ở layer 8; phase 2 đủ baseline | (1) JSON Schema `https://json.schemastore.org/claude-code-settings.json` qua Python `jsonschema` (✅ có). (2) Test khóa **theo đường dẫn** (ví dụ `defaultMode`, `disableBypassPermissionsMode` dưới `permissions`; `autoAllowBashIfSandboxed` dưới `sandbox`): mọi khóa phải nằm trong `properties` của schema tại đúng vị trí **hoặc** trong một allowlist ghi rõ dòng R 📖 | Lệnh kiểm bên dưới gộp khóa ở mọi cấp, nên chỉ chứng minh khóa tồn tại đâu đó trong schema, không chứng minh đúng vị trí. Schema do cộng đồng duy trì, không phải nguồn chính thức; top-level `additionalProperties: true` (reviewer kiểm), nên (1) không bắt được khóa viết sai — vì vậy cần (2). ✅ 2026-11-09, lệnh: `curl -sL <schema> \| jq '[.. \| objects \| .properties? // empty \| keys[]] \| unique'` rồi grep 14 khóa: `strictKnownMarketplaces`, `allowManagedHooksOnly`, `allowManagedMcpServersOnly`, `allowManagedPermissionRulesOnly`, `requiredMinimumVersion`, `disableSideloadFlags`, `allowedProviders`, `forceLoginOrgUUID`, `disableBypassPermissionsMode`, `autoAllowBashIfSandboxed`, `blockedMarketplaces`, `allowedMcpServers`, `disableClaudeAiConnectors`, `managedSourcesBehavior` → có 12, **thiếu `allowedProviders` và `managedSourcesBehavior`** (hai khóa này chỉ dựa vào 📖 R1.1.15, R1.1.3/R1.1.4) |
| E9 | `examples/claude/marketplace/.claude-plugin/marketplace.json` + `catalogue-entry.example.md` | Layer 4/ADR-0006: catalogue là marketplace nội bộ, nguồn pin theo `sha`; mẫu bản ghi review một MCP/plugin (checklist layer 4) | `claude plugin validate <path>` (✅ có trong Claude Code 2.1.319) + test: mọi nguồn plugin bên ngoài có `sha`; nguồn đường dẫn tương đối (plugin nằm ngay trong repo marketplace, R1.4.1) được miễn vì đã nằm dưới ruleset của repo đó | `validate` chỉ kiểm schema manifest, không kiểm việc pin: reviewer vòng 2 thử một khóa viết sai (`"shaa"`) và `validate` vẫn cho qua — nên có test riêng. Nếu docs xác nhận khóa `sha` khi viết, R1.4.1b nâng từ "link only" |
| E10 | `examples/pulumi-policy/` (TypeScript, 1–3 policy) | Layer 5 / OD8: bù cho việc owner stack duyệt thay đổi IAM — ví dụ mandatory: cấm IAM `Action: "*"`, Aurora phải có deletion protection, S3 claim bucket chặn public | `npm ci && npx tsc --noEmit` (tải `@pulumi/policy`, `@pulumi/aws` từ npm; không chạm cloud). `package-lock.json` tạo một lần bằng `npm install` và commit, để `npm ci` chạy được | `tsc` chỉ chứng minh code biên dịch được, **không** chứng minh policy kích hoạt đúng. Tên sản phẩm hiện là **Pulumi Policies**; "CrossGuard" là tên cũ (📖 R4.2.1) |

### 3.3 Tier C — chỉ làm nếu còn thời gian

- `examples/github/workflows/claude-ci-agent.yml` (claude-code-action với GitHub App riêng, `--restricted`, `--tools`):
  nhiều điểm ⚠️ (truyền flag qua `claude_args` — research 6.9.4 Q5; PR do app mở được tính tác giả thế nào — R3.7, G19). Nếu làm
  thì gắn nhãn "illustrative".

### 3.4 Phản biện gợi ý ban đầu (phần examples)

| Gợi ý | Đánh giá | Thay bằng / bổ sung |
|---|---|---|
| "GitHub Actions OIDC + environment approval" | **Sai với thiết kế đã chốt.** Trên GitHub Team, repo private không có required reviewers cho environment (📖 R3.1.2; gói Team là giả định owner đã chốt, GĐ-5). Example dùng `required_reviewers` sẽ mâu thuẫn ADR-0003 và làm người chấm nghĩ thiết kế dựa vào tính năng không có | E3 + E3b: environment chỉ có branch restriction + secrets; cổng duyệt là **E1 ruleset**. Có thể thêm comment "nếu lên Enterprise thì thêm required reviewers" |
| "IAM permission set" | Đúng nhưng chưa đủ: permission set chỉ chứng minh quyền đọc. Ranh giới thật ở layer 1 là trust policy của role deploy và SCP | Giữ E6, thêm E4 (định dạng `sub` immutable) và E5 |
| "CODEOWNERS" | Đồng ý; là nửa còn lại của cổng | E2, test theo luật "dòng khớp cuối thắng", vì GitHub bỏ qua dòng sai mà không báo (📖 R3.2.7) |
| "managed settings" | Đồng ý, nhưng là hygiene (ADR-0007), không phải lõi | Tier B (E8), hai file theo phase để thể hiện OD4 |
| "Pulumi CrossGuard policy" | Hữu ích nhưng là control phase 2, chỉ bù cho OD8 | Tier B (E10), tên Pulumi Policies |
| Thiếu | Ruleset `main` — artifact quan trọng nhất (chính là "named person approved") | E1 |
| Thiếu | Risk stop — điểm [design] mới nhất, chưa có gì chứng minh nó làm được | E7 |
| Thiếu | Catalogue plugin/MCP — ưu tiên số 3 trong 30 ngày (framing Q8) | E9 |
| checkov (nêu như ví dụ công cụ) | Không dùng làm công cụ chính: checkov quét Terraform/CloudFormation/Kubernetes/Actions; file IAM ở đây là JSON thuần, hỗ trợ của checkov cho JSON IAM rời ⚠️ chưa kiểm. Có thể chạy thêm trên workflow (E3) nếu cài được | `actionlint` + `zizmor` + test thiết kế cho workflow; test Python cho policy |

---

## 4. Cố ý KHÔNG đưa vào

| Không đưa vào | Lý do |
|---|---|
| Đề xuất thay Pulumi/Serverless/GitHub Actions; ví dụ Terraform | Ràng buộc cứng của đề (`CLAUDE.md`) |
| Config cụ thể cho k0s, Firebase, GCP | Chưa research (G1–G3). Viết ra là bịa; framework chỉ nêu nguyên tắc ở mức này (framing Q7) |
| Example hook Claude Code (managed hook) — **owner chốt bỏ, §5 Q6; README ghi lệch so với framing Q14** | Framing Q14 và README khung có nhắc "hooks". Nhưng framework không định nghĩa hook cụ thể nào: chỉ khóa `allowManagedHooksOnly` (phase 2) và giới hạn "hooks fail open unless `onFailure: "block"`" (layer 2). Viết một hook mẫu là thêm một control chưa có trong thiết kế đã duyệt, và nó chỉ là lớp tư vấn (ADR-0007). E8 vẫn chứa khóa `allowManagedHooksOnly` |
| Chương trình Pulumi đầy đủ cho Identity Center / SCP stack | Không chạy được (không có Pulumi, Rule 4); JSON policy đủ chứng minh nội dung |
| Code JIT (TEAM sample, bot Slack), code GitHub App cho required check | Là gap mở (G19, G20) hoặc lựa chọn sản phẩm chưa làm; code minh họa sẽ trông như đã thiết kế xong |
| Runbook SSM Automation | Phase 2, chưa kiểm (OD4, G6) |
| Cấu hình paging/alert routing | Phase 2, công cụ chưa chọn (G5) |
| `managed-mcp.json`, cấu hình MDM | Không biết Papaya có MDM (layer 2) |
| Bảo mật AI agent production | Ngoài phạm vi (framing §1.4, A7a) |
| Statement of Applicability đầy đủ, phân tích pháp lý HIPAA/luật VN | Ngoài chuyên môn; HIPAA có áp dụng hay không là câu hỏi pháp lý (⚠️ R1.11.1.11). Register chỉ trỏ tới mã điều khoản với marker |
| Ước tính effort / chi phí bằng con số | Không có dữ liệu; framework ghi "effort not estimated" |
| Slide, deck, trang web | Hình thức đã chốt là markdown + examples (framing Q14) |
| Phương án mới, mở lại quyết định đã chốt | Bước này là đóng gói. Viết lại mà lộ mâu thuẫn thì ghi thành câu hỏi cho owner |
| Dịch `work/` sang tiếng Anh | Rule 3 chỉ yêu cầu `## English summary` |
| CI cho chính repo nộp bài | Thêm việc, ít giá trị cho người chấm; output kiểm dán vào `examples/README.md` |

---

## 5. Câu hỏi cho owner (đã trả lời 2026-11-09)

Owner chọn đề xuất ở cả 7 câu (trả lời "OK" cho từng câu).

| # | Câu hỏi | Đề xuất | Quyết định |
|---|---|---|---|
| Q1 | Framework: (a) giữ ~11k từ, chỉ sửa link; (b) ~9.5–10k: chuyển rollout và chi tiết evidence ra file riêng, mỗi layer giữ một câu tóm tắt evidence; (c) như (b) và biên tập thêm câu chữ xuống ~8k, coi là sửa tài liệu đã duyệt (cần owner duyệt lại + review); (d) tách thành 8 file theo layer | **(b).** (c) tốn thêm vòng review cho tài liệu đã qua 17 vòng; (d) phá mọi tham chiếu "layer N" trong ADR, threat model, map | OK → (b) |
| Q2 | Có viết `02-engineer-guide.md` không? | **Có**, ~1 200 từ, chỉ trình bày lại. Mục đầu tiên cắt nếu thiếu thời gian | OK → Có |
| Q3 | Đổi tên docs sang tiền tố số (`01-framework.md` …) theo quy ước repo? | **Có.** Việc cơ học, kiểm bằng grep link; ADR giữ tên vì đã có số riêng | OK → Có |
| Q4 | Phạm vi examples: Tier A + B, bỏ Tier C? | **Có** | OK → Tier A + B |
| Q5 | Cho phép cài cục bộ, trong venv/thư mục scratch, không global: `actionlint`, `zizmor`, thử `parliament` hoặc `policy_sentry` (hoặc tải JSON Service Authorization Reference) làm danh mục IAM action cho E6; và `npm ci` tải `@pulumi/policy`, `@pulumi/aws` cho E10? (Test Python dùng `unittest` nên không cần `pytest`) | **Có**. Không chạm hạ tầng | OK → Có |
| Q6 | Framing Q14 có liệt kê "hooks". Bỏ example hook (lý do ở §4), hay thêm một hook nhỏ gắn nhãn advisory? | **Bỏ**, ghi lệch so với Q14 trong README. Thêm hook là thêm control mới | OK → Bỏ hook, ghi lệch so với Q14 |
| Q7 | `docs/problem-control-map.md` vẫn ghi "draft for owner review". Coi là đã duyệt (owner cho commit sau mục 4) và đổi status, hay review thêm? | **Đổi status thành approved** nếu owner xác nhận; không review thêm | OK → Approved |

---

## 6. Review log

- **Vòng 1 (2026-11-09, agent độc lập):** 1 HIGH, 9 MEDIUM, 12 LOW. Đã sửa hết:
  - HIGH: E4 dùng định dạng `sub` cũ, lệch với giả định A2 (immutable, 📖 R3.4.4) → sửa sang dạng có ID.
  - MEDIUM:
    - Mục tiêu ~8k từ không đạt được chỉ bằng chuyển nội dung (chỉ bớt ~1 270 từ) → đổi mục tiêu, thêm Q1 (c).
    - E1 thiếu "branch up to date".
    - E3: linter không kiểm điều kiện thiết kế → thêm test riêng và E3b (environment).
    - E8: schema có `additionalProperties: true` và không chính thức → thêm test khóa, ghi lệnh kiểm.
    - E7: research chưa có cấu trúc JSON của preview → thêm định dạng chuẩn hóa và adapter gắn ⚠️, nói rõ không chứng minh được hash ổn định.
    - Thiếu hooks so với framing Q14 → ghi vào §4, thêm Q6.
    - `pytest` chưa cài, `npm ci` cần tải → chuyển sang `unittest`, bổ sung Q5.
    - Thứ tự viết: lõi phụ thuộc layer 5 → sửa bước 3.
    - Kiểm CODEOWNERS ngây thơ → resolve theo luật "dòng khớp cuối thắng".
  - LOW: trích dẫn (R2.3.4, R3.4.1), action Lambda chính xác, phase của SCP, định dạng E6, G19 cho `integration_id`, kiểm pin `sha` cho E9, giới hạn của `tsc`, status của map (Q7), mục đồng bộ ở bước 6.
- **Vòng 2 (2026-11-09, agent độc lập mới):** 0 HIGH, 3 MEDIUM, 8 LOW. Các sửa của vòng 1 được xác nhận. Đã sửa hết:
  - MEDIUM:
    - E3b không thể là một body REST → tách thành body environment, body branch policy và danh sách tên secret.
    - E1: schema không chặn khóa lạ → thêm test khóa theo đường dẫn; ghi việc chuyển `nullable`/`$ref`.
    - E6: test chưa kiểm phần quan trọng nhất → thêm kiểm ARN theo service cho action đọc log/cấu hình; nêu nguồn danh mục action.
  - LOW:
    - Marker cho E4 (dạng environment là ⚠️ A2) và E1 ("up to date" là ⚠️ R4.6 #1).
    - E3 dùng reusable workflow; test thêm kiểm pin SHA và `permissions`.
    - E8 kiểm khóa theo đường dẫn; E9 miễn nguồn tương đối; E10 có lockfile.
    - Sửa trích dẫn Tier C; đánh số liền E1–E10.
    - English summary rút còn ~10 dòng.
    - E5 đo cả hai kích thước.
    - `validate.sh` bỏ qua công cụ chưa cài kèm thông báo.
    - Ghi số từ bớt ròng.
  - Vòng 2 không còn HIGH; các sửa của vòng 2 chưa có vòng kiểm lại.
