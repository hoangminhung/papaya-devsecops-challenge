"""Find keys in a JSON document that its schema does not define, by path.

A JSON Schema without `additionalProperties: false` accepts any extra key, so a
misspelled key (e.g. `require_last_pusher_approval`) passes validation. This helper
walks the document next to the schema and reports every key that is not in the
`properties` of the schema node at that position.

For `oneOf` / `anyOf` it uses the first branch the value validates against, which
for GitHub rule objects is the branch whose `type` enum matches.
"""
import jsonschema


def _branch(value, schema):
    for key in ("oneOf", "anyOf"):
        if key in schema:
            for sub in schema[key]:
                if jsonschema.Draft7Validator(sub).is_valid(value):
                    return _branch(value, sub)
    return schema


def unknown_keys(value, schema, path="$", allow=()):
    """Return a list of JSON paths whose key is not defined by the schema.

    `allow` lists extra paths (e.g. "$.permissions.defaultMode") known from
    documentation but missing from the schema; each one must be cited by the caller.
    """
    found = []
    schema = _branch(value, schema)
    if isinstance(value, dict):
        props = schema.get("properties")
        extra = schema.get("additionalProperties")
        for k, v in value.items():
            p = f"{path}.{k}"
            if props is not None and k in props:
                found += unknown_keys(v, props[k], p, allow)
            elif p in allow:
                continue
            elif isinstance(extra, dict):
                found += unknown_keys(v, extra, p, allow)
            else:
                found.append(p)
    elif isinstance(value, list) and isinstance(schema.get("items"), dict):
        for i, v in enumerate(value):
            found += unknown_keys(v, schema["items"], f"{path}[{i}]", allow)
    return found
