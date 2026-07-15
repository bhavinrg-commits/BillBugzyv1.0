import sqlite3
import datetime
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import os
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import session
from config import DB_PATH
def open_expenses(parent):
    def save_expense():
        print("save_expense called")

        if category_var.get() == "":
            messagebox.showerror("Error", "Please select Category")
            return

        if amount_var.get() == "":
            messagebox.showerror("Error", "Please enter Amount")
            return
        try:
            amount = float(amount_var.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid Amount")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute("""
                INSERT INTO expense_master
                (
                    expense_date,
                    category,
                    description,
                    amount,
                    payment_mode,
                    created_by
                )
                VALUES (?,?,?,?,?,?)
            """,
                      (
                          expense_date.get(),
                          category_var.get(),
                          description_var.get(),
                          amount,
                          payment_var.get(),
                          session.CURRENT_USER
                      ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Expense Added Successfully")

            category_var.set("")
            amount_var.set("")
            payment_var.set("Cash")
            description_var.set("")

            load_expenses()

        except Exception as e:
            print(e)
            messagebox.showerror("Error", str(e))

    def export_expense_excel():

        folder = "ExpenseReports"

        os.makedirs(folder, exist_ok=True)

        filename = os.path.join(
            folder,
            f"Expense_Report_{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.xlsx"
        )

        wb = Workbook()

        ws = wb.active

        ws.title = "Expenses"

        ws.append([
            "Date",
            "Category",
            "Description",
            "Amount",
            "Payment",
            "Created By"
        ])

        # conn = sqlite3.connect(DB_PATH)
        #
        # c = conn.cursor()
        #
        # date_filter = filter_date.get()
        #
        # if date_filter:
        #     c.execute("""
        #         SELECT
        #             expense_date,
        #             category,
        #             description,
        #             amount,
        #             payment_mode,
        #             created_by
        #         FROM expense_master
        #         WHERE expense_date=?
        #         ORDER BY expense_id DESC
        #     """, (date_filter,))
        # else:
        #     c.execute("""
        #         SELECT
        #             expense_date,
        #             category,
        #             description,
        #             amount,
        #             payment_mode,
        #             created_by
        #         FROM expense_master
        #         ORDER BY expense_id DESC
        #     """)
        #
        # rows = c.fetchall()
        rows = []

        for item in expense_tree.get_children():
            rows.append(expense_tree.item(item)["values"])

        total = 0

        for row in rows:
            ws.append(row)

            total += float(row[3])

        ws.append([])

        ws.append(["", "", "", "TOTAL", total])

        wb.save(filename)

        # conn.close()

        os.startfile(filename)

        messagebox.showinfo(
            "Success",
            "Expense Excel exported successfully."
        )

    def export_expense_pdf():

        folder = "ExpenseReports"

        os.makedirs(folder, exist_ok=True)

        filename = os.path.join(
            folder,
            f"Expense_Report_{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf"
        )

        c = canvas.Canvas(filename, pagesize=A4)

        width, height = A4

        y = height - 40

        c.setFont("Helvetica-Bold", 16)

        c.drawString(180, y, "BUGZY EXPENSE REPORT")

        y -= 35

        c.setFont("Helvetica-Bold", 10)

        c.drawString(20, y, "Date")

        c.drawString(90, y, "Category")

        c.drawString(200, y, "Description")

        c.drawString(380, y, "Amount")

        c.drawString(450, y, "Payment")

        y -= 20

        # conn = sqlite3.connect(DB_PATH)
        #
        # cur = conn.cursor()
        #
        # date_filter = filter_date.get()
        #
        # if date_filter:
        #     cur.execute("""
        #         SELECT
        #             expense_date,
        #             category,
        #             description,
        #             amount,
        #             payment_mode,
        #             created_by
        #         FROM expense_master
        #         WHERE expense_date=?
        #         ORDER BY expense_id DESC
        #     """, (date_filter,))
        # else:
        #     cur.execute("""
        #         SELECT
        #             expense_date,
        #             category,
        #             description,
        #             amount,
        #             payment_mode,
        #             created_by
        #         FROM expense_master
        #         ORDER BY expense_id DESC
        #     """)
        #
        # rows = cur.fetchall()
        rows = []

        for item in expense_tree.get_children():
            rows.append(expense_tree.item(item)["values"])

        total = 0

        c.setFont("Helvetica", 9)

        for row in rows:

            if y < 40:
                c.showPage()

                y = height - 40

                c.setFont("Helvetica", 9)

            c.drawString(20, y, str(row[0]))

            c.drawString(90, y, str(row[1]))

            c.drawString(200, y, str(row[2])[:30])

            c.drawString(380, y, str(row[3]))

            c.drawString(450, y, str(row[4]))

            total += float(row[3])

            y -= 18

        y -= 15

        c.setFont("Helvetica-Bold", 12)

        c.drawString(300, y, f"Total Expense : ₹ {total:.2f}")

        c.save()

        # conn.close()

        os.startfile(filename)

        messagebox.showinfo(
            "Success",
            "Expense PDF exported successfully."
        )
        load_expenses()


    win = Toplevel(parent)

    win.title("Expense Manager")

    win.state("zoomed")

    win.configure(bg="#FFF8E7")

    win.grab_set()
    banner = Frame(
        win,
        bg="#DC2626",
        height=80
    )

    banner.pack(fill="x")

    Label(
        banner,
        text="💰 Expense Manager",
        font=("Segoe UI",22,"bold"),
        bg="#DC2626",
        fg="white"
    ).pack(pady=18)
    entry_frame = Frame(
        win,
        bg="#FFF8E7"
    )

    entry_frame.pack(fill="x", padx=15, pady=10)
    date_var = StringVar(
        value=datetime.datetime.now().strftime("%d-%m-%Y")
    )

    category_var = StringVar()

    amount_var = StringVar()

    payment_var = StringVar(value="Cash")

    description_var = StringVar()
    Label(
        entry_frame,
        text="Date",
        bg="#FFF8E7",
        font=("Segoe UI",10,"bold")
    ).grid(row=0,column=0,padx=5,pady=5)

    expense_date = DateEntry(

        entry_frame,

        date_pattern="dd-mm-yyyy",

        width=12

    )

    expense_date.grid(row=0,column=1,padx=5)
    Label(
        entry_frame,
        text="Category",
        bg="#FFF8E7",
        font=("Segoe UI",10,"bold")
    ).grid(row=0,column=2,padx=5)

    category = ttk.Combobox(

        entry_frame,

        textvariable=category_var,

        width=20,

        state="readonly"

    )

    category["values"]=(

        "Rent",

        "Electricity",

        "Internet",

        "Tea & Snacks",

        "Petrol",

        "Courier",

        "Packing",

        "Maintenance",

        "Salary Advance",

        "Miscellaneous"

    )

    category.grid(row=0,column=3,padx=5)
    Label(
        entry_frame,
        text="Amount",
        bg="#FFF8E7",
        font=("Segoe UI",10,"bold")
    ).grid(row=0,column=4,padx=5)

    Entry(

        entry_frame,

        textvariable=amount_var,

        width=15,

        font=("Segoe UI",10)

    ).grid(row=0,column=5,padx=5)
    Label(
        entry_frame,
        text="Payment",
        bg="#FFF8E7",
        font=("Segoe UI",10,"bold")
    ).grid(row=0,column=6,padx=5)

    payment = ttk.Combobox(

        entry_frame,

        textvariable=payment_var,

        width=15,

        state="readonly"

    )

    payment["values"]=(

        "Cash",

        "UPI",

        "Card"

    )

    payment.grid(row=0,column=7,padx=5)
    # ---------- Filter Date ----------
    Label(
        entry_frame,
        text="Filter Date",
        bg="#FFF8E7",
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=8, padx=5)

    filter_date = DateEntry(
        entry_frame,
        date_pattern="dd-mm-yyyy",
        width=12
    )

    filter_date.grid(row=0, column=9, padx=5)
    Label(
        entry_frame,
        text="Description",
        bg="#FFF8E7",
        font=("Segoe UI",10,"bold")
    ).grid(row=1,column=0,pady=10)

    Entry(

        entry_frame,

        textvariable=description_var,

        width=90,

        font=("Segoe UI",10)

    ).grid(
        row=1,
        column=1,
        columnspan=7,
        sticky="w"
    )
    def load_expenses(filter_date_value=None):

        expense_tree.delete(*expense_tree.get_children())

        print("Filter received:", filter_date_value)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        if filter_date_value:

            c.execute("""
                SELECT
                    expense_date,
                    category,
                    description,
                    amount,
                    payment_mode,
                    created_by
                FROM expense_master
                WHERE expense_date=?
                ORDER BY expense_id DESC
            """, (filter_date_value,))

        else:

            c.execute("""
                SELECT
                    expense_date,
                    category,
                    description,
                    amount,
                    payment_mode,
                    created_by
                FROM expense_master
                ORDER BY expense_id DESC
            """)

        rows = c.fetchall()

        print("Rows Found:", rows)

        conn.close()

        for row in rows:
            expense_tree.insert("", END, values=row)
    def search_expenses():
        load_expenses(filter_date.get())
    btn_frame = Frame(entry_frame, bg="#FFF8E7")
    btn_frame.grid(row=2, column=0, columnspan=8, pady=15)

    Button(
        btn_frame,
        text="💾 Add Expense",
        command=save_expense,
        bg="#16A34A",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=18
    ).grid(row=0, column=0, padx=8)
    Button(
        btn_frame,
        text="🔍 Search",
        bg="#2563EB",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=16,
        command=lambda: (
            print("Searching:", filter_date.get()),
            load_expenses(filter_date.get())
        )
    ).grid(row=0, column=1, padx=8)

    Button(
        btn_frame,
        text="🧹 Clear",
        bg="#6B7280",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=16,
        command=lambda: (
    filter_date.set_date(datetime.datetime.now()),
    load_expenses()
)
    ).grid(row=0, column=2, padx=8)
    Button(
        btn_frame,
        text="📊 Export Excel",
        command=export_expense_excel,
        bg="#2563EB",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=18
    ).grid(row=0, column=3, padx=8)

    Button(
        btn_frame,
        text="📄 Export PDF",
        command=export_expense_pdf,
        bg="#DC2626",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=18
    ).grid(row=0, column=4, padx=8)
    columns=(

        "Date",

        "Category",

        "Description",

        "Amount",

        "Payment",

        "User"

    )

    expense_tree=ttk.Treeview(

        win,

        columns=columns,

        show="headings",

        height=18

    )

    for col in columns:

        expense_tree.heading(col,text=col)

        expense_tree.column(col,width=180)

    expense_tree.pack(

        fill="both",

        expand=True,

        padx=15,

        pady=15

    )

    load_expenses()
