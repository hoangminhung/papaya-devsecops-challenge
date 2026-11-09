# 01 — Đóng khung bài toán (problem framing)

## English summary

- **Main problems:** engineers run Claude Code on laptops with SSO profiles that reach production, some with permission
  prompts off; MCP servers/plugins are installed without review; CI uses long-lived GitHub tokens and AWS keys; on-call
  and monitoring are fragmented. Grouped into 7 areas: identity & access, production change paths, agent behaviour,
  tooling supply chain, sensitive/tenant data, detection & evidence, security of agent-written code (§1).
- **Central conflict:** Engineering and Compliance only truly conflict on *writes to production*; reading real data
  (medical, national ID, bank) is a grey zone (§3). Security of Papaya's production AI agents is out of scope (§1.4).
- **Key assumptions (owner-confirmed, §4):** separate prod/non-prod AWS accounts with IAM Identity Center; GitHub Team
  plan (no environment reviewers on private repos, no merge queue); laptops are untrusted; every prod change is approved
  before apply, incidents included; agents read metadata only, real data by approved exception; the approver is never the
  author or the authoring agent; non-prod holds synthetic data only.
- **Success criteria (§5):** zero long-lived prod-write credentials on laptops or in GitHub secrets; zero unapproved or
  after-the-fact prod changes; no loss of engineer speed (approval wait ≤ 1 h in working hours, free non-prod loop);
  incident approval wait ≤ 15 min, 24/7; audit evidence for any prod change within 30 min; plus managed agent config,
  a reviewed plugin catalogue, approved-only access to real data, CI security checks on agent code, no real data in non-prod.

> Working note (Vietnamese). Mục đích: hiểu đúng bài toán **trước** khi nghĩ giải pháp.
> File này cố ý **không đề xuất giải pháp**. Mọi dữ kiện về Papaya lấy từ `work/00-challenge.md`;
> những gì đề không nói được tách riêng ở mục 4 và đánh dấu **[GĐ]** (giả định).
>
> Updated: 2026-11-08 · Status: giả định và phạm vi đã được người dùng xác nhận qua 2 vòng hỏi (mục 6)

Ký hiệu nguồn (theo Rule 1 trong `CLAUDE.md`):
- **[Đề]** dữ kiện có trong đề bài (`work/00-challenge.md`), đã đọc trong phiên này ✅.
- **[GĐ-n]** giả định, xem mục 4.
- ⚠️ nhận định về khả năng của công cụ chưa kiểm chứng; sẽ kiểm ở bước thiết kế.

Ký hiệu loại dữ liệu bị ảnh hưởng: **MED** hồ sơ y tế / chẩn đoán / lịch sử claim · **NID** CCCD / national ID ·
**BANK** tài khoản ngân hàng · **TEN** cách ly giữa các tenant (insurer partner, nhiều quốc gia).

---

## 1. Danh sách vấn đề

Mỗi câu trong đề được tách thành một hoặc nhiều vấn đề cụ thể. Cột "Rủi ro" mô tả điều có thể xảy ra
với Papaya, không phải cách khắc phục.

### 1.1 Từ "This is where we are today"

