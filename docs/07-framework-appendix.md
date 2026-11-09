# Framework appendix: detail, gaps and decisions

> Detail moved out of the [framework](01-framework.md) so that the framework reads in one pass.
> The text is unchanged except for cross-references; each section is summarised, with a link here, where the framework
> needs it. Markers and codes as in the framework's
> [How to read this](01-framework.md#how-to-read-this). Updated: 2026-11-09

| Section | Summarised in |
|---|---|
| [A. Limits and trade-offs, in detail](#a-limits-and-trade-offs-in-detail) | §1a |
| [B. SCPs on the prod OU](#b-scps-on-the-prod-ou) | layer 1 |
| [C. Who administers the administrators](#c-who-administers-the-administrators) | layer 1 |
| [D. GCP, Firebase and k0s identity](#d-gcp-firebase-and-k0s-identity) | layer 1 |
| [E. AWS credentials on laptops](#e-aws-credentials-on-laptops) | layer 2 |
| [F. Running the approval-gate app](#f-running-the-approval-gate-app) | layer 3 |
| [G. Who approves at night](#g-who-approves-at-night) | layer 3 |
| [H. GitHub Team or Enterprise Cloud](#h-github-team-or-enterprise-cloud) | layer 3 |
| [I. Risk stop, mechanics](#i-risk-stop-mechanics) | layer 3 |
| [J. Database changes, mechanism](#j-database-changes-mechanism) | layer 3; decision in [ADR-0011](adr/0011-database-changes-through-the-pipeline.md) |
| [K. Pinning what every laptop runs](#k-pinning-what-every-laptop-runs) | layer 4 |
| [L. Conditions on stored deploy credentials](#l-conditions-on-stored-deploy-credentials) | layer 5 |
| [M. Mobile releases through Expo EAS](#m-mobile-releases-through-expo-eas) | layer 5 |
| [N. Audit stores](#n-audit-stores) | layer 7 |
| [O. Drift detection](#o-drift-detection) | layer 7 |
| [P. Alert routing and incident declaration](#p-alert-routing-and-incident-declaration) | layer 7 |
| [Q. Gaps](#q-gaps) | framework, compliance register |
| [R. Author's design decisions (OD-n, 2026-11-09)](#r-authors-design-decisions-od-n-2026-11-09) | every document |

---

## A. Limits and trade-offs, in detail

- **The fallback meets the approval rule only partly** (approves a command list, not an applied
  change); accepted by the author (Options §9 Q2), to be signed off by Papaya's Compliance (§1). It is a second, process-controlled path, while the
  framing asked for one technically enforced path (framing §3.3, Options §7). It stays narrow only
  if most incidents are expressible in IaC (unknown, Options §8); layer 7 measures this.
- **On GitHub Team nobody sees the prod diff before apply** (⚠️ R4.6 #1; Team assumed, GĐ-5).
  Risky prod diffs stop the deploy until an owner of the stack approves the prod preview [design].
- **Admins can edit the gate**; logged, not prevented (logging 📖 R3.2.2; ability to edit ⚠️ R3.2.2,
  R3.6 #1). An admin's agent has
  the same power, because the agent uses its engineer's GitHub login (⚠️ R6.5 #10).
- **Some rules are process, not technology:** see "Process rules" in layer 1. The owner's rule
  "the PR approver is always an engineer, never an agent" (OD5) is absolute as policy, but on
  laptops it rests on policy, training and managed deny rules for `gh pr review` (OD25), which
  are hygiene: another form of the same call is not matched (📖 R9.4.1). An agent could still
  approve through its engineer's login. A review does not show whether it came from the web or
  the API (📖 R9.1.10); the approval-gate app only flags suspicious approvals (OD27). And "named"
  means a GitHub account that a register maps to a person: SAML SSO needs Enterprise Cloud
  (📖 R9.1.2), so on Team the mapping is a process (layer 1, OD25).
- **Incident approvers vs domain review:** code-owner review means an approver must own the file,
  at L2 as at L3. So that one on-call primary can approve any deployable path at 2 a.m., the on-call approver
  group co-owns every deployable path (owner decision OD9, layer 3). GitHub accepts an
  approval from any listed owner (📖 R3.2.7), so the approval-gate app enforces the rest (OD27,
  [design]): an on-call approval counts for another team's file only if the PR links an open
  incident and the approver is on shift. A label alone grants nothing, since anyone with Triage
  can apply it (📖 R9.1.9). Because on-call approvers only
  approve (OD7), a night incident needs two people awake: the incident responder and the on-call
  approver (the backup only replaces an unavailable primary).
- **One approver for most high-risk changes.** L3 changes in deployable code (IAM, stateful
  deletes, network) get one approver, like L2, from the owners of the path (the stack's owners for
  L3 content in domain files, OD8), and risky prod diffs stop for a look at the prod preview (OD2,
  OD8, layer 3). A single reviewer can miss things; this is the owner's trade-off for speed. The
  exception is the **process paths** (workflows, CODEOWNERS, agent config, catalogue, SCP and IAM
  stacks, risk stop): two L3 owner team members, enforced by the approval-gate app (OD26). They change
  rarely, are never urgent at night, and one compromised login must not be enough to change them.
- **k0s and Firebase are weaker:** no prod preview or risk stop, no break-glass when Actions is
  down (G1, G2), and their deploy credentials are stored in GitHub (OD1). For k0s, the interim
  controls of OD24 (a namespaced, time-limited deploy token and the Kubernetes API audit log) rely
  on `extraArgs`, which is "outside k0s support" (📖 R9.3.1).
- **New dependencies on two GitHub Apps** (required check, CI agent): if the required-check app is
  down, every merge to `main` is blocked, incident PRs included; that counts as "pipeline
  unavailable" for JIT. The required-check app now enforces OD26 and OD27 too, so it is a hard
  phase-1 prerequisite (rollout); its decision logic is an example (E12), its keys and hosting are
  open (G19). It is also the longest phase-1 item (10–15 person-days, ⚠️ estimate, OD35).
- **HIPAA applicability is a legal question** (⚠️ R1.11.1.11); the design treats Papaya as a
  business associate, as the brief implies.

---

## B. SCPs on the prod OU

- **SCPs on the prod OU** [design] (SCPs cap member-account principals, 📖 R2.3.1, R2.3.2):
  - deny data-plane reads on claim stores except application roles and the approved data-read role,
    by `aws:PrincipalArn` (📖 R2.3.8; pattern ⚠️ R2.9 #4). Actions, e.g. `s3:GetObject`,
    `sqs:ReceiveMessage`, `states:GetExecutionHistory`, are incomplete and unchecked (⚠️ G13);
  - deny `lambda:UpdateFunctionCode` / `lambda:UpdateFunctionConfiguration` (⚠️ R4.6 #3) except
    CloudFormation `deploymentRole`s, the Pulumi prod deploy role (if Pulumi manages Lambdas) and the
    JIT roles. The Serverless prod deploy role is a separate role and is not exempt: it only passes
    the `deploymentRole` (examples finding 13). This closes `serverless deploy function`, which changes config outside CloudFormation
    (📖 R4.4.4), and needs `deploymentRole` set on every Serverless stack (key 📖 R4.4.5; need ⚠️ R4.6 #3);
  - a pre-deployed revocation Deny on `identitystore:UserId` (📖 R2.4.4); deny changes to any trail
    in prod accounts, since member accounts cannot touch the organization trail anyway (📖 R2.6.2;
    examples findings 10, 15);
  - exempt role names are protected: only the IAM stack's deploy role may create or change such
    roles (OD19), and from phase 1 that is a role of its own (OD22): the IAM stack deploys from a
    separate GitHub environment, `production-iam`, whose OIDC subject only that role trusts. So
    code running in a domain stack's deploy job cannot obtain it. Domain deploy roles (and the
    CloudFormation `deploymentRole` of each Serverless stack) may create or change only `svc-*`
    roles, and only with a fixed permissions boundary attached that they cannot remove or edit
    (pattern 📖 R9.2.1; role action list ⚠️; examples E4b). The boundary denies `iam:*` and
    root sessions. Cost: Lambda and ECS roles that read claim data (`app-claims-*`) live in the
    IAM stack and are referenced by ARN (examples finding 16);
  - deny every action of `OrganizationAccountAccessRole` in the prod OU (OD23). Organizations
    creates this role with "full administrative permissions" in each account it creates, trusted
    by the management account (📖 R9.2.4); SCPs cover it as any other member-account role
    (📖 R9.2.6, inference). Using it in an emergency needs an SCP change, an L3 path.
  - Limits: 10 SCPs per target, 10,240 characters; no SCP applies to the management account
    (📖 R2.3.2, R2.3.4), so whatever deploys SCPs there is the most sensitive role (L3 path, held by the L3 owner team only, not co-owned by the on-call group; OD13).

---

## C. Who administers the administrators

- **Who administers the administrators (OD23).** Whoever administers IAM Identity Center can
  assign themselves any permission set, so "no standing prod write" holds only if that power is
  itself controlled [design unless marked]:
  - permission sets and account assignments are code in an identity stack (an L3 path, L3 owner
    team only, not the on-call group), applied from CI; the only other writer is the JIT flow's
    automation, which creates and deletes `InfraOperator-*` and `DataRead-*` assignments;
  - an alert fires on Identity Center changes (`CreateAccountAssignment`, `CreatePermissionSet`,
    `PutInlinePolicyToPermissionSet`, `AttachManagedPolicyToPermissionSet` and the other events
    with source `sso.amazonaws.com`, 📖 R9.2.2) made by any principal other than those two;
    which account's trail records changes made from a delegated administrator is not documented
    (📖 R9.2.2 "not found"), so the organization trail covers both accounts;
  - day-to-day administration from a delegated administrator account (📖 R9.2.3). It cannot touch
    permission sets provisioned in the management account, which stays a smaller circle;
  - the management account: no workloads, a named group of at least two L3 owners with hardware
    MFA, reviewed quarterly (C-03). SCPs never apply there (📖 R9.2.6), so this group is a
    detective control only;
  - member-account root users: credentials removed through centralized root access; privileged
    root tasks run from the management account with `sts:AssumeRoot` (📖 R9.2.5).

---

## D. GCP, Firebase and k0s identity

- **CI → GCP (OD36):** Workload Identity Federation. Google requires a condition that limits the pool
  to Papaya's GitHub organization and advises the numeric `*_id` claims, which cannot be reused (📖
  [WIF with deployment pipelines](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines);
  R3.4.5b). Narrower than that, as on AWS [design]: the pool condition also names the monorepo by
  `repository_id`; `google.subject` maps `assertion.sub` (📖 same page), so the subject carries the
  environment (`repo:…:environment:production`, 📖 R3.4.3); and only the `production` subject may
  impersonate the prod service account. Granting by subject rather than by a mapped attribute is
  ⚠️ (the page shows the `principalSet …/attribute.` form, which works with an `environment`
  attribute mapped from the token: also ⚠️, since the page lists no GitHub `environment` claim).
  Vertex AI model and endpoint changes deploy this way, from the monorepo, like any other stack.
- **GCP for humans and agents (OD36) [design unless marked]:** no standing role on prod projects for
  people. Agents and engineers get a custom read-metadata role (no `storage.objects.get`, no Vertex
  prediction calls such as `generateContent`, which is a data read, 📖 R9.6.3); writes and data reads
  come from Privileged Access Manager entitlements with approval, time-bound (30 min to 7 days, 📖
  R9.6.1), approved by the on-call approver. Whether PAM stops a requester approving their own
  grant is not documented (📖 R9.6.1 "not found"), so the entitlement lists the on-call group as
  approvers and the engineers as requesters, tested in phase 2. Data Access audit logs are off by
  default except BigQuery (📖 R9.6.3), so they are switched on for Vertex AI and for the buckets
  that hold partner documents; cost: log volume. The HIPAA list names the renamed products
  ("Generative AI on Agent Platform"), not "Vertex AI Gemini API" (📖 R9.6.4): Papaya confirms in
  writing with Google that its use is covered before PHI goes there.
- **Firebase Hosting (OD36):** not on the GCP BAA list (📖 R5.5.3), so it holds no PHI (⚠️ R5.7 #7).
  Deploy: the official action needs a service-account JSON key (📖 R9.6.5), kept as a secret of the
  `production-k0s` environment (OD24). A phase-2 spike tries WIF (`google-github-actions/auth`
  writes an Application Default Credentials file, 📖 R9.6.5) with `firebase deploy`; no official
  page says that works (📖 R9.6.5 "not found"). If it does, the key goes. Rollback creates a new
  release that serves an earlier version (console or `firebase hosting:clone`, 📖 R9.6.6): in an
  incident, a revert PR, or JIT when Actions is down. Preview channel URLs are public to anyone with
  the link (📖 R9.6.6), so previews come from the non-prod Firebase project only.
- **k0s for humans (OD36):** today kubeconfigs, no SSO (GĐ-4, unconfirmed). Target: OIDC through the
  API server's `extraArgs` (`oidc-issuer-url` and related flags) against Papaya's identity
  provider, which k0s documents but places outside its support (📖 R9.6.9); IdP groups map to a
  read-only ClusterRole without Secrets, exec or logs of claim services. Client-certificate
  kubeconfigs from `k0s kubeconfig create` are valid one year and "cannot be revoked" (📖 R9.6.9),
  so after OIDC works none is issued to a person except one break-glass admin certificate in the L3
  owner team's sealed store, alerted on use through the API audit log (E11). Interim: no admin
  kubeconfig and no GCP owner role on laptops; prod deploys only from CI.
- **k0s deploy identity (OD24).** Interim, phase 1: the CI credential is a time-limited
  ServiceAccount token, not an admin kubeconfig, bound to a namespaced Role that cannot read
  Secrets, exec into pods, read pod logs, issue tokens, change RBAC, impersonate or delete
  (📖 R9.3.6, R9.3.7; examples E11). Creating a workload grants it the API access of any
  ServiceAccount in its namespace (📖 R9.3.7), so deploy namespaces hold no privileged
  ServiceAccount. Target: kube-apiserver trusts GitHub's OIDC tokens directly through structured
  authentication, stable from Kubernetes 1.34 (📖 R9.3.4), so nothing is stored in GitHub; k0s
  does not document it (📖 R9.3.5), the API server must be reachable from the runner (📖 R9.3.8),
  and the claim rule must use the repository's real `sub` format (📖 R9.3.9).

---

## E. AWS credentials on laptops

- **Trade-off on AWS credentials [design].** With `~/.aws` hidden from the sandbox, phase 2 lists
  `aws *`, `pulumi *` and `serverless *` (with `sls *` and the `npx` forms) in `sandbox.excludedCommands`. Excluded commands run "with
  full access" (📖 R1.6.4), network included ("no filesystem restrictions and no network proxy", 📖 [sandboxing](https://code.claude.com/docs/en/sandboxing.md#run-commands-outside-the-sandbox-with-excludedcommands)). Matching follows `Bash(...)` rule
  syntax on the command text (same page; details in examples finding 22); each excluded
  call prompts through the `ask` rules of layer 2. This is worse than an
  egress channel: `pulumi preview` runs the Pulumi program and `serverless` loads its config and
  plugins, all code in the repo that the agent can edit, so excluding them lets repo code run
  outside the sandbox with network access and with `~/.aws` readable (⚠️ inference). For these
  commands the sandbox gives no protection. And an injected `aws` command could send out the SSO
  token cache itself. That token likely opens every role assigned to the engineer for the rest of the
  portal session (📖 R2.1.5; token reuse ⚠️ R2.2.2), probably including JIT or data-read grants added
  later in that session (⚠️ inference). Mitigations [design]: a short portal session (📖 R2.1.5); end
  the existing portal session and sign in fresh **before** a JIT or data-read grant is created
  (whether ending a session invalidates a token already stolen is unverified ⚠️; ending it does not
  end role sessions, 📖 R2.4.3); an SCP that denies writes to resources outside Papaya's organization using
  `aws:ResourceOrgID` (key 📖 R2.3.8), on every OU, since the token can be stolen from a non-prod
  session; legitimate writes to outside resources need exceptions (⚠️ not inventoried). That SCP only stops Papaya's own credentials writing to a
  foreign bucket; it does not stop a command that sends the token to a non-AWS endpoint or uses the
  attacker's credentials (⚠️ inference). Prefer running `pulumi` and `serverless` against real
  accounts only in CI; on laptops keep them to non-prod roles, and move them into the phase-3
  container. Residual risk: token theft during a session. It is accepted
  because the engineer holds no **standing** prod write and no **standing** PHI read; during a JIT
  or data-read window the protection is the process rule in layer 1 (D2). Stronger option, phase 3:
  a separate OS user or container for prod-reading sessions
  (⚠️ R6.5 #2).

---

## F. Running the approval-gate app

- **Running it [design; ⚠️ not researched beyond E12]:** the app runs in a dedicated tooling
  AWS account, outside prod and non-prod workloads; its private key sits in that account's
  secrets store, readable only by the app's role, and is listed in the secrets inventory with an
  owner and rotation (C-14), like the S2 exceptions; its code has its own repository with the
  marketplace's rules (two L3 approvals). It **fails closed**: no answer means no merge. If it is
  down during an incident, the pipeline counts as unavailable and JIT applies (layer 7). If it
  is down for longer, removing its check from the ruleset is an admin edit of the gate (T13):
  allowed only with two L3 owner team members' approval recorded in a ticket, alerted
  (`repository_ruleset.update`), and reverted when the app is back. A workflow
instead of an app is weaker: pinning the source to GitHub Actions likely lets any workflow set a
check of the same name, and the trigger that runs on review events from trusted code is not
researched (⚠️ G19).

---

## G. Who approves at night

- **Who approves at night (OD9):** a fixed GitHub team with write permission (owners without it
  are silently not assigned, 📖 R3.2.7; the CODEOWNERS validation check covers this), the on-call approvers, is listed as
  co-owner on every deployable path in CODEOWNERS (infrastructure and service code), next to the
  domain team. Confirmed by the owner (OD13): the group does **not** co-own the paths that
  define the process (`.github/**`, CODEOWNERS, `CLAUDE.md` and agent config, catalogue); those stay
  with the L3 owner team only. If a broken workflow blocks a night fix, the pipeline counts as
  unavailable and the JIT fallback applies (layer 7). One primary and one backup from that team are on call. Technically any member can approve any
  path; by rule the primary approves and the backup only if the primary is unavailable (OD2).
  Membership is fixed, not changed per shift [design]. GitHub team membership is set in organization
  settings, not by a PR; managing it as code (e.g. with Pulumi's GitHub provider) and the audit
  event for a membership change are not researched (⚠️ G16). Meanwhile the layer-7 settings
  comparison includes the group's member list. An approval from any listed owner satisfies
  code-owner review (📖 R3.2.7), so on its own GitHub would let a member approve another domain's
  PR on a normal day. **OD27 makes the rule technical** [design]: the approval-gate app counts an
  on-call member's approval for a file of another team only if the PR carries the `incident`
  label, links an incident that is open when the check runs, and the approver is primary or
  backup on shift. The label alone grants nothing, since anyone with Triage can apply it
  (📖 R9.1.9). In phase 1 the open incidents are incident issues in Linear and the shift comes from
  `oncall/schedule.yaml`, an L3 path whose content engineering management decides; from phase 2
  both come from the paging tool (G5). The monthly report lists every PR labelled `incident` with
  its incident, the incident's creator and the approver (layer 7). Residual: in phase 1 anyone can
  open an incident issue, so the report, not the app, catches an invented incident. Cost: a stale schedule file blocks a night approval until
  the backup or a domain owner approves; on normal days a cross-team PR needs an owner of each
  team. Whether Papaya's team size allows full coverage is unknown (§1, S7).

---

## H. GitHub Team or Enterprise Cloud

- **GitHub plan: Team or Enterprise Cloud (OD44).** Several controls here work around GitHub
  Team. Enterprise Cloud lists at $21 against $4 per user per month (📖 R9.1.3, read 2026-11-09).
  What the upgrade replaces, and what stays custom either way [estimates ⚠️, as in the rollout plan]:

  | Built here for Team | With Enterprise Cloud | Effort saved |
  |---|---|---|
  | GitHub login register from HR joiners and leavers (OD25, rollout 1.21) | SAML SSO ties each GitHub login to the identity provider (📖 R9.1.2) | 1–2 pd, plus monthly upkeep; closes "a GitHub login tied to the identity provider" in the README's "does not give" |
  | Monthly manual audit-log export (C-21) | Audit-log API and streaming (📖 R9.1.5, R9.1.6) | about half a day a month, and the 180-day gap risk |
  | Prod diff seen only when the risk stop fires | Environment required reviewers on private repos (📖 R9.1.4): a risky deploy can wait for a reviewer who sees the preview (only risky deploys waiting, e.g. through a second environment used after the risk stop fires, is [design] ⚠️) | part of the approval-PR mechanics of 1.14; closes "prod diff unseen" in §1 |
  | Approval-gate app rules R1–R4, W1 (E12), JIT receiver, risk-stop classifier, database path, evidence bucket (6 years is longer than any GitHub retention) | unchanged: no GitHub rule found that counts on-call approvals only in an incident, needs a tenant's data owner, or classifies a prod diff | none |

  **Recommendation:** the saving in build effort is small (roughly 5–10 person-days once and
  6–10 a year, ⚠️); the case for the upgrade is Compliance's: approvals tied to the identity
  provider and a prod diff seen before apply. For 50 users the difference is about $10,200 a
  year (⚠️ Papaya's user count unknown). Recommended: move to Enterprise Cloud in phase 2, before
  the first ISO evidence pack (rollout 3.4), if Papaya has up to about 100 GitHub users [design
  threshold]; above that, decide with the measured value of the manual steps. The design does not
  depend on it: everything here works on Team (GĐ-5).

---

## I. Risk stop, mechanics

- **Risk stop [design]:** applies to every deploy, whatever the level. The deploy job previews prod;
  on stateful replace/delete, an IAM change, a network or security-group change, or an advisory
  policy finding (from phase 2) it stops and posts the filtered preview. The original author opens a second PR that adds
  `deploy-approvals/<stack>/<sha>.yaml` (`<sha>` = the stopped commit) holding that SHA and the
  preview hash; the workflow does not open it, because the setting that lets Actions create and approve PRs stays
  off (📖 R3.3.3; ⚠️ R3.6 #3). CODEOWNERS on `deploy-approvals/<stack>/` names the owners of that stack and the
  on-call group (OD8, OD9). The approver is ≠ author and may be the first PR's approver, who now sees
  which prod resources and properties change; values stay out of the summary to keep secrets out
  of logs, and are reviewed in the code of the stopped PR. Merging it triggers the deploy on the new HEAD, which previews again and continues
  only if the hash matches the approved one; if another PR merged in between, the hash differs and
  the deploy stops again (Options §1; hash stability ⚠️ Options §8). The approval is bound to git
  history, not only to the hash (six conditions, 7-day expiry; examples E7, finding 2) [design].
  Known gap (OD18): an early approval can match a later change outside the stack (G19 closes it: the app checks that the stopped run's summary carries the same hash).
  The stop catches risky diffs nobody looked at, not approved malicious code (OD15); OD22 limits what such code can reach (layer 5). Cost: while a stack is
  stopped, later merges to that stack stop too until a matching approval lands; in an incident, a
  risky change already waiting on `main` blocks the fix for the same stack until it is approved or
  reverted. A
  `mandatory` policy violation always blocks `pulumi up` (📖 R4.2.2): the fix is a code change, or a
  change to the policy pack through its own L3 PR. Preview output is filtered for
  outputs and secrets before it is posted (Options §1; ⚠️ R4.6 #2).

---

## J. Database changes, mechanism

- **Database changes (OD29, ADR-0011) [design].** Aurora schema migrations, GraphQL-engine
  (Hasura) metadata and data fixes are files under `db/<service>/`, merged like code and applied by
  a `sql` job of the deploy workflow (examples E3):
  - where it runs [design]: Aurora is reachable only inside the prod VPC, and layer 5 avoids
    self-hosted runners, so the GitHub-hosted job never connects to the database. Its OIDC role may
    only start one ECS task definition (`db-change-<service>`) on one cluster, pass that task's two
    roles, and use one S3 prefix, and it trusts only the `production-db` environment, so no other
    deploy job can obtain it (examples E15). The bundle hash proves integrity between the job and
    the task; approval comes from the job itself, which runs only reviewed L3 code from `main`. The one-off Fargate task runs in private subnets
    from an image pinned by digest; its role may only `rds-db:connect` as the migration user (IAM
    database authentication, 📖 R9.2.11). ECS lets the caller override the command and environment
    of a task (📖 [RunTask](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_RunTask.html)),
    so the task re-checks the SHA-256 of the file bundle the risk stop classified and refuses any
    other; `ecs:ExecuteCommand` is denied. That `iam:PassRole` is what lets a caller start a task
    with a role is ⚠️ recalled, not checked in this round;
  - GraphQL-engine metadata is not a database change: the task applies it with
    `hasura metadata apply`, which needs the engine's admin secret and replaces all metadata
    (📖 [Hasura CLI](https://hasura.io/docs/2.0/hasura-cli/commands/hasura_metadata_apply/),
    [manage metadata](https://hasura.io/docs/2.0/migrations-metadata-seeds/manage-metadata/)). The
    secret sits in Secrets Manager and reaches only the task, through its task definition. No
    person holds database credentials or the admin secret day to day; a break-glass role that
    can read Secrets Manager can read it, which the JIT record shows (layer 7);
  - it lists the pending files through `tools/db/` wrappers around Papaya's migration tool (an L3
    path; the tool is not known here), runs the risk stop on them with `--tool sql`, and applies
    exactly the classified files, each in its own transaction;
  - the SQL risk stop (a heuristic, not a parser; examples E7) stops on DROP, TRUNCATE, column type
    changes, DELETE or UPDATE without a top-level WHERE, grants, roles, row-level security, COPY,
    function bodies and `EXECUTE`; every metadata change stops too, because it holds row
    permissions per role, i.e. tenant isolation; and any INSERT, UPDATE or DELETE inside a
    migration stops, because data changes belong in `data-fixes/<tenant>/`, where the data owner
    approves;
  - data fixes (`db/<service>/data-fixes/<tenant>/<ticket>.sql`) touch one tenant, declare
    `-- expected_rows: N`, and are rolled back when the count differs; approval is L3-data-write
    (layer-3 table); the job summary shows statement kinds and row counts, never values;
  - a data fix names records only by opaque internal IDs, because the file stays in git and every
    engineer and agent session can read it (OD48). A sensitive value the fix needs (a corrected
    bank account) goes into a values file that the data owner puts in the `db-change` bucket,
    which only the in-VPC task reads; the SQL refers to it as a psql variable [design]. A required
    check, `data-fix-scan`, fails a PR whose data fix matches one of the masking identifiers of
    layer 6 or holds a run of 9 or more digits (examples E19);
  - IAM database authentication is not in CloudTrail (📖 R9.2.11), so database-side evidence comes
    from Database Activity Streams (layer 7). Expand/contract migrations are recommended, not
    enforced. Cost: a data fix takes a PR and two approvals instead of a `psql` session.

---

## K. Pinning what every laptop runs

- **Pinning what every laptop runs (OD26).** A plugin, hook or local MCP server runs on every
  engineer's laptop, outside the sandbox, with that engineer's GitHub and AWS sessions. One
  compromised entry would hand an attacker many logins at once, enough to be both author and
  approver of a PR (threat T23). So nothing that reaches laptops follows a moving branch [design
  unless marked]:
  - managed settings pin the marketplace to one release tag: marketplace sources take a `ref`,
    with no `sha` field (📖 R9.4.4; a community schema describes `ref` as "branch, tag, or SHA",
    a SHA there is ⚠️ untested). In the marketplace repository, release tags can be created only by
    the L3 owner team and never moved or deleted, and every change needs two approvals (rulesets,
    examples E9b);
  - every plugin entry, internal ones included, carries a commit `sha` (📖 R9.4.5) and a review
    record; a relative `./plugins/…` source is not used, because it follows the marketplace's files;
  - auto-update stays off for the marketplace, locked through managed `extraKnownMarketplaces`
    (📖 R9.4.6); an update is a reviewed change of the pin;
  - engineers keep the GitHub CLI token in the system credential store; `gh` falls back to a
    plain-text file when there is none (📖 R9.1.11), so the guide asks them to check `gh auth status`.
  Cost: a plugin release takes three reviewed steps (change, tag, settings), and onboarding a local
  MCP server means packaging it (layer 4, "MCP").

---

## L. Conditions on stored deploy credentials

  - stored only as an **environment secret** of a protected environment (`production-k0s`), never as a repository secret. Anyone
    with write access can read repository secrets (📖 R3.5.3b), which would turn the exception into
    standing prod write for every engineer and their agent. Environment secrets and a deployment
    branch rule limited to `main` are available on Team for private repos (📖 R3.1.2, R3.1.3), and
    only the reviewed deploy workflow references the environment (layer 3);
  - the deploy job runs on GitHub-hosted runners. On self-hosted runners, jobs "are not run in an
    isolated container, even if they use environments", so environment secrets there must be
    treated like repository secrets (📖 R3.1.5). Self-hosted runners "can be persistently
    compromised by untrusted code" from anyone who can open a PR, and runner groups limit only which
    repositories use them (📖 R3.5.2); in a monorepo any workflow can likely target the runner's label (⚠️ G15).
    How to restrict a runner to one workflow is not researched (⚠️ G15); just-in-time runners exist
    (📖 R3.5.2, not read in detail). If reaching k0s needs a self-hosted runner, that
    runner is dedicated to the `production-k0s` deploy, and the residual risk is recorded;
  - that environment secret is the single source of truth: no copy elsewhere (OD1);
  - an owner, an expiry and rotation in the exception register;
  - a separate environment `production-k0s` (required since OD24, was optional), limited to
    `main` and referenced only by the k0s/Firebase deploy workflow, so AWS deploy jobs cannot read
    these secrets [design];
  - for k0s, the credential is the namespaced, time-limited ServiceAccount token of layer 1
    (OD24), rotated before it expires, and the cluster writes a Kubernetes API audit log: k0s has
    none by default and enables it only through `spec.api.extraArgs`, "outside k0s support"
    (📖 R9.3.1, R9.3.2). Secrets and token requests are logged at `Metadata` level so their
    contents stay out of the log (📖 R9.3.3; examples E11). A leaked token is then limited to
    deploys in its namespaces and leaves a trace; shipping that log to the log archive is part
    of G1.

  Residual risk: admins can change the environment, and a deleted environment comes back without
  protection (⚠️ R3.1.4); the alerts and settings comparison in layer 7 cover this. The exception
  covers **CI deploy credentials only**. Runtime credentials, such as a k0s autoscaler's AWS access to
  add or remove nodes, live in the cluster, not in GitHub; they follow layer 1 (no static keys, a
  role attached to the machine; ⚠️ not researched for k0s, G1).

---

## M. Mobile releases through Expo EAS

- **Mobile releases (OD40) [design unless marked].** EAS Update can push JavaScript to every
  installed app on a channel without a store review (📖 R9.8.1, R9.8.2), so it is a prod write path:
  - the `production` channel and the build and submit credentials are protected in Expo; only
    Release Manager, Admin or Owner may publish, republish, roll back or change rollout there
    (📖 R9.8.5). No person holds those roles day to day; the CI publishes as a robot user with the
    Release Manager role from a job in its own environment, `production-mobile` (limited to `main`,
    used by the mobile release workflow only, like `production-k0s`), so only a run of a merged
    `main` reaches the token and AWS deploy jobs cannot read it (layer 3; examples E3b);
  - Expo has no OIDC for GitHub (📖 R9.8.7 "not found"), so the robot token is a long-lived secret
    in that environment, on the secrets inventory (S2 exception, like k0s/Firebase), rotated;
    Owner and Admin can remove the protection: at least two named Owners, in the identity register;
  - updates are signed (EAS Update code signing; Production or Enterprise plan, 📖 R9.8.8): the app
    carries the certificate, and the private key lives only in `production-mobile`, so a stolen
    Expo token alone cannot ship code. Whether the app rejects an unsigned update is not stated
    plainly (⚠️ R9.8.8): tested before relying on it. The certificate in the repository is an L3
    path (CODEOWNERS, examples E2);
  - EAS Workflows cannot publish to a protected channel (📖 R9.8.11), and Expo's GitHub app is not
    connected for prod triggers; production builds and store submissions run from the same CI job;
    Android submissions go to a draft release that a person finishes in Play Console (📖 R9.8.13);
  - evidence: Expo's audit log is Enterprise-only and does not list update publishes (📖 R9.8.9),
    so the nightly evidence export also compares the updates on the `production` channel with the
    deploy runs and merged commits; an update without a run is an incident;
  - rollback is `eas update:republish` of the previous update or `eas update:rollback`, both
    protected actions (📖 R9.8.3): a revert PR in the normal lane, JIT on the robot in an incident.

---

## N. Audit stores

- **Audit stores:**
  - organization CloudTrail to a log-archive account with integrity validation (📖 R2.6.2, R2.6.4,
    R2.6.5); change records ≥ 6 years; raw-log retention for Papaya's compliance owner (⚠️ R5.7 #2).
    Data events only on PHI buckets, prod Lambda invoke and prod SQS (cost 📖 R2.6.3; selection
    ⚠️ R2.9 #5), which makes the archive
    PHI-bearing (⚠️ research 1.11.4 L15). CloudTrail Lake is closed to new customers (📖 R2.6.6);
  - **evidence bucket** (OD30) [design]: an S3 bucket in the log-archive account with Object Lock
    in compliance mode, 6 years, which nobody, root included, can shorten or delete (📖 R9.2.12;
    a new bucket, since enabling it on an existing one was not confirmed). From phase 1 a nightly
    workflow writes the last day's merged PRs with their reviews and check runs, and the logs and
    artifacts (`risk-summary`) of deploy runs, through a role that may only `PutObject`
    (examples E13). Actions keeps logs 90 days by default, at most 400 (📖 R9.1.8): set 400 as
    a buffer;
  - GitHub org audit log kept 180 days (📖 R3.5.6). Its REST API is documented for Enterprise
    Cloud, not Team (📖 R9.1.5), so an org owner exports it monthly from the UI (JSON) into the
    evidence bucket, a manual step in the monthly report (📖 R9.1.7);
  - **JIT and real-data request records** (OD30): an issue in a dedicated Linear team, from a
    template with required fields (command list or store, scope, tenant, reason, incident link,
    agreement); the approver approves by moving it to an "Approved" state. Linear's audit log is
    Enterprise-only and kept 90 days, and its CSV export has no field history (📖 R9.1.14), so a
    webhook receiver in the tooling account (the approval-gate app's) writes every change, with
    the previous values Linear sends, to the evidence bucket. Not Slack;
  - alerts on `repository_ruleset.update`, `environment.update_protection_rule`,
    `environment.remove_protection_rule`, `environment.delete`, `protected_branch.policy_override`
    (📖 R3.5.6, R3.1.4; selection ⚠️ R3.6 #1). UI changes to the branch policy may leave no event, and a
    deleted `production` environment comes back unprotected (⚠️ R3.1.4): a job compares live settings
    with an expected copy (G8);
  - Aurora SQL is likely invisible to CloudTrail (⚠️ R2.7.1): Database Activity Streams, alerts on
    lost-record events (📖 R2.7.2; Serverless v2 ⚠️), stream treated as PHI (⚠️ R2.7.3);
  - Claude Code OTel without prompt content (layer 2);
  - Kubernetes API audit log of prod k0s (OD24, layer 5); destination open (G1).

---

## O. Drift detection

- **Drift [design]:** its own role, trusted only from a `drift` environment on `main`; it can read
  prod secrets in state, which is noted (⚠️ R4.6 #2). Scheduled `pulumi preview --refresh
  --expect-no-changes` or `pulumi refresh --preview-only` (📖 R4.1.1, R4.3.1, R4.3.2). On a DIY S3
  backend, preview needs state-write permission (📖 R4.3.3); whether a refresh preview writes more
  than locks is open (⚠️ R4.6 #2, G14). So either the drift role gets state write (and the same
  trust care as the deploy role), or Pulumi Cloud drift detection is used (📖 R4.3.2, Pro+). The
  latter runs on Pulumi Deployments, which holds credentials to prod, so it re-opens a side path that
  layer 5 excludes and needs the same trust narrowing and audit (📖 R4.4.9; ⚠️ R4.6 #6). CloudFormation
  drift detection, explicitly set properties only (📖 R4.4.6). No auto-remediation: it is an unreviewed
  `pulumi up --refresh` (📖 R4.3.2). Each finding gets an actor and a ticket.

---

## P. Alert routing and incident declaration

- **Alerts and incident declaration, target (OD38) [design unless marked].** Today alerts are
  spread over CloudWatch, GCP and Slack, with no paging (brief). Target, built in phase 2 (item 2.8):

  | Step | Design |
  |---|---|
  | Sources | CloudWatch alarms → SNS topics per severity; GCP Cloud Monitoring alert policies; GitHub audit alerts and the evidence-reconciliation jobs (layers 3, 7, OD40) |
  | Paging | One paging tool (product open, a decision for Papaya: G5) holds the on-call schedule and pages the primary, then the backup. SNS reaches it through an HTTPS subscription; SNS cannot call private endpoints (📖 R9.6.7). GCP sends to it directly and also to email or Pub/Sub, because Google states that Slack, PagerDuty, webhook and mobile channels "share a single point of failure" (📖 R9.6.8). AWS Incident Manager is not an option: closed to new customers since 2025-11-07 (📖 R9.6.7) |
  | Chat | Amazon Q Developer in chat applications (formerly AWS Chatbot) posts SNS notifications to one Slack alerts channel (📖 R9.6.7); the paging tool opens one Slack channel per incident |
  | Severities | SEV1: claims cannot be submitted or paid, or data exposure suspected → page now, 24/7, open an incident. SEV2: degraded for one tenant or a backlog that will breach the insurer SLA → page in working hours, at night only if it grows. SEV3: ticket. Thresholds per service with the service owners [design] |
  | Escalation | Responder unanswered after 10 min → backup responder; approver unanswered → backup approver (OD2); no answer after 20 min → engineering manager on call [design times] |
  | Declaration | The responder (or the paging tool) opens the Linear incident issue with severity and tenant; that open issue is what the approval-gate app and the JIT receiver read (OD27, OD33). A suspected data exposure also starts the breach-notification clock of the tenant's country (compliance register, C-26) |
  | Agents | The incident-analysis session (layer 2) starts from the alert: metrics and masked logs through `ProdReadMetadata`; it proposes a fix, the responder writes the PR (layer 3) |

  Approving a PR from a phone works through GitHub Mobile (⚠️ not checked for code-owner reviews);
  until it is, the approver uses a laptop. The routing is the same for AWS and GCP from day one of
  phase 2; k0s alerts follow its monitoring stack (not known here, ⚠️).

---

## Q. Gaps

Not covered, or only as an open item, in `work/02-research.md`.

| # | Gap | Layers |
|---|---|---|
| G1 | k0s: OIDC for humans designed (OD36), not tested on Papaya's version; placing the audit policy on controllers and shipping the audit log; the target OIDC trust for CI (OD24 gives interim controls); break-glass when Actions is down | 1, 3, 6, 7 |
| G2 | Firebase Hosting deploy from CI without a stored key: a phase-2 spike (OD36); break-glass when Actions is down | 1, 5, 7 |
| G3 | GCP: the read-metadata role's permission list and PAM self-approval are not checked (OD36); BAA coverage of the renamed Vertex products to confirm with Google | 1, 6 |
| G4 | Tool choice where no licence is bought (secret scan, SAST, dependency scanner); non-prod data scanning; k0s admission (OD39) | 5, 6 |
| G5 | Choice of the paging tool; alert thresholds per service; approving a PR from GitHub Mobile (routing designed, OD38) | 7 |
| G6 | SSM Automation `aws:approve` (read in `work/03-options.md` §2, not in 02-research) | 7 |
| G7 | GitHub Actions log and artifact retention, and export | 3, 7 |
| G8 | Rulesets and environment settings through the API | 7, 8 |
| G9 | How Linear and Slack MCP servers authenticate | 4, 6 |
| G10 | OIDC subject customisation (`job_workflow_ref`) on GitHub Team | 1 |
| G11 | Closing provider/login bypasses on laptops without MDM | 2 |
| G12 | `pulumi up` flag reference for the prod allowlist | 3 |
| G13 | IAM actions for every data-plane read (S3, SQS, Step Functions, Secrets Manager, RDS, ECS Exec, Lambda invoke) | 1, 6 |
| G14 | Which state writes a Pulumi refresh preview needs on a DIY S3 backend | 3, 7 |
| G15 | Restricting a self-hosted runner to one workflow in a monorepo; just-in-time runners | 5 |
| G16 | Managing GitHub team membership as code; audit event for a membership change | 3, 7 |
| G17 | Who forms the L3 owner team and how many people (GĐ-1: never a single reviewer) | 3, 8 |
| G18 | Reading the live values of server-managed settings (API or local cache) to compare with git | 2, 8 |
| G19 | Required-check app and CI-agent app: review-event triggers, source pinning against same-name checks, hosting, private-key storage and whether those keys count against S2; the app's check that a risk-stop approval matches the stopped run's hash (OD18); reading Linear incidents and the schedule (OD27). The decision logic itself is examples E12 | 3, 5 |
| G20 | Emergency revocation at night: who can apply the revocation Deny SCP (management account) within minutes; `aws:TokenIssueTime` kill switch (⚠️ R2.9 #3) | 1, 7 |

Open checks from `work/03-options.md` §8 remain open.

---

## R. Author's design decisions (OD-n, 2026-11-09)

"Owner" here is the author of this submission. These decisions shaped the design; none is a
Papaya sign-off. Papaya's own decisions are listed in §1.

The owner answered the open questions of draft v3. English rendering; the original Vietnamese
answers are recorded in `work/session-log.md`.

| # | Question | Decision |
|---|---|---|
| OD1 | Exception to S2 = 0 for k0s/Firebase deploy credentials? | Yes, provided each credential has a single source of truth. (The first reason given, continuous scale-in/scale-out, concerns runtime credentials; OD6 narrowed the scope.) |
| OD2 | L3: must one approver be from the platform team? | Not necessarily; one approval procedure is agreed for all engineers, and the on-call engineer is enough. Clarified in follow-ups: every change involves two people, one who makes it and one who approves; the on-call backup only replaces an unavailable primary. Asked whether L3 should need more approvers than L2, the owner chose "L3 = 1 approver at all times"; in the agent's framing of that option, the approver must own the path. |
| OD3 | `CLAUDE.md` changes: L2 or L3? | L3, because the workflow must be consistent across the whole team. |
| OD4 | Move the rest of the managed baseline and the SSM check to phase 2? | Yes. |
| OD5 | "An agent does not approve PRs" only a process rule? | It is a rule: the PR approver is always an engineer, never an agent. |
| OD6 | Scope of OD1: CI deploy credentials only, or also runtime scaling credentials? | CI deploy credentials (k0s kubeconfig/token, Firebase token in GitHub secrets) only, until it is checked whether k0s and Firebase can use OIDC. |
| OD7 | (a) If the on-call engineer writes an L3 fix, who approves? (b) Keep the read-only allowlist in phase 1? | (a) "While on call, never change the process"; clarified: on-call engineers only approve, and fixes are written by another engineer (the incident responder), so the approver is never the author. (b) Yes, as proposed. |
| OD8 | IAM/network/stateful changes inside a domain file: who approves the risk stop? | The stack's owners (may be the first approver); always two people. The L3 owner team keeps only the real L3 paths; Access Analyzer and policy packs compensate. |
| OD9 | How can one on-call primary approve any path at night? | The on-call approver group co-owns every deployable path; one primary + one backup. Normal-day domain review is a process rule with a monthly check. |
| OD10 | A PR touching files of several domain teams: split, or one approval? | One approval is enough (two-person rule kept); domain review on such PRs is a recommendation, counted in the monthly report. |
| OD11 | Risk stop when the first approver is unavailable: may another owner of the stack approve? | Yes; it makes three people and is recorded as a deviation. |
| OD12 | `sandbox.autoAllowBashIfSandboxed`: `true` or `false`? | Keep `true` (fewer prompts, relies on the sandbox, which arrives in phase 2). |
| OD13 | Confirm three agent readings: (1) OD8, who opens and approves the risk-stop approval PR; (2) OD9, scope of the on-call group; (3) L3-JIT, does the on-call approver count as service owner? | Confirmed: (1) the original author opens it and the first approver approves it; (2) the on-call group does not co-own process-defining paths or the SCP stack, which only the L3 owner team approves; (3) yes. |
| OD14 | Add the risk-stop classifier (`tools/risk-stop/`) to the canonical L3 path list? (found while writing `examples/`) | Yes: it is a control, so only the L3 owner team may change it. |
| OD15 | Scope of the risk stop: risky diffs nobody looked at, or also malicious approved code? | Keep the current scope and state its limits; a separate prod preview role and a job split go to the phase-2 roadmap. |
| OD16 | Squash-only merges to `main` (needed so a PR cannot carry its own risk-stop approval)? | Yes; the cost is that PR-internal commit history is not kept on `main`. |
| OD17 | Deploy only the current tip of `main`, so re-running an old run cannot roll prod back? | Yes; added to the layer-3 "merge approval = deploy approval" conditions. |
| OD18 | An approval merged before a deploy stops, matched by a later change outside the stack's directory, is still accepted | Accepted as a stated limit; the approval-gate app (G19) is to close it by checking the stopped run's hash. |
| OD19 | Protect the names of SCP-exempt roles (`app-claims-*`, `cfn-deployment-*`, `github-prod-deploy-*`) so that only the IAM stack's deploy role can create or change them? (found while writing `examples/`) | Yes. Confirmed reading: "only the IAM stack" holds once OD20 gives the IAM stack its own role and OIDC subject; until then the protection is "only an approved prod Pulumi deploy". OD22 gives the IAM stack that role and subject in phase 1. |
| OD20 | Code in the deploy job (install scripts, Pulumi program, Serverless plugins) can request the job's OIDC token for either prod deploy role: fix now or roadmap? | Roadmap phase 2, together with OD15: a build job without `id-token`, and per-role environments (different OIDC subjects) or `job_workflow_ref`. Until then it is a stated limit. **Superseded in timing by OD22:** per-environment roles move to phase 1. |
| OD21 | Phase 1 lets built-in read-only commands (`cat`, `head` …) read `~/.aws` without a prompt, and allow rules skip the auto-mode classifier: add keys to the phase-1 subset? | Yes: add a `Read(~/.aws/**)` deny rule and `autoMode.classifyAllShell: true` (examples finding 19). |

**Fixes after the independent review** (`work/07-review.md`; proposals and the owner's choices in
`work/08-fix-proposals.md`, documentation checks in `work/09-fix-research.md`). The owner accepted
every proposal on 2026-11-09:

| # | Review finding | Decision |
|---|---|---|
| OD22 | Approved code runs with a prod deploy role, which can change SCP-exempt roles (review A-1) | Moves OD20 into phase 1: the IAM stack gets its own environment `production-iam` and role; domain deploy roles change only `svc-*` roles under a fixed permissions boundary; no install scripts in deploy and preview jobs except a reviewed allowlist (L3 path); agent review on every PR touching infrastructure code. The separate preview role (OD15) stays in phase 2. |
| OD23 | Identity Center administrators and `OrganizationAccountAccessRole` can grant prod write outside the design (review C-4) | Identity Center permission sets and assignments as code (L3 owner team only) with alerts on other changes; an SCP denies `OrganizationAccountAccessRole` in the prod OU; member-account root credentials removed; a named management-account group. |
| OD24 | The long-lived k0s deploy credential is undetectable if leaked, on the cluster that runs AI agents reading partner documents (review A-4) | Phase 1: a namespaced, time-limited ServiceAccount token without Secret, exec, log, token, RBAC or delete rights; `production-k0s` environment required; Kubernetes API audit log. Target: k0s trusts GitHub OIDC directly. |
| OD25 | An approval proves a GitHub account, not a named person; an agent can approve through its engineer's login (review C-1) | Required 2FA, a login register fed by HR with quarterly review, restricted personal access tokens; from phase 1, managed deny rules for `gh pr review`, `gh api …reviews…` and the `gh` token file (hygiene); Enterprise Cloud (SAML, environment reviewers, audit-log streaming) is listed with its price as a decision for Papaya. |
| OD26 | A component that runs on every laptop (plugin, hook, local MCP server) can give an attacker many logins at once, so author ≠ approver is no longer two independent people (review A-2, A-3) | Threat T23; marketplace pinned to a protected release tag, every plugin (internal too) pinned by `sha`, auto-update off; local MCP servers only as immutable artifacts (image digest or pinned plugin); approval-gate app flags suspicious approvals; **process paths need two L3 owner team members** (partly reverses OD2, ADR-0012). |
| OD27 | The `incident` label opens cross-domain approval, and anyone with Triage can apply it (review E-2) | The approval-gate app counts an on-call approval for another team's file only with an open incident and the approver on shift; the label alone grants nothing; every `incident` PR is in the monthly report. Consequence: on normal days a cross-team PR needs an owner of each team (changes the effect of OD10; ADR-0012). The app becomes a hard phase-1 prerequisite. |
| OD28 | PHI could reach the agent through a log group it may read, if one approved PR logs a whole event (review A-1b) | CloudWatch Logs masking with custom identifiers on those log groups, set before they open; no `logs:Unmask` for agent-usable roles; a SAST rule against logging whole events. Stated as a second layer: AWS has no managed identifiers for VN/TH/HK. |
| OD29 | No designed path for schema migrations and data fixes (review E-1) | `sql` job of the deploy workflow with its own database role (IAM auth), SQL risk stop, metadata changes always stop, data fixes per tenant with expected rows and a data owner's approval (L3-data-write); ADR-0011. A hard prerequisite of removing standing prod write. |
| OD30 | Evidence before phase 2 can expire; JIT and data-read approvals have no store (review C-2, C-3) | From phase 1: evidence bucket with Object Lock (compliance, 6 years), nightly export of PRs, reviews, checks, deploy logs and artifacts; monthly manual export of the org audit log; Linear template for JIT and data-read requests, mirrored to the bucket by webhook. Closes O-1 and O-4. |
| OD31 | Strict up-to-date branches plus head-commit-only approvals make every merge stale every other PR (independent review round 3, #4) | The approval-gate check counts an approval on an earlier commit when the PR's diff against its merge base is unchanged (patch ID), as GitHub's own stale-approval rule does; the last pusher is the last person who changed that diff. Strict up-to-date stays. |
| OD32 | The IAM stack, which creates and re-trusts the SCP-exempt roles and the boundary, needed one approver co-owned by on-call (round 3, #5) | `infra/pulumi/iam/` and `deploy-approvals/iam/` become process paths: two L3 owner team members, no on-call co-owner; a night IAM fix uses JIT. |
| OD33 | Nothing checked "approver ≠ requester" before a JIT grant (round 3, #7) | A receiver in the tooling account grants `InfraOperator-*` only after checking the signed Linear webhook, a person's state change, approver ≠ requester, on shift, open incident and the allowed set (E16); manual grant by the L3 owner team as the degraded mode, alerted. |
| OD34 | Phase-2 costs for Engineering were stated only in the examples (independent review G1 #3, G2 #4, G3 #1) | Costs listed in §1, layer 2, the README and S4; mitigations: push and PR at the `!` prompt, cloud CLIs against real accounts in CI, Docker tests in CI, a read-only registry token in the sandbox, a deadline for masked logs per service and Logs Insights through masking as the agent-safe debugging path; per-group settings via the Claude apps gateway as a phase-3 option. |
| OD35 | Phase 1 had no effort estimate (review G-7; rounds G1 #7, G2 #5, G3 #9) | Rough estimate per item (≈ 75–110 person-days), critical path through the approval-gate app, a minimum safe phase 1 (≈ 57–83 pd: 2 DevSecOps + 1 platform engineer for ~45 days, or 1–2 people for ~60 days), and a detective degraded mode if the app is late, accepted only by Compliance in writing. |
| OD36 | GCP, Firebase and human k0s access were "same principles"; several prod write paths were never named (review G-4; rounds G1 #8, G2 #8, G3 #6) | GCP: WIF limited to the monorepo and the `production` subject, PAM entitlements instead of standing roles, Data Access logs for Vertex AI and partner documents, written BAA confirmation; Firebase: WIF spike, rollback by revert PR, previews from non-prod only; k0s: OIDC for people, one sealed break-glass certificate; a table of every prod write path and its gate in layer 3. |
| OD37 | Thailand and Hong Kong were not mentioned (round G1 #9) | Register rows for transfers per tenant country and breach notification (C-18, C-26), a tenant compliance profile, and open items for the insurance regulators (O-10, O-11); the controls stay the same, the paperwork and the clock change. |
| OD38 | Fragmented monitoring had one principle and a placeholder (review G-4; rounds G1 #10, G2 #9, G3 #10) | Target routing: CloudWatch → SNS → one paging tool and Slack via Amazon Q Developer; GCP → the paging tool plus email or Pub/Sub; no AWS Incident Manager; three severities, escalation times, incident declaration as a Linear issue that the gate and JIT read; agents start from the alert. |
| OD39 | S10 checks had names only; no image scanning or signing; no limit on agent PR size (round G1 #12) | Concrete checks per tool with the two GitHub licences as a priced decision for Papaya, Trivy for Dockerfiles, manifests and generated templates, ECR enhanced scanning and managed signing, a PR-size check for app-opened PRs; k0s admission open. |
| OD40 | Mobile releases through Expo EAS (OTA updates) bypassed the merge gate (round G2 #8) | Protected `production` channel and credentials, CI robot with Release Manager only in the `production-mobile` environment, signed updates, no EAS Workflows for prod, nightly reconciliation of channel updates against deploy runs. |
| OD41 | Open points of OD31–OD33 (owner, 2026-11-09) | OD31: the semantic-clash residual is accepted and recorded; GitHub's behaviour is tested when built. OD32: stated as rare (the IAM stack holds only exempt roles and the boundary); a JIT metric for IAM-stack grants decides whether an incident rule is needed. OD33: real payload checked when built; scope from a label and the incident from an issue relation; one grant per request; Linear through SSO in the people register; compared with the AWS TEAM sample. |
| OD42 | Independent review round after G5 (2026-11-09) | `production-db` environment for the database job; DML in a migration stops; data owners read by the gate from the path, not code owners; `production-mobile` for the Expo secrets; threats for the tooling account and its keys (T26) and a scoped role for the JIT receiver; 1.7 a hard prerequisite. |
| OD43 | The first 45–60 days keep writable SSO sessions with auto mode and no prompts for cloud CLIs (round after G5, #6) | The `ask` rules for `aws`, `pulumi` and `serverless` move into the phase-1 subset (may not slip); auto mode stays allowed (D1). |
| OD44 | No cost comparison of the custom tooling with GitHub Enterprise Cloud (#7) | A table of what Enterprise replaces (identity register, manual audit-log export, prod diff before apply) and what stays custom (gate rules, JIT receiver, risk stop, database path, evidence bucket); recommendation: upgrade in phase 2 up to about 100 users. |
| OD45 | Changes to the production AI agents had no risk class (#11) | Their prompts and model settings: owned by the AI team, with a required evaluation check; their tool permissions and identity: a process path (two L3 approvers). Runtime security of those agents stays out of scope. |
| OD46 | The panel could not read the deliverable quickly; "owner" read as Papaya's sign-off; agents appeared mostly as a risk (review G-1–G-3 and the later review rounds) | An executive brief without codes; §1 rewritten as one page with the decisions Papaya must take and their recommendations; "owner" stated as the author everywhere it matters; §2 with eight agent-assisted DevSecOps workflows, three new skills, a shared `CLAUDE.md` template and a PR template (E17). |
| OD47 | Final review round: the internal skills did not load under `--restricted`; the incident session kept MCP servers; path-filtered required checks could hang (2026-11-09) | Internal plugin force-enabled through managed `enabledPlugins`; `--strict-mcp-config` in the incident session; every required check runs on every PR; a CI review workflow example (E18) and value baselines for §2. |
| OD48 | Data-fix files could carry tenant personal data into git (final review #4) | Data fixes name records by opaque IDs; sensitive values come at run time from a values file only the in-VPC task reads; the required check `data-fix-scan` fails on masking identifiers or long digit runs (E19). |
| OD49 | Custom tooling on the critical path; phase headings still "0–30" (final review #3) | Phases re-baselined to days 0–45, 45–75, 75–100; the approval-gate app runs two weeks report-only before it is required, with an availability target, an alert and a drilled removal runbook. |
| OD50 | Engineering loses agent push and PR in phase 2 through controls the design calls hygiene (final review #2) | The phase-2 sandbox goes to one pilot team first and to everyone only once S4 holds; a narrow push-and-PR credential for the agent is evaluated in the pilot. |
| OD51 | Blast radius of approved domain-stack code understated (final review #6); on-call not sized (#10) | #6: the real blast radius is stated, with per-domain environments as the next step. #10: not changed; the rota is sized by Papaya's engineering management (author's choice). |
| OD52 | The framework was too dense to read in one pass (final review #1) | Detail blocks moved verbatim into this appendix, each replaced in the framework by a summary with a link; gaps and decisions moved here; nothing decided changed. Framework 1,309 → 937 lines. |
| OD53 | The minimum safe phase 1 deferred laptop-deploy migration and the S10 checks while still removing standing write and requiring those checks (review after OD52, #1) | Laptop deploys to CI (1.4) and one measured incident-lane drill (minimal 1.1) become hard prerequisites 9 and 10; the ruleset requires only checks that already run, each S10 check joining when it runs on every PR; S9–S11 and C-09/C-15/C-17 say when their item lands. |
| OD54 | S5 depends on MDM, which Papaya may not have (#3) | S5 is met only on laptops with MDM and reported as not met elsewhere, with OTel's share of sessions under the managed policy measured instead. Not added to Papaya's decisions (author's choice). |
| OD55 | A night IAM-stack fix was sent to JIT, which the SCP blocks (#2) | In an open incident the approval-gate app accepts one L3 owner team member, reached by phone, plus a different on-call approver on shift for the IAM stack (rule R3i), flagged for the monthly report; other process paths keep two L3 approvals; the SCP is unchanged. |
| OD56 | The data owner role was undefined (#9) | A Papaya employee named per insurer tenant, not the insurer's staff; read access to the repository; co-approves that tenant's data reads and data fixes. |
| OD57 | Run cost of the custom tooling unstated (#5) | A yearly run-effort table (≈ 60–105 pd ⚠️) and a lean first version (GitHub's rules plus the nightly E12 check) offered as a decision for Papaya, with Compliance's written acceptance; rota sizing stays with Papaya (OD51). |
| OD58 | No agent identity separate from the engineer (#6) | An isolated agent runtime (development box with its own AWS role and per-session GitHub App token) evaluated with the phase-2 pilot (rollout 2.14), next to OD50's credential; listed as a decision for Papaya. |
| OD59 | Past §1 the framework chained decision codes and working-note references (#4) | Layer 3's principle, the L3 rows, on-call and break-glass rewritten as current-state rules with the decision codes after them; references to the working notes kept only where they back a number or an open point; review-process notes removed from the status line. |
