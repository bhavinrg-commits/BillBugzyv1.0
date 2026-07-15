import os
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox

# Change if your DB path is different
DB_PATH = "store.db"
BACKUP_FOLDER = "Backups"

def backup_database():

    backup_folder = "Backups"

    os.makedirs(backup_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    backup_file = os.path.join(
        backup_folder,
        f"store_{timestamp}.db"
    )

    shutil.copy2(DB_PATH, backup_file)

    messagebox.showinfo(
        "Backup Successful",
        f"Database backed up successfully.\n\n{backup_file}"
    )


def restore_database():

    backup_file = filedialog.askopenfilename(
        title="Select Backup File",
        filetypes=[("SQLite Database", "*.db")]
    )

    if not backup_file:
        return

    confirm = messagebox.askyesno(
        "Restore Database",
        "This will overwrite the current database.\n\nContinue?"
    )

    if not confirm:
        return

    shutil.copy2(
        backup_file,
        DB_PATH
    )

    messagebox.showinfo(
        "Restore Complete",
        "Database restored successfully.\n\nPlease restart Bugzy Billing."
    )


def open_backup_folder():

    folder = os.path.abspath("Backups")

    os.makedirs(folder, exist_ok=True)

    os.startfile(folder)

def get_database_size():

    if not os.path.exists(DB_PATH):
        return "0 MB"

    size = os.path.getsize(DB_PATH)

    return f"{size / (1024*1024):.2f} MB"


def get_total_backups():

    if not os.path.exists(BACKUP_FOLDER):
        return 0

    return len(
        [
            f for f in os.listdir(BACKUP_FOLDER)
            if f.endswith(".db")
        ]
    )


def get_last_backup():

    if not os.path.exists(BACKUP_FOLDER):
        return "No Backup"

    files = [
        os.path.join(BACKUP_FOLDER, f)
        for f in os.listdir(BACKUP_FOLDER)
        if f.endswith(".db")
    ]

    if not files:
        return "No Backup"

    latest = max(files, key=os.path.getmtime)

    dt = datetime.fromtimestamp(
        os.path.getmtime(latest)
    )

    return dt.strftime("%d-%b-%Y %I:%M %p")


def get_backup_history():

    history = []

    if not os.path.exists(BACKUP_FOLDER):
        return history

    files = [
        os.path.join(BACKUP_FOLDER, f)
        for f in os.listdir(BACKUP_FOLDER)
        if f.endswith(".db")
    ]

    files.sort(
        key=os.path.getmtime,
        reverse=True
    )

    for file in files:

        history.append({

            "name": os.path.basename(file),

            "date": datetime.fromtimestamp(
                os.path.getmtime(file)
            ).strftime("%d-%b-%Y %I:%M %p"),

            "size": f"{os.path.getsize(file)/(1024*1024):.2f} MB"

        })

    return history