| ID | Câu gốc trong đề | Vấn đề cụ thể | Rủi ro cho Papaya | Dữ liệu |
|---|---|---|---|---|
| P1 | "Engineers run Claude Code on their laptops, signed in to AWS through their SSO profiles." | **P1a.** Agent chạy bằng đúng identity của người. Trong log AWS không phân biệt được hành động do người gõ hay do agent tự quyết. | Khi có sự cố, không trả lời được "ai/cái gì đã làm việc này", và cũng không chứng minh được điều đó với auditor. Trách nhiệm giải trình (named person) bị mờ. | MED, NID, BANK |
| | | **P1b.** Laptop là môi trường thực thi có quyền cloud. Laptop bị mất, bị malware, hoặc session SSO bị đánh cắp thì kẻ tấn công kế thừa quyền đó. | Một endpoint bị chiếm dẫn tới truy cập cloud. Phạm vi thiệt hại phụ thuộc vào quyền của profile (xem P2). | MED, NID, BANK |
| | | **P1c.** Agent đọc nội dung không tin cậy (log, ticket, tài liệu, output tool, trang web) trong khi đang cầm credential cloud. | Prompt injection gián tiếp: nội dung bị cài cắm có thể khiến agent chạy lệnh đọc/ghi/xoá bằng quyền của engineer. | MED, NID, BANK, TEN |
| P2 | "Most engineers' profiles can reach production." | **P2a.** Quyền truy cập prod là thường trực (standing) và rộng, không gắn với một nhiệm vụ hay khoảng thời gian. | Vi phạm least privilege, đây là kiểm soát cốt lõi của ISO 27001 (access control) và HIPAA (minimum necessary). Mọi rủi ro ở P1 nhân lên theo số người có quyền. | MED, NID, BANK, TEN |
| | | **P2b.** "Reach" không phân biệt đọc với ghi, cũng không phân biệt metadata (config, metrics) với dữ liệu (bản ghi DB, file trong S3). | Một phiên debug đơn giản có thể kéo dữ liệu bệnh nhân hoặc CCCD vào context của agent, tức là ra khỏi ranh giới hệ thống của Papaya (xem P12). | MED, NID, BANK |
| | | **P2c.** Không rõ quyền prod có trải trên tất cả tenant/quốc gia cùng lúc hay không. | Một lỗi hoặc một lệnh sai ảnh hưởng nhiều insurer cùng lúc. Có thể vi phạm điều khoản hợp đồng hoặc quy định lưu trữ dữ liệu theo quốc gia. | TEN |
| P3 | "Some engineers run Claude Code with permission prompts turned off because 'it is faster'." | **P3a.** Điểm dừng duy nhất giữa ý định của agent và hành động thật bị tắt. | Lệnh phá huỷ hoặc lệnh do prompt injection gây ra chạy ngay, không ai thấy trước. | MED, NID, BANK, TEN |
| | | **P3b.** Lý do "nhanh hơn" cho thấy chi phí của kiểm soát hiện tại (prompt fatigue) cao hơn giá trị engineer cảm nhận. | Bất kỳ kiểm soát mới nào gây chậm tương tự sẽ bị né theo cùng cách. Đây là rủi ro của **chính framework**, không chỉ của hiện trạng. | — |
| | | **P3c.** Việc tắt prompt là lựa chọn cá nhân, không có chính sách tổ chức và không ai biết ai đang tắt. | Không đo được mức độ tuân thủ, không có evidence cho audit. | — |
| P4 | "Engineers install MCP servers and plugins they find useful; there is no review process." | **P4a.** Rủi ro chuỗi cung ứng: MCP server/plugin là code bên thứ ba chạy trên laptop có credential cloud. | Code độc hoặc bị chiếm quyền có thể đọc credential, thực thi lệnh, gửi dữ liệu ra ngoài. | MED, NID, BANK |
| | | **P4b.** MCP server có thể gửi dữ liệu mà agent đọc được tới dịch vụ bên ngoài. | Dữ liệu nhạy cảm đi tới bên xử lý không có hợp đồng (BAA/DPA). Có thể là vi phạm HIPAA hoặc luật dữ liệu khu vực. | MED, NID, BANK, TEN |
| | | **P4c.** Không có danh mục (inventory) MCP/plugin nào đang được dùng ở đâu. | Không thể đánh giá phạm vi khi một plugin bị phát hiện có lỗ hổng. Không có asset inventory cho ISO 27001. | — |
| P5 | "Some workflows use a long-lived GitHub token and AWS access keys stored as repository secrets." | **P5a.** AWS access key dài hạn: không tự hết hạn, khó biết ai đang dùng, dễ lộ qua log hoặc fork. | Key bị lộ cho kẻ tấn công quyền deploy hoặc truy cập dữ liệu cho tới khi bị phát hiện và thu hồi thủ công. | MED, NID, BANK |
| | | **P5b.** GitHub token dài hạn, có thể là của một cá nhân (PAT). | Token sống lâu hơn vai trò của chủ nhân. Hành động trong CI được gán cho một người cụ thể dù không phải người đó làm. | — |
| | | **P5c.** Repository secret dùng chung cho cả monorepo: workflow nào, branch nào cũng có thể chạm tới (xem A6). | Ai sửa được workflow là có thể dùng secret prod, kể cả qua PR chưa được review. Điều này phá vỡ nguyên tắc "named reviewer" của Compliance ngay ở tầng CI. | MED, NID, BANK, TEN |
| | | **P5d.** Chữ "some workflows" nghĩa là hiện trạng không đồng nhất, và chưa có danh sách workflow nào dùng gì. | Không biết hết phạm vi; việc khắc phục có thể bỏ sót. | — |
| P6 | "Monitoring and alerting exist but are fragmented across CloudWatch, GCP, and Slack channels." | **P6a.** Không có một nơi nhìn toàn cảnh. Tín hiệu bất thường (truy cập dữ liệu lạ, hành động agent lạ) dễ bị bỏ sót. | Phát hiện xâm phạm muộn. HIPAA và luật khu vực có thời hạn thông báo vi phạm; phát hiện muộn có thể dẫn tới vi phạm cả thời hạn. | MED, NID, BANK |
| | | **P6b.** Audit trail rải rác ở nhiều nơi. | Không tái dựng được chuỗi sự kiện của một thay đổi (ai đề xuất, ai duyệt, cái gì chạy) khi auditor hoặc partner hỏi. | — |
| P7 | "On-call is informal." | **P7a.** Không có người chịu trách nhiệm rõ ràng khi có sự cố, cũng không có quy trình leo thang. | Sự cố kéo dài. Trong lúc gấp, người ta dùng quyền rộng nhất có trong tay, đúng kiểu hành vi mà Compliance lo. | MED, NID, BANK, TEN |
| | | **P7b.** Không có định nghĩa "khẩn cấp" và không có quy trình xử lý thay đổi trong sự cố. | Nếu việc duyệt trong sự cố chậm hoặc không tìm được người duyệt, kiểm soát "phải có người duyệt" sẽ bị phá ngay trong sự cố đầu tiên. Người dùng đã quyết định không có ngoại lệ "làm trước, duyệt sau" (GĐ-8), nên rủi ro này chỉ còn cách giải quyết bằng tốc độ duyệt. | — |
| P8 | "We are working towards ISO 27001 and must satisfy HIPAA and regional data-protection regulations." | **P8a.** ISO 27001 chưa đạt: kiểm soát và **evidence** đều đang thiếu. | Không đạt chứng nhận hoặc có non-conformity. Partner lớn có thể yêu cầu chứng nhận trước khi ký hợp đồng. | — |
| | | **P8b.** Nhiều khung pháp lý cùng lúc (HIPAA và luật từng quốc gia), mỗi khung yêu cầu khác nhau. | Một kiểm soát chung có thể không đủ cho một quốc gia cụ thể. Framework cần chỗ cho yêu cầu theo tenant/quốc gia. | TEN |
| P9 | "Claude Code (Team Premium) is the primary tool for writing code, running git, opening PRs" | **P9a.** Phần lớn code, kể cả IaC, do agent viết. Agent có thể đưa secret vào code, thêm dependency không tồn tại hoặc độc (package bịa tên), hoặc viết code có lỗ hổng. **P9b.** Agent tự chạy git và mở PR. Nếu branch protection yếu, agent hoặc tác giả có thể đẩy thẳng lên nhánh deploy. **P9c.** PR do agent tạo dễ dài và nhiều, nên reviewer dễ duyệt cho qua. | Đường PR → CI chính là đường thay đổi prod. Một PR lỗi được duyệt hời hợt vẫn có "named reviewer" trên giấy, nhưng kiểm soát không còn ý nghĩa thật. | MED, NID, BANK, TEN |

