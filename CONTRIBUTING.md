# Contributing to MicroLLM-PrivateStack

Thank you for contributing! To maintain a high-quality codebase, please follow these guidelines.

## 🌿 Branching Model
We use a **Git Flow** strategy.
- Always branch new features from `develop`.
- Name your branch `feature/short-description`.
- Ensure all tests pass before opening a Pull Request.

See [BRANCHING.md](docs/BRANCHING.md) for a detailed visual guide.

## 📝 Commit Message Convention
We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` for new features.
- `fix:` for bug fixes.
- `docs:` for documentation changes.
- `style:` for formatting/UI changes.
- `refactor:` for code changes that neither fix a bug nor add a feature.
- `perf:` for performance improvements.
- `test:` for adding or correcting tests.
- `chore:` for maintenance tasks.

*Example: `feat: add hybrid search mechanism`*

## 🧪 Pull Request Process
1. Update documentations if you add new features.
2. Ensure `pytest` passes locally.
3. PRs to `develop` require at least one approval.
4. Squash and merge is preferred for feature branches.

## 🚀 Release Process
Releases are triggered by tagging `main` with a version tag (e.g., `v1.1.0`). This will automatically trigger the GitHub Release workflow.
