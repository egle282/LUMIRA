# Autonomy Policy

| Risk | Default execution |
|---|---|
| low | auto |
| medium | auto + review |
| high | approval required |
| critical | human required |

Critical/high examples include production, payments, auth/RLS, tenant isolation,
secrets, destructive DB changes and deployment.

The system may plan, retrieve context, test, review and propose improvements.
It must not silently weaken gates or governing rules.