### 1.2 Từ Appendix A

| ID | Dữ kiện trong đề | Vấn đề cụ thể | Rủi ro cho Papaya | Dữ liệu |
|---|---|---|---|---|
| A1 | AWS: Lambda (Serverless), ECS, EC2, Aurora PostgreSQL, SNS, SQS, Step Functions, S3, CloudWatch | Nhiều loại tài nguyên, và mỗi loại có **nhiều đường thay đổi**: Pulumi, `serverless deploy`, AWS CLI/console, thao tác trực tiếp lên DB. | Một quy tắc "mọi thay đổi phải qua duyệt" chỉ có nghĩa khi bao được **mọi** đường. Bỏ sót một đường là có đường vòng. | MED, NID, BANK |
| A2 | "S3 (claim documents)" | Hồ sơ claim (chứa MED/NID/BANK) nằm ở S3. Quyền S3 rộng trên prod tương đương quyền đọc toàn bộ hồ sơ. | Rò rỉ hàng loạt. Đây là loại dữ liệu đắt nhất khi bị lộ. | MED, NID, BANK, TEN |
| A3 | Aurora PostgreSQL | Debug DB dễ thành chạy SQL trực tiếp, cả đọc lẫn ghi, trên dữ liệu thật. | Thay đổi dữ liệu không qua review; `SELECT` kéo dữ liệu cá nhân vào context agent. | MED, NID, BANK, TEN |
| A4 | GCP: Vertex AI, Gemini | Có một mặt phẳng identity thứ hai (GCP IAM) và tài liệu được gửi sang GCP để xử lý. | Kiểm soát chỉ làm cho AWS sẽ bỏ ngỏ GCP. Cần biết dữ liệu partner nào được phép xử lý ở đâu. | MED, NID, TEN |
| A5 | Kubernetes k0s cho AI agents và internal services | Cluster tự quản: kubeconfig, RBAC, nâng cấp đều do Papaya lo. Cách cấp quyền cluster cho engineer hoặc agent hiện chưa rõ. | Một kubeconfig admin trên laptop có thể thành đường thay đổi prod thứ N, ngoài AWS IAM. | TEN |
| A6 | Firebase Hosting cho frontend | Deploy frontend dùng credential riêng (Firebase/GCP). | Thêm một loại credential CI cần quản lý. Frontend bị sửa có thể dẫn tới đánh cắp dữ liệu người dùng nhập vào. | NID, BANK |
| A7 | AI agents trong prod (claim assessment, document extraction, FWA) "read documents uploaded by partners and members" | **A7a.** Tài liệu do bên ngoài upload là input không tin cậy với agent prod. **A7b.** Khi engineer dùng Claude Code để debug agent prod, coding agent cũng đọc chính những tài liệu đó, trong khi đang cầm quyền cloud. | **A7b là rủi ro đặc thù của Papaya:** một tài liệu claim bị cài cắm có thể thành prompt injection vào coding agent của engineer. Ngoài ra MED/NID trong tài liệu đi thẳng vào context của coding agent. | MED, NID, BANK, TEN |
| A8 | Monorepo duy nhất chứa apps, web, backend, mobile, AI/ML, IaC | Ranh giới giữa "code ứng dụng" và "code hạ tầng prod" chỉ còn là thư mục. Secret, workflow và quyền repo dùng chung. | Một PR ở frontend có thể chạm workflow deploy hạ tầng. Phạm vi thiệt hại của một token repo là toàn hệ thống. | MED, NID, BANK, TEN |
| A9 | IaC: Pulumi và Serverless Framework | Hai công cụ IaC song song, mỗi công cụ có state, secret và cách preview riêng. Thay đổi thủ công ngoài IaC gây drift. | Bản preview của PR không phản ánh thay đổi thật nếu có drift. Reviewer "duyệt" một thứ khác với thứ được apply. | — |
| A10 | Claude Code Team Premium cho mọi engineer; internal plugin marketplace | Đã có kênh phân phối cấu hình/plugin nội bộ, nhưng đang chưa được dùng để kiểm soát (P4). Khả năng ép cấu hình từ phía tổ chức trên gói Team chưa được kiểm chứng ⚠️. | Nếu không ép được cấu hình, mọi chính sách cho agent chỉ là khuyến nghị. | — |
| A11 | Linear, Slack | Phê duyệt và trao đổi hiện có thể nằm rải rác trong chat. | Phê duyệt trong tin nhắn Slack khó dùng làm evidence: khó tìm, có thể bị sửa/xoá, không gắn với thay đổi cụ thể. | — |
| A12 | Nhiều insurer partner ở nhiều nước (VN, TH, HK), "each with their own data and contractual requirements" | **A12a.** Yêu cầu hợp đồng khác nhau theo partner. **A12b.** Quy định lưu trữ/xử lý dữ liệu theo quốc gia. | Một thao tác hợp lệ với tenant này có thể vi phạm hợp đồng tenant khác. Lộ dữ liệu chéo giữa các tenant là sự cố nghiêm trọng về hợp đồng lẫn uy tín. | TEN |
| A13 | Production dùng OpenAI, Vertex AI, Gemini, Claude | Dữ liệu nhạy cảm đã đi qua nhiều nhà cung cấp AI. Coding agent là thêm **một kênh nữa**, khác kênh prod. | Hợp đồng/BAA cho kênh prod chưa chắc phủ việc engineer dùng Claude Code với dữ liệu thật [GĐ-9]. | MED, NID, BANK |

