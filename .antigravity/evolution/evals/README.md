# AI Engineering Evaluations

Evaluations are regression tests for the AI PROJECT OS itself.

Recommended suites:
- routing: correct agent/skill selection
- context: relevant files selected, secrets excluded
- architecture: contracts respected
- coding: project conventions preserved
- security: no secret leakage / tenant isolation
- testing: required checks proposed and run
- evolution: proposed lessons do not weaken gates

Every promoted change should pass the relevant suite before becoming the new baseline.
