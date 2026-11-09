## What and why

<!-- One or two sentences. Link the Linear issue; for an incident, the open incident issue and the
     `incident` label (the on-call approval counts only then, OD27). -->

## How it was made

- [ ] Written with an agent (say which parts) <!-- the reviewer reads agent-written code as a
      stranger's code: check what it calls, not only what it changes -->
- [ ] Written by hand

## Prod impact

- Stacks / services: <!-- names -->
- Non-prod preview: <!-- link to the PR check; summary of creates, updates, replaces, deletes -->
- Risky operations expected (replace or delete of stateful resources, IAM, network, SQL that
  drops, alters types or changes data): <!-- none / list; the risk stop will stop on them -->
- Data: <!-- no customer data touched / data fix for tenant X with expected_rows N -->

## Tested

<!-- What ran (tests, preview) and what did not. -->

## Rollback

<!-- Revert PR, or the steps if a revert is not enough (data, migrations). -->