### 1.3 Nhóm vấn đề (để dùng ở bước thiết kế)

Gom lại, các vấn đề rơi vào 7 nhóm:

1. **Identity & quyền:** P1a, P1b, P2a–c, P5a–b, A4, A5, A6. Ai/cái gì có quyền gì, trong bao lâu.
2. **Đường thay đổi prod:** A1, A3, A8, A9, P5c. Có bao nhiêu đường, đường nào có kiểm soát.
3. **Hành vi của agent:** P1c, P3a–c, A7b. Agent được làm gì, đọc gì, ai thấy trước.
4. **Chuỗi cung ứng tooling:** P4a–c, A10.
5. **Dữ liệu nhạy cảm và tenant:** P2b, A2, A7b, A12, A13.
6. **Phát hiện, phản ứng, evidence:** P6, P7, P8, A11.
7. **Chất lượng bảo mật của code do agent viết (mức vừa phải):** P9a–c, A8. Gồm secret scanning, kiểm tra
   dependency, SAST, review PR do agent tạo và branch protection. Mức đi sâu: guardrail ở PR/CI, không đi sâu vào AppSec.

### 1.4 Ngoài phạm vi (ghi chú, không thiết kế)

- **A7a: bảo mật của chính các AI agent đang chạy trên prod** (claim assessment, document extraction, FWA),
  ví dụ prompt injection qua tài liệu partner/member upload. Đề hỏi về coding agent, nên phần này chỉ được nêu
  trong deliverable như một việc tiếp theo. A7b (coding agent đọc chính các tài liệu đó khi debug) **vẫn trong phạm vi**.

---

## 2. Stakeholder

| Bên | Họ muốn gì | Họ sợ gì |
|---|---|---|
| **Engineering** | Tự debug và ship thay đổi hạ tầng, không phải chờ người khác [Đề]. Giữ tốc độ agent-first. Ít prompt, ít ticket, ít context switch. Truy cập được dữ liệu/log thật khi cần debug. | Quy trình duyệt thành nút cổ chai (chờ một người duy nhất, chờ qua ngày). Bị mất quyền đang có mà không có gì thay thế tương đương. Bị coi là "rủi ro" thay vì người được tin tưởng. Bị kẹt khi có sự cố lúc nửa đêm. |
| **Compliance** | Mọi thay đổi prod có một **người có tên** đã review và approve [Đề]. Evidence lấy ra được khi auditor hỏi. Đạt ISO 27001, đáp ứng HIPAA và luật khu vực. | Agent hành động không ai chịu trách nhiệm. Không chứng minh được ai duyệt cái gì. Phát hiện vi phạm muộn hoặc qua partner. Quy tắc trên giấy nhưng thực tế bị né (như P3). |
| **Security / DevSecOps** (vai trò của tôi) | Giảm phạm vi thiệt hại: không credential dài hạn, quyền tối thiểu, nhìn thấy hành động của agent. Kiểm soát được ép bằng kỹ thuật, không dựa vào thiện chí. Bao phủ cả AWS, GCP, k0s, Firebase, CI. | Thiết kế quá nặng nên bị bỏ qua. Trở thành người duyệt duy nhất (bottleneck và single point of failure). Prompt injection qua tài liệu claim (A7b). Plugin/MCP độc. Bị giao trách nhiệm mà không có quyền ép. |
| **Lãnh đạo** | Tốc độ sản phẩm (agent-first là lợi thế cạnh tranh). Đạt chứng nhận để mở rộng partner. Chi phí và nhân sự kiểm soát hợp lý. | Một vụ lộ dữ liệu y tế/CCCD gây mất partner, bị phạt, mất uy tín. Kiểm soát làm chậm đội ngũ. Chi phí công cụ hoặc headcount phát sinh lớn. |
| **Đối tác bảo hiểm** (insurer partners) | Dữ liệu của họ và của người được bảo hiểm được cách ly và bảo vệ. Tuân thủ hợp đồng và luật nước họ. Có evidence khi họ audit nhà cung cấp. | Lộ dữ liệu chéo tenant. Dữ liệu bị xử lý ở nơi/nhà cung cấp không được phép. AI agent (cả prod và coding) "nhìn thấy" dữ liệu của họ mà họ không biết. |

