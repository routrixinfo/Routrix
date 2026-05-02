#!/usr/bin/env python3
import subprocess
import os

os.chdir('d:\\Routrix_transport\\Routrix')

try:
    # Stage changes
    subprocess.run(['git', 'add', '-A'], check=True, capture_output=True)
    print("[*] Staged all changes")
    
    # Commit
    subprocess.run([
        'git', 'commit', '-m',
        'Fix admin page login, vercel.json, manifest.json, and service worker\n\n- Fix admin JWT token validation (use admin_token key)\n- Fix admin login/logout flow with proper state management\n- Remove conflicting window.onload - use DOMContentLoaded only\n- Fix vercel.json: remove conflicting routes, keep rewrites only\n- Add manifest.json link to index.html for PWA\n- Fix admin_token localStorage key consistency\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>'
    ], check=True, capture_output=True)
    print("[✓] Committed changes")
    
    # Push to master
    subprocess.run(['git', 'push', 'origin', 'master'], check=True, capture_output=True)
    print("[✓] Pushed to master")
    
    print("\n✓✓✓ All fixes committed and pushed! ✓✓✓")
    
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Error: {e}")
