#!/usr/bin/env python3
import subprocess
import os

os.chdir('d:\\Routrix_transport')

# Push all changes to master (vercel uses master)
result = subprocess.run(['git', 'add', '-A'], capture_output=True, text=True)
result = subprocess.run(['git', 'commit', '-m', 'Fix: Push latest frontend fixes (legal page, admin auth, PWA)'], capture_output=True, text=True)
result = subprocess.run(['git', 'push', 'origin', 'master'], capture_output=True, text=True)

print("✓ Pushed to master branch")
print("✓ Vercel will redeploy in 1-2 minutes")
print("\nTest legal page again in 2 minutes:")
print("  https://routrix.in/legal")
