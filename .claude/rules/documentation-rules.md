# Documentation Rules

## Obsidian Vault Convention
This project is an Obsidian vault. All markdown files use `[[wikilinks]]` for cross-referencing.

## After EVERY Session, Update:

| Condition | File to Update |
|-----------|---------------|
| New/modified DB models | `Docs/DATABASE_SCHEMA.md` |
| New/modified API endpoints | `Docs/API_ENDPOINTS.md` |
| New/modified web pages | `Docs/FRONTEND_PAGES.md` |
| New/modified mobile screens | `Docs/MOBILE_PAGES.md` |
| New offline capabilities | `Docs/LOCAL_MOBILE_FUNCTIONALITY.md` |
| Architecture decisions | `Docs/ARCHITECTURE.md` + `Docs/knowledge/ADR-NNN.md` |
| Always | `Docs/PROGRESS.md` (mark session status) |
| Always | `Docs/CHANGELOG.md` (add entry) |

## Format Rules
- Use `[[wikilinks]]` for cross-referencing between docs
- Mark temporary implementations with `<!-- TODO: ... -->`
- Keep descriptions concise, link to source files
- New ADRs go in `Docs/knowledge/` following `ADR-template.md`
- Update `Docs/INDEX.md` when adding new documentation pages
