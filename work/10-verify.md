# 10 — Verify: kiểm tra máy móc examples/, diagrams/, docs/ và toàn repo

## English summary

Machine checks of 2026-11-09 (session 26fa6806); commands and trimmed output below. Nothing in
`docs/`, `examples/`, `diagrams/` was changed by the checks themselves (fixes: §10). Results: (1) syntax of all JSON/YAML/workflows/Python
passes; (2) checkov (k8s 13/0, Actions 196/0, IAM via a CloudFormation wrapper 68/13, OIDC trust via
a Terraform wrapper: CKV_AWS_393 fails 5/5 as a false positive on the immutable `sub` format) and
parliament find no defect beyond by-design items, plus one unstated evidence-bucket setting (V4);
(3) all 3 Mermaid sources render, but `diagrams/03-incident-lane.svg` is stale (V1); (4) 167 internal
links and 12 URLs, none broken; (5) gitleaks: 3,511 hits, all false positives in `transcripts/`;
the owner checked the email addresses in transcripts and had the two work addresses redacted (V13);
(6) of 349 identifiers, 181 match
`02-research.md` (an upper bound); about 15 tool capabilities lack a marker (§6.4, 📖 sources now
proposed for most); the JIT role's tag condition was first flagged as unverified (V7), later found
documented (R9.9.11). Independent reviews: §9, §10. Fix list in §7; V1, V7, V11 and the action-SHA
check were done the same day (§10).

## 0. Môi trường và công cụ

| Công cụ | Version | Nguồn |
|---|---|---|
| Python | 3.10.12 (validate.sh), 3.12 (venv) | hệ thống |
| jsonschema / PyYAML | 4.26.0 / 6.0.3 | đã có |
| jq / yamllint / shellcheck | 1.6 / 1.38.0 / 0.8.0 | đã có |
| actionlint | 1.7.12 | binary do session 6db3dd9e tải về, trong scratchpad của session đó (không cài lại) |
| zizmor | 1.30.1 | như trên |
| claude | 2.1.319 | đã có |
| mmdc (@mermaid-js/mermaid-cli) | 11.12.0 | đã có |
| gitleaks | 8.30.1 | đã có |
| gh / aws-cli / docker / git | 2.103.3 / 2.17.8 / 29.2.1 / 2.34.1 | đã có; **chỉ đọc `--help`**, không gọi API nào |
| checkov | 3.4.3 | **cài mới** (owner đồng ý) vào venv trong scratchpad của session này |
| parliament | 1.6.4 (+ `setuptools` 80.10.2, cần cho `pkg_resources`) | như trên |

Ghi chú cài đặt: `python3 -m venv` (3.10) lỗi vì thiếu `ensurepip`, nên dựng venv bằng
`python3.12 -m venv`. Repo và `~/.local` không bị đụng tới.

Thư mục kết quả thô (không commit): scratchpad của session này, `out/*.txt|json`.

---

## 1. Cú pháp mọi file trong `examples/`

### 1.1 Script có sẵn

```bash
ACTIONLINT=<scratchpad 6db3dd9e>/tools/bin/actionlint ZIZMOR=<scratchpad 6db3dd9e>/tools/py/bin/zizmor \
  examples/validate.sh
```

```text
=== JSON syntax (jq) ===            checked 40 files
=== YAML style (yamllint) ===       (no output)
=== GitHub Actions (actionlint) === actionlint done
=== GitHub Actions security (zizmor, offline, auditor persona) ===
 ... completed 6 workflows ... No findings to report. Good job!
=== Claude Code plugin marketplace (claude plugin validate) ===  ✔ Validation passed
=== Pulumi policy pack ===          35/35 cases passed; all policies mandatory
=== unit tests ===                  Ran 192 tests in 1.598s  OK
RESULT: all executed checks passed        (exit 0)
```

### 1.2 Bổ sung (validate.sh chỉ chạy yamllint trên `github/workflows`)

| Lệnh | Kết quả |
|---|---|
| Kiểm kê `git ls-files examples/` | json 40, yml 6, yaml 6, md 12, py 18, ts 3, sh 1, txt 1, + `.gitignore`, `CODEOWNERS` |
| `yaml.safe_load_all` cho mọi `*.yml`/`*.yaml` | `12 files, 0 failed` |
| Front matter YAML của 4 `SKILL.md` | cả 4 parse được, có `name` + `description` |
| `yamllint` (cấu hình như validate.sh) trên **cả 12** file YAML | exit 0, không có dòng nào |
| `actionlint -verbose … github/workflows/*.yml` | `Found 0 errors in 6 files` |
| `actionlint` **không có** `-ignore` | 4 lỗi, đều cùng một loại: `deploy-on-main.yml:15,26,37,47` `reusable workflow call "$/.github/workflows/deploy-prod.yml" … is not following the format` |
| `shellcheck examples/validate.sh work/setup-clean-config.sh` | exit 0 |
| `ast.parse` cho 18 file `.py` | `18 py files parse OK` |
| TypeScript (`tsc` trong `npm test` của policy pack) | pass (mục 1.1) |

Về cú pháp `$/`: GitHub docs ghi: "`$/.github/workflows/{filename}` for a reusable workflow in
the same repository. This is the recommended syntax …" (📖
[reusable-workflow-calling-syntax.md](https://raw.githubusercontent.com/github/docs/main/data/reusables/actions/reusable-workflow-calling-syntax.md),
HTTP 200, đọc lại 2026-11-09). Vì vậy `-ignore` trong validate.sh là đúng. Bản đã render trên
docs.github.com (trang `workflow-syntax`, mục `jobs.<job_id>.uses`) cũng có câu này, và đây là link
nên dùng làm nguồn chính.

