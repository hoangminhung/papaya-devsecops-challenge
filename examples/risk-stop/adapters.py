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
import re

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


# ---------------------------------------------------------------- SQL (framework layer 3,
# "Database changes"; ADR-0011) [design]. Not a SQL parser: a heuristic that sorts each
# statement of a pending migration or data-fix file into a kind. classify.py decides which
# kinds are risky; anything it cannot read safely (function bodies, DO blocks, EXECUTE) gets
# the kind `dynamic_sql`, which stops the deploy (fail closed).
#
# Input, written by the deploy step that lists pending files (how it finds them depends on
# Papaya's migration tool, not known here):
#   {"files": [{"path": "db/migrations/20261109_add_col.sql", "kind": "migration",
#               "sql": "<file content>"}]}
#   kind: migration | data-fix | metadata
#   `metadata` = a GraphQL-engine metadata file (Hasura: permissions per role, i.e. access and
#   tenant isolation). It is not parsed: every change gets the kind `metadata`, which stops.

_SQL_KINDS = [
    # (kind, pattern on one statement after comments, strings and nested parentheses are gone)
    ("privilege", r"^(GRANT|REVOKE)\b|^(CREATE|ALTER|DROP)\s+(ROLE|USER|GROUP|POLICY)\b"
                  r"|^ALTER\s+DEFAULT\s+PRIVILEGES\b|\bSECURITY\s+DEFINER\b|\bOWNER\s+TO\b"),
    ("row_security", r"^ALTER\s+TABLE\b.*\b(ENABLE|DISABLE|FORCE|NO\s+FORCE)\s+ROW\s+LEVEL\s+SECURITY\b"),
    ("truncate", r"^TRUNCATE\b"),
    ("drop_column", r"^ALTER\s+TABLE\b.*\bDROP\s+(COLUMN\b|CONSTRAINT\b|(IF\s+EXISTS\s+)?\w)"),
    ("alter_column_type", r"^ALTER\s+TABLE\b.*\bALTER\s+(COLUMN\s+)?\S+\s+(SET\s+DATA\s+)?TYPE\b"),
    ("drop", r"^DROP\b"),
    ("copy", r"^COPY\b"),
    ("dynamic_sql", r"^(DO|EXECUTE)\b|^CALL\b"),
    ("delete", r"^(WITH\b.*?)?\bDELETE\s+FROM\b"),
    ("update", r"^(WITH\b.*?)?\bUPDATE\s+\S+\s+(AS\s+\S+\s+)?SET\b"),
    ("insert", r"^(WITH\b.*?)?\bINSERT\s+INTO\b"),
    ("alter", r"^ALTER\b"),
    ("create", r"^CREATE\b"),
]


_DML = {"insert", "update_scoped", "update_unscoped", "delete_scoped", "delete_unscoped"}


def _sql_statements(text):
    """Split SQL into upper-case statements without comments, string literals or bodies.

    Returns (statements, has_body): has_body is True if a dollar-quoted body ($$ or $tag$)
    was found; its content cannot be classified."""
    has_body = bool(re.search(r"\$\w*\$", text))
    text = re.sub(r"\$(\w*)\$.*?\$\1\$", " $BODY$ ", text, flags=re.S)  # function / DO bodies
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)                  # block comments
    text = re.sub(r"--[^\n]*", " ", text)                               # line comments
    text = re.sub(r"'(?:[^']|'')*'", "''", text)                        # string literals
    text = re.sub(r'"(?:[^"]|"")*"', "ident", text)                     # quoted identifiers
    out = []
    for stmt in text.split(";"):
        s = " ".join(stmt.split()).upper()
        if s:
            out.append(s)
    return out, has_body


def _top_level(stmt):
    """Remove everything inside parentheses, so a WHERE in a subquery is not mistaken for the
    statement's own WHERE."""
    prev = None
    while prev != stmt:
        prev, stmt = stmt, re.sub(r"\([^()]*\)", "()", stmt)
    return stmt


def sql_kinds(text):
    """Sorted kinds found in one SQL file, e.g. ["create", "delete_unscoped"]."""
    statements, has_body = _sql_statements(text)
    kinds = set()
    if has_body:
        kinds.add("dynamic_sql")
    for s in statements:
        top = _top_level(s)
        for kind, pattern in _SQL_KINDS:
            if re.search(pattern, top):
                if kind in ("delete", "update"):
                    # Scoped only if the statement itself (not a subquery) has a WHERE.
                    verb = "DELETE" if kind == "delete" else "UPDATE"
                    tail = top[top.find(verb):]
                    kind += "_scoped" if re.search(r"\bWHERE\b", tail) else "_unscoped"
                kinds.add(kind)
                break
        else:
            kinds.add("other")
    return sorted(kinds)


def sql(raw):
    changes = []
    for f in raw["files"]:
        if f["kind"] not in ("migration", "data-fix", "metadata"):
            raise ValueError(f"unknown SQL file kind '{f['kind']}'")
        kinds = ["metadata"] if f["kind"] == "metadata" else sql_kinds(f["sql"])
        if f["kind"] == "migration" and set(kinds) & _DML:
            # Data changes belong in data-fixes/<tenant>/, where the data owner approves (R4). In a
            # migration they would skip the data owner, the one-tenant scope and expected_rows.
            kinds = sorted(set(kinds) | {"dml_in_migration"})
        changes.append({
            "type": f"sql:{f['kind']}",
            "name": f["path"],
            "op": "update",
            "changed_keys": kinds,  # statement kinds only, never SQL text
            "detail_digest": _digest(f["path"], f["sql"]),  # the approval covers this exact SQL
        })
    return {"changes": changes}


def normalized(raw):
    for c in raw["changes"]:
        for key in ("type", "name", "op"):
            if not isinstance(c.get(key), str):
                raise ValueError(f"change without '{key}'")
    return raw


ADAPTERS = {"pulumi": pulumi, "serverless": serverless, "sql": sql, "normalized": normalized}
