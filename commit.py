#!/usr/bin/env python3
import subprocess
import os

os.chdir('d:\\Routrix_transport')

# Add all changes
subprocess.run(['git', 'add', '-A'], check=True)

# Commit
subprocess.run([
    'git', 'commit', '-m',
    'Fix SMTP career form, admin JWT auth, OTP cleanup\n\n- Fix career.html: remove hardcoded URLs, use BACKEND variable\n- Add JWT token validation on admin.html page load\n- Add auto-logout on token expiry\n- Add OTP cleanup scheduler (runs every 5 minutes)\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>'
], check=True)

print("✓ Changes committed successfully")
