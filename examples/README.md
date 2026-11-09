# Examples

> Status: step 1 of the writing plan (change workflow, layer 3), after three independent reviews.
> Identity examples (E4–E6) and agent/supply-chain examples (E8–E10) follow. · Updated: 2026-11-09

Concrete files behind [`../docs/01-framework.md`](../docs/01-framework.md). Each one exists to
prove one claim of the framework, and each has a local check. **Nothing here was run against
GitHub, AWS or any live system.** A passing check shows that the file says what the framework
says; it does not show that the platform enforces it. Every row lists what the check does
**not** prove.

Markers: ✅ checked in this repository's sessions (command output in the transcript) ·
📖 official documentation, linked · ⚠️ assumption, not verified · [design] proposal of this
submission, untested.

Placeholders: `example-org`, `<owner team>`, `123456` (app ID), `<AWS_ACCOUNT_ID>`. The monorepo
layout (`services/`, `infra/pulumi/`, `k8s/`, `web/`, `tools/`) is invented; Papaya's is unknown.

Where each file would live in the monorepo:

| Here | In the monorepo |
|---|---|
| `github/workflows/*.yml` | `.github/workflows/` |
| `github/CODEOWNERS` | `.github/CODEOWNERS` |
| `github/ruleset-main.json`, `github/environment-production/` | repository settings (REST API bodies), with an expected copy in git (layer 8) |
| `risk-stop/classify.py`, `risk-stop/adapters.py` | `tools/risk-stop/` |
| `risk-stop/deploy-approvals/<stack>/` | `deploy-approvals/<stack>/` at the root |
| `risk-stop/fixtures/`, `tests/`, `schemas/`, `tools/`, `validate.sh` | only here, to check the examples |

## How to run

```bash
examples/validate.sh            # tools that are not installed are SKIPPED, and reported as such
ACTIONLINT=/path/actionlint ZIZMOR=/path/zizmor examples/validate.sh
```

Needs Python 3 with `jsonschema`, `PyYAML` and `git`; optional `jq`, `yamllint`, `shellcheck`,
`actionlint`, `zizmor`. Tests use the standard `unittest`.

## What each file proves

| # | Files | Proves (framework) | Checked by | Does not prove |
|---|---|---|---|---|
| E1 | [`github/ruleset-main.json`](github/ruleset-main.json) | The approval gate is the merge to `main` (layer 3, ADR-0003): PR required, 1 approval, code-owner review, stale approvals dismissed, approval by someone other than the last pusher, branch up to date (no merge queue), required checks pinned to a source app, no force push or deletion, empty bypass list | JSON Schema of the create-ruleset request body; key-by-path check; design tests | That GitHub enforces it. `approval-gate` comes from a dedicated app whose ID (`123456`) is a placeholder (gap G19). The other checks are pinned to GitHub Actions (ID 15368 ✅ `GET https://api.github.com/apps/github-actions`), so any workflow in the repo can likely post a check with the same name (⚠️ layer 3, G19) |
| E2 | [`github/CODEOWNERS`](github/CODEOWNERS) | L3 process paths: owned by the L3 owner team only; deployable paths: co-owned by the domain team and the on-call group, so one approval from either satisfies code-owner review (OD9, OD13; 📖 R3.2.7); risk-stop approvals: co-owned by the stack's owners and on-call (OD8). Fail-safe default so no file is unowned [design] | Effective owners resolved with GitHub's "last matching pattern takes the most precedence" (📖 [about code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)); every stack in `deploy-on-main.yml` checked for code and approvals owners | That the teams exist and have write access: GitHub drops such owners silently. [`codeowners-validate.yml`](github/workflows/codeowners-validate.yml) covers that in a real repo |
| E3 | [`github/workflows/`](github/workflows/) | "Merge approval = deploy approval" (layer 3): only the reusable [`deploy-prod.yml`](github/workflows/deploy-prod.yml) uses `production`; no ref/SHA input; no `workflow_dispatch`, `issue_comment`, `pull_request_target`, `workflow_run`; one concurrency group per stack, running deploys never cancelled; only the current tip of `main` is deployed (no re-run of an old run) [design]; preview → risk stop → apply, and the stop cannot be skipped, ignored or bypassed by an `if:`; apply commands use only allowed flags. Layer 5: OIDC, per-job permissions, SHA-pinned actions; `npm ci`, Pulumi plugins and the policy pack installed before prod credentials (the Serverless framework download: ⚠️ assumed to happen at `serverless --version`). PRs preview non-prod only | `actionlint`, `zizmor --persona=auditor`, `yamllint`; design tests (`test_workflow_policy.py`) | That the workflows run: the Pulumi/Serverless steps were never executed. The tests see only these files, not a whole monorepo |
| E3b | [`github/environment-production/`](github/environment-production/) | `production` accepts deployments from `main` only and has no required reviewers (not available on GitHub Team for private repos, R3.1.2); names of the k0s/Firebase exception secrets (OD1, OD6) and of the prod variables | JSON Schemas of the two request bodies (environment PUT, branch-policy POST); key-by-path check; design tests | That GitHub applies it; admins can still change or delete the environment (layer 7 compares live settings) |
| E7 | [`risk-stop/`](risk-stop/) | The risk stop (layer 3, ADR-0004) can be built: risky prod diffs stop the deploy (per category, for Pulumi and CloudFormation types alike, plus property names on any type); an approval counts only for the exact preview, only if it was merged to `main` on its own after the stopped commit, never edited, and the stack's code is unchanged since the stopped commit; approvals expire 7 days after they were merged; the summary shows which resources and properties change, never values; unreadable input stops | 25 unit tests; approval tests run against throwaway git repositories, including the bypasses found in review (edited approval, merge-commit PR, approval on a side branch, approval merged before a change inside the stack, runtime edit of the file) and one test that documents a gap that stays open (see Limits) | ⚠️ The JSON shapes of `pulumi preview --json` and `serverless diff --json` are **assumed** ([`adapters.py`](risk-stop/adapters.py)). That a real preview gives the same hash twice for unchanged code (Options §8). See "Limits of the risk stop" |

