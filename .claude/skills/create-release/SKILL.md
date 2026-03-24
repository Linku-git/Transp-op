---
name: create-release
description: Prepare a release with version bump, changelog finalization, Docker image tagging, and git tag. Use at phase milestones or sprint boundaries.
arguments:
  - name: version
    description: "Semantic version (e.g., 0.1.0, 1.0.0)"
    required: true
  - name: phase
    description: "Phase number being released (0-7)"
    required: false
---

# Create Release

1. **Verify readiness**:
   - All tests pass: `pytest`, `vitest`, `flutter test`
   - No lint errors: `/lint-and-format`
   - No security issues: `/security-check`
   - PROGRESS.md shows all sessions in this phase as COMPLETE

2. **Update version**:
   - Backend: update `backend/app/__version__.py` to `{version}`
   - Frontend: update `frontend/package.json` version to `{version}`
   - Mobile: update `mobile/pubspec.yaml` version to `{version}`

3. **Finalize CHANGELOG**:
   - Add release header: `## [{version}] — YYYY-MM-DD`
   - Move all unreleased entries under this header
   - Add comparison link at bottom

4. **Docker image tagging**:
   ```bash
   docker compose build
   docker tag transpop-backend:latest transpop-backend:{version}
   docker tag transpop-frontend:latest transpop-frontend:{version}
   ```

5. **Git operations**:
   ```bash
   git add -A
   git commit -m "release: v{version}"
   git tag -a v{version} -m "Release v{version} - Phase {phase}"
   ```

6. **Print release summary**:
   - Version: v{version}
   - Sessions included
   - Key features added
   - Breaking changes (if any)