`-ignore` cũng tắt luôn việc actionlint đối chiếu `with:`/`secrets:` giữa workflow gọi và
`workflow_call` của workflow được gọi. Để biết nó có che lỗi nào không: copy 6 workflow vào
`<scratchpad>/r7/.github/workflows/`, đổi `uses: $/.github…` thành `uses: ./.github…` (4 chỗ), rồi chạy
`actionlint` **không có** `-ignore` → `exit=0`. Không có lỗi nào bị che.

**Cần sửa:** không có lỗi cú pháp. Ghi nhận (V2, LOW): nguồn của `$/` chỉ nằm trong
`work/07-review.md:41-44`, chưa có trong `02-research.md`.

---

## 2. checkov và công cụ tương đương trên IAM policy / config cloud

### 2.1 checkov trực tiếp

```bash
checkov -d examples --compact --skip-download
```

```text
kubernetes scan results:
Passed checks: 13, Failed checks: 0, Skipped checks: 0      # chỉ examples/k0s/deploy-rbac.yaml
```

Hai giới hạn của checkov 3.4.3 thấy được ở đây:

- Framework `github_actions` chỉ quét file nằm dưới `.github/workflows/`. `checkov -f <file>
  --framework github_actions` không ra kết quả nào. Khi copy 6 workflow vào
  `<scratchpad>/gha/.github/workflows/` thì có kết quả: `github_actions scan results: Passed checks:
  196, Failed checks: 0`.
- Các file IAM JSON đứng riêng không được framework nào nhận (ngay cả `-d aws --framework
  cloudformation` cũng không ra kết quả). Framework `secrets` không có finding nào.

### 2.2 checkov qua một CloudFormation template bọc ngoài

Để chạy được các check IAM/S3/Logs của checkov, một script trong scratchpad bọc 15 file
`examples/aws/*.json` thành 16 resource CloudFormation: policy → `AWS::IAM::ManagedPolicy`, trust →
`AWS::IAM::Role`, SCP → `AWS::Organizations::Policy`, permission set → `AWS::SSO::PermissionSet`
(cộng một bản `ManagedPolicy` của inline policy), Object Lock → `AWS::S3::Bucket`, data protection
→ `AWS::Logs::LogGroup`. Repo không thay đổi.

```bash
checkov -f <scratchpad>/cfn/template.json --framework cloudformation --compact --skip-download
```

```text
Passed checks: 68, Failed checks: 13, Skipped checks: 0
CKV_AWS_107/108/109/110/111  FAILED  AWS::IAM::ManagedPolicy.AppPermissionsBoundary
CKV_AWS_53/54/55/56/18/21    FAILED  AWS::S3::Bucket.EvidenceBucketObjectLock
CKV_AWS_158/66               FAILED  AWS::Logs::LogGroup.LogsDataProtectionPolicy
```

| Finding | Đánh giá |
|---|---|
| 5 check IAM trên `app-permissions-boundary.json` (`Allow "*"`) | **Đúng thiết kế.** Đây là permissions boundary, tức trần quyền chứ không phải quyền được cấp; quyền thực tế là phần giao với identity policy (E4b). Không sửa |
| 6 check S3 (Block Public Access ×4, access logging, versioning) | Template bọc ngoài chỉ có phần Object Lock, vì file example chỉ chứa body `PutObjectLockConfiguration`. **Nhưng** docs cũng không nói evidence bucket chặn public access hay bật access logging (grep `docs/`, `examples/README.md` không thấy) → V4. Versioning: ⚠️ theo trí nhớ, S3 tự bật khi bucket tạo với Object Lock; chưa kiểm |
| 2 check Logs (KMS, retention) | Do template bọc ngoài: file example là data protection policy, không phải cấu hình log group. Không sửa |

Phạm vi thật của con số 68/13: `AWS::Organizations::Policy` (SCP) và `AWS::SSO::PermissionSet`
**không nhận check checkov nào** (`-o json`, gom theo resource: không có dòng cho `ScpProdOu` và
`PermissionSetProdReadMetadata`). Hai check của LogGroup không liên quan tới data protection policy.
SCP chỉ được parliament kiểm (2.3) và được kiểm bằng unit test của repo. Inline policy của permission
set thì được checkov kiểm qua bản `PermissionSetProdReadMetadataMp`.

### 2.3 parliament (linter IAM offline)

Lưu ý khi chạy: shell của tool không có TTY nên parliament coi như có stdin. `--file` vì thế
thoát `exit=2` mà không in gì ("You cannot pass a file with --file and use stdin together").
Truyền nội dung qua `--string` thì chạy đúng. Lệnh đối chứng với một action gõ sai cho kết quả
`LOW - Unknown action - … s3:GetObjectt` (exit 1), chứng tỏ công cụ có bắt lỗi.

```bash
parliament --string "$(cat <file>)" --include-community-auditors --minimum_severity INFO
# chạy 2 lần: bản gốc, và bản thay placeholder <…ACCOUNT_ID>/<REGION> bằng giá trị mẫu
```

Kết quả sau khi thay placeholder (bỏ các finding chỉ do placeholder):

