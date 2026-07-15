from tkinter import *

from expenses import open_expenses


def open_employee_operations(parent):

    win = Toplevel(parent)

    win.title("Employee & Operations")

    win.geometry("900x650")

    win.resizable(False, False)

    win.configure(bg="#F4F6F9")

    win.grab_set()

    # ---------------- HEADER ----------------

    header = Frame(
        win,
        bg="#1E3A8A",
        height=80
    )

    header.pack(fill="x")

    Label(
        header,
        text="👨‍💼 Employee & Operations",
        bg="#1E3A8A",
        fg="white",
        font=("Segoe UI", 24, "bold")
    ).pack(pady=18)

    # ---------------- BODY ----------------

    body = Frame(
        win,
        bg="#F4F6F9"
    )

    body.pack(expand=True)

    btn_font = ("Segoe UI", 16, "bold")

    # ---------------- Expenses ----------------

    Button(
        body,
        text="💰\nExpenses",
        font=btn_font,
        bg="#DC2626",
        fg="white",
        width=18,
        height=5,
        cursor="hand2",
        relief="flat",
        command=lambda: open_expenses(win)
    ).grid(row=0, column=0, padx=30, pady=25)

    # ---------------- Employee ----------------

    Button(
        body,
        text="👥\nEmployee Master",
        font=btn_font,
        bg="#2563EB",
        fg="white",
        width=18,
        height=5,
        cursor="hand2",
        relief="flat",
        command=lambda: print("Employee Master")
    ).grid(row=0, column=1, padx=30)

    # ---------------- Attendance ----------------

    Button(
        body,
        text="🕒\nAttendance",
        font=btn_font,
        bg="#059669",
        fg="white",
        width=18,
        height=5,
        cursor="hand2",
        relief="flat",
        command=lambda: print("Attendance")
    ).grid(row=1, column=0, padx=30, pady=25)

    # ---------------- Leave ----------------

    Button(
        body,
        text="📝\nLeave",
        font=btn_font,
        bg="#F59E0B",
        fg="white",
        width=18,
        height=5,
        cursor="hand2",
        relief="flat",
        command=lambda: print("Leave")
    ).grid(row=1, column=1)

    Button(
        win,
        text="Close",
        font=("Segoe UI", 12, "bold"),
        bg="#6B7280",
        fg="white",
        width=18,
        cursor="hand2",
        command=win.destroy
    ).pack(pady=20)