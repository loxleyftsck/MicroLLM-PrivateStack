# Git Branching Strategy

## Branch Structure

```
main (production)
  ↓
dev (development)
  ↓
testing (QA/staging)
```

## Branch Purpose

### `main` - Production
- **Purpose:** Stable, deployable code
- **Protection:** Requires PR approval
- **Deploy:** Auto-deploy to production (future)
- **Updates:** Only from `dev` via PR

### `dev` - Development
- **Purpose:** Active development, Sprint work
- **Protection:** Optional review
- **Testing:** Local + CI tests
- **Updates:** Feature branches merge here

### `testing` - QA/Staging
- **Purpose:** Pre-production testing
- **Protection:** Requires passing tests
- **Deploy:** Staging environment
- **Updates:** From `dev` when ready for QA

## Workflow

### For New Features (Sprint 2+)

```bash
# 1. Start from dev
git checkout dev
git pull origin dev

# 2. Create feature branch
git checkout -b feature/auth-jwt

# 3. Work on feature
git add .
git commit -m "feat: implement JWT authentication"

# 4. Push feature
git push origin feature/auth-jwt

# 5. Create PR to dev
# (via GitHub UI)

# 6. After merge, delete feature branch
git branch -d feature/auth-jwt
```

### For Testing/QA

```bash
# When dev is stable, merge to testing
git checkout testing
git merge dev
git push origin testing

# Test on staging environment
# If OK, proceed to main
```

### For Production Release

```bash
# When testing passes, merge to main
git checkout main
git merge testing
git push origin main
git tag -a v1.0.0 -m "Sprint 1 release"
git push --tags
```

## Branch Naming Convention

### Feature Branches
- `feature/short-description` - New features
- `fix/bug-description` - Bug fixes
- `docs/what-changed` - Documentation
- `refactor/what-refactored` - Code refactoring

### Examples
```
feature/jwt-auth
feature/rag-module
fix/import-error
fix/cors-issue
docs/api-guide
refactor/llm-engine
```

## Current Status

```bash
✅ main    - Sprint 1 complete
✅ dev     - Created, ready for Sprint 2
✅ testing - Created, ready for QA
```

## Quick Commands

```bash
# Switch branches
git checkout main       # Production
git checkout dev        # Development  
git checkout testing    # QA

# Check current branch
git branch

# See all branches (local + remote)
git branch -a

# Pull latest changes
git pull origin <branch-name>

# Create new feature
git checkout dev
git checkout -b feature/my-feature
```

## Protection Rules (GitHub Settings)

### `main` branch:
- [ ] Require pull request reviews (1 approval)
- [ ] Require status checks to pass
- [ ] No direct pushes
- [ ] No force pushes

### `dev` branch:
- [ ] Optional: Require CI to pass
- [ ] Allow direct pushes (for quick iteration)

### `testing` branch:
- [ ] Require all tests to pass
- [ ] Auto-deploy to staging

---

**Setup Date:** 2026-01-13  
**Strategy:** Git Flow (simplified)  
**Next:** Sprint 2 development on `dev` branch
