---
trigger: always_on
description: Security baseline.
---
- Never commit secrets.
- Never trust client-side authorization.
- Validate untrusted inputs.
- Treat uploads, URLs, webhooks and model output as untrusted.
- Critical security findings block release.
