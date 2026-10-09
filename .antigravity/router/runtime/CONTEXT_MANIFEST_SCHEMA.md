# Context Manifest Schema
The manifest is the handoff contract between Director/Router and downstream agents.

Required: `schema_version`, `task`, `project_root`, `selection`, `context[]`, `skipped`, `counts`, `safety`.

Each `context[]` item: `path`, `score`, `size_bytes`, `reasons[]`, `sha256`.

Safety: secrets, binaries, generated/dependency/cache directories and oversized files are excluded. The loader is read-only.
