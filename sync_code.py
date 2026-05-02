#!/usr/bin/env python3
"""
Sync latest code from Routrix/ nested folders to root deployment folders
- Routrix/backend/main.py → backend/main.py
- Routrix/frontend/* → frontend/*
"""
import shutil
import os

root = 'd:\\Routrix_transport'

print("SYNCING LATEST CODE TO DEPLOYMENT FOLDERS...")
print("="*50)

# Copy backend/main.py (and other critical files)
print("\n[BACKEND] Syncing Routrix/backend/ → backend/")
try:
    src_main = os.path.join(root, 'Routrix', 'backend', 'main.py')
    dst_main = os.path.join(root, 'backend', 'main.py')
    
    if os.path.exists(src_main):
        shutil.copy2(src_main, dst_main)
        print(f"  ✓ Copied main.py")
    else:
        print(f"  ✗ Source not found: {src_main}")
        
    # Also copy requirements files
    for fname in ['requirements.txt', 'requirements-prod.txt']:
        src = os.path.join(root, 'Routrix', 'backend', fname)
        dst = os.path.join(root, 'backend', fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  ✓ Copied {fname}")
            
except Exception as e:
    print(f"  ✗ Error: {e}")

# Copy frontend files
print("\n[FRONTEND] Syncing Routrix/frontend/ → frontend/")
try:
    # Copy only the critical files that changed
    critical_files = [
        'admin.html', 'career.html', 'index.html',
        'vercel.json', 'manifest.json', 'sw.js'
    ]
    
    for fname in critical_files:
        src = os.path.join(root, 'Routrix', 'frontend', fname)
        dst = os.path.join(root, 'frontend', fname)
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  ✓ Copied {fname}")
        else:
            print(f"  ⚠ Not found: {fname}")
            
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "="*50)
print("✓ SYNC COMPLETE")
print("="*50)
print("\nNow run:")
print("  cd d:\\Routrix_transport")
print("  git add -A")
print("  git commit -m 'Sync: Latest code to deployment folders (main branch)'")
print("  git push origin main")