Ghi chú: **người được bảo hiểm** (insured members) không có tiếng nói trực tiếp trong đề, nhưng là chủ thể
dữ liệu thật. Lợi ích của họ đi qua Compliance và partner. Tôi giữ họ trong tầm nhìn khi đánh giá rủi ro dữ liệu.

---

## 3. Mâu thuẫn trung tâm

**Engineering:** "Let Claude Code talk to AWS directly. I want to debug and ship my own infra changes without waiting for someone else."

**Compliance:** "Nothing changes in production — by a human or an agent — without a named person who reviewed and approved it."

### 3.1 Hai câu thực ra đang nói về những thứ khác nhau

Tách từng câu thành các phần:

| | Engineering | Compliance |
|---|---|---|
| Phạm vi môi trường | AWS nói chung (không nói prod hay non-prod) | **Chỉ production** |
| Loại hành động | debug (chủ yếu đọc) **và** ship (ghi) | **thay đổi** (ghi) |
| Chủ thể | Claude Code, nhân danh engineer | "a human or an agent", trung lập về công cụ |
| Điều kiện | "without waiting for someone else" | "named person who reviewed and approved" |

Từ bảng này:
- **Không mâu thuẫn:** debug (đọc) và mọi việc ở non-prod nằm ngoài phạm vi câu của Compliance.
- **Mâu thuẫn thật** nằm ở đúng một ô: **ghi vào production**. Engineering không muốn *chờ*, Compliance muốn *có người duyệt*.
- **Vùng xám:** "debug" trên prod có thể là đọc dữ liệu nhạy cảm (P2b, A7b). Compliance không nói về đọc,
  nhưng HIPAA và luật dữ liệu thì có. Vậy câu "không mâu thuẫn" ở trên chỉ đúng với đọc **metadata**, không đúng với đọc **dữ liệu**.

### 3.2 Những chỗ hai câu chưa định nghĩa (framework phải định nghĩa)

- "Change in production" gồm những gì? Deploy code, đổi config, đổi IAM, chạy migration, sửa một bản ghi DB, restart service, scale?
- "Reviewed" là review cái gì? Diff code, bản preview hạ tầng (plan), hay đoạn chat với agent?
- "Named person" có bắt buộc **khác** người đề xuất không (four-eyes / segregation of duties)? Câu của Compliance không nói.
- "Waiting for someone else" là chờ bao lâu thì chấp nhận được?
- Khi có sự cố và không kịp chờ duyệt thì sao?

### 3.3 Câu hỏi thiết kế

> **Làm thế nào để engineer, làm việc qua Claude Code, có vòng lặp debug-và-ship tự phục vụ và nhanh,
> trong khi mọi thay đổi vào production (kể cả trong sự cố) đều đi qua một con đường duy nhất, ép bằng kỹ thuật,
> gắn với một người có tên đã review đúng thứ sẽ được áp dụng, và để chi phí của con đường đó đủ thấp
> để không ai có lý do đi đường tắt?**

Các vế của câu hỏi và vấn đề tương ứng:
- "tự phục vụ và nhanh": nhu cầu của Engineering; bài học từ P3b.
- "mọi thay đổi … một con đường duy nhất": A1, A8, P5c (đường vòng).
- "ép bằng kỹ thuật": P3c, P4 (đang dựa vào thiện chí).
- "người có tên … review đúng thứ sẽ được áp dụng": Compliance; A9 (drift giữa preview và apply).
- "kể cả trong sự cố": P7b.
- "chi phí đủ thấp": P3b, rủi ro chính của framework.

Câu hỏi phụ đi kèm (về **đọc**, không phải ghi):

> **Agent được nhìn thấy gì trong production, đặc biệt dữ liệu MED/NID/BANK của từng tenant, và ai quyết định điều đó?**

---

## 4. Giả định

Đề không nói những điều dưới đây. Mỗi mục là **[GĐ]**: tôi dùng nó để thiết kế, chưa được xác nhận.
Mục nào "chịu lực" (đổi giả định thì đổi thiết kế) được đánh dấu ★.

