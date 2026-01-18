"""
MicroLLM-PrivateStack Backup Script
Backs up database, RAG store, and configuration
"""

import os
import shutil
import datetime
import json
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent.parent
BACKUP_DIR = BASE_DIR / "backups"
DATA_DIR = BASE_DIR / "data"
BACKEND_DIR = BASE_DIR / "backend"

# Files to backup
BACKUP_ITEMS = [
    {"src": BACKEND_DIR / "data" / "llm_database.db", "name": "database.db"},
    {"src": DATA_DIR / "rag_store.json", "name": "rag_store.json"},
    {"src": DATA_DIR / "rag_store.npy", "name": "rag_store.npy"},
    {"src": BASE_DIR / ".env", "name": "env_config"},
    {"src": BASE_DIR / ".env.optimal", "name": "env_optimal"},
]

def create_backup():
    """Create timestamped backup"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = BACKUP_DIR / backup_name
    
    print("=" * 60)
    print("MicroLLM-PrivateStack Backup Utility")
    print("=" * 60)
    print(f"Timestamp: {timestamp}")
    print(f"Backup location: {backup_path}")
    print()
    
    # Create backup directory
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Backup each item
    backed_up = []
    skipped = []
    
    for item in BACKUP_ITEMS:
        src = item["src"]
        dest = backup_path / item["name"]
        
        if src.exists():
            try:
                if src.is_file():
                    shutil.copy2(src, dest)
                else:
                    shutil.copytree(src, dest)
                backed_up.append(item["name"])
                print(f"  ✅ {item['name']}")
            except Exception as e:
                print(f"  ❌ {item['name']}: {e}")
                skipped.append(item["name"])
        else:
            print(f"  ⏭️ {item['name']} (not found)")
            skipped.append(item["name"])
    
    # Create manifest
    manifest = {
        "timestamp": timestamp,
        "backed_up": backed_up,
        "skipped": skipped,
        "version": "1.0.1-optimized"
    }
    
    with open(backup_path / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print()
    print("=" * 60)
    print(f"Backup complete: {len(backed_up)} files")
    print(f"Location: {backup_path}")
    print("=" * 60)
    
    return backup_path

def list_backups():
    """List available backups"""
    print("\nAvailable backups:")
    print("-" * 40)
    
    if not BACKUP_DIR.exists():
        print("No backups found.")
        return []
    
    backups = sorted(BACKUP_DIR.iterdir(), reverse=True)
    for i, b in enumerate(backups[:10]):
        manifest_path = b / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
            print(f"  [{i+1}] {b.name} - {len(manifest['backed_up'])} files")
        else:
            print(f"  [{i+1}] {b.name}")
    
    return backups

def restore_backup(backup_name: str):
    """Restore from backup"""
    backup_path = BACKUP_DIR / backup_name
    
    if not backup_path.exists():
        print(f"Backup not found: {backup_name}")
        return False
    
    print(f"Restoring from: {backup_path}")
    
    for item in BACKUP_ITEMS:
        src = backup_path / item["name"]
        dest = item["src"]
        
        if src.exists():
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if src.is_file():
                    shutil.copy2(src, dest)
                else:
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                print(f"  ✅ Restored {item['name']}")
            except Exception as e:
                print(f"  ❌ Failed {item['name']}: {e}")
    
    print("Restore complete. Restart server to apply changes.")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_backups()
        elif sys.argv[1] == "restore" and len(sys.argv) > 2:
            restore_backup(sys.argv[2])
        else:
            print("Usage:")
            print("  python backup.py         # Create backup")
            print("  python backup.py list    # List backups")
            print("  python backup.py restore <name>  # Restore backup")
    else:
        create_backup()
