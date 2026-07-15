from tkinter import *
from tkinter import messagebox
from backup_restore import (
    backup_database,
    restore_database,
    open_backup_folder,
    get_database_size,
    get_total_backups,
    get_last_backup,
    get_backup_history
)

BG = "#DCE6F2"
CARD = "#FDFDFD"

def open_settings(parent):

    win = Toplevel(parent)
    win.title("BUGZY Settings")
    win.state("zoomed")
    win.configure(bg="#E8EEF7")

    # ---------------- TITLE ----------------

    Label(
        win,
        text="⚙ BUGZY SETTINGS",
        font=("Segoe UI", 30, "bold"),
        bg="#E8EEF7",
        fg="#1F2937"
    ).pack(pady=20)

    # ================= MAIN CONTAINER =================

    container = Frame(
        win,
        bg="#E8EEF7"
    )

    container.pack(fill=BOTH, expand=True, padx=40, pady=10)

    # ==================================================
    # DATABASE INFO CARD
    # ==================================================

    db_card = Frame(
        container,
        bg="white",
        bd=1,
        relief="solid"
    )

    db_card.pack(fill=X, pady=(0,20))

    Label(
        db_card,
        text="DATABASE INFORMATION",
        bg="white",
        fg="#2563EB",
        font=("Segoe UI",16,"bold")
    ).pack(pady=(15,10))

    Label(
        db_card,
        text=f"💾 Database Size : {get_database_size()}",
        bg="white",
        fg="#374151",
        font=("Segoe UI",12)
    ).pack(anchor="w", padx=25, pady=2)

    Label(
        db_card,
        text=f"🗄 Total Backups : {get_total_backups()}",
        bg="white",
        fg="#374151",
        font=("Segoe UI",12)
    ).pack(anchor="w", padx=25, pady=2)

    Label(
        db_card,
        text=f"🕒 Last Backup : {get_last_backup()}",
        bg="white",
        fg="#374151",
        font=("Segoe UI",12)
    ).pack(anchor="w", padx=25, pady=(2,18))

    # ==================================================
    # SETTINGS CARD
    # ==================================================

    settings_card = Frame(
        container,
        bg="white",
        bd=1,
        relief="solid"
    )

    settings_card.pack(fill=X, pady=(0,20))

    Label(
        settings_card,
        text="APPLICATION SETTINGS",
        bg="white",
        fg="#2563EB",
        font=("Segoe UI",16,"bold")
    ).pack(pady=(15,15))

    # ---------------- BUTTONS ----------------

    buttons_frame = Frame(
        settings_card,
        bg="white"
    )

    buttons_frame.pack(pady=10)

    button_style = {
        "font": ("Segoe UI", 12, "bold"),
        "width": 22,
        "height": 2,
        "bd": 0,
        "fg": "white",
        "cursor": "hand2"
    }

    Button(
        buttons_frame,
        text="🖨 Printer Settings",
        bg="#3B82F6",
        command=lambda: messagebox.showinfo(
            "Coming Soon",
            "Printer Settings will be added next."
        ),
        **button_style
    ).grid(row=0, column=0, padx=15, pady=12)

    Button(
        buttons_frame,
        text="💾 Backup Database",
        bg="#10B981",
        command=backup_database,
        **button_style
    ).grid(row=0, column=1, padx=15, pady=12)

    Button(
        buttons_frame,
        text="♻ Restore Database",
        bg="#F59E0B",
        command=restore_database,
        **button_style
    ).grid(row=1, column=0, padx=15, pady=12)

    Button(
        buttons_frame,
        text="📂 Open Backup Folder",
        bg="#8B5CF6",
        command=open_backup_folder,
        **button_style
    ).grid(row=1, column=1, padx=15, pady=12)

    Button(
        buttons_frame,
        text="👤 User Management",
        bg="#EC4899",
        command=lambda: messagebox.showinfo(
            "Coming Soon",
            "User Management will be added."
        ),
        **button_style
    ).grid(row=2, column=0, padx=15, pady=12)

    Button(
        buttons_frame,
        text="ℹ About",
        bg="#6B7280",
        command=lambda: messagebox.showinfo(
            "BUGZY BILLING SYSTEM",
            "Version : 1.0\n\nDeveloped by\nBhavin Gajjar"
        ),
        **button_style
    ).grid(row=2, column=1, padx=15, pady=12)

    Button(
        settings_card,
        text="❌ Close",
        font=("Segoe UI", 12, "bold"),
        bg="#EF4444",
        fg="white",
        bd=0,
        width=20,
        height=2,
        cursor="hand2",
        command=win.destroy
    ).pack(pady=15)
    # ======================================================
    # BACKUP HISTORY CARD
    # ======================================================

    history_card = Frame(
        container,
        bg="white",
        bd=1,
        relief="solid"
    )

    history_card.pack(fill=BOTH, expand=True)

    Label(
        history_card,
        text="BACKUP HISTORY",
        bg="white",
        fg="#2563EB",
        font=("Segoe UI",16,"bold")
    ).pack(pady=(15,10))

    history = Listbox(
        history_card,
        font=("Consolas",10),
        height=8,
        bd=0,
        highlightthickness=0
    )

    history.pack(
        fill=BOTH,
        expand=True,
        padx=20,
        pady=10
    )

    for item in get_backup_history():

        history.insert(
            END,
            f"{item['date']}      {item['size']}      {item['name']}"
        )

    # ======================================================
    # BOTTOM BUTTONS
    # ======================================================

    bottom = Frame(
        history_card,
        bg="white"
    )

    bottom.pack(
        pady=15
    )

    Button(
        bottom,
        text="ℹ About",
        font=("Segoe UI",12,"bold"),
        width=15,
        bg="#6B7280",
        fg="white",
        bd=0,
        pady=6,
        cursor="hand2",
        command=lambda: messagebox.showinfo(
            "BUGZY BILLING SYSTEM",
            "Version : 1.0\n\nDeveloped by\nBhavin Gajjar"
        )
    ).pack(
        side=LEFT,
        padx=10
    )

    Button(
        bottom,
        text="❌ Close",
        font=("Segoe UI",12,"bold"),
        width=15,
        bg="#EF4444",
        fg="white",
        bd=0,
        pady=6,
        cursor="hand2",
        command=win.destroy
    ).pack(
        side=LEFT,
        padx=10
    )