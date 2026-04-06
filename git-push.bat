@echo off
cd /d "c:\Users\DEll\OneDrive\Desktop\E&A\events 1"
git init
git config user.email "blackboxai@example.com"
git config user.name "BLACKBOXAI"
git remote add origin https://github.com/satyam1289/Events-Awards.git 2>nul || git remote set-url origin https://github.com/satyam1289/Events-Awards.git
git add .
git commit -m "Full E&A v5.0 project + enhanced README with comprehensive flow blocks" || echo Commit skipped - no changes
git branch -M main
git push -u origin main -f || echo Push failed - check auth/branch/repo
pause

