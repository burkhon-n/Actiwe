#!/bin/bash
# Git cleanup script to apply .gitignore changes

echo "🧹 Cleaning up git repository based on .gitignore..."

# Remove cached files that should now be ignored
echo "Removing __pycache__ directories from git tracking..."
git rm -r --cached __pycache__/ 2>/dev/null || echo "  ⚠️  __pycache__/ not tracked or already removed"
git rm -r --cached models/__pycache__/ 2>/dev/null || echo "  ⚠️  models/__pycache__/ not tracked or already removed"  
git rm -r --cached routes/__pycache__/ 2>/dev/null || echo "  ⚠️  routes/__pycache__/ not tracked or already removed"

# Remove .pyc files
echo "Removing .pyc files from git tracking..."
git rm --cached **/*.pyc 2>/dev/null || echo "  ⚠️  No .pyc files tracked or already removed"

# Remove .DS_Store files (common on macOS)
echo "Removing .DS_Store files from git tracking..."
git rm --cached .DS_Store 2>/dev/null || echo "  ⚠️  .DS_Store not tracked or already removed"
git rm --cached **/.DS_Store 2>/dev/null || echo "  ⚠️  No nested .DS_Store files tracked or already removed"

# Remove any .env files (if accidentally committed)
echo "Removing .env files from git tracking..."
git rm --cached .env 2>/dev/null || echo "  ⚠️  .env not tracked or already removed"
git rm --cached .env.* 2>/dev/null || echo "  ⚠️  No .env.* files tracked or already removed"

# Remove log files
echo "Removing log files from git tracking..."
git rm --cached *.log 2>/dev/null || echo "  ⚠️  No .log files tracked or already removed"

# Add the new .gitignore and .gitkeep files
echo "Adding .gitignore and .gitkeep files..."
git add .gitignore
git add static/uploads/.gitkeep

# Show status
echo ""
echo "📊 Current git status:"
git status --short

echo ""
echo "✅ Git cleanup completed!"
echo ""
echo "📝 Next steps:"
echo "1. Review the changes with: git status"
echo "2. Commit the changes with: git commit -m 'Add .gitignore and clean up tracked files'"
echo "3. Push changes with: git push"