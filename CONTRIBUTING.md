# Contributing

Thank you for considering contributing. This document explains how to report issues, propose changes, and submit code so maintainers can review and merge work efficiently.

## Table of contents
- Reporting issues
- Requesting features
- Submitting changes (PRs)
- Branching & commit guidelines
- Tests & CI
- Code style & linting
- Documentation
- Security
- Code of Conduct

## Reporting issues
- Search existing issues before opening a new one.
- Create a clear title and description describing:
    - Expected behavior
    - Actual behavior
    - Steps to reproduce
    - Environment (OS, runtime, versions)
- Provide logs, screenshots, or minimal reproducible examples when possible.

## Requesting features
- Explain the problem and why the feature is needed.
- Describe alternatives considered and proposed API or UX.
- Link related issues or external references.

## Submitting changes (Pull Requests)
1. Fork the repository and create a branch:  
     git checkout -b feat/short-description
2. Make small, focused commits with descriptive messages.
3. Rebase or merge the latest main before opening a PR.
4. Push your branch and open a PR against the main branch with:
     - Purpose of the change
     - What was changed
     - How to test
     - Any migration notes
5. Address review feedback and squash commits when requested.

Suggested PR checklist:
- [ ] Follows the coding style
- [ ] Includes/updated tests
- [ ] Documentation updated if applicable
- [ ] All CI checks pass

## Branching & commit guidelines
- Branch names: type/short-description (e.g., fix/login-bug, feat/add-logger)
- Commit messages: short summary on the first line, optional body with motivation and details.
- Consider Conventional Commits for automation (e.g., feat:, fix:, docs:).

## Tests & Continuous Integration
- Use the existing `pytest` framework.
- Run the test suite locally before submitting.
- Add tests for new features and bug fixes.
- Ensure linters and formatters run and pass.
- Fix CI failures promptly.

CI is run on GitHub for all contributions to main and pushes to any branch.

## Code style & linting
- Follow existing project style and patterns.
- Use numpydoc style docstrings for all user facing functions.
- Run automatic formatter `gruff` as configured.
- Keep changes minimal and consistent.

## Documentation
- Update README, docs, and inline comments when behavior or APIs change.
- Include examples for public APIs and configuration.

## Security
- Do not disclose security vulnerabilities in public issues. Report them privately to the maintainers or to the security contact listed in the repository.
- If a security contact is not listed, use the repository's support channel or the platform's private reporting mechanism.

## Code of Conduct
- Be respectful and collaborative.

## Maintainer process
- Maintainers review PRs and may request changes or tests.
- Large or breaking changes may require design discussion before implementation.
- Merges are at the maintainers’ discretion.

Thank you for contributing — small improvements help the project a lot.