#!/usr/bin/env python3
import subprocess
import os

os.chdir('d:\\Routrix_transport')

print("Pushing fixes...")

# Stage all changes
subprocess.run(['git', 'add', '-A'], capture_output=True)

# Commit
subprocess.run([
    'git', 'commit', '-m',
    'Fix: Admin login - correct API path, error handling, logging'
], capture_output=True)

# Push to master (for Vercel frontend)
subprocess.run(['git', 'push', 'origin', 'master'], capture_output=True)
print("✓ Pushed to master (Vercel frontend)")

# Copy latest backend to root and push to main
import shutil
shutil.copy2('Routrix/backend/main.py', 'backend/main.py')

subprocess.run(['git', 'add', 'backend/main.py'], capture_output=True)
subprocess.run(['git', 'commit', '-m', 'Fix: Sync backend logging for admin login'], capture_output=True)
subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True)
print("✓ Pushed to main (Render backend)")

print("\n✓ DONE! Wait 2-3 minutes for deployments to update.")
print("\nThen test admin login again:")
print("  https://routrix.in/admin")
print("\nCheck Render logs for debugging info:")
print("  Look for [ADMIN LOGIN] messages")
