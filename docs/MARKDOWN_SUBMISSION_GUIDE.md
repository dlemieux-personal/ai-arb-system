# How to Submit Architecture Reviews

This system now accepts both **JSON** and **Markdown** formats for architecture submissions.

## Quick Start

### Choose Your Format

#### Option 1: Markdown (Recommended for humans)
```markdown
---
submission_id: ACME-2024-001ABC
team_name: "Your Team Name"
submission_date: 2024-02-28
system_title: "Your Architecture Title"
---

# Architecture Submission

## 2. Security Architecture
### 2.1 Authentication & Authorization
- OAuth 2.0 implementation
- RBAC with service mesh

### 2.2 Data Protection
- Encryption in Transit: - [x] Enabled
- Encryption at Rest: - [x] Enabled
```

#### Option 2: JSON (Recommended for automation)
```json
{
  "submission_id": "JSON-0001-ABC123",
  "team_name": "Your Team",
  "submission_date": "2024-02-28T10:00:00Z",
  "system_overview": {
    "title": "Your Architecture",
    "description": "Description here..."
  },
  "sections": {
    "security": { ... }
  }
}
```

## Markdown Format Details

### Frontmatter (YAML)
Required fields in the YAML header:
- `submission_id` - Format: `CODE-YYYY-XXXXXX` (e.g., ACME-2024-ABC123)
- `team_name` - Your team or organization name
- `submission_date` - Flexible date format (see below)
- `system_title` - Clear title of your architecture

### Date Format Options
All these formats work:
- ISO format: `2024-02-28T14:30:00Z`
- Date only: `2024-02-28`
- Natural language: `Feb 28, 2024`
- US format: `02-28-2024`

### Boolean Fields
Three ways to indicate true/false:

```markdown
- Explicit keywords: true/false, yes/no
- [x] Checkboxes (checked = true): - [x] Enabled
- [ ] Checkboxes (unchecked = false): - [ ] Disabled
```

### Arrays (Lists)
Use bullet points:

```markdown
### Example
- First item
- Second item
- Third item

### Or with details
**Required Frameworks:**
- OAuth 2.0
- Service Mesh (Istio)
- GraphQL Federation
```

### Risk Items
Use this format:
```markdown
## 10. Risk Assessment

### 10.1 Technical Risks
- **Complex Kubernetes setup** (Severity: high, Mitigation: Provide training and documentation)
- **Data consistency** (Severity: medium, Mitigation: Implement event sourcing)
```

## Sections Supported

The parser automatically detects and extracts:

| Section | Keywords | Required? |
|---------|----------|-----------|
| Security | `security`, `encryption` | No |
| Scalability | `scalability`, `performance` | No |
| Reliability | `reliability`, `resilience` | No |
| Data Architecture | `data`, `architecture` | No |
| Cost | `cost`, `pricing` | No |
| Compliance | `compliance`, `governance` | No |
| Risks | `risk`, `threats` | No |

**Note:** Sections are optional—submit only what's relevant to your architecture.

## Validation Rules

### What Must Be Present
- Valid YAML frontmatter with all 4 required fields
- Proper Markdown syntax (valid heading levels, etc.)

### What's Invalid
- ✗ Unclosed frontmatter delimiters
- ✗ Missing required frontmatter fields
- ✗ Invalid date formats
- ✗ Boolean fields with unrecognized values (use only: true/false/yes/no/checkboxes)
- ✗ Enum fields with invalid values (but case-insensitive matching works)

### What Gets Ignored
- Unknown section headings (forward-compatible)
- Extra metadata fields in frontmatter (only required 4 are mandatory)

## Enums (Case-Insensitive)

These values are case-insensitive:

```markdown
Severity: HIGH, high, High (all equivalent)
Redundancy: NONE, none, None (all equivalent)
Consistency: STRONG, strong, Eventual, eventual (all equivalent)
```

## Examples

See `submissions/incoming/example-markdown-submission.md` for a complete, realistic example with:
- All security fields
- Performance targets
- Risk assessment
- Compliance requirements
- Operational considerations

## Troubleshooting

**"Missing required frontmatter fields"**
- Ensure all 4 fields are present: submission_id, team_name, submission_date, system_title
- Check YAML syntax (colons, quotes, indentation)

**"Invalid boolean value"**
- Use: true, false, yes, no, or checkboxes (- [x] or - [ ])
- Not: 1, 0, enabled, disabled, T, F

**"Invalid enum value"**
- Check the valid options for that field (see schema or error message)
- Enums are case-insensitive but spelling must match

## Next Steps

1. Copy `templates/architecture_submission_template.md`
2. Fill in your frontmatter
3. Write your architecture description
4. Submit to `submissions/incoming/` directory
