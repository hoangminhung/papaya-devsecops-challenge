#!/usr/bin/env python3
"""Extract request-body schemas from GitHub's REST OpenAPI description.

Usage:
  python3 extract_github_schemas.py <api.github.com.json> <spec-commit-sha> <out-dir>

The spec is github/rest-api-description, descriptions/api.github.com/api.github.com.json.
It is OpenAPI 3.0: schemas use `nullable` and `$ref`. This script resolves every
`$ref` inline and turns `nullable: true` into a JSON Schema type union with "null",
so Python `jsonschema` (Draft 7) can use the result offline.

The extracted schemas do NOT set `additionalProperties: false` where GitHub does not,
so a schema check alone does not catch misspelled keys. See tests/schema_keys.py.
"""
import copy
import json
import sys

BODIES = {
    "github-ruleset-create.json": ("/repos/{owner}/{repo}/rulesets", "post"),
    "github-environment-put.json": ("/repos/{owner}/{repo}/environments/{environment_name}", "put"),
    "github-deployment-branch-policy-post.json": (
        "/repos/{owner}/{repo}/environments/{environment_name}/deployment-branch-policies",
        "post",
    ),
}


def resolve(node, spec, depth=0):
    if depth > 40:
        raise RecursionError("schema nesting too deep; recursive $ref?")
    if isinstance(node, list):
        return [resolve(x, spec, depth + 1) for x in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        path = node["$ref"].lstrip("#/").split("/")
        target = spec
        for part in path:
            target = target[part]
        merged = copy.deepcopy(target)
        merged.update({k: v for k, v in node.items() if k != "$ref"})
        return resolve(merged, spec, depth + 1)
    out = {k: resolve(v, spec, depth + 1) for k, v in node.items()}
    if out.pop("nullable", False):
        t = out.get("type")
        if isinstance(t, str):
            out["type"] = [t, "null"]
        elif t is None and "enum" not in out:
            out = {"anyOf": [out, {"type": "null"}]}
        if "enum" in out and None not in out["enum"]:
            out["enum"] = out["enum"] + [None]
    # OpenAPI-only keywords that Draft 7 does not know are harmless; drop the noisy ones.
    for k in ("example", "examples", "x-github"):
        out.pop(k, None)
    return out


def main():
    spec_path, sha, out_dir = sys.argv[1:4]
    with open(spec_path) as f:
        spec = json.load(f)
    for name, (path, method) in BODIES.items():
        body = spec["paths"][path][method]["requestBody"]["content"]["application/json"]["schema"]
        schema = resolve(body, spec)
        schema["$schema"] = "http://json-schema.org/draft-07/schema#"
        schema["$comment"] = (
            f"Extracted from github/rest-api-description@{sha} "
            f"(OpenAPI {spec['openapi']}, API {spec['info']['version']}), "
            f"{method.upper()} {path}, by examples/tools/extract_github_schemas.py"
        )
        with open(f"{out_dir}/{name}", "w") as f:
            json.dump(schema, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote {out_dir}/{name}")


if __name__ == "__main__":
    main()
