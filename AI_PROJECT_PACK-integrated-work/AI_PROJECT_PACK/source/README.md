# Portable AI Development Pack

Copy AGENTS.md, USER.md, PROJECT_STATUS.md, SECURITY.md, CONTRIBUTING.md, README.md, .gitignore, .claude/settings.json, .claude/mcp.json, and .antigravity/ralph.sh to a new project.

Then fill PROJECT_STATUS with verified values, set WORKSPACE to the new project root, disable unused MCP servers, run a secret scan, and validate JSON and shell syntax.

The default policy is safe: local reversible work may proceed; external, paid, public, production, destructive, and irreversible actions require confirmation.

Checks:
jq empty .claude/settings.json
bash -n .antigravity/ralph.sh
git diff --check
