#!/usr/bin/env python3
"""
Commit the fixes to git and push to master
"""
import subprocess
import os
import sys

os.chdir('d:\\Routrix_transport\\Routrix')

try:
    # Stage all changes
    print("[*] Staging changes...")
    subprocess.run(['git', 'add', '-A'], check=True, capture_output=True)
    
    # Commit with message
    print("[*] Committing changes...")
    commit_msg = """Fix SMTP, admin auth, and OTP cleanup

- Fix career.html: remove hardcoded URLs, use BACKEND variable
- Add JWT token validation on admin.html page load
- Auto-logout on token expiry
- Add OTP cleanup scheduler (runs every 5 minutes)

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"""
    
    subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True)
    print("✓ Changes committed")
    
    # Push to master
    print("[*] Pushing to master...")
    subprocess.run(['git', 'push', 'origin', 'master'], check=True, capture_output=True)
    print("✓ Pushed to master")
    
    # Also push to main
    print("[*] Pushing to main...")
    subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=False)
    print("✓ Pushed to main")
    
except subprocess.CalledProcessError as e:
    print(f"✗ Command failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("\n✓✓✓ All fixes committed and pushed! ✓✓✓")
