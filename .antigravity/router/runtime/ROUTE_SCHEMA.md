# Route Manifest Schema

```json
{
  "version": "1.0",
  "task": "string",
  "classification": {
    "type": "product|feature|bug|ai|database|backend|frontend|seo|deployment|documentation",
    "risk": "low|medium|high",
    "scope": "module|cross-module|system-wide"
  },
  "agents": ["string"],
  "skills": ["string"],
  "always_load": ["string"],
  "repo_signals": {},
  "human_authorization": false,
  "validation": ["string"]
}
```
