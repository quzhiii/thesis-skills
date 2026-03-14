# Word Formatter Plan Schema (v1)

Defines minimum JSON contracts for lint findings and executable fix plans.

## 1) report.json

```json
{
  "doc_id": "thesis.docx",
  "ruleset": "thu_v1",
  "generated_at": "2026-03-03T12:00:00Z",
  "issues": [
    {
      "issue_id": "ISSUE-0001",
      "type": "pseudo_heading",
      "severity": "error",
      "location": {
        "paragraph_index": 25,
        "bookmark": null
      },
      "evidence": "1.2 研究背景",
      "suggested_action": {
        "action_type": "CONVERT_PSEUDO_HEADING",
        "params": {
          "level": 2,
          "style_name": "Heading 2"
        }
      }
    }
  ]
}
```

### Required fields
- `doc_id`, `ruleset`, `generated_at`, `issues`
- each issue: `issue_id`, `type`, `severity`, `location`, `evidence`, `suggested_action`

### Severity
- `info` | `warning` | `error`

## 2) fix_plan.json

```json
{
  "plan_id": "PLAN-20260303-001",
  "doc_id": "thesis.docx",
  "ruleset": "thu_v1",
  "generated_at": "2026-03-03T12:01:00Z",
  "actions": [
    {
      "action_id": "ACT-0001",
      "action_type": "CONVERT_PSEUDO_HEADING",
      "target": {
        "paragraph_index": 25,
        "bookmark": null
      },
      "params": {
        "level": 2,
        "style_name": "Heading 2"
      },
      "preconditions": [
        "paragraph exists",
        "text matches heading pattern"
      ],
      "rollback_hint": "set style back to previous style name"
    }
  ]
}
```

### Required fields
- `plan_id`, `doc_id`, `ruleset`, `generated_at`, `actions`
- each action: `action_id`, `action_type`, `target`, `params`, `preconditions`, `rollback_hint`

## 3) Validation Rules
- `action_type` must be in `actions_spec.md` whitelist.
- Unknown fields are allowed but ignored by v1 executor.
- Executor must reject plans with unknown action types.
