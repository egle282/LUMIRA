# Architecture Drift Policy

Drift means the implemented system diverges from declared architecture/contracts.

Detection layers:
1. static markers and dependency boundaries
2. API/schema contract checks
3. database migration/schema checks
4. test-derived invariants
5. periodic architecture review

Do not silently rewrite architecture documentation to match code.
First report drift, identify evidence, decide whether code or architecture is authoritative, then update deliberately.
