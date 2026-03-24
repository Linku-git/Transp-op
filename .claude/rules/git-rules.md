# Git Rules

## Branch Naming
- `feature/session-XX-short-description`
- `fix/session-XX-issue-description`
- `refactor/session-XX-what-changed`

## Commit Format
`[Session-XX] <type>: <short description>`
Types: feat, fix, refactor, test, docs, chore

## Workflow
- Each session = one branch = one PR
- All tests must pass before merge
- Update documentation before merge
- Small, focused commits (one logical change each)
- Never commit: `.env`, `__pycache__/`, `node_modules/`, `.dart_tool/`, `build/`

## Initial Setup
Run `git init` in project root during Session 01.
Create `.gitignore` covering Python, Node, Flutter, IDE files, and secrets.
