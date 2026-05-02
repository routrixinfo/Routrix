#!/usr/bin/env python3
import os
import shutil

os.chdir('d:\\Routrix_transport')

# Delete old root folders
for folder in ['frontend', 'backend', 'banners']:
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print(f"Deleted {folder}")

# Move from Routrix to root
for folder in ['frontend', 'backend']:
    src = f'Routrix\\{folder}'
    if os.path.isdir(src):
        shutil.move(src, folder)
        print(f"Moved Routrix/{folder} to {folder}")

# Delete Routrix if empty
try:
    os.rmdir('Routrix')
    print("Deleted empty Routrix folder")
except:
    print("Note: Routrix folder still has files, please delete manually")

# Delete .md files at root
files_to_delete = [
    'ARCHITECTURE_DIAGRAMS.md', 'ARCHITECTURE_FIXES.md',
    'CLOUDINARY_FIXES.md', 'DEPLOYMENT_GUIDE.md',
    'DOCUMENTATION_INDEX.md', 'IMPLEMENTATION_SUMMARY.md',
    'QUICK_REFERENCE.md', 'README_PRODUCTION_READY.md',
    'RENDER_DEPLOYMENT_GUIDE.md', 'SYSTEM_REMEDIATION_GUIDE.md',
    'TROUBLESHOOTING_ORIGINAL_ISSUES.md', 'WORK_COMPLETED_SUMMARY.md',
    'START_HERE.txt', 'commit.py', 'cleanup.py', 'requirements-prod.txt',
    'cleanup_duplicates.py', 'final_push.py', 'git_push.py', 'push_fixes.py'
]

for f in files_to_delete:
    if os.path.isfile(f):
        os.remove(f)
        print(f"Deleted {f}")

print("\n✓ Cleanup complete!")
print("\nDirectory structure:")
for root, dirs, files in os.walk('.'):
    level = root.replace('.', '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    if level < 2:  # Only show 2 levels deep
        for file in files[:5]:  # Show first 5 files
            print(f'{subindent}{file}')
        if len(files) > 5:
            print(f'{subindent}... and {len(files) - 5} more files')
