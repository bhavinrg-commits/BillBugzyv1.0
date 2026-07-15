from tkinter import *
from tkinter import ttk
import sqlite3

from config import DB_PATH


def open_bill_history(parent):

    win = Toplevel(parent)

    win.title("Bill History")

    win.state("zoomed")

    win.configure(bg="#EEF2F7")

    Label(
        win,
        text="📜 BILL HISTORY",
        font=("Segoe UI",24,"bold"),
        bg="#EEF2F7",
        fg="#1E293B"
    ).pack(pady=15)

    # ---------------- SEARCH ----------------

    search_frame = Frame(
        win,
        bg="#EEF2F7"
    )

    search_frame.pack(fill="x", padx=20)

    Label(
        search_frame,
        text="Search",
        bg="#EEF2F7",
        font=("Segoe UI",12,"bold")
    ).pack(side=LEFT)

    search_var = StringVar()

    search_entry = Entry(
        search_frame,
        textvariable=search_var,
        font=("Segoe UI",12),
        width=40
    )

    search_entry.pack(side=LEFT, padx=10)

    # ---------------- TREE ----------------

    columns = (

        "Bill No",

        "Date",

        "Time",

        "Customer",

        "Mobile",

        "Amount",

        "Payment"

    )

    tree = ttk.Treeview(

        win,

        columns=columns,

        show="headings",

        height=25

    )

    for col in columns:

        tree.heading(col, text=col)

        tree.column(

            col,

            anchor="center",

            width=160

        )

    tree.pack(

        fill=BOTH,

        expand=True,

        padx=20,

        pady=20

    )

    # ---------------- LOAD BILLS ----------------

    def load_bills(keyword=""):

        tree.delete(*tree.get_children())

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
            SELECT
                bill_id,
                bill_no,
                bill_date,
                bill_time,
                customer_name,
                contact,
                total,
                payment_mode
            FROM bill_master
            WHERE
                bill_no LIKE ?
                OR customer_name LIKE ?
                OR contact LIKE ?
            ORDER BY bill_id DESC
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ))

        rows = c.fetchall()

        conn.close()

        for row in rows:
            bill_id = row[0]

            tree.insert(
                "",
                END,
                iid=str(bill_id),
                values=row[1:]  # Skip bill_id (hidden)
            )

    # ---------------- SEARCH ----------------

    def search_bill(event=None):

        load_bills(search_var.get().strip())

    search_entry.bind("<KeyRelease>", search_bill)

    # Initial Load
    load_bills()