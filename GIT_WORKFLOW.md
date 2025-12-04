# 🌳 Git Feature Branch Workflow

## Quick Commands

### Create Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### Work on Feature
```bash
# Make changes
# Test locally: ./run_local.py

# Commit changes
git add .
git commit -m "Description of changes"
```

### Check What Changed
```bash
# See diff from main
git diff main

# See commit history
git log --oneline
```

### Merge to Main (After Testing)
```bash
# Make sure everything is committed
git status

# Switch to main
git checkout main

# Merge feature
git merge feature/your-feature-name

# Push to production
git push origin main
```

### Delete Feature Branch (After Merge)
```bash
git branch -d feature/your-feature-name
```

### Undo/Reset (If Needed)
```bash
# Discard uncommitted changes
git checkout -- filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Abandon feature and start over
git checkout main
git branch -D feature/your-feature-name
```

---

## 🚨 Emergency: Pushed Wrong Code to Production

```bash
# 1. DON'T PANIC

# 2. Revert last commit (creates new commit that undoes it)
git revert HEAD
git push origin main

# 3. Or reset to specific commit (DANGEROUS - use only if just pushed)
git reset --hard COMMIT_HASH
git push origin main --force  # ⚠️ Use with caution!
```

---

## 📋 Best Practices

1. **Always test locally before merging**
   ```bash
   ./run_local.py
   # Test all features thoroughly
   ```

2. **Keep feature branches small and focused**
   - ✅ `feature/fix-forgot-password`
   - ❌ `feature/fix-everything`

3. **Use descriptive commit messages**
   - ✅ `Fix: Secure forgot password with email token`
   - ❌ `fixed stuff`

4. **Check what you're committing**
   ```bash
   git status
   git diff
   ```

5. **Never commit sensitive data**
   - ❌ `.env.local`
   - ❌ Database dumps with real data
   - ❌ API keys, passwords

---

## 🔄 Typical Workflow Example

```bash
# Start new feature
git checkout main
git pull
git checkout -b feature/add-barcode-system

# Work and test
# ... edit files ...
./run_local.py  # Test
git add .
git commit -m "Add barcode generation for inventory items"

# More work
# ... edit files ...
./run_local.py  # Test again
git commit -am "Add barcode scanner UI"

# Ready to deploy
git checkout main
git merge feature/add-barcode-system
git push origin main  # 🚀 Deploys to Vercel

# Cleanup
git branch -d feature/add-barcode-system
```

---

## 🛠️ Local Development Commands

```bash
# Start local server (with PostgreSQL)
cd /Users/rishjain/Downloads/attendence_app
./run_local.py

# Access app
http://mahaveerelectricals.lvh.me:5001/admin/login

# Check database
podman exec bizbooks-local-db psql -U bizbooks_dev -d bizbooks_dev

# View logs
# Check terminal where ./run_local.py is running
```

---

## 📚 Useful Git Commands

```bash
# See all branches
git branch -a

# See current branch
git branch --show-current

# Switch branch
git checkout branch-name

# Create and switch
git checkout -b new-branch-name

# See remote URL
git remote -v

# See what would be pushed
git diff main --stat

# Stash changes temporarily
git stash
git stash pop  # Restore stashed changes
```


