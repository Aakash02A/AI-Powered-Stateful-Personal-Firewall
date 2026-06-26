import sqlite3
import argparse
import os
import time
from datetime import datetime

def backup_database(source_db: str, dest_dir: str):
    if not os.path.exists(source_db):
        print(f"[!] Source database {source_db} not found.")
        return
        
    os.makedirs(dest_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_db = os.path.join(dest_dir, f"firewall_backup_{timestamp}.db")
    
    print(f"[*] Starting backup from {source_db} to {dest_db}...")
    start_time = time.time()
    
    try:
        # SQLite backup API safely copies the DB without locking the source for writes
        src = sqlite3.connect(source_db)
        dst = sqlite3.connect(dest_db)
        
        with dst:
            src.backup(dst)
            
        src.close()
        dst.close()
        
        duration = time.time() - start_time
        print(f"[+] Backup completed successfully in {duration:.2f} seconds.")
    except Exception as e:
        print(f"[!] Backup failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely backup the SQLite database.")
    parser.add_argument("--source", default="data/firewall.db", help="Path to source firewall.db")
    parser.add_argument("--dest", default="data/backups", help="Directory to save the backup")
    
    args = parser.parse_args()
    backup_database(args.source, args.dest)
