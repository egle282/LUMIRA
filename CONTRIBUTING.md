# Contributing to LUMIRA

First off, thank you for considering contributing to LUMIRA! We welcome contributions from everyone.

## Code of Conduct
By participating in this project, you are expected to uphold a welcoming and respectful environment.

## How Can I Contribute?

### Reporting Bugs
- Ensure the bug was not already reported by searching on GitHub under Issues.
- If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.

### Suggesting Enhancements
- Open a new issue with a clear title and description of the requested feature.
- Explain why this enhancement would be useful to most users.

### Pull Requests
1. Fork the repo and create your branch from `master`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Setup for Development
1. Clone the repository.
2. Create `.env` based on `.env.example`.
3. Install frontend dependencies: `cd frontend && npm install`
4. Install backend dependencies: `cd backend && pip install -r requirements.txt`

## Architecture Notes
- The Astrology Engine (Swiss Ephemeris) is the strict source of truth for all calculations.
- LLMs are used for interpretation only, never calculation.
- Read `.antigravity/` directories to understand the AI-Agent orchestration logic.

Thank you!