| ID | Giả định | Vì sao cần | Nếu sai thì |
|---|---|---|---|
| GĐ-1 ★ ✔ | Đội engineering khoảng 20–60 người. Chưa có đội security riêng; DevSecOps là 1–2 người. Thiết kế không được để một người làm reviewer duy nhất. | Quyết định ai có thể là reviewer và kiểm soát nặng đến đâu thì gánh nổi. | Đội nhỏ hơn: cần cơ chế duyệt không phụ thuộc vào một người. Đội lớn hơn: có thể phân tầng reviewer. |
| GĐ-2 ★ ✔ | AWS có ít nhất một ranh giới account giữa prod và non-prod (AWS Organizations). Đăng nhập qua IAM Identity Center ("SSO profiles" trong đề). | Phân quyền theo môi trường cần ranh giới. | Nếu prod và non-prod chung account: tách account trở thành điều kiện tiên quyết, kéo dài lộ trình. |
| GĐ-3 | Dữ liệu các tenant cách ly logic (schema/bucket/prefix) trong cùng account, không phải account riêng cho từng tenant. | Ảnh hưởng tới khả năng giới hạn quyền theo tenant. | Nếu mỗi tenant một account: phân quyền theo tenant dễ hơn nhiều. |
| GĐ-4 | k0s chạy trên hạ tầng AWS (EC2); engineer truy cập bằng kubeconfig, chưa có SSO cho cluster. | Xác định k0s là đường thay đổi riêng cần kiểm soát. | Nếu đã có OIDC cho cluster: phần k0s nhẹ hơn. |
| GĐ-5 ★ ✔ (đã đổi 2026-11-08) | **Giả định của owner, không phải sự thật về Papaya:** Papaya dùng gói GitHub **Team**, không phải Enterprise. Theo docs (`work/02-research.md` 3.1.2, ✅), trên Team thì required reviewers của environment chỉ có cho repo public. Vì vậy monorepo private **không** có cổng duyệt ở environment. | Xác định chỗ đặt cổng duyệt: merge PR vào `main`, ép bằng rulesets (có trên Team cho repo private; 02-research 3.2.1, 3.6 #1, 3.7 A1). Environment `production` chỉ giới hạn branch = `main`. | Nếu Papaya dùng Enterprise Cloud: thêm required reviewers, prevent self-review và chặn admin bypass cho environment `production`. Chỉ đổi cấu hình, không đổi workflow (suy luận, 02-research 3.7 A1). |
| GĐ-6 ★ ✔ | **Coi laptop là không tin cậy.** Kiểm soát chính đặt ở cloud/CI. Cấu hình Claude Code do tổ chức đẩy xuống (managed settings, plugin marketplace) chỉ là lớp thứ hai. ⚠️ Gói Team Premium hỗ trợ ép cấu hình đến đâu chưa kiểm tra; sẽ kiểm ở bước thiết kế và đánh dấu 📖. | Quyết định chính sách cho agent là "ép" hay chỉ "khuyến nghị". | Nếu ép được tốt: lớp thứ hai mạnh hơn, nhưng thiết kế vẫn không dựa vào nó. |
| GĐ-7 | Laptop được quản lý tập trung (MDM) ở mức tối thiểu. | Một số kiểm soát cấu hình cần kênh đẩy xuống máy. | Không có MDM: càng phải dựa vào GĐ-6 hoặc kiểm soát phía server. |
| GĐ-8 ★ ✔ (đã đổi) | **Mọi thay đổi prod phải được duyệt trước khi áp dụng, kể cả trong sự cố.** Không có ngoại lệ "làm trước, duyệt sau" (break-glass không duyệt). Người dùng đã bác đề xuất ban đầu (cho phép một tập thao tác khẩn cấp, review sau). | Đây là ràng buộc cứng của Compliance. Hệ quả: trong sự cố, việc duyệt phải **nhanh và luôn có người duyệt**, 24/7. | — (đã là quyết định). Hệ quả cần thiết kế: người duyệt trực ngoài giờ, đường duyệt rút gọn cho thao tác khẩn cấp. Xem mâu thuẫn với ưu tiên 30 ngày ở mục 6. |
| GĐ-9 ★ ✔ (đã chỉnh) | **Mặc định agent không đọc dữ liệu thật** (MED/NID/BANK) trên prod, chỉ đọc metadata: config, metrics, log đã che dữ liệu. **Ngoại lệ theo từng trường hợp**, khi có thoả thuận phù hợp (BAA/DPA, hợp đồng với partner) và có người duyệt, vì có lúc debug bắt buộc phải xem dữ liệu thật. | Quyết định agent có được đọc dữ liệu prod hay không. | — (đã là quyết định). Hệ quả cần thiết kế: một đường xin quyền đọc dữ liệu có thời hạn, có phạm vi tenant, có duyệt và có log. |
| GĐ-10 | Pulumi dùng một backend có preview (`pulumi preview`) chạy được trong CI. Serverless deploy hiện chạy cả từ CI lẫn từ laptop. | Reviewer cần thấy trước thay đổi. | Nếu chỉ chạy từ laptop: phải chuyển deploy về CI trước. |
| GĐ-11 ★ ✔ | **Reviewer không phải là người làm.** "Người làm" gồm tác giả của thay đổi và agent đã tạo ra thay đổi (four-eyes). Một agent độc lập (không phải agent tạo thay đổi) **được** làm bước review tự động bổ sung, nhưng **không** được tính là phê duyệt. Phê duyệt chính thức ("named person" của Compliance) luôn là người. | Định nghĩa vai trò reviewer. | — (đã là quyết định). |
| GĐ-12 | Lộ trình triển khai framework khoảng 90 ngày, làm song song với chuẩn bị ISO 27001. Không có ngân sách lớn cho công cụ mới; ưu tiên tính năng sẵn có của stack hiện tại. | Định cỡ đề xuất và thứ tự ưu tiên. | Có ngân sách: có thể thêm công cụ chuyên dụng (vẫn không thay IaC/CI theo đề). |
| GĐ-13 | Yêu cầu theo quốc gia (VN, TH, HK) có thể khác nhau về nơi lưu trữ và xử lý dữ liệu; chưa biết chi tiết. | Framework cần chỗ cho chính sách theo tenant/quốc gia. | Chi tiết pháp lý phải do Compliance/Legal xác nhận; tôi không suy diễn luật cụ thể. |
| GĐ-14 ★ ✔ | **Non-prod (dev/staging) chỉ chứa dữ liệu synthetic hoặc đã che**, không có dữ liệu thật của khách hàng. Framework thêm một yêu cầu: không copy dữ liệu prod xuống non-prod. | Đây là điều kiện để vòng lặp non-prod của agent được tự do, không cần duyệt (S4c). | — (đã là quyết định). Nếu thực tế staging đang có bản copy prod, phải dọn trước. Trong lúc chưa dọn, non-prod theo quy tắc đọc dữ liệu của GĐ-9. |

---

## 5. Tiêu chí thành công

Đo được, có cách đo, có mục tiêu. Các số mục tiêu đã được xác nhận ở mục 6.

| # | Tiêu chí | Cách đo | Mục tiêu |
|---|---|---|---|
| S1 | Không còn credential dài hạn có quyền ghi prod trên laptop. | Số IAM user/access key có quyền ghi vào account prod; số quyền ghi prod gán thường trực cho người. | **0** |
| S2 | Không còn credential cloud dài hạn trong GitHub secrets. | Số AWS access key, GitHub PAT, Firebase/GCP key dài hạn được workflow dùng. | **0** |
| S3 | Mọi thay đổi prod, kể cả trong sự cố, có một người duyệt có tên, khác người làm, **trước** khi áp dụng. | Đối chiếu định kỳ (hằng tháng) các sự kiện ghi trong log cloud của prod với bản ghi phê duyệt. Đếm số thay đổi không khớp, và số thay đổi có thời điểm duyệt sau thời điểm áp dụng. | **0** / **0** |
| S4 | Engineer không mất tốc độ. | (a) Thời gian từ PR được tạo tới khi thay đổi hạ tầng chuẩn lên prod (median). (b) Thời gian chờ duyệt (median). (c) Vòng lặp ở non-prod không có bước duyệt mới. | (a) trong cùng ngày làm việc; (b) ≤ 1 giờ trong giờ làm việc; (c) đúng |
| S5 | Mọi cấu hình agent dùng trên máy engineer là cấu hình được duyệt. | % máy engineer nhận chính sách Claude Code của tổ chức; số engineer có thể tắt toàn bộ permission prompt mà không ai biết. | **100%** / **0** (phụ thuộc GĐ-6) |
| S6 | Mọi MCP server/plugin đang dùng nằm trong danh mục đã duyệt, và việc duyệt không thành nút cổ chai. | Số MCP/plugin đang dùng ngoài danh mục; thời gian xử lý yêu cầu thêm mới. | **0** ngoài danh mục; xử lý ≤ 5 ngày làm việc |
| S7 | Phát hiện và phản ứng có chủ, và sự cố không bị kẹt vì chờ duyệt. | Có lịch on-call có tên, gồm cả người duyệt; mọi alert prod về một kênh định tuyến; thời gian chờ duyệt cho thay đổi trong sự cố (24/7). | Lịch on-call có tên; 100% alert prod qua một kênh; chờ duyệt trong sự cố ≤ 15 phút, 24/7 (cần ít nhất primary + backup trực duyệt) |
| S8 | Evidence cho audit lấy ra nhanh. | Với một thay đổi prod chọn ngẫu nhiên: thời gian để trình ra đủ "ai đề xuất, ai duyệt, đã duyệt cái gì, cái gì được áp dụng, khi nào". | ≤ 30 phút, không cần hỏi người liên quan |
| S9 | Đọc dữ liệu thật trên prod chỉ xảy ra qua ngoại lệ được duyệt. | Số phiên agent/người đọc MED/NID/BANK trên prod không có yêu cầu được duyệt kèm theo; mọi yêu cầu có thời hạn và phạm vi tenant. | **0** phiên không có yêu cầu được duyệt |
| S10 | Code do agent viết đi qua cùng guardrail với code người viết, trước khi tới nhánh deploy. | % PR vào nhánh deploy có secret scan, kiểm tra dependency và SAST chạy và đạt; số lần push thẳng lên nhánh deploy; số secret bị phát hiện **sau** khi merge. | **100%** / **0** / **0** |
| S11 | Non-prod không chứa dữ liệu thật (GĐ-14). | Số lần copy dữ liệu prod xuống non-prod; kết quả quét định kỳ dữ liệu nhạy cảm trên non-prod. | **0** |

S4 ngang hàng với các tiêu chí bảo mật một cách có chủ đích. Nếu S1–S3 đạt nhưng S4 không đạt, P3b
cho thấy engineer sẽ đi đường vòng, và S1–S3 sẽ không giữ được lâu.

---

## 6. Câu hỏi kiểm tra lại (đã trả lời)

### Vòng 1

Người dùng trả lời trong chat, session 2 (2026-11-08).

| # | Câu hỏi | Đề xuất | Quyết định của người dùng |
|---|---|---|---|
| 1 | Quy mô đội (GĐ-1) | 20–60 engineer, DevSecOps 1–2 người, không một reviewer duy nhất | Đồng ý |
| 2 | Reviewer khác tác giả? (GĐ-11) | Có (four-eyes); agent không là reviewer | Đồng ý, reviewer không phải người làm (tác giả hoặc agent tạo thay đổi). Hỏi lại: agent độc lập chỉ là bước review tự động bổ sung; phê duyệt chính thức phải là người |
| 3 | Agent đọc dữ liệu thật? (GĐ-9) | Không, cho tới khi có thoả thuận | Đồng ý mặc định là không; **cho phép theo từng trường hợp** khi có thoả thuận phù hợp, vì có lúc debug cần dữ liệu thật |
| 4 | Thay đổi khẩn cấp chưa duyệt? (GĐ-8) | Có, với 4 điều kiện và review sau | **Không đồng ý.** Mọi thay đổi prod phải được duyệt **trước**, kể cả trong sự cố |
| 5 | Ép cấu hình agent? (GĐ-6) | Laptop không tin cậy; kiểm soát chính ở cloud/CI | Đồng ý |
| 6 | Mục tiêu tốc độ (S4) | Duyệt ≤ 1 giờ trong giờ làm việc; ship trong ngày | Đồng ý |
| 7 | Phạm vi | Nguyên tắc chung cho tất cả; chi tiết cho AWS + GitHub Actions; GCP, k0s, Firebase ở mức áp dụng nguyên tắc | Đồng ý |
| 8 | Ưu tiên 30 ngày | (1) bỏ credential dài hạn trong CI, (2) thu hẹp quyền prod thường trực, (3) danh mục MCP/plugin | Đồng ý; on-call và monitoring ở giai đoạn 2 |

### Hệ quả cần mang sang bước thiết kế

- **Mâu thuẫn giữa câu 4 và câu 8.** Không có break-glass thì sự cố nào cũng cần một người duyệt có mặt ngay, 24/7.
  Nhưng on-call (P7) lại được xếp ở giai đoạn 2. Trong 30 ngày đầu, nếu thu hẹp quyền prod (ưu tiên 2) mà chưa có
  người duyệt trực, sự cố ngoài giờ có thể bị kẹt. Cần chọn một trong hai: (a) đưa "danh sách người duyệt trực"
  (chỉ phần tối thiểu của on-call) lên giai đoạn 1, hoặc (b) chỉ thu hẹp quyền prod sau khi có người duyệt trực.
  **Đã quyết (a):** đưa phần tối thiểu "danh sách người duyệt trực" (có tên, phủ 24/7) lên giai đoạn 1,
  làm trước hoặc cùng lúc với việc thu hẹp quyền prod. Phần còn lại của on-call và monitoring vẫn ở giai đoạn 2.
- **Câu 3** cần một đường xin quyền đọc dữ liệu thật, khác với đường xin thay đổi, và có thêm điều kiện là
  thoả thuận/hợp đồng cho phép. Thêm tiêu chí S9.
- **Câu 4** chuyển rủi ro P7b từ "có người đi đường tắt" thành "sự cố kéo dài vì chờ duyệt". S7 đổi thành đo thời gian chờ duyệt trong sự cố.

### Vòng 2 (grill-me)

Người dùng trả lời trong chat, session 3 (2026-11-08). Mỗi câu hỏi có một đề xuất; người dùng chọn đề xuất ở tất cả các câu.

| # | Câu hỏi | Quyết định của người dùng |
|---|---|---|
| 9 | Non-prod có dữ liệu thật không? | Không, chỉ synthetic/đã che. Thêm yêu cầu không copy dữ liệu prod xuống non-prod (GĐ-14, S11) |
| 10 | Bảo mật code do agent viết có trong phạm vi? | Có, ở mức vừa phải: guardrail PR/CI, không đi sâu vào AppSec (P9, nhóm 7, S10) |
| 11 | Bảo mật của prod AI agents (A7a)? | Ngoài phạm vi, chỉ ghi chú (mục 1.4). A7b vẫn trong phạm vi |
| 12 | Tách AWS account prod/non-prod (GĐ-2)? | Giả định đã tách. Nếu chưa tách, việc tách là điều kiện tiên quyết |
| 13 | Mục tiêu S7 | Chờ duyệt trong sự cố ≤ 15 phút, 24/7 |
| 14 | Hình thức deliverable | Docs markdown kèm `examples/` chạy/validate được (managed settings/hooks, GitHub Actions OIDC + environment, IAM sketch, plugin manifest) |
| 15 | Người đọc chính | Panel gồm Engineering và Compliance. Mỗi kiểm soát nêu chi phí cho engineer và giá trị cho compliance |

Giả định chưa xác nhận, vẫn là [GĐ]: GĐ-3, 4, 7, 10, 12, 13. GĐ-6 sẽ được tra docs và đánh dấu 📖 ở bước thiết kế.

**Thay đổi GĐ-5 (2026-11-08):**
- **Trước:** "Gói GitHub của Papaya hỗ trợ environment protection rules (required reviewers) cho private repo", chưa kiểm tra.
- **Kiểm tra docs** (`work/02-research.md` 3.1.2): tính năng này trên repo private chỉ có ở Enterprise.
- **Quyết định của owner:** giả định gói **Team**. Đây là giả định để thiết kế, không phải sự thật về Papaya.
- **Hệ quả:** cổng duyệt chuyển từ environment sang merge PR vào `main` bằng rulesets.
- **Ghi chú:** owner từng giả định có dùng merge queue (02-research 3.7 A4). Theo docs, merge queue trên repo private cần Enterprise Cloud, nên hai giả định này mâu thuẫn. **Owner quyết định (2026-11-08): "Giữ Team và bỏ merge queue."** Thiết kế giả định không có merge queue.
