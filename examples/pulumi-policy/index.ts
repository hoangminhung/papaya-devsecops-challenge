// Entry point of the policy pack. Constructing PolicyPack starts the policy analyzer when the
// Pulumi CLI runs it (`pulumi up --policy-pack <dir>`); the checks live in policies.ts.
import { PolicyPack } from "@pulumi/policy";
import { policies } from "./policies";

new PolicyPack("example-org-aws-policies", { policies });
