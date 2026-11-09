// Calls each check with hand-made resource properties, without the Pulumi engine or any cloud.
// Proves the checks' logic; does NOT prove how the Pulumi CLI wires them in (type tokens, unknown
// values during preview). Run: npm test.
import * as assert from "node:assert/strict";
import { policies } from "./policies";

// The minimal part of ResourceValidationArgs the checks use. The Pulumi CLI builds the real one;
// isType compares the class's Pulumi type token, as the generated resource classes do.
type FakeArgs = {
    type: string;
    props: Record<string, unknown>;
    isType: (cls: { __pulumiType?: string }) => boolean;
    notApplicable: (reason?: string) => void;
};
type Validation = (args: FakeArgs, report: (m: string) => void) => void;

function violations(policyName: string, type: string, props: Record<string, unknown>): string[] {
    const policy = policies.find((p) => p.name === policyName)!;
    const checks = ([] as unknown[]).concat(policy.validateResource) as Validation[];
    const found: string[] = [];
    const args: FakeArgs = {
        type,
        props,
        isType: (cls) => cls.__pulumiType === type,
        notApplicable: () => undefined,
    };
    for (const check of checks) check(args, (m) => found.push(m));
    return found;
}

const cases: Array<[string, string, Record<string, unknown>, boolean]> = [
    // [policy, Pulumi type token, props, expect a violation]
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "*", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/rolePolicy:RolePolicy",
        { policy: { Statement: [{ Effect: "Allow", Action: ["s3:*"], Resource: "*" }] } }, true],
    ["iam-no-wildcard-actions", "aws:iam/role:Role",
        { inlinePolicies: [{ name: "x", policy: JSON.stringify({ Statement: { Effect: "Allow", NotAction: "iam:*", Resource: "*" } }) }] }, true],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: ["s3:GetObject"], Resource: "arn:aws:s3:::b/*" }] }) }, false],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Deny", Action: "*", Resource: "*" }] }) }, false],
    // review step 3, H3: user and group inline policies, wildcards inside iam/sts actions
    ["iam-no-wildcard-actions", "aws:iam/userPolicy:UserPolicy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "*", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/groupPolicy:GroupPolicy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "*", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: ["iam:Pass*"], Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/rolePolicy:RolePolicy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "iam:*Role*", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "sts:Assume*", Resource: "*" }] }) }, true],
    // review step 3 round 2, M5: `?` spellings of a full wildcard
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "s3:?*", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "ec2:**", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "*?", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "iam:PassRol?", Resource: "*" }] }) }, true],
    // round 3, L1: wildcard in the service prefix, padding, other sso-* services
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "*:*", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "s?:Get*", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: " s3:*", Resource: "*" }] }) }, true],
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "sso-directory:Create*", Resource: "*" }] }) }, true],
    // a read wildcard outside identity services stays allowed
    ["iam-no-wildcard-actions", "aws:iam/policy:Policy",
        { policy: JSON.stringify({ Statement: [{ Effect: "Allow", Action: "s3:Get*", Resource: "arn:aws:s3:::b/*" }] }) }, false],
    // admin-equivalent AWS managed policies, by every attachment route
    ["iam-no-admin-managed-policies", "aws:iam/rolePolicyAttachment:RolePolicyAttachment",
        { role: "r", policyArn: "arn:aws:iam::aws:policy/AdministratorAccess" }, true],
    ["iam-no-admin-managed-policies", "aws:iam/userPolicyAttachment:UserPolicyAttachment",
        { user: "u", policyArn: "arn:aws:iam::aws:policy/PowerUserAccess" }, true],
    ["iam-no-admin-managed-policies", "aws:iam/groupPolicyAttachment:GroupPolicyAttachment",
        { group: "g", policyArn: "arn:aws:iam::aws:policy/IAMFullAccess" }, true],
    ["iam-no-admin-managed-policies", "aws:iam/policyAttachment:PolicyAttachment",
        { roles: ["r"], policyArn: "arn:aws-us-gov:iam::aws:policy/AdministratorAccess" }, true],
    ["iam-no-admin-managed-policies", "aws:iam/rolePolicyAttachmentsExclusive:RolePolicyAttachmentsExclusive",
        { roleName: "r", policyArns: ["arn:aws:iam::aws:policy/AmazonS3FullAccess"] }, true],
    ["iam-no-admin-managed-policies", "aws:iam/userPolicyAttachmentsExclusive:UserPolicyAttachmentsExclusive",
        { userName: "u", policyArns: ["arn:aws:iam::aws:policy/AdministratorAccess"] }, true],
    ["iam-no-admin-managed-policies", "aws:iam/groupPolicyAttachmentsExclusive:GroupPolicyAttachmentsExclusive",
        { groupName: "g", policyArns: ["arn:aws:iam::aws:policy/AdministratorAccess"] }, true],
    ["iam-no-admin-managed-policies", "aws:iam/role:Role",
        { managedPolicyArns: ["arn:aws:iam::aws:policy/AdministratorAccess"] }, true],
    ["iam-no-admin-managed-policies", "aws:iam/rolePolicyAttachment:RolePolicyAttachment",
        { role: "r", policyArn: "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" }, false],
    ["iam-no-admin-managed-policies", "aws:iam/rolePolicyAttachment:RolePolicyAttachment",
        { role: "r", policyArn: "arn:aws:iam::123456789012:policy/AdministratorAccess" }, false],
    ["aurora-deletion-protection", "aws:rds/cluster:Cluster", { deletionProtection: false }, true],
    ["aurora-deletion-protection", "aws:rds/cluster:Cluster", {}, true],
    ["aurora-deletion-protection", "aws:rds/cluster:Cluster", { deletionProtection: true }, false],
    ["s3-public-access-block-all-on", "aws:s3/bucketPublicAccessBlock:BucketPublicAccessBlock",
        { blockPublicAcls: true, blockPublicPolicy: true, ignorePublicAcls: true, restrictPublicBuckets: false }, true],
    ["s3-public-access-block-all-on", "aws:s3/bucketPublicAccessBlock:BucketPublicAccessBlock",
        { blockPublicAcls: true, blockPublicPolicy: true, ignorePublicAcls: true, restrictPublicBuckets: true }, false],
    // a check must ignore other resource types
    ["aurora-deletion-protection", "aws:s3/bucket:Bucket", { deletionProtection: false }, false],
];

let failed = 0;
for (const [name, type, props, expected] of cases) {
    const got = violations(name, type, props).length > 0;
    try {
        assert.equal(got, expected);
        console.log(`ok   ${name} ${type} -> ${expected ? "violation" : "pass"}`);
    } catch {
        failed++;
        console.log(`FAIL ${name} ${type}: expected ${expected ? "violation" : "pass"}`);
    }
}
for (const p of policies) assert.equal(p.enforcementLevel, "mandatory", p.name);
console.log(`${cases.length - failed}/${cases.length} cases passed; all policies mandatory`);
process.exit(failed ? 1 : 0);
