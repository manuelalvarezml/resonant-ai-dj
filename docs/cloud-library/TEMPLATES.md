# Planning record templates

These are reusable record formats. They are not observations or approvals. Replace placeholders with actual evidence and omit inapplicable fields with an explicit reason.

## Decision / ADR

```text
ID:
Date:
Title:
Status: proposed
Problem / trigger:
Scope and authorization reference:
Alternatives considered:
Decision criteria:
Evidence IDs and limitations:
Recommendation / decision:
Why each alternative was rejected:
Consequences and tradeoffs:
Affected contracts/tasks/gates:
Owner / approver:
Reopen condition:
Supersedes:
```

## Steer

```json
{
  "event_id": "new-CE-id",
  "date": "YYYY-MM-DD",
  "type": "steer",
  "source": "exact user instruction or decision reference",
  "target_ids": [],
  "previous_state": "",
  "new_state": "",
  "reason": "",
  "evidence_refs": [],
  "authorization_change": "none unless explicitly granted",
  "supersedes_event": null
}
```

## Experiment

```text
ID / title:
Hypothesis:
Gate / task:
Authorization reference:
Owner:
Protocol and version fixed before test:
Sample, recruitment or fixture license:
Provider / region / runtime / tool/model hashes:
Maximum bytes / jobs / runtime / spend:
Stop conditions:
Expected observation and pass threshold:
Actual start/end:
Actual sample and exclusions:
Observed result (including negative results):
Raw evidence / manifest / invoice references:
Cost and resource measurements:
Threats to validity:
Conclusion: supported / unsupported / inconclusive
Failures and root-cause confidence:
Next action / cleanup:
```

## Failure / incident / unviable route

```text
ID / date:
Kind: research_access / source_conflict / experiment_failure / product_incident
Related task / experiment / decision:
What was attempted:
Expected:
Observed:
Impact and affected scope:
Reproduction evidence:
Cause: confirmed or hypothesis
Mitigation / containment:
Why this route is unviable under current constraints:
Alternatives:
Owner and next action:
Resolution verification:
Reopen condition:
Status:
```

## Implementation task brief

```text
Task ID / title:
Explicit authorization:
Parent milestone / dependencies:
Goal and supported user journey:
Current code/contracts to read:
Required behavior and invariants:
Out of scope / preserved boundaries:
Files owned / independent components:
Fixtures and resource/spend limits:
Acceptance tests and expected evidence:
Failure cases / rollback:
Logs and registers to update:
Definition of done:
```

## Gate review

```text
Gate ID / release scope:
Threshold version fixed before evidence:
Observed sample and result:
Evidence artifacts and source freshness:
Unresolved risks / exceptions:
Reviewer / authority:
Outcome: not_passed / passed / failed / waived_for_scoped_release
Reason:
Permitted next action:
Capabilities still unauthorized:
Next review trigger:
```

## Source record

```json
{
  "id": "new-S-id",
  "publisher": "",
  "title": "",
  "url": "",
  "published_or_updated": null,
  "accessed": "YYYY-MM-DD",
  "type": "primary",
  "claim": "",
  "confidence": "documented",
  "limitations": "",
  "supersedes_observation": null,
  "affected_ids": [],
  "refresh_before": ""
}
```

## Handoff

```text
As of / revision:
Current recommendation:
Authorized work:
Completed artifacts and checks:
Empirical evidence collected:
Highest-impact unresolved questions:
Open failures and rejected paths:
Next independent task:
Next dependent task and missing approval/evidence:
Preserved local engine / playlist boundaries:
Files to update at completion:
```
