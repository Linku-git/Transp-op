---
name: generate-adr
description: Create a new Architecture Decision Record (ADR) in Docs/knowledge/. Use when making significant architecture or technology decisions.
arguments:
  - name: title
    description: Short title for the ADR (e.g., "use-redis-for-caching")
    required: true
---

# Generate ADR

1. Find the next ADR number by listing existing ADRs:
   ```bash
   ls Docs/knowledge/ADR-*.md 2>/dev/null | sort | tail -1
   ```
2. Increment the number (start at 001 if none exist)
3. Create `Docs/knowledge/ADR-{NNN}-{title}.md` using the template:

```markdown
# ADR-{NNN}: {Title}

## Status
Proposed

## Context
[Describe the issue or need motivating this decision]

## Decision
[Describe the chosen approach and why]

## Consequences
### Positive
- [What becomes easier]

### Negative
- [What becomes harder or what trade-offs exist]

## Related
- [[ARCHITECTURE]]
- [[sessions/session-XX]]
```

4. Update `Docs/INDEX.md` — add the new ADR to the Architecture Decisions section
5. Print the file path and ADR number for reference
