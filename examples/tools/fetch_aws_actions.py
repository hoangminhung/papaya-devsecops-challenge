#!/usr/bin/env python3
"""Fetch a small offline IAM action catalogue from AWS's Service Authorization Reference.

Usage:
  python3 fetch_aws_actions.py <out.json> [service ...]

Source: https://servicereference.us-east-1.amazonaws.com/ (AWS's machine-readable service
reference: one JSON file per service with its actions, resource types and annotations).
Only what the tests need is kept, per action:
  resource_scoped  the action supports at least one resource type (else it needs "*")
  write            AWS annotation IsWrite
  list             AWS annotation IsList
  data_plane       AWS annotation IsDataPlane
  permission_mgmt  AWS annotation IsPermissionManagement
"""
import datetime
import json
import sys
import urllib.request

INDEX = "https://servicereference.us-east-1.amazonaws.com/"
DEFAULT_SERVICES = [
    "cloudformation", "cloudtrail", "cloudwatch", "dynamodb", "ec2", "ecs", "elasticloadbalancing",
    "health", "iam", "kms", "lambda",
    "logs", "rds", "rds-data", "s3", "secretsmanager", "sns", "sqs", "ssm", "states", "sts", "xray",
]


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:  # noqa: S310 (fixed https host)
        return json.load(r)


def main():
    out = sys.argv[1]
    services = sys.argv[2:] or DEFAULT_SERVICES
    index = {e["service"]: e["url"] for e in get(INDEX)}
    catalogue = {}
    for svc in services:
        doc = get(index[svc])
        actions = {}
        for a in doc["Actions"]:
            props = (a.get("Annotations") or {}).get("Properties") or {}
            actions[a["Name"]] = {
                "resource_scoped": bool(a.get("Resources")),
                "write": bool(props.get("IsWrite")),
                "list": bool(props.get("IsList")),
                "data_plane": bool(props.get("IsDataPlane")),
                "permission_mgmt": bool(props.get("IsPermissionManagement")),
            }
        catalogue[svc] = dict(sorted(actions.items()))
        print(f"{svc}: {len(actions)} actions")
    with open(out, "w") as f:
        json.dump({
            "$comment": f"From {INDEX} on {datetime.date.today().isoformat()} by "
                        "examples/tools/fetch_aws_actions.py",
            "services": catalogue,
        }, f, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
