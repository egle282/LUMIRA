---
trigger: glob
globs:
  - "**/api/**"
  - "**/server/**"
  - "**/backend/**"
description: Backend boundary and reliability constraints.
---
- Authenticate and authorize protected operations.
- Validate all external input.
- Use parameterized data access.
- Return stable errors without leaking secrets.
- Enforce tenant boundaries server-side.
- Test critical business rules.
