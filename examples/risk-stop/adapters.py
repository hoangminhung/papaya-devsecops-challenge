"""Adapters from each tool's preview JSON to the normalized format used by classify.py.

⚠️ NOT VERIFIED. Neither tool's JSON structure is documented in the research for this
submission (work/02-research.md R4.1.1 and R4.4.2 only name the `--json` flag), and neither
tool was run here. The field names below are assumptions to check against real output
before use. Any input they cannot read raises an error, and classify.py then stops the
deploy (fail closed).

Assumed shapes:
  pulumi preview --json:
    {"steps": [{"op": "update", "urn": "urn:pulumi:<stack>::<project>::<type>::<name>",
                "newState": {"type": "...", "inputs": {...}},
                "oldState": {"type": "...", "inputs": {...}}}]}
    Pulumi ops seen in its docs/CLI output: same, create, update, delete, replace,
    create-replacement, delete-replaced, read, refresh, import ... (⚠️ list not checked).
  serverless diff --json (sf-core >= 4.37.0):
    {"resources": [{"logicalId": "...", "type": "AWS::...", "action": "add|modify|remove",
                    "replacement": true|false, "properties": {<changed properties only>}}]}
"""
import hashlib
import json

PULUMI_OPS = {
    "same": "same",
    "create": "create",
    "update": "update",
    "delete": "delete",
    "replace": "replace",
    "create-replacement": "replace",
    "delete-replaced": "replace",
    "read": "same",
}


def _digest(*values):
    return hashlib.sha256(json.dumps(values, sort_keys=True, default=str).encode()).hexdigest()


def _changed_keys(old, new):
    return sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))


def pulumi(raw):
    changes = []
    for step in raw["steps"]:
        urn = step["urn"]
        name = urn.rsplit("::", 1)[-1]
        state = step.get("newState") or step.get("oldState") or {}
        # URN type part is "parent$...$type" for child resources; keep the last segment.
        rtype = state.get("type") or urn.split("::")[-2].rsplit("$", 1)[-1]
        old = (step.get("oldState") or {}).get("inputs") or {}
        new = (step.get("newState") or {}).get("inputs") or {}
        changes.append({
            "type": rtype,
            "name": name,
            "op": PULUMI_OPS.get(step["op"], step["op"]),  # unknown ops pass through -> risky
            "changed_keys": _changed_keys(old, new),
            "detail_digest": _digest(old, new),
        })
    return {"changes": changes}


SLS_ACTIONS = {"add": "create", "modify": "update", "remove": "delete"}


def serverless(raw):
    changes = []
    for r in raw["resources"]:
        op = SLS_ACTIONS.get(r["action"], r["action"])
        if op == "update" and r.get("replacement"):
            op = "replace"
        props = dict(r.get("properties") or {})
        # ⚠️ Values that change on every `serverless package` would make the hash unstable, so
        # an approval could never match. From memory, not checked: the Lambda code location
        # (Code.S3Key) holds a timestamped artifact path, and AWS::Lambda::Version logical IDs
        # carry a code hash. `Code` is left out of the hash and of changed_keys (it is code, not
        # access); Version changes are left out of the hash only. Not handled: resources that
        # reference the version logical ID (aliases, provisioned concurrency) also change on
        # every build, so their stacks may never get a stable hash.
        if r["type"] == "AWS::Lambda::Function":
            props.pop("Code", None)
        changes.append({
            "type": r["type"],
            "name": r["logicalId"],
            "op": op,
            "changed_keys": sorted(props),
            "detail_digest": _digest(props),
            "volatile": r["type"] == "AWS::Lambda::Version",
        })
    return {"changes": changes}


def normalized(raw):
    for c in raw["changes"]:
        for key in ("type", "name", "op"):
            if not isinstance(c.get(key), str):
                raise ValueError(f"change without '{key}'")
    return raw


ADAPTERS = {"pulumi": pulumi, "serverless": serverless, "normalized": normalized}
