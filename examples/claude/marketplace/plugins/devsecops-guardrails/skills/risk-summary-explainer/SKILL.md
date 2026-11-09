---
name: risk-summary-explainer
description: Use when an approver asks what a stopped deploy will change. Explains a risk-stop summary in plain words for the approval pull request; never approves.
---

# Explain a risk-stop summary

The deploy job stopped and posted a filtered summary: resource type, name, operation and changed
property names, never values (framework layer 3, examples E7).

1. Read the summary and the merged pull request that caused it. Read the IaC for the named
   resources in the repository.
2. Explain, for each stopped item: what the operation does to the running system (replace means
   delete and create; a delete of a stateful resource loses data unless a backup or retention
   exists), which tenants or services depend on it, and whether it can be undone.
3. Point out anything the summary does not show: properties hidden as values, SDK calls the program
   makes while it runs, and drift since the last preview.
4. Write the explanation as a comment for the approver on the approval pull request
   (`deploy-approvals/<stack>/`). Do not approve or request changes; the decision is the
   approver's (OD5).
