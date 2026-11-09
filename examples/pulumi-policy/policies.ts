// Mandatory guardrails for prod stacks (framework layer 5; they compensate OD8, where the stack's
// owners, not the L3 owner team, approve IAM and stateful changes inside domain files).
// Phase 2. Run by `pulumi up --policy-pack` in deploy-prod.yml; "a violation of a mandatory
// policy stops the deployment" (R4.2.2). Exported separately from index.ts so that tests can
// call the checks without the Pulumi engine.
//
// Limits (examples/README.md, E10):
// - A value that is unknown during preview (e.g. a policy document built with
//   pulumi.jsonStringify from a resource created in the same update) makes @pulumi/policy 1.21.0
//   report the check as advisory during preview (✅ server.js). The update should then stop at
//   that resource once the value is known (⚠️ not run here), after earlier resources in the same
//   update may already exist. Access Analyzer (layer 5) is the preview-time check for IAM.
// - Only resources declared in the stack are checked: a customer-managed policy created outside
//   Pulumi and attached here by ARN is checked by name only (admin-equivalent AWS policies).
import * as aws from "@pulumi/aws";
import { ReportViolation, ResourceValidationPolicy, validateResourceOfType } from "@pulumi/policy";

type Statement = { Effect?: string; Action?: string | string[]; NotAction?: string | string[] };

function statementsOf(policy: unknown): Statement[] {
    if (policy === undefined || policy === null) return [];
    const doc = typeof policy === "string" ? JSON.parse(policy) : policy;
    const st = (doc as { Statement?: Statement | Statement[] }).Statement ?? [];
    return Array.isArray(st) ? st : [st];
}

// Services where any wildcard in the action name grants privilege escalation or identity changes,
// e.g. iam:Pass*, iam:*Role*, sts:Assume*.
const NO_WILDCARD_SERVICES = /^(iam|sts|organizations|sso[a-z-]*|identitystore[a-z-]*):/i;

function wildcardActions(policy: unknown): string[] {
    const found: string[] = [];
    for (const st of statementsOf(policy)) {
        if (st.Effect !== "Allow") continue;
        if (st.NotAction !== undefined) found.push("NotAction");
        const actions = st.Action === undefined ? [] : Array.isArray(st.Action) ? st.Action : [st.Action];
        for (const raw of actions) {
            const a = raw.trim();
            // A wildcard in the service prefix is treated as a full wildcard (whether IAM accepts
            // one there is ⚠️ not verified; refusing it costs nothing).
            if (/[*?]/.test(a.split(":")[0])) { found.push(raw); continue; }
            // IAM accepts `*` and `?` in action names (📖 IAM JSON policy elements: Action), so
            // `*?`, `s3:?*` or `ec2:**` mean the same as `*` / `<service>:*`.
            if (/^[*?]+$/.test(a) || /^[a-z0-9-]+:[*?]+$/i.test(a)) found.push(a);
            else if (NO_WILDCARD_SERVICES.test(a) && /[*?]/.test(a)) found.push(a);
        }
    }
    return found;
}

function report(actions: string[], reportViolation: ReportViolation) {
    if (actions.length > 0) {
        reportViolation(`IAM Allow with a wildcard action (${actions.join(", ")}); name the actions.`);
    }
}

// AWS managed policies that grant `*` or `<service>:*`: the same grants iam-no-wildcard-actions
// refuses in an inline or customer-managed document. Matched on any partition and path.
function adminEquivalent(arn: unknown): boolean {
    if (typeof arn !== "string") return false;
    const m = /^arn:aws[a-z-]*:iam::aws:policy\/(?:.*\/)?([^/]+)$/.exec(arn);
    return m !== null && (["AdministratorAccess", "PowerUserAccess"].includes(m[1]) || m[1].endsWith("FullAccess"));
}

