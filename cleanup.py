import shutil
import os

root = 'd:\\Routrix_transport'

# Delete duplicate directories
for path in ['backend', 'frontend', 'banners']:
    full_path = os.path.join(root, path)
    if os.path.exists(full_path):
        try:
            shutil.rmtree(full_path)
            print(f"✓ Deleted {path}")
        except Exception as e:
            print(f"✗ Failed to delete {path}: {e}")

# Delete MD files at root (should be in Routrix only)
md_files = [
    'ARCHITECTURE_DIAGRAMS.md',
    'ARCHITECTURE_FIXES.md',
    'CLOUDINARY_FIXES.md',
    'DEPLOYMENT_GUIDE.md',
    'DOCUMENTATION_INDEX.md',
    'IMPLEMENTATION_SUMMARY.md',
    'QUICK_REFERENCE.md',
    'README.md',
    'README_PRODUCTION_READY.md',
    'RENDER_DEPLOYMENT_GUIDE.md',
    'SYSTEM_REMEDIATION_GUIDE.md',
    'TROUBLESHOOTING_ORIGINAL_ISSUES.md',
    'WORK_COMPLETED_SUMMARY.md',
    'commit.py',
    'requirements-prod.txt',
    'START_HERE.txt'
]

for f in md_files:
    path = os.path.join(root, f)
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"✓ Deleted {f}")
        except Exception as e:
            print(f"✗ Failed to delete {f}: {e}")

print("\n✓ Cleanup complete - only Routrix folder remains")
