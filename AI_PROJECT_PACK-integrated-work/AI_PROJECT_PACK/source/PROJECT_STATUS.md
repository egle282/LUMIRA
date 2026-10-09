# PROJECT_STATUS.md - universal workspace status

> Fill only verified values. Never store secrets here. This file is the source of truth for the current project, not a historical plan.

## 1. Portable pack

| File or directory | Purpose | Present |
|---|---|---|
| AGENTS.md | Canonical AI-agent rules and safety boundaries | yes/no |
| USER.md | User profile and collaboration preferences | yes/no |
| SECURITY.md | Security baseline, CI/CD and incident response | yes/no |
| CONTRIBUTING.md | Change and PR workflow | yes/no |
| .pre-commit-config.yaml | Local quality and security hooks | yes/no |
| .claude/settings.json | Least-privilege local permissions | yes/no |
| .claude/mcp.json | Explicit external tool configuration | yes/no |
| .antigravity/ralph.sh | Bounded local AI loop | yes/no |
| .gitignore | Secret and artifact exclusions | yes/no |

## 2. Project identity

| Field | Value |
|---|---|
| Name | TODO |
| Purpose | TODO |
| Owner | TODO |
| Stage | planning / development / staging / production |
| L| L| L| L| L| L| L| L| L| L| L| L| L| L| L| L|# 3. Actual stack

| Layer | Technology and version |
|---|---|
| Language | TODO |
| Frontend | TODO / N/A |
| Backend/API | TODO / N/A |
| Database | TODO / N/A |
| Queue/cache | TODO / N/A |
| External| External|O / N/A |
| Payments | TODO / N/A |
| CI/CD | TODO |
| Runtime/deployment | TODO |
| Monitoring | TODO |

## 4. Verified commands

```text
InInInInInInInInInInInInInInInInInInInInInInInInInIe check: TODO
Unit tests: TODO
Integration tests: TODO
Build: TODO
Dependency scan: TODO
Secret scan: pre-commit run --all-files
Security scan: TODO
```

## 5. Environments and access

| Environment | URL | Credential source | Deployment approval | Rollback |
|---|---|---|---|---|
| Local | TODO | local secret manager | no | TODO |
| Development | TODO | TODO | TODO | TODO |
| Staging | TODO | TODO | yes/| Staging | TODO | ction | TODO | secret manager/OIDC | required | TODO |

## 6. Quality gates

- [ ] `pre-commit install` completed.
- [ ] `pre-commit run --all-files` passes.
- [ ] CI repeats secret, SAST, dependency and configuration checks.
- [ ] Production sec- [ ] Pe unavailable to forks and untrusted pipelines.
- [ ] Deployment has review, approval, monitoring and rollback.

## 7. Critical scenarios

- Main user flow: TODO
- - - - - - - - - - authorization failure: TODO
- External service timeout or outage: TODO
- Duplicate webhook or payment: TODO
- Migration and rollback: TODO
- Secret compromise response: TODO

## 8. Known limitations and decisions

- TODO

## 9. Change log

| Date | Change | Evidence | Reviewer |
|---|---|---|---|
| TODO | TODO | TODO | TODO |
