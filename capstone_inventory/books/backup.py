import shutil
from datetime import datetime
import os


def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    shutil.copy2('db.sqlite3', f'{backup_dir}/backup_{timestamp}.sqlite3')

    # Keep last 7 backups
    backups = sorted(os.listdir(backup_dir))
    for old_backup in backups[:-7]:
        os.remove(f'{backup_dir}/{old_backup}')


if __name__ == "__main__":
    backup_db()

'''
Add to Windows Task Scheduler:

Open Task Scheduler

Create Basic Task:

Trigger: Daily at 11 PM

Action: Start a program

Program: python

Arguments: C:\path\to\backup.py


'''
