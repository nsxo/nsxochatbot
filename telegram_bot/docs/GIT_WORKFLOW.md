# 🔄 Git Workflow Guide

## 📋 **Branch Strategy**

This project follows a **GitFlow-inspired** branching strategy for organized development:

```
main          ←── Production-ready code (stable releases)
  ↑
development   ←── Integration branch (ongoing development)
  ↑
feature/*     ←── Feature development branches
hotfix/*      ←── Critical production fixes
```

## 🌿 **Branch Descriptions**

### **`main` - Production Branch**
- **Purpose**: Production-ready, stable code
- **Protection**: Protected branch, no direct commits
- **Updates**: Only via pull requests from `development`
- **Triggers**: Automatic deployment to production

### **`development` - Integration Branch**  
- **Purpose**: Integration of completed features
- **Testing**: All features tested together
- **Updates**: Via pull requests from `feature/*` branches
- **Staging**: Automatically deployed to staging environment

### **`feature/*` - Feature Branches**
- **Purpose**: Individual feature development
- **Naming**: `feature/feature-name` (e.g., `feature/webhook-improvements`)
- **Base**: Created from `development`
- **Lifecycle**: Deleted after merge

### **`hotfix/*` - Emergency Fix Branches**
- **Purpose**: Critical production fixes
- **Naming**: `hotfix/issue-description` (e.g., `hotfix/payment-bug`)
- **Base**: Created from `main`
- **Merge**: Into both `main` and `development`

## 🚀 **Development Workflow**

### **1. Starting New Feature**
```bash
# Switch to development and pull latest
git checkout development
git pull origin development

# Create feature branch
git checkout -b feature/new-admin-panel

# Work on your feature...
# Make commits with descriptive messages
```

### **2. Feature Development**
```bash
# Regular commits during development
git add .
git commit -m "feat: add user management to admin panel"

# Push feature branch
git push -u origin feature/new-admin-panel
```

### **3. Feature Completion**
```bash
# Ensure branch is up to date
git checkout development
git pull origin development
git checkout feature/new-admin-panel
git rebase development

# Create pull request to development
# After review and approval, merge via GitHub/GitLab
```

### **4. Release Process**
```bash
# Create release from development
git checkout development
git pull origin development

# Create release branch (optional for testing)
git checkout -b release/v1.1.0

# Final testing, bug fixes...
# Create pull request to main
# After approval, merge to main and tag
```

## 📝 **Commit Message Standards**

Use **Conventional Commits** format for clear history:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### **Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Build process or auxiliary tool changes

### **Examples:**
```bash
feat(payments): add auto-recharge functionality
fix(admin): resolve user ban status bug
docs(api): update webhook documentation
refactor(database): optimize user queries
chore(deps): update telegram-bot library
```

## 🛡️ **Pre-commit Checks**

Every commit automatically runs these checks:

- **🔐 Security Scan**: Detects potential secrets (API keys, tokens)
- **🐍 Python Syntax**: Validates all Python files
- **📏 File Size**: Prevents large files (>10MB)
- **🚫 Environment Files**: Blocks .env commits

### **Bypassing Checks (Emergency Only)**
```bash
git commit --no-verify -m "emergency: critical production fix"
```

## 🏷️ **Version Tagging**

### **Semantic Versioning**
- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### **Creating Releases**
```bash
# Update VERSION file
echo "1.1.0" > VERSION

# Commit version bump
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 1.1.0"

# Create and push tag
git tag -a v1.1.0 -m "Release v1.1.0: Enhanced Admin Panel"
git push origin v1.1.0
```

## 🔄 **Common Workflows**

### **Hotfix Process**
```bash
# Critical bug in production
git checkout main
git pull origin main
git checkout -b hotfix/payment-processing-bug

# Fix the bug
git add .
git commit -m "fix(payments): resolve stripe webhook timeout"

# Create PR to main (emergency review)
# After merge, also merge to development
git checkout development
git merge hotfix/payment-processing-bug
```

### **Feature Review Process**
1. **Create Feature Branch**: From `development`
2. **Develop & Test**: Regular commits, local testing
3. **Push & PR**: Create pull request to `development`
4. **Code Review**: Team review and approval
5. **Merge**: Squash and merge into `development`
6. **Cleanup**: Delete feature branch

### **Release Cycle**
1. **Feature Complete**: All planned features in `development`
2. **Testing**: Comprehensive testing in staging
3. **Release PR**: `development` → `main`
4. **Final Review**: Production readiness check
5. **Deploy**: Merge triggers production deployment
6. **Tag**: Create version tag for tracking

## 📊 **Repository Status**

### **Current Structure**
```bash
# Check current branch and status
git status
git branch -a

# View commit history
git log --oneline --graph --all
```

### **Useful Commands**
```bash
# See what's changed
git diff development main

# Check branch differences
git log development..main --oneline

# Clean up merged branches
git branch --merged | grep -v "main\|development" | xargs -n 1 git branch -d
```

## 🎯 **Best Practices**

1. **🔄 Regular Updates**: Pull latest changes frequently
2. **📝 Clear Commits**: Descriptive commit messages
3. **🧪 Test Before Push**: Run tests locally
4. **📋 Small PRs**: Keep pull requests focused and small
5. **🔍 Code Review**: Always review before merging
6. **🏷️ Tag Releases**: Tag all production releases
7. **📚 Update Docs**: Keep documentation current
8. **🔐 Security First**: Never commit secrets

## 🚨 **Emergency Procedures**

### **Rollback Production**
```bash
# Find last good commit
git log --oneline main

# Create hotfix branch from good commit
git checkout -b hotfix/rollback-to-stable <good-commit-hash>

# Deploy immediately
```

### **Recovery Commands**
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Recover deleted branch
git reflog
git checkout -b recovery-branch <commit-hash>
```

---

This workflow ensures **code quality**, **team collaboration**, and **production stability** for the Telegram Bot project! 🎉 