function reportArns(arns: unknown, reportViolation: ReportViolation) {
    const bad = ([] as unknown[]).concat(arns ?? []).filter(adminEquivalent);
    if (bad.length > 0) {
        reportViolation(`Attaches an admin-equivalent AWS managed policy (${bad.join(", ")}); write a scoped policy.`);
    }
}

export const policies: ResourceValidationPolicy[] = [
    {
        name: "iam-no-wildcard-actions",
        description: "IAM policies may not allow `*`, `<service>:*`, wildcards in iam/sts/organizations/sso " +
            "actions, or use NotAction with Allow.",
        enforcementLevel: "mandatory",
        validateResource: [
            validateResourceOfType(aws.iam.Policy, (p, _args, v) => report(wildcardActions(p.policy), v)),
            validateResourceOfType(aws.iam.RolePolicy, (p, _args, v) => report(wildcardActions(p.policy), v)),
            validateResourceOfType(aws.iam.UserPolicy, (p, _args, v) => report(wildcardActions(p.policy), v)),
            validateResourceOfType(aws.iam.GroupPolicy, (p, _args, v) => report(wildcardActions(p.policy), v)),
            validateResourceOfType(aws.iam.Role, (r, _args, v) => {
                for (const inline of r.inlinePolicies ?? []) report(wildcardActions(inline.policy), v);
            }),
        ],
    },
    {
        name: "iam-no-admin-managed-policies",
        description: "No attachment of AdministratorAccess, PowerUserAccess or any AWS managed *FullAccess policy.",
        enforcementLevel: "mandatory",
        validateResource: [
            validateResourceOfType(aws.iam.RolePolicyAttachment, (a, _args, v) => reportArns(a.policyArn, v)),
            validateResourceOfType(aws.iam.UserPolicyAttachment, (a, _args, v) => reportArns(a.policyArn, v)),
            validateResourceOfType(aws.iam.GroupPolicyAttachment, (a, _args, v) => reportArns(a.policyArn, v)),
            validateResourceOfType(aws.iam.PolicyAttachment, (a, _args, v) => reportArns(a.policyArn, v)),
            validateResourceOfType(aws.iam.RolePolicyAttachmentsExclusive, (a, _args, v) => reportArns(a.policyArns, v)),
            validateResourceOfType(aws.iam.UserPolicyAttachmentsExclusive, (a, _args, v) => reportArns(a.policyArns, v)),
            validateResourceOfType(aws.iam.GroupPolicyAttachmentsExclusive, (a, _args, v) => reportArns(a.policyArns, v)),
            validateResourceOfType(aws.iam.Role, (r, _args, v) => reportArns(r.managedPolicyArns, v)),
        ],
    },
    {
        name: "aurora-deletion-protection",
        description: "Aurora / RDS clusters must have deletion protection on.",
        enforcementLevel: "mandatory",
        // Retiring a cluster needs `deletionProtection: false` first, which this policy refuses.
        // Exception route [design]: an L3 pull request to the policy pack that lists that one
        // cluster by URN, approved by the L3 owner team, removed again after the deletion.
        validateResource: validateResourceOfType(aws.rds.Cluster, (c, _args, v) => {
            if (c.deletionProtection !== true) v("Set deletionProtection: true on every prod cluster.");
        }),
    },
    {
        name: "s3-public-access-block-all-on",
        description: "Every public access block must set all four flags to true.",
        enforcementLevel: "mandatory",
        validateResource: validateResourceOfType(aws.s3.BucketPublicAccessBlock, (b, _args, v) => {
            const flags = {
                blockPublicAcls: b.blockPublicAcls,
                blockPublicPolicy: b.blockPublicPolicy,
                ignorePublicAcls: b.ignorePublicAcls,
                restrictPublicBuckets: b.restrictPublicBuckets,
            };
            const off = Object.entries(flags).filter(([, val]) => val !== true).map(([k]) => k);
            if (off.length > 0) v(`Public access block must set ${off.join(", ")} to true.`);
        }),
    },
];