| File | Finding | Đánh giá |
|---|---|---|
| `evidence-export-role-policy.json`, `scp-prod-ou.json` | 0 | — |
| `app-permissions-boundary.json` | HIGH privesc (`lambda:UpdateFunctionCode`, `glue:UpdateDevEndpoint`), MEDIUM credentials exposure, MEDIUM permissions management | Hệ quả của `Allow *` trong boundary; đúng thiết kế (như 2.2) |
| `db-change-ci-role-policy.json` | MEDIUM permissions management: `iam:PassRole` | Đã giới hạn bằng `iam:PassedToService = ecs-tasks.amazonaws.com` và hai role ARN cụ thể; chấp nhận được |
| `db-change-task-role-policy.json` | MEDIUM credentials/permissions: `rds-db:connect` | Đúng mục đích (IAM auth vào một DB user) |
| `deploy-role-domain-iam-limits.json` | MEDIUM permissions management (`iam:DetachRolePolicy`, `iam:UpdateAssumeRolePolicy`…); LOW `StringEquals` so với ARN ở dòng 17 (`iam:PermissionsBoundary`) | Đúng phạm vi `svc-*`; `iam:UpdateAssumeRolePolicy` không có điều kiện boundary là giới hạn đã ghi ở E4b. Kiểu của key `iam:PermissionsBoundary` là `ARN` (📖 service reference `iam.json`: `{"Types":["ARN"]}`), nên cảnh báo của parliament đúng về kỹ thuật. Việc ví dụ của AWS cũng dùng `StringEquals` thì vẫn là ⚠️ theo trí nhớ |
| `jit-receiver-role-policy.json` | MEDIUM "No resources match" cho `sso:Create/DeleteAccountAssignment` | parliament xét **từng statement riêng**, còn policy cố ý tách permission set (có điều kiện tag) khỏi instance + account. Format ARN của cả ba resource đúng (📖 Service Authorization Reference `sso.json`, đọc 2026-11-09). Về điều kiện tag, xem V7 và §10 |
| 5 file `oidc-trust-*.json` | HIGH "neither Resource nor NotResource", MEDIUM "Unknown federation source" | False positive: trust policy không có `Resource`; parliament không biết provider OIDC của GitHub |
| inline policy của permission set | LOW "Unnecessary use of Resource *" (vd. `ecs:DescribeServices`, `cloudwatch:DescribeAlarms`, `lambda:GetFunctionConcurrency`) | Allowlist metadata đã review (E6); nếu muốn có thể thu hẹp theo resource. Không bắt buộc |

### 2.4 checkov trên OIDC trust policy (thêm sau review, §9 R1)

Check checkov đúng chỗ nhất cho trust policy GitHub OIDC là CKV_AWS_358 và CKV_AWS_393. Cả hai **chỉ
có cho Terraform**, nên lớp bọc CloudFormation ở 2.2 không bao giờ chạy chúng. Reviewer bọc 5 file
`oidc-trust-*.json` thành `aws_iam_role` Terraform, ở `<scratchpad>/review/tf/main.tf`.

```bash
checkov -d <scratchpad>/review/tf --framework terraform --check CKV_AWS_358,CKV_AWS_393 --compact --skip-download
```

```text
Check: CKV_AWS_393: "Ensure AWS GitHub Actions OIDC authorization policies only allow safe claims and claim order on IAM role"   ×5
Passed checks: 0, Failed checks: 5, Skipped checks: 0
```

Nguyên nhân nằm trong `checkov/common/util/oidc_utils.py:12`:
`gh_repo_regex = re.compile(r"(\$\{)?[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*(\})?/[^/]+")`. Regex không
chấp nhận `@`, nên `sub` dạng immutable `repo:example-org@<ORG_ID>/monorepo@<REPO_ID>:…`
(📖 R3.4.4) bị coi là sai. Theo reviewer: đổi sang dạng cũ `example-org/monorepo` thì 5/5 pass, và đổi
sang ID dạng số thì vẫn 5/5 fail. Kết luận: **false positive của checkov 3.4.3**, trust policy không
sai. Hệ quả cho Papaya: nếu sau này đưa checkov vào CI thì cần skip có ghi lý do (V12).

**Cần sửa:** V4 (evidence bucket) và V7 (điều kiện tag của JIT). Ghi nhận V12. Các mục còn lại
không cần sửa.

---

## 3. Diagrams

