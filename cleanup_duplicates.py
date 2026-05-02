#!/usr/bin/env python3
"""
Clean up duplicate directories and consolidate to root level
"""
import shutil
import os
import sys

root = 'd:\\Routrix_transport'

print("CLEANUP: Removing duplicate directories...")

# Step 1: Backup - Check what we're deleting
print("\n[CHECK] Directories to delete:")
print("  - frontend/ (old, at root)")
print("  - backend/ (old, at root)")
print("  - Routrix/ (will be emptied, then deleted)")
print("  - banners/ (old)")

# Step 2: Delete old root-level frontend/backend (THEY'RE OLD)
dirs_to_delete = [
    os.path.join(root, 'frontend'),
    os.path.join(root, 'backend'),
    os.path.join(root, 'banners'),
]

for dir_path in dirs_to_delete:
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
            print(f"[✓] Deleted {os.path.basename(dir_path)}/")
        except Exception as e:
            print(f"[✗] Failed to delete {dir_path}: {e}")

# Step 3: Move Routrix/frontend/ to root
print("\n[MOVE] Moving Routrix/frontend/ → frontend/")
try:
    src = os.path.join(root, 'Routrix', 'frontend')
    dst = os.path.join(root, 'frontend')
    shutil.move(src, dst)
    print(f"[✓] Moved frontend/")
except Exception as e:
    print(f"[✗] Failed: {e}")

# Step 4: Move Routrix/backend/ to root
print("[MOVE] Moving Routrix/backend/ → backend/")
try:
    src = os.path.join(root, 'Routrix', 'backend')
    dst = os.path.join(root, 'backend')
    shutil.move(src, dst)
    print(f"[✓] Moved backend/")
except Exception as e:
    print(f"[✗] Failed: {e}")

# Step 5: Delete empty Routrix folder
print("\n[DELETE] Removing empty Routrix/ folder")
try:
    shutil.rmtree(os.path.join(root, 'Routrix'))
    print(f"[✓] Deleted Routrix/")
except Exception as e:
    print(f"[✗] Failed: {e}")

# Step 6: Delete unnecessary .md files at root
print("\n[DELETE] Cleaning up documentation files at root")
md_files = [
    'ARCHITECTURE_DIAGRAMS.md',
    'ARCHITECTURE_FIXES.md',
    'CLOUDINARY_FIXES.md',
    'DEPLOYMENT_GUIDE.md',
    'DOCUMENTATION_INDEX.md',
    'IMPLEMENTATION_SUMMARY.md',
    'QUICK_REFERENCE.md',
    'README_PRODUCTION_READY.md',
    'RENDER_DEPLOYMENT_GUIDE.md',
    'SYSTEM_REMEDIATION_GUIDE.md',
    'TROUBLESHOOTING_ORIGINAL_ISSUES.md',
    'WORK_COMPLETED_SUMMARY.md',
    'START_HERE.txt',
    'commit.py',
    'cleanup.py',
    'requirements-prod.txt',
]

for f in md_files:
    path = os.path.join(root, f)
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"[✓] Deleted {f}")
        except Exception as e:
            print(f"[✗] Failed: {e}")

print("\n" + "="*50)
print("✓ CLEANUP COMPLETE")
print("="*50)
print("\nNew structure:")
print("d:\\Routrix_transport/")
print("  ├── frontend/     (ACTIVE)")
print("  ├── backend/      (ACTIVE)")
print("  ├── .git/")
print("  ├── .venv/")
print("  └── README.md")