Schemas in [`schemas/`](schemas/) are extracted from GitHub's REST OpenAPI description
(`github/rest-api-description` at commit `2f8f80e47ea4d3292cf4e37ba9d9b25475e06140`, OpenAPI 3.0.3 ✅)
by [`tools/extract_github_schemas.py`](tools/extract_github_schemas.py), which resolves `$ref` and
`nullable`. They do not forbid unknown keys, so a misspelled key passes schema validation; the
key-by-path check ([`tests/schema_keys.py`](tests/schema_keys.py)) catches it (✅ mutation run:
`require_last_pusher_approval` passes the schema and is reported by the key check).

Mutation runs ✅ (each must make the tests fail, and did): `continue-on-error: true` on the risk
stop; `|| true` after the classifier; `if: always() && …` on an apply step; `pulumi up -f`;
a non-"Apply" step running `pulumi up` with `if: failure()`; `exit 1` replaced by `true` in the
tip-of-`main` guard; the guard reading `commits/main` instead of `git/ref/heads/main`; removing
the "approval merged on main's first-parent history" check;
removing the CODEOWNERS line for `deploy-approvals/claims-api/`; a broad CODEOWNERS line after
the L3 section.

## Limits of the risk stop

The risk stop answers one framework problem: on GitHub Team nobody sees the prod diff before
apply (framework §1). It catches **risky prod diffs that nobody looked at**. It is not a boundary
against **malicious or prompt-injected code that was approved**:

- The stack's own code runs with the prod deploy role: `npm` packages are installed before the
  credentials (so install scripts get none), but the Pulumi program runs during `preview` and
  `up`, and Serverless plugins during `package`/`diff`/`deploy`. That code could call AWS
  directly, or tamper with files the classifier reads, in the same job. The defence against it
  is the PR review itself, and from phase 2 IAM Access Analyzer and policy packs (layer 5).
- A stronger variant [design, not in the framework]: preview with a separate prod **preview**
  role (read and state access, no write), run the classifier in its own job on a fresh
  checkout without credentials, and assume the deploy role only in a later job after the stop.
  It adds a role and a job split; it is an open question for the owner.
- `pulumi up` previews again before applying. A change made outside the pipeline between the
  two previews (JIT, drift) is not re-checked. `pulumi preview --save-plan` + `pulumi up --plan`
  would bind the two, but update plans are experimental (📖 R4.1.3).
- Concurrency: a running deploy is never cancelled, but GitHub cancels a run that is still
  pending when a newer one arrives for the same group (📖 GitHub docs source,
  `data/reusables/actions/actions-group-concurrency.md`). Some merged commits therefore have no
  deploy run of their own; the newer run deploys them too, and the change record must link both
  commits to that run. `queue: max` would give every commit its own run, but the same page says
  the order "is not guaranteed": an older commit could then deploy after a newer one and undo it
  in prod. So the default is kept on purpose [design].
- The type lists are examples. For types that are missing, the rule on property names
  (`policy`, `role`, `securityGroup`, `vpcConfig`, `public`, `authorization`, `logging`, …;
  a narrower set on creates) catches some changes, not all.
- **Open gap:** nothing proves that a deploy really stopped at `stopped_commit` with the
  approved hash. An approval merged early (naming a commit whose deploy did not stop, with a
  hash computed in advance, which needs knowledge of prod inputs) is accepted if a later change
  **outside** the stack's directory, such as a shared library, produces exactly that diff. Changes
  inside the stack's directory are rejected. Watching the whole repository instead would cancel
  every approval at each unrelated merge in a monorepo. The fix is for the approval-gate app to
  check, on the approval PR, that the stopped run's summary carries the same hash (G19) [design].
  `test_known_gap_early_approval_and_change_outside_the_stack` documents the current behaviour.
- The approver of the approval PR sees **which** prod resources and properties change, not the
  new values (the summary never prints values, to keep secrets out of logs). The values are
  reviewed in the code of the stopped PR. Framework layer 3 and ADR-0004 say the approver "sees
  the prod diff"; that wording is too strong and is corrected in the framework's final pass.