Repo **không có file `*.mermaid`**; nguồn là `diagrams/*.mmd`, nên kiểm các file đó. Docs và
README không có khối ```` ```mermaid ```` nào nhúng trực tiếp.

```bash
for f in diagrams/*.mmd; do mmdc -q -i $f -o <scratchpad>/mmd/$(basename $f .mmd).svg; done
```

```text
diagrams/01-change-workflow.mmd          exit=0 svg_bytes=42546
diagrams/02-identity-trust-boundaries.mmd exit=0 svg_bytes=41104
diagrams/03-incident-lane.mmd            exit=0 svg_bytes=34529
grep 'Syntax error' (fresh + committed SVGs): none
```

So nhãn chữ giữa SVG đã commit và bản render lại:

```text
01-change-workflow.svg           labels committed=59 fresh=59 IDENTICAL
02-identity-trust-boundaries.svg labels committed=58 fresh=58 IDENTICAL
03-incident-lane.svg             labels committed=40 fresh=40 DIFFER
  committed: "Approval before apply is met only partly here (accepted by the owner, Options §9)"
  source   : "Approval before apply is met only partly here (accepted by the author, for Papaya Compliance sign-off)"
```

**Cần sửa (V1, MEDIUM):** `diagrams/03-incident-lane.svg` đã cũ so với `03-incident-lane.mmd:33`, và
`docs/02-engineer-guide.md:150` trỏ tới file SVG này. Render lại theo lệnh trong
`diagrams/README.md:4`: `mmdc -i 03-incident-lane.mmd -o 03-incident-lane.svg -b white`.

---

## 4. Link nội bộ và link ngoài trong `docs/` và `README.md`

Script `linkcheck.py` (scratchpad) xử lý như sau:

- **Link nội bộ:** file đích phải tồn tại; `#anchor` phải khớp slug heading kiểu GitHub hoặc
  `<a id>`; `#Lnn` không được vượt quá số dòng của file.
- **Link ngoài:** gửi HEAD, nếu lỗi thì GET; timeout 30 s; User-Agent chung chung.
- Code block và inline code bị bỏ qua.

```bash
python3 -I linkcheck.py "$PWD" out/links.json README.md docs
```

```text
files: 22; internal links: 167, problems: 0; external URLs (unique): 12, non-200 or note: 0
```

Đối chiếu bằng `grep -oE 'https?://…'`: cũng ra 12 URL duy nhất, khớp với script. Cả 12 đều trả 200.
Fragment được kiểm riêng với heading thật trên trang:

| URL | Fragment |
|---|---|
| `code.claude.com/docs/en/settings-reference.md#allowmanagedhooksonly` | khớp heading `` `allowManagedHooksOnly` `` |
| `code.claude.com/docs/en/sandboxing.md#run-commands-outside-the-sandbox-with-excludedcommands` | khớp heading |
| `code.claude.com/docs/en/claude-directory#cleaned-up-automatically` | có `id="cleaned-up-automatically"` |

Lượt thêm (ngoài phạm vi yêu cầu): `examples/README.md`, `diagrams/README.md` có 53 link nội bộ
và 11 URL ngoài, 0 lỗi.

**Cần sửa:** không có.

Lưu ý: docs dẫn phần lớn nguồn qua mã `R…` (02/09-research) chứ không qua URL, nên check này
chỉ phủ 12 URL. Còn URL trong `work/` thì chưa được kiểm.

---

## 5. gitleaks trên toàn repo

```bash
gitleaks git . --redact --no-banner -r out/gitleaks-git.json -f json   # 23 commits, 138.72 MB
gitleaks dir . --redact --no-banner -r out/gitleaks-dir.json -f json   # working tree incl. untracked transcripts
```

```text
git: 23 commits scanned … leaks found: 3511
dir: scanned ~138390434 bytes … leaks found: 3511
by rule: 3511 generic-api-key ; by top dir: 3511 transcripts ; outside transcripts/: 0
```

Phân loại (script Python đọc đúng vị trí gitleaks báo, **chỉ in hình dạng giá trị, không in giá trị**):

| Mẫu khớp | Số lượng | Giá trị thực tế | Kết luận |
|---|---|---|---|
| `oauth-2025-04-20","…` trong mảng `betas` | 3,442 | tên beta flag dạng `xxx-YYYY-MM-DD` | false positive |
| `turnAttributionKey":"…` | 63 | UUID | false positive (định danh, không phải credential) |
| `token = …` | 6 | văn xuôi trong transcript ("OIDC org token = …/…/…") | false positive |

Kiểm thêm cho Rule 2 (gitleaks không bắt các loại này): grep số 12 chữ số và email trong các file
đã commit ngoài `transcripts/`. Không có account ID thật. Các số 12 chữ số còn lại là toạ độ SVG,
một phần URL trong `09-fix-research.md:214`, và dữ liệu test tổng hợp. Email duy nhất là
`test@example.invalid`.

Phần grep trên **bỏ qua `transcripts/`**, mà đó lại là chỗ có rủi ro. Reviewer (§9 R6) kiểm
`transcripts/` và chỉ in hình dạng và số lượng, không in giá trị:

- **ARN có 12 chữ số:** 6 ID khác nhau. 5 ID là ID mẫu trong docs AWS. ID còn lại nằm trong một ví
  dụ CloudTrail lấy từ docs AWS. Không có ID thật.
- **Email:** 22 địa chỉ khác nhau. 6 thuộc domain example/noreply/anthropic. 1 trùng git author.
  5 địa chỉ thuộc 4 domain công khai (github.com, google.com, amazon.com, domain.com). Còn lại
  1 "gmail không phải git author" và 9 địa chỉ trên 6 domain lạ. Muốn phân loại thì phải xem giá trị,
  nên owner tự xem (V13).
- **Kết quả owner xem (2026-11-09):** "gmail khác git author", `nhung.do@…` và `tgit@github.com` là
  **lỗi do grep**. Transcript lưu xuống dòng/tab thành `\n`/`\t`, grep bỏ dấu `\` nên dính chữ `n`/`t`
  vào đầu địa chỉ. Đếm lại: 4/6, 2/4, 4/6 lần có `\` đứng ngay trước. Cả lượt đếm của reviewer (N1)
  lẫn của tác giả đều tính nhầm cái đầu là một địa chỉ riêng. Địa chỉ thật chỉ có 2 địa chỉ công
  việc của tác giả. Các địa chỉ còn lại là địa chỉ công khai lấy từ docs/vendor, và
  `cc-plugin-sec-default@builtin.options.allow` là key cấu hình. Owner quyết định thay 2 địa chỉ
  công việc trong mọi transcript và trong toàn bộ lịch sử git (`work/redact-emails.py`), chỉ giữ
  địa chỉ cá nhân.

**Cần sửa (V10, LOW):** không có secret thật. Repo chưa có `.gitleaks.toml`, nên ai chạy
gitleaks (kể cả grader) cũng sẽ thấy 3,511 hit. Nên thêm allowlist cho hai field `betas` và
`turnAttributionKey` trong phạm vi `transcripts/`, hoặc thêm một dòng giải thích trong `README.md`.
Transcript của session này chưa có trong `transcripts/`, nên phải quét lại sau khi copy vào.

---

## 6. Đối chiếu chéo: tên tính năng, setting, flag ↔ `work/02-research.md`

### 6.1 Cách làm

Script `xref.py` (scratchpad) trích:

- trong mọi `.md` của `docs/`, `examples/` và `README.md`: các identifier trong backtick, gồm CLI
  flag, camelCase key, dotted key, biến môi trường, IAM key, snake_case keyword và permission rule;
- flag trong `run:` của workflow;
- mọi key của `examples/claude/*.json`, `examples/k0s/*.yaml`, `PulumiPolicy.yaml` và các body
  AWS không phải policy;
- condition key và operator của `examples/aws/*.json`.

Với mỗi term, script tìm (khớp chuỗi, phân biệt hoa/thường) lần lượt ở:

1. `02-research.md`;
2. các work note khác;
3. schema/catalogue đã tải (`examples/schemas/`) và bảng nguồn trong `test_claude_settings.py`;
4. link 📖 trên cùng dòng trong docs.

Sau đó triage bằng tay và kiểm bằng máy những gì kiểm được.

Lượt bổ sung cho tên tính năng viết bằng văn xuôi: 44 tên lấy từ docs (auto mode, sandbox,
server-managed settings, merge queue, Object Lock, Access Analyzer, CrossGuard, Workload Identity
Federation…), tìm không phân biệt hoa/thường trong 02 và 09.

### 6.2 Kết quả tổng

| Nhóm | Số term |
|---|---|
| Có trong `02-research.md` | 181 |
| Không có trong 02, có trong work note khác (chủ yếu R9.x của `09-fix-research.md`) | 34 |
| Có trong schema đã tải (GitHub REST, schemastore, catalogue AWS) hoặc bảng nguồn của test | 42 |
| Có link 📖 trên cùng dòng | 8 |
| **Không thấy nguồn ở đâu** | **84** |
| Tổng | 349 |

Tên tính năng văn xuôi: không cái nào thiếu nguồn hoàn toàn. Những tên không có trong 02 (push
protection, secret scanning, CodeQL, artifact attestation, EAS Update, CloudWatch Logs data
protection) đều có trong `09-fix-research.md` (R9.5.x, R9.8.x, R9.2.7–R9.2.9). Riêng
`claude plugin validate` chỉ có trong 07-review, nhưng đã chạy thật ở check 1 (✅).

### 6.3 Triage 84 term không thấy nguồn

**(a) Tên do bài nộp tự đặt [design], không cần nguồn (≈ 30):**

- tên secret/biến môi trường của environment: `K0S_DEPLOY_TOKEN`, `EXPO_ROBOT_TOKEN`,
  `EAS_UPDATE_SIGNING_KEY`, `FIREBASE_SERVICE_ACCOUNT_KEY`, `PROD_*_ROLE_ARN`, `NODE_VERSION`,
  `PULUMI_CLI_VERSION`
- `example-org-plugins`, `devsecops-guardrails@example-org-plugins`
- `expected_rows`, `stopped_commit`, `tenant_id`, tên test
- `--approvals`/`--summary`/`--workdir`: flag riêng của `classify.py` (✅ có trong `add_argument` của
  file đó)
- `require_last_pusher_approval`: `examples/README.md:105` dùng làm ví dụ lỗi gõ mà key check bắt
  được; key đúng `require_last_push_approval` có trong schema GitHub

**(b) Script đánh trượt vì tiền tố hoặc dạng viết; thực ra đã có nguồn:**

- `token.actions.githubusercontent.com:aud` (R3.4.1, 02:722)
- `autoMode.classifyAllShell`, `denyWrite`, `credentials` (có trong schemastore)
- `Edit(…)`, `auto-mode-setup` (từ template `settings-hipaa.json` ✅, lấy ở commit 9196319)
- `assertion.sub`, `google.subject` (📖 trang GCP ngay dòng trước, `07-framework-appendix.md:139`)
- `eventTime` (📖 R2.5.3 trên cùng dòng)
- `GITHUB_SHA` (📖 trên cùng dòng)
- `runner.temp` (✅ actionlint)
- `ec2:Describe*`, `iam:Pass*`, `s3:Get*` (wildcard, test mở rộng bằng catalogue: 194 action `ec2:Describe*`)

**(c) Kiểm bằng máy trong session này, nay là ✅/📖 (nên bổ sung vào research):**

| Term | Bằng chứng |
|---|---|
| `lambda:CreateFunction`, `lambda:ListFunctions`, `logs:DescribeQueries`, `iam:UpdateAssumeRolePolicy`, `sts:TagSession` | ✅ có trong `examples/schemas/aws-actions.json` (AWS service reference, 2026-11-09) |
| `ecs:cluster` (condition key của `ecs:RunTask`), `iam:PassedToService` (của `iam:PassRole`) | 📖 [AWS service reference `ecs.json`, `iam.json`](https://servicereference.us-east-1.amazonaws.com/), đọc 2026-11-09 |
| ARN format của `sso:CreateAccountAssignment`: Account, Instance, PermissionSet | 📖 service reference `sso.json` |
| `gh api --jq`, `--paginate`; `gh run download --dir`, `-R/--repo`; `gh pr create --body-file` | ✅ `--help` của gh 2.103.3 |
| `aws ecs update-service --cluster --service --force-new-deployment`; `aws s3 cp --recursive` | ✅ `help` của aws-cli 2.17.8 (cục bộ, không gọi AWS) |
| `docker run --rm` | ✅ docker 29.2.1 `--help` |
| `git log --output=<file>` (cơ sở cho câu "`Bash(git log *)` can write files", `docs/01-framework.md:291`) | ✅ `git log --help`, git 2.34.1 |
| `claude --restricted`, `--strict-mcp-config`, `--tools` | ✅ `claude --help` 2.1.319 |
| `ArnEquals`, `ArnLike`, `ArnNotLike` | ✅ parliament parse được, không cảnh báo về operator (có báo kiểu `StringEquals` ở chỗ khác, tức là có kiểm operator) |
| `zizmor --persona` | ✅ đã chạy ở check 1 |
| `securityGroup`, `vpcConfig`: tên property thật của provider mà regex của risk stop khớp (§9 R4 chuyển từ nhóm (a) sang đây) | ✅ `vpcConfig` có trong `@pulumi/aws` 7.51.1 `lambda/function.d.ts` |
| 51 tiền tố type Pulumi (`"aws:…/…"`) trong `risk-stop/classify.py` và `pulumi-policy/policies.ts` | ✅ cả 51 khớp với 2,467 type token có trong `@pulumi/aws` 7.51.1 (`node_modules`), `missing=0` |

**(d) Đã đánh dấu ⚠️ trong docs, trung thực nhưng vẫn mở** (cập nhật §10: `FIREBASE_TOKEN`,
`PULUMI_CONFIG_PASSPHRASE`, `NPM_CONFIG_USERCONFIG` nay là 📖 R9.9.6/R9.9.9/R9.9.10):

- body `PutObjectLockConfiguration`: `ObjectLockEnabled`, `Rule.DefaultRetention.Mode/Years` (E13)
- field `PermissionSet` (`Description`, `SessionDuration`…) (E6)
- tên `FIREBASE_TOKEN`, `PULUMI_CONFIG_PASSPHRASE`, `SERVERLESS_ACCESS_KEY` (`examples/README.md:130`)
- `NPM_CONFIG_USERCONFIG` (`docs/01-framework.md:322`)
- SSM `aws:approve` (gap G6, tự ghi "not in 02-research")

### 6.4 Không có nguồn và không có marker: báo owner

Các nguồn 📖 đề xuất bên dưới đều đã được tải lại ngày 2026-11-09 (HTTP 200), và term có mặt trên
trang (đếm bằng `grep -oF`). Cập nhật §10: dòng 1–6 và 8 nay ghi thành R9.9.1–R9.9.8 và R9.9.2 trong
`work/09-fix-research.md`, và docs/examples đã có marker; dòng 7 giữ nguyên ([design]); dòng 9 đã kiểm.

| # | Term | Dùng ở | Đề xuất |
|---|---|---|---|
| 1 | `GITHUB_ENV`, `GITHUB_PATH`, `RUNNER_TEMP` | `examples/README.md:213, 270`; workflows | 📖 đề xuất: [GitHub variables reference](https://docs.github.com/en/actions/reference/workflows-and-actions/variables) (mỗi term xuất hiện 3 lần) |
| 2 | `apiVersion: apiserver.config.k8s.io/v1`, `jwt[].issuer.audiences`, `…expression` | `examples/k0s/authentication-config.target.yaml:7-18` | R9.3.4 (`09-fix-research.md:106`) **có** trích `claimValidationRules` và `claimMappings.username`. Thứ thiếu là apiVersion `v1`, `audiences`, `expression`. 📖 đề xuất: [Kubernetes authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/) (`apiserver.config.k8s.io/v1` ×6, `audiences` ×24, `expression` có mặt) |
| 3 | `omitStages` (audit `Policy`), `audit-log-maxage` (kube-apiserver flag) | `examples/k0s/audit-policy.yaml`, `k0s-apiserver-audit.yaml:12` | 📖 đề xuất: [Kubernetes auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/) (`omitStages` ×2, `audit-log-maxage` ×1) |
| 4 | Field RBAC lõi (`roleRef`, `apiGroups`, `automountServiceAccountToken`) | `examples/k0s/deploy-rbac.yaml` | Rủi ro thấp: checkov parse file là Kubernetes, 13 check pass. Nhưng đó không phải nguồn tài liệu |
| 5 | `pulumi … --stack`, `serverless … --stage`, `PULUMI_BACKEND_URL` | `examples/claude/repo-templates/CLAUDE.md:16-17`, `deploy-prod.yml`, `pr-preview-nonprod.yml`, `environment-production/secrets.md:33` | Máy này không có pulumi và serverless. Thêm 📖 docs CLI của Pulumi và Serverless, hoặc ⚠️ |
| 6 | GCP permission `storage.objects.get` | `docs/07-framework-appendix.md:148` | 📖 đề xuất: [Cloud Storage IAM permissions](https://cloud.google.com/storage/docs/access-control/iam-permissions) (×3) |
| 7 | Permission rule `Read(~/.kube/**)`, `Bash(git diff *)`, `Bash(git show *)` | `examples/README.md:120, 342-343` | Cú pháp rule đã có nguồn qua template (`Read(~/.aws/**)`); đây là ví dụ [design]. Có thể bỏ qua |
| 8 | Cú pháp `$/` của reusable workflow | `examples/github/workflows/deploy-on-main.yml`, `validate.sh` | 📖 chỉ có trong `07-review.md`; nên chép vào research (V2) |
| 9 | 7 action pin bằng SHA kèm comment version (vd. `actions/checkout@3d3c… # v7.0.1`) | `examples/github/workflows/*.yml` | Đã kiểm (§10): 7/7 SHA khớp commit của tag |

Giới hạn của check 6:

- **181 và 42 chỉ là cận trên.** Khớp chuỗi con làm 22 term trong 181 được tính "có trong 02" dù
  thật ra không phải (đối chiếu bằng word boundary), ví dụ `--tool`←`--tools`,
  `--preview`←`--preview-only`, `--output`←`--output-format`. Khớp schema theo phần cuối của key
  cũng khớp nhầm sang công cụ khác: `verbs` (k8s) khớp với schemastore của Claude, `repository_id`
  (claim OIDC) khớp với schema ruleset GitHub.
- **Loại file không được trích identifier:**
  - `.py`, `.ts`: type token đã được kiểm riêng ở (c);
  - `uses:` và input của action;
  - key của `examples/github/*.json`: đã có test JSON Schema GitHub che (`test_github_settings.py`).
- Tên tính năng văn xuôi chỉ được kiểm qua danh sách 44 tên tự chọn, không trích tự động.
- Script không kiểm *nội dung* của nguồn có đúng với điều docs nói hay không.

---

## 7. Tổng hợp việc cần sửa (chưa sửa; chỉ báo)

| ID | Mức | File | Vấn đề | Đề xuất |
|---|---|---|---|---|
| V1 | MEDIUM | `diagrams/03-incident-lane.svg` | SVG cũ hơn `.mmd:33`; người đọc guide thấy chữ cũ "accepted by the owner, Options §9" | `mmdc -i 03-incident-lane.mmd -o 03-incident-lane.svg -b white` |
| V7 | MEDIUM → đóng (§10) | `examples/aws/jit-receiver-role-policy.json` (E16) | (Kết luận ban đầu, nay đã sai: nguồn đầy đủ là trang HTML, và simulator đã bị bỏ; xem §10.) Service reference `sso.json` liệt kê `aws:ResourceTag/${TagKey}` cho resource type `PermissionSet`, nhưng mục resource `PermissionSet` của action `CreateAccountAssignment` chỉ ghi `sso:PrimaryRegion`. Nếu điều kiện tag không được đánh giá như mong đợi thì nó fail-closed: JIT sẽ **không cấp được quyền** khi có sự cố (không cấp thừa). Đây là đường break-glass | Đánh dấu ⚠️ trong E16 và layer 7; thêm một bước rollout: thử bằng IAM policy simulator hoặc trong sandbox account trước khi dựa vào nó. Phương án dự phòng: liệt kê ARN permission set cụ thể thay cho điều kiện tag |
| V4 | LOW | `docs/07-framework-appendix.md:454`, E13 | Evidence bucket chỉ mô tả Object Lock; không nói tới Block Public Access, access logging hoặc CloudTrail data events, bucket policy | Thêm một dòng [design] cho các thiết lập này |
| V10 | LOW | repo root | gitleaks: 3,511 false positive trong `transcripts/`, chưa có allowlist | `.gitleaks.toml` (allowlist `betas`, `turnAttributionKey` trong `transcripts/`) hoặc giải thích trong `README.md` |
| V2 | LOW | `work/02-research.md` | Nguồn `$/` chỉ ở `07-review.md` | Chép dòng 📖 vào research |
| V3 | LOW | `examples/validate.sh` | checkov không nằm trong validate.sh; nếu thêm vào thì workflow phải được copy dưới `.github/workflows/`, và IAM JSON cần lớp bọc CloudFormation | Tùy chọn |
| V11 | MEDIUM (nâng sau review: Rule 1 bắt buộc có marker, và grader chấm điều này) | xem §6.4 | Khoảng 15 tên tính năng của công cụ không có marker trong bài nộp; đa số đã có 📖 đề xuất kèm link | Gắn các link 📖 ở §6.4 vào docs/research; mục nào còn lại thì đánh dấu ⚠️ |
| V13 | Đã đóng (2026-11-09) | `transcripts/` | Owner đã xem: không có địa chỉ của người khác; "gmail khác git author" là lỗi do escape `\n` (§5) | Theo quyết định của owner, 2 địa chỉ công việc được thay bằng `<redacted-work-email>` trong working tree và trong mọi commit (`work/redact-emails.py`, `git filter-branch`) |
| V12 | INFO | §2.4 | checkov CKV_AWS_393 fail cả 5 trust policy vì không hiểu dạng `sub` immutable | Nếu đưa checkov vào CI: skip CKV_AWS_393 kèm lý do; có thể ghi một dòng ở E4 |
| — | INFO | 2.2, 2.3 | Boundary `Allow *`, `Resource *` của ProdReadMetadata, trust policy không có `Resource`, `StringEquals` cho `iam:PermissionsBoundary` | Không sửa; có thể ghi trong E4b/E6 rằng scanner sẽ báo những chỗ này |

## 8. Giới hạn của lần verify này

- Không chạy gì vào AWS, GitHub settings hay k0s (Rule 4). Các check ở đây chỉ chứng minh file
  đúng cú pháp và nhất quán với nguồn; không chứng minh nền tảng thực thi đúng như vậy.
- Không có `pulumi`, `serverless`, `kubeconform`, nên chưa kiểm schema của manifest k8s ngoài
  phần checkov parse.
- Các URL trong `work/` và mã nguồn `R…` không được kiểm link.
- Transcript của session này chưa nằm trong `transcripts/` nên chưa được gitleaks quét.
- Identity Center có thật sự áp dụng `aws:ResourceTag` của permission set khi gọi
  `CreateAccountAssignment` hay không (V7): trang HTML của Service Authorization Reference có liệt kê
  (R9.9.11, §10); hành vi thật chỉ kiểm được bằng drill grant trong sandbox account (rollout 1.13).

## 9. Review độc lập

Một subagent mới được giao file này, yêu cầu gốc và bộ tiêu chí (độ chính xác, độ đầy đủ, mức
severity, marker, Rule 2/3); nó không nhận kết luận nào của tác giả ngoài nội dung file. Kết quả: tất cả
số liệu chính chạy lại đều khớp; V1 và V7 được xác nhận; phát hiện 1 MEDIUM và 8 LOW. Tác giả tự chạy
lại R1 (checkov 0/5 cùng regex), R3 (4 URL trả 200, term có mặt), R4 (51/51 type Pulumi), R7
(actionlint `exit=0`) trước khi đưa vào.

| ID | Mức | Nội dung | Đã xử lý |
|---|---|---|---|
| R1 | MEDIUM | Thiếu check OIDC của checkov (chỉ có cho Terraform) | §2.4, V12 |
| R2 | LOW | Chưa nói con số 68/13 phủ những resource nào | §2.2 |
| R3 | LOW | Các mục §6.4 kiểm được bằng docs công khai; câu nói về R9.3.4 sai | §6.4 #1–3, #6 |
| R4 | LOW | 181/42 bị thổi lên; một số loại file không được quét; `securityGroup`/`vpcConfig` bị xếp nhầm nhóm | §6.3(c), giới hạn ở §6.4 |
| R5 | LOW | SHA pin của action chưa được kiểm | §6.4 #9, §8 |
| R6 | LOW | Grep account ID và email bỏ qua `transcripts/` | §5, V13 |
| R7 | LOW | `-ignore` có thể che lỗi `with:`/`secrets:` | §1.2: đã kiểm, không che lỗi nào |
| R8 | LOW | V11 nên là MEDIUM | §7 |
| R9 | LOW | Kiểu ARN của `iam:PermissionsBoundary` có thể ghi 📖 | §2.3 |

Re-review (vòng 2, cùng reviewer, đọc lại file từ đầu): R1–R9 đã được xử lý; **không còn HIGH/MEDIUM**.
Còn 3 LOW, đã sửa:

- N1: bullet email ở §5 bỏ sót 1 địa chỉ gmail không phải git author. Sau đó owner xem và thấy
  đây là lỗi do escape `\n`, không phải một địa chỉ khác (§5);
- N2: mức của V13 là "?", nay là MEDIUM tạm thời;
- N3: sai tên resource ở §2.2.

## 10. Sau verify: các việc đã sửa (2026-11-09, owner yêu cầu)

File này được đổi tên từ `08-verify.md` thành `10-verify.md`, để không trùng tiền tố với
`08-fix-proposals.md`.

| Mục | Đã làm | Kiểm |
|---|---|---|
| V1 | `mmdc -i 03-incident-lane.mmd -o 03-incident-lane.svg -b white` (trong `diagrams/`) | exit 0; SVG có chữ mới, không còn chữ cũ, không có "Syntax error" |
| V11 | Nguồn ghi thành R9.9.1–R9.9.12 trong `work/09-fix-research.md`. Marker gắn ở `examples/README.md` (E3, bảng E8 deviations, finding 9, mục npm), `docs/01-framework.md` (`NPM_CONFIG_USERCONFIG`), `docs/07-framework-appendix.md` (`storage.objects.get`), `examples/github/environment-production/secrets.md` (`PULUMI_BACKEND_URL`), comment trong 4 file `examples/k0s/*.yaml`. Câu ⚠️ về thứ tự rule audit nay là 📖 (R9.9.4). `SERVERLESS_ACCESS_KEY` giữ ⚠️ (R9.9.7: không thấy trong docs) | Mỗi trang tải về, HTTP 200, đếm term (§6.4 và R9.9) |
| V7 | Lần đầu ghi ⚠️ vì chỉ đọc `sso.json`. Review vòng 3 (bên dưới) chỉ ra trang HTML của Service Authorization Reference có liệt kê `aws:ResourceTag/${TagKey}` cho `PermissionSet*` trong `CreateAccountAssignment`/`DeleteAccountAssignment`; tác giả đã đọc lại bảng actions trên trang và xác nhận. E16, layer 7 và rollout 1.13 nay cite 📖 R9.9.11. Drill grant trong sandbox account là bước nghiệm thu (một permission set có tag thì grant được, một không có tag thì bị từ chối); IAM policy simulator bị bỏ, vì nó không trả lời được câu hỏi này | `curl` trang `list_iam-identity-center.html` (200), đọc dòng của action; `sso.json` có 0 mục action-resource chứa `aws:ResourceTag`, trong khi `ecs.json` có 59 mục, nên JSON không phải nguồn đầy đủ |
| Action SHA | `git ls-remote --tags https://github.com/<repo>.git refs/tags/<tag> refs/tags/<tag>^{}`, lấy commit của tag | 7/7 MATCH: `actions/checkout` v7.0.1, `actions/create-github-app-token` v3.3.0, `actions/setup-node` v7.1.0, `actions/upload-artifact` v7.0.2, `anthropics/claude-code-action` v1.0.269, `aws-actions/configure-aws-credentials` v6.3.0, `pulumi/actions` v7.0.0. Lệnh `uses:` không pin duy nhất là lời gọi `$/` tới reusable workflow nội bộ |
| V2 | `$/` nay có nguồn R9.9.2 (trang workflow-syntax), được trích ở examples finding 8 | — |
| V4, V12 | Chưa sửa (LOW/INFO), vẫn mở | — |
| Backup | Owner yêu cầu bỏ các backup của lần rewrite email. Đã xoá branch `backup/pre-redact-2026-11-09`, `refs/original/refs/heads/master`, tag `backup/pre-email-rewrite`, file bundle; `git reflog expire --expire=now --all`; `git gc --prune=now` | Chỉ còn `master` = `origin/master`; 0 object trong `.git` (kể cả unreachable) chứa địa chỉ công việc; `git fsck --unreachable` = 0 |
| Link | Lượt chạy lại `linkcheck.py` trên README, docs, `examples/README.md`, `diagrams/README.md`, 2 work note: 221 link nội bộ, 0 lỗi; 141 URL ngoài, 3 URL `legco.gov.hk` (R9.7) trả `000` từ máy này: chưa kiểm được, không có nghĩa là link hỏng | — |

Review độc lập vòng 3 (agent mới, cho phần sửa ở trên): 1 HIGH, 2 MEDIUM, 5 LOW. Tất cả đã xử lý:

- **F1 (HIGH):** V7 sai nguồn. Đã sửa như dòng V7 ở trên.
- **F2 (MEDIUM):** bỏ IAM policy simulator.
- **F3 (MEDIUM):** `SERVERLESS_LICENSE_KEY` ghi vào R9.9.7 và README; owner quyết định thêm vào env denylist
  của phase 2 (`managed-settings.phase2.json`, test), giữ cả `SERVERLESS_ACCESS_KEY`.
- **F4:** `ecs:cluster` ở E15 nay là 📖 R9.9.12.
- **F5:** finding 8 nay cite R9.9.2.
- **F6:** không cần sửa nữa sau F1.
- **F7:** note này đã cập nhật.
- **F8:** đã thêm link tagging guide vào R9.9.11.
