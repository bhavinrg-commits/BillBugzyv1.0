import sqlite3
import datetime
import os

from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from tkcalendar import DateEntry
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from config import DB_PATH
def open_product_performance(parent):
    win = Toplevel(parent)
    win.title("Product Performance Report")
    win.state("zoomed")
    win.configure(bg="#F8FAFC")
    summary_frame = Frame(
        win,
        bg="#F8FAFC"
    )
    summary_frame.pack(fill="x", pady=10)
    products_lbl = Label(
        summary_frame,
        text="Products Sold\n0",
        bg="#2563EB",
        fg="white",
        font=("Segoe UI", 14, "bold"),
        width=18,
        height=3
    )
    products_lbl.pack(side=LEFT, padx=10)
    qty_lbl = Label(
        summary_frame,
        text="Total Qty\n0",
        bg="#16A34A",
        fg="white",
        font=("Segoe UI", 14, "bold"),
        width=18,
        height=3
    )
    qty_lbl.pack(side=LEFT, padx=10)
    sales_lbl = Label(
        summary_frame,
        text="Sales Amount\n₹0",
        bg="#F59E0B",
        fg="white",
        font=("Segoe UI", 14, "bold"),
        width=18,
        height=3
    )
    sales_lbl.pack(side=LEFT, padx=10)
    avg_lbl = Label(
        summary_frame,
        text="Avg Qty\n0",
        bg="#DC2626",
        fg="white",
        font=("Segoe UI", 14, "bold"),
        width=18,
        height=3
    )
    avg_lbl.pack(side=LEFT, padx=10)
    banner = Frame(
        win,
        bg="#2563EB",
        height=80
    )
    banner.pack(fill="x")
    filter_frame = Frame(
        win,
        bg="#F8FAFC"
    )
    filter_frame.pack(fill="x", padx=20, pady=15)
    # btn_frame = Frame(win, bg="#F8FAFC")
    # btn_frame.pack(pady=10)
    # banner.pack(fill="x")
    Label(
        banner,
        text="🏆 Product Performance Report",
        bg="#2563EB",
        fg="white",
        font=("Segoe UI",22,"bold")
    ).pack(pady=18)
    # filter_frame.pack(fill="x", padx=20, pady=15)
    filter_frame.pack(fill="x", padx=20, pady=15)
    Label(
        filter_frame,
        text="From Date",
        bg="#F8FAFC",
        font=("Segoe UI",10,"bold")
    ).grid(row=0,column=0,padx=5)
    from_date = DateEntry(
        filter_frame,
        date_pattern="dd-mm-yyyy",
        width=12
    )
    from_date.grid(row=0,column=1,padx=5)
    Label(
        filter_frame,
        text="To Date",
        bg="#F8FAFC",
        font=("Segoe UI",10,"bold")
    ).grid(row=0,column=2,padx=5)
    to_date = DateEntry(
        filter_frame,
        date_pattern="dd-mm-yyyy",
        width=12
    )
    to_date.grid(row=0,column=3,padx=5)
    Label(
        filter_frame,
        text="Show",
        bg="#F8FAFC",
        font=("Segoe UI",10,"bold")
    ).grid(row=0,column=4,padx=5)
    def create_top_tree(parent):
        columns = (
            "Product ID",
            "Product Name",
            "Qty Sold",
            "Sales Amount"
        )
        top_tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings"
        )
        for col in columns:
            top_tree.heading(col, text=col)
        top_tree.column("Product ID", width=120, anchor=CENTER)
        top_tree.column("Product Name", width=450)
        top_tree.column("Qty Sold", width=150, anchor=CENTER)
        top_tree.column("Sales Amount", width=180, anchor=E)
        top_tree.pack(fill="both", expand=True)
        return top_tree
    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=20, pady=15)
    top_frame = Frame(notebook)
    least_frame = Frame(notebook)
    never_frame = Frame(notebook)
    slow_frame = Frame(notebook)
    notebook.add(top_frame, text="🏆 Top Selling")
    notebook.add(least_frame, text="📉 Least Selling")
    notebook.add(never_frame, text="🚫 Never Sold")
    notebook.add(slow_frame, text="🐢 Slow Moving")
    top_tree = create_top_tree(top_frame)
    least_tree = create_top_tree(least_frame)
    never_tree = create_top_tree(never_frame)
    slow_tree = create_top_tree(slow_frame)
    top_var = StringVar(value="10")
    def load_report():
        top_tree.delete(*top_tree.get_children())
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT

                d.productid,

                d.product_name,

                SUM(d.qty) qty,

                SUM(d.line_total) amount

            FROM bill_details d

            JOIN bill_master b

            ON d.bill_no=b.bill_no

            WHERE b.bill_date BETWEEN ? AND ?

            GROUP BY
                d.productid,
                d.product_name

            ORDER BY qty DESC

            LIMIT ?
        """,
                  (
                      from_date.get(),
                      to_date.get(),
                      int(top_var.get())
                  ))

        rows = c.fetchall()

        total_products = len(rows)
        total_qty = 0
        total_sales = 0

        for row in rows:
            top_tree.insert("", END, values=row)

            total_qty += row[2]
            total_sales += row[3]

        conn.close()

        avg = round(total_qty / total_products, 2) if total_products else 0

        products_lbl.config(
            text=f"Products Sold\n{total_products}"
        )

        qty_lbl.config(
            text=f"Total Qty\n{total_qty}"
        )

        sales_lbl.config(
            text=f"Sales Amount\n₹{total_sales:,.2f}"
        )

        avg_lbl.config(
            text=f"Avg Qty\n{avg}"
        )
    def export_excel():

        folder = "Reports"
        os.makedirs(folder, exist_ok=True)

        filename = os.path.join(
            folder,
            f"Top_Selling_Report_{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.xlsx"
        )

        wb = Workbook()
        ws = wb.active
        ws.title = "Top Selling Products"

        ws.append([
            "Product ID",
            "Product Name",
            "Qty Sold",
            "Sales Amount"
        ])

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
            SELECT
                d.productid,
                d.product_name,
                SUM(d.qty) qty,
                SUM(d.line_total) amount
            FROM bill_details d
            JOIN bill_master b
            ON d.bill_no=b.bill_no
            WHERE b.bill_date BETWEEN ? AND ?
            GROUP BY d.productid,d.product_name
            ORDER BY qty DESC
            LIMIT ?
        """,
                  (
                      from_date.get(),
                      to_date.get(),
                      int(top_var.get())
                  ))

        rows = c.fetchall()

        total_qty = 0
        total_sales = 0

        for row in rows:
            ws.append(row)
            total_qty += row[2]
            total_sales += row[3]

        ws.append([])
        ws.append(["", "", "TOTAL QTY", total_qty])
        ws.append(["", "", "TOTAL SALES", total_sales])

        wb.save(filename)
        conn.close()

        os.startfile(filename)

        messagebox.showinfo(
            "Success",
            "Excel exported successfully."
        )

    def export_pdf():

        folder = "Reports"
        os.makedirs(folder, exist_ok=True)

        filename = os.path.join(
            folder,
            f"Top_Selling_Report_{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf"
        )

        pdf = canvas.Canvas(filename, pagesize=A4)

        width, height = A4
        y = height - 40

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(170, y, "BUGZY PRODUCT PERFORMANCE REPORT")

        y -= 35

        pdf.setFont("Helvetica-Bold", 10)

        pdf.drawString(20, y, "Product ID")
        pdf.drawString(110, y, "Product Name")
        pdf.drawString(360, y, "Qty")
        pdf.drawString(430, y, "Sales")

        y -= 20

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
            SELECT
                d.productid,
                d.product_name,
                SUM(d.qty) qty,
                SUM(d.line_total) amount
            FROM bill_details d
            JOIN bill_master b
            ON d.bill_no=b.bill_no
            WHERE b.bill_date BETWEEN ? AND ?
            GROUP BY d.productid,d.product_name
            ORDER BY qty DESC
            LIMIT ?
        """,
                  (
                      from_date.get(),
                      to_date.get(),
                      int(top_var.get())
                  ))

        rows = c.fetchall()

        total_qty = 0
        total_sales = 0

        pdf.setFont("Helvetica", 9)

        for row in rows:

            if y < 50:
                pdf.showPage()
                y = height - 40
                pdf.setFont("Helvetica", 9)

            pdf.drawString(20, y, str(row[0]))
            pdf.drawString(110, y, str(row[1])[:35])
            pdf.drawRightString(395, y, str(row[2]))
            pdf.drawRightString(520, y, f"{row[3]:,.2f}")

            total_qty += row[2]
            total_sales += row[3]

            y -= 18

        y -= 20

        pdf.setFont("Helvetica-Bold", 11)

        pdf.drawString(250, y, f"Total Qty : {total_qty}")

        y -= 18

        pdf.drawString(250, y, f"Total Sales : ₹ {total_sales:,.2f}")

        pdf.save()

        conn.close()

        os.startfile(filename)

        messagebox.showinfo(
            "Success",
            "PDF exported successfully."
        )

    # Button(
    #     filter_frame,
    #     text="Search",
    #     bg="#16A34A",
    #     fg="white",
    #     font=("Segoe UI", 11, "bold"),
    #     width=15,
    #     command=load_report
    # ).grid(row=0, column=6, padx=15)
    #
    # Button(
    #     filter_frame,
    #     text="📊 Export Excel",
    #     bg="#2563EB",
    #     fg="white",
    #     font=("Segoe UI", 11, "bold"),
    #     width=15,
    #     command=export_excel
    # ).grid(row=0, column=7, padx=8)
    #
    # Button(
    #     filter_frame,
    #     text="📄 Export PDF",
    #     bg="#DC2626",
    #     fg="white",
    #     font=("Segoe UI", 11, "bold"),
    #     width=15,
    #     command=export_pdf
    # ).grid(row=0, column=8, padx=8)
    #
    # Button(
    #     filter_frame,
    #     text="Back",
    #     bg="#6B7280",
    #     fg="white",
    #     font=("Segoe UI", 11, "bold"),
    #     width=15,
    #     command=win.destroy
    # ).grid(row=0, column=9, padx=8)
    # load_report()
    # # top_var = StringVar(value="10")
    # top_combo = ttk.Combobox(
    #     filter_frame,
    #     width=10,
    #     textvariable=top_var,
    #     state="readonly"
    # )
    # top_combo["values"]=("10","200")
    # top_combo.grid(row=0,column=5,padx=5)
    # columns=(
    #
    #     "Product ID",
    #
    #     "Product Name",
    #
    #     "Qty Sold",
    #
    #     "Sales Amount"
    #
    # )
    # ----------------------------
    # Show Combo
    # ----------------------------

    top_combo = ttk.Combobox(
        filter_frame,
        width=10,
        textvariable=top_var,
        state="readonly"
    )

    top_combo["values"] = ("10", "20", "50", "100", "200")
    top_combo.current(0)
    top_combo.grid(row=0, column=5, padx=5)

    # ----------------------------
    # Buttons
    # ----------------------------

    Button(
        filter_frame,
        text="Search",
        bg="#16A34A",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=15,
        command=load_report
    ).grid(row=0, column=6, padx=10)

    Button(
        filter_frame,
        text="📊 Export Excel",
        bg="#2563EB",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=15,
        command=export_excel
    ).grid(row=0, column=7, padx=5)

    Button(
        filter_frame,
        text="📄 Export PDF",
        bg="#DC2626",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=15,
        command=export_pdf
    ).grid(row=0, column=8, padx=5)

    Button(
        filter_frame,
        text="Back",
        bg="#6B7280",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=15,
        command=win.destroy
    ).grid(row=0, column=9, padx=5)

    # ----------------------------
    # Finally load data
    # ----------------------------

    load_report()