- Any commit to the stack's directory between the stop and the approval merge cancels the
  approval: the author names the newer stopped commit and the owner approves again. In an
  incident that is one more review round.
- `npm ci` runs before the credentials, but its lifecycle scripts can still write to
  `$GITHUB_ENV` / `$GITHUB_PATH` and so influence later steps that hold them.
  `npm ci --ignore-scripts` reduces this where the stack's packages allow it.
- If the newest merge to `main` carries `[skip ci]` (or similar) in its message, no push run
  exists for the tip and the older runs refuse to deploy; prod stays behind until the next merge
  (📖 GitHub docs source, `content/actions/how-tos/manage-workflow-runs/skip-workflow-runs.md`,
  via review). Operator action: merge an empty change.
- Within 7 days, an approved change that is reverted and then merged again with identical code
  passes without a new approval. This is intended: it is the same code and the same prod diff
  that an owner approved.
- The binding relies on squash-only merges (`ruleset-main.json`); with merge commits, a PR's
  inner commits would be invisible to the first-parent check.

## Findings from writing these files

Points the framework text does not yet say; carried into the framework in the final pass.
Owner decisions 2026-11-09 (framework OD14–OD18): findings 1, 3 and 4 accepted; the risk stop keeps
its current scope (OD15); the early-approval gap is an accepted limit for G19 to close (OD18).

1. **The risk-stop classifier must be an L3 path** [design]. The deploy runs it from the merged
   commit, so a PR that edits it together with an IAM change, approved by the domain team, could
   switch the stop off. `CODEOWNERS` adds `/tools/risk-stop/` to the L3 owner team. Needs owner
   confirmation: it extends the canonical L3 list of framework layer 5.
2. **An approval must be bound to git history, not only to a hash** [design]. Two review rounds
   found ways for one PR to carry its own risky change and approval, or for an approval to be
   reused. Rules now: read from git objects only; file named `<stopped_commit>.yaml`, never
   edited; stopped commit and approval commit both on `main`'s first-parent history, in that
   order; the approval commit touches only `deploy-approvals/<stack>/`; the stack's directory
   and the classifier unchanged since the stopped commit; at most 7 days old.
3. **Squash-only merges** [design]: `ruleset-main.json` allows only squash, so each PR is one
   commit on `main`. Cost: PR-internal history is not kept on `main`.
4. **Deploy only the tip of `main`** [design]: people with write access can re-run a workflow run
   for up to 30 days, with the same `GITHUB_SHA` (📖 GitHub docs source,
   `content/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs.md`, via review). An
   old deploy run re-run would roll prod back without any approval. `deploy-prod.yml` stops unless
   the run's commit is the current tip of `main`, read with `GET /repos/{owner}/{repo}/git/ref/heads/main`
   (✅ branch-only form; `commits/main` could resolve to a tag named `main`). This is a new
   condition for framework layer 3's "merge approval = deploy approval" list.
5. **Classification beyond the framework's categories** [design]: the property-name rule, the
   audit/detection category and "an unknown operation stops" go beyond layer 3's list
   (stateful replace/delete, IAM, network, policy finding).
6. **The approval hash must cover changed values**, not only resource names, or an approval for
   one IAM policy would let a different change to the same policy through; and it must leave out
   values that change on every build, or an approval never matches. ⚠️ From memory, not checked:
   Serverless puts a timestamped path in the Lambda `Code.S3Key` and a code hash in
   `AWS::Lambda::Version` logical IDs; both are left out of the hash.
7. **Fail-safe CODEOWNERS default** [design]: without it, root `package.json`, a new stack or a new
   `deploy-approvals/<stack>/` folder would be unowned, and GitHub then accepts an approval from
   any writer (📖 about code owners).
8. **Same-repository reusable workflows can use `uses: $/.github/workflows/<file>`**, which GitHub
   now recommends: it resolves to the running commit, not to the runner's workspace (📖 GitHub docs
   source, `data/reusables/actions/reusable-workflow-calling-syntax.md`; flagged by zizmor's
   `self-repository` audit). `actionlint` 1.7.12 (✅ latest release on 2026-11-09, published
   2026-03-30) does not know the syntax; `validate.sh` ignores only that message.
9. **`runner.temp` is not available in job-level `env`** (✅ caught by `actionlint`); paths use
   `$RUNNER_TEMP` inside steps.

## Latest run

`validate.sh` on 2026-11-09 (✅, output shortened):

```text
=== tool versions ===
Python 3.10.12
jsonschema 4.26.0 | PyYAML 6.0.3
jq: jq-1.6
yamllint: yamllint 1.38.0
actionlint: 1.7.12
zizmor: zizmor 1.30.1
=== JSON syntax (jq) ===
checked 11 files
=== GitHub Actions security (zizmor, offline, auditor persona) ===
No findings to report. Good job!
=== unit tests (python3 -m unittest) ===
Ran 62 tests
OK
=== result ===
RESULT: all executed checks passed
```
