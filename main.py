import os
import sys
import barcode
from barcode.writer import ImageWriter
import os
import win32print
import win32ui
from PIL import ImageWin

import win32print


def print_tspl_label(barcode_no, product_name, mrp, sell_price, qty):

    printer_name = "4BARCODE 4B-2054N"

    hPrinter = win32print.OpenPrinter(printer_name)

    try:

        tspl = f"""
SIZE 38 mm,38 mm
GAP 2 mm,0 mm
DENSITY 10
SPEED 4
DIRECTION 1
REFERENCE 0,0
OFFSET 0 mm
CLS

BARCODE 15,20,"128",70,1,0,2,2,"{barcode_no}"

TEXT 60,100,"3",0,1,1,"{barcode_no}"

BAR 10,125,280,2

TEXT 10,140,"3",0,1,1,"BUGZY"

TEXT 10,170,"2",0,1,1,"{product_name[:20]}"

TEXT 10,200,"2",0,1,1,"MRP : {mrp}"

TEXT 10,225,"2",0,1,1,"Price : {sell_price}"

TEXT 10,250,"2",0,1,1,"Qty : {qty}"

PRINT 1
"""

        hJob = win32print.StartDocPrinter(
            hPrinter,
            1,
            ("Barcode Label", None, "RAW")
        )

        win32print.StartPagePrinter(hPrinter)

        win32print.WritePrinter(
            hPrinter,
            tspl.encode("utf-8")
        )

        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)

    finally:
        win32print.ClosePrinter(hPrinter)


if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "store.db")


import datetime
from tkcalendar import DateEntry
from tkinter import *
import sqlite3
from tkinter import ttk
from PIL import Image, ImageTk   # use Pillow for JPG/PNG
from tkinter import ttk, messagebox
print("Using database:", DB_PATH)



def enable_cell_copy(tree):
    """
    Lets the user right-click a Treeview cell to copy its value (or the
    whole row), and press Ctrl+C to copy the last-clicked cell.
    Call this once on any ttk.Treeview right after it's created.
    """
    last_cell = {"row": None, "col": None}

    def remember_cell(event):
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        if row and col:
            last_cell["row"] = row
            last_cell["col"] = col

    def get_cell_value():
        row, col = last_cell["row"], last_cell["col"]
        if not row or not col:
            return None
        try:
            col_index = int(col.replace("#", "")) - 1
        except ValueError:
            return None
        values = tree.item(row)["values"]
        if values and 0 <= col_index < len(values):
            return values[col_index]
        return None

    def copy_cell(event=None):
        value = get_cell_value()
        if value is not None:
            tree.clipboard_clear()
            tree.clipboard_append(str(value))

    def copy_row(event=None):
        row = last_cell["row"] or (tree.selection()[0] if tree.selection() else None)
        if not row:
            return
        values = tree.item(row)["values"]
        text = "\t".join(str(v) for v in values)
        tree.clipboard_clear()
        tree.clipboard_append(text)

    def show_context_menu(event):
        remember_cell(event)
        row = tree.identify_row(event.y)
        if row:
            tree.selection_set(row)
        menu = Menu(tree, tearoff=0)
        menu.add_command(label="📋 Copy Cell", command=copy_cell)
        menu.add_command(label="📋 Copy Row", command=copy_row)
        menu.tk_popup(event.x_root, event.y_root)

    tree.bind("<Button-1>", remember_cell, add="+")
    tree.bind("<Button-3>", show_context_menu)
    tree.bind("<Control-c>", copy_cell)

def open_customers():
    cust_win = Toplevel(window)
    cust_win.title("Customer Management")
    cust_win.state("zoomed")
    cust_win.configure(bg="#FFF8E7")
    cust_win.grab_set()

    # ================= Background =================
    top_frame = Frame(cust_win, bg="#4ECDC4")
    top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.30)

    bottom_frame = Frame(cust_win, bg="#FFF8E7")
    bottom_frame.place(relx=0, rely=0.40, relwidth=1, relheight=0.60)

    # ================= Header =================
    Label(
        top_frame,
        text="Customer Management",
        bg="#FFF8E7",
        fg="#1E3A5F",
        font=("Segoe UI", 28, "bold")
    ).pack(pady=35)

    Label(
        top_frame,
        text="Manage your customers and view customer records",
        bg="#4ECDC4",
        fg="white",
        font=("Segoe UI", 12)
    ).pack()

    # ================= Button Container =================
    btn_frame = Frame(bottom_frame, bg="#FFF8E7")
    btn_frame.pack(expand=True)

    # -------- Customer Details --------

    button_frame = Frame(bottom_frame, bg="#FFF8E7")
    button_frame.pack(pady=15)


    Button(
        btn_frame,
        text="👥\nCustomer Details",
        font=("Segoe UI", 18, "bold"),
        bg="#F59E0B",
        fg="white",
        width=18,
        height=4,
        relief="flat",
        bd=0,
        cursor="hand2",
        command=lambda: show_all_customers(cust_win)
    ).grid(row=0, column=0, padx=40, pady=40)

    # -------- Add Customer --------
    Button(
        btn_frame,
        text="➕\nAdd Customer",
        font=("Segoe UI", 18, "bold"),
        bg="#10B981",
        fg="white",
        width=18,
        height=4,
        relief="flat",
        bd=0,
        cursor="hand2",
        command=lambda: add_customer(cust_win)
    ).grid(row=0, column=1, padx=40, pady=40)

    # -------- Back --------
    Button(
        bottom_frame,
        text="← Back",
        font=("Segoe UI", 11, "bold"),
        bg="#EF4444",
        fg="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        command=cust_win.destroy
    ).pack(pady=20)



def add_customer(parent, mobile="", callback=None):
    win = Toplevel(parent)
    win.title("Add Customer")
    win.geometry("600x450")
    win.configure(bg="#D6EAF8")
    win.grab_set()

    customer_id = int(datetime.datetime.now().timestamp())
    entry_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    Label(win,text=f"Customer ID : {customer_id}",
          font=("arial",12,"bold"),
          bg="#D6EAF8").pack(pady=10)

    name_var = StringVar()
    mobile_var = StringVar(value=mobile)
    address_var = StringVar()

    Label(win,text="Customer Name",bg="#FFF8E7").pack()
    Entry(win,textvariable=name_var,width=35,bg="#FFFFFF",fg="#1F2937").pack()

    Label(win,text="Mobile Number",bg="#FFF8E7").pack()
    Entry(win,textvariable=mobile_var,width=35,bg="#FFFFFF",fg="#1F2937").pack()

    Label(win,text="Address / City",bg="#FFF8E7").pack()
    Entry(win,textvariable=address_var,width=35,bg="#FFFFFF",fg="#1F2937").pack()

    def save_customer():

        if name_var.get()=="":
            messagebox.showerror("Error","Customer name required")
            return

        try:

            with sqlite3.connect(DB_PATH) as conn:

                c=conn.cursor()

                c.execute("""
                INSERT INTO customer_master
                VALUES(?,?,?,?,?)
                """,
                (
                    customer_id,
                    name_var.get(),
                    mobile_var.get(),
                    address_var.get(),
                    entry_time
                ))

                conn.commit()

            messagebox.showinfo("Success", "Customer Added Successfully")

            if callback:
                callback()

            win.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error","Mobile Number already exists")

    Button(
        win,
        text="Save Customer",
        bg="#27AE60",
        fg="white",
        font=("arial",12,"bold"),
        command=save_customer
    ).pack(pady=25)

def show_all_customers(parent):

    win = Toplevel(parent)
    win.title("Customer Details")
    win.state("zoomed")
    win.configure(bg="#FFF8E7")

    # ================= Header =================

    top_frame = Frame(win, bg="#3B82F6")
    top_frame.pack(fill="x")

    Label(
        top_frame,
        text="👥 Customer Details",
        bg="#3B82F6",
        fg="white",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(12, 2))

    Label(
        top_frame,
        text="Search, Update and Delete Customer Records",
        bg="#3B82F6",
        fg="white",
        font=("Segoe UI", 10)
    ).pack(pady=(0, 12))

    # ================= Search =================

    search_var = StringVar()

    search_frame = Frame(win, bg="#FFF8E7")
    search_frame.pack(fill="x", padx=15, pady=12)

    Label(
        search_frame,
        text="Search :",
        bg="#FFF8E7",
        fg="#374151",
        font=("Segoe UI", 11, "bold")
    ).pack(side="left")

    search_entry = Entry(
        search_frame,
        textvariable=search_var,
        width=35,
        font=("Segoe UI", 11)
    )
    search_entry.pack(side="left", padx=10)

    search_btn = Button(
        search_frame,
        text="🔍 Search",
        bg="#3B82F6",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=12,
        command=lambda: search_customer()
    )

    search_btn.pack(side="left", padx=5)

    refresh_btn = Button(
        search_frame,
        text="🔄 Refresh",
        bg="#10B981",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=12,
        command=lambda: refresh_customer()
    )

    refresh_btn.pack(side="left", padx=5)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Customer.Treeview",
        background="FFFDF7",
        foreground="#374151",
        fieldbackground="#FFFDF7",
        rowheight=34,
        font=("Segoe UI", 10)
    )
    style.configure(
        "Customer.Treeview.Heading",
        background="#3B82F6",
        foreground="white",
        font=("Segoe UI", 11, "bold")
    )
    style.map(
        "Customer.Treeview",
        background=[("selected", "#D6EFFF")],
        foreground=[("selected", "black")]
    )
    tree = ttk.Treeview(
        win,
        columns=("ID", "Name", "Mobile", "Address", "Created"),
        show="headings",
        style="Customer.Treeview"
    )

    cols=("ID","Name","Mobile","Address","Created")

    for col in cols:
        tree.heading(col,text=col)
        tree.column(col,width=220)

    # tree.pack(fill="both",expand=True,padx=15,pady=10)
    tree.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=(5, 10)
    )
    enable_cell_copy(tree)

    def load_customers():

        tree.delete(*tree.get_children())

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            c.execute("""
                SELECT *
                FROM customer_master
                ORDER BY customer_name
            """)

            rows = c.fetchall()

        for row in rows:
            tree.insert("", END, values=row)

    def search_customer():

        keyword = search_var.get().strip()

        tree.delete(*tree.get_children())

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            c.execute("""
                SELECT *
                FROM customer_master
                WHERE customer_name LIKE ?
                   OR mobile LIKE ?
                   OR address LIKE ?
                ORDER BY customer_name
            """, (
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%"
            ))

            rows = c.fetchall()

        for row in rows:
            tree.insert("", "end", values=row)

    def refresh_customer():
        search_var.set("")
        load_customers()

    def update_customer():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No customer selected")
            return

        vals = tree.item(selected[0])["values"]
        customer_id = vals[0]

        upd_win = Toplevel(win)
        upd_win.title("Update Customer")
        upd_win.geometry("400x350")
        upd_win.configure(bg="#D6EAF8")
        upd_win.grab_set()

        name_var = StringVar(value=vals[1])
        mobile_var = StringVar(value=vals[2])
        address_var = StringVar(value=vals[3])

        for lbl, var in [
            ("Customer Name", name_var),
            ("Mobile Number", mobile_var),
            ("Address / City", address_var)
        ]:
            Label(upd_win, text=lbl, font=("arial", 12, "bold"), bg="#D6EAF8").pack(pady=(15, 0))
            Entry(upd_win, textvariable=var, width=30, font=("arial", 12)).pack(pady=5)

        def save_update():
            if name_var.get().strip() == "":
                messagebox.showerror("Error", "Customer Name is required.")
                return
            if mobile_var.get().strip() == "":
                messagebox.showerror("Error", "Mobile Number is required.")
                return
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    c = conn.cursor()
                    c.execute("""
                        UPDATE customer_master
                        SET customer_name=?, mobile=?, address=?
                        WHERE customer_id=?
                    """, (
                        name_var.get().strip(),
                        mobile_var.get().strip(),
                        address_var.get().strip(),
                        customer_id
                    ))
                    conn.commit()
                messagebox.showinfo("Updated", "Customer updated successfully!")
                upd_win.destroy()
                load_customers()
            except sqlite3.IntegrityError:
                messagebox.showerror("Duplicate", "This mobile number already exists.")

        Button(
            upd_win,
            text="Save Update",
            bg="#27AE60",
            fg="white",
            font=("arial", 12, "bold"),
            command=save_update
        ).pack(pady=20)

    def delete_customer():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No customer selected")
            return

        vals = tree.item(selected[0])["values"]
        customer_id = vals[0]
        customer_name = vals[1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete customer '{customer_name}'?"
        )
        if not confirm:
            return

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM customer_master WHERE customer_id=?", (customer_id,))
            conn.commit()

        messagebox.showinfo("Deleted", f"Customer '{customer_name}' deleted successfully!")
        load_customers()

    bottom_frame = Frame(win, bg="#FFF8E7")
    bottom_frame.pack(fill="x", pady=12)
    update_btn = Button(
        bottom_frame,
        text="✏ Update",
        bg="#3B82F6",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=14,
        command=update_customer
    )

    update_btn.pack(side="left", padx=10)

    delete_btn = Button(
        bottom_frame,
        text="🗑 Delete",
        bg="#EF4444",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=14,
        command=delete_customer
    )

    delete_btn.pack(side="left", padx=10)
    load_customers()

    Button(
        bottom_frame,
        text="← Back",
        bg="#6B7280",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=14,
        command=win.destroy
    ).pack(side="right", padx=10)


def open_products():
    prod_win = Toplevel(window)
    prod_win.title("Products")
    prod_win.state("zoomed")
    prod_win.configure(bg="#FFF8E7")
    prod_win.grab_set()

    # ================= Top Banner =================
    top_frame = Frame(prod_win, bg="#6366F1")
    top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.30)

    Label(
        top_frame,
        text="Product Management",
        bg="#6366F1",
        fg="white",
        font=("Segoe UI", 28, "bold")
    ).pack(pady=35)

    Label(
        top_frame,
        text="Add, view, update and delete your products",
        bg="#6366F1",
        fg="white",
        font=("Segoe UI", 12)
    ).pack()

    # ================= Bottom Section =================
    bottom_frame = Frame(prod_win, bg="#FFF8E7")
    bottom_frame.place(relx=0, rely=0.30, relwidth=1, relheight=0.70)

    # ================= Button Grid =================
    btn_frame = Frame(bottom_frame, bg="#FFF8E7")
    btn_frame.pack(expand=True)

    def check_password_and_add():
        pass_win = Toplevel(prod_win)
        pass_win.title("Enter Password")
        pass_win.geometry("300x180")
        pass_win.resizable(False, False)
        pass_win.grab_set()
        pass_win.focus_force()

        Label(pass_win, text="Enter Admin Password:",
              font=("Arial", 11, "bold")).pack(pady=15)

        pass_var = StringVar()
        pass_entry = Entry(pass_win, textvariable=pass_var,
                           show="*", font=("Arial", 13), width=15, justify="center")
        pass_entry.pack(pady=5)
        pass_entry.focus_set()

        def verify():
            if pass_var.get() == "bugzy123":
                pass_win.destroy()
                add_product(prod_win)
            else:
                pass_var.set("")
                messagebox.showerror("Access Denied", "Wrong Password!", parent=pass_win)
                pass_entry.focus_set()

        Button(pass_win, text="Submit", bg="#27AE60", fg="white",
               font=("Arial", 11, "bold"), width=12,
               command=verify).pack(pady=15)

        pass_win.bind("<Return>", lambda e: verify())

    # Show All Products
    Button(
        btn_frame,
        text="📦\nShow All Products",
        font=("Segoe UI", 18, "bold"),
        bg="#6366F1",
        fg="white",
        width=18,
        height=4,
        relief="flat",
        bd=0,
        cursor="hand2",
        command=lambda: show_all_products(prod_win)
    ).grid(row=0, column=0, padx=40, pady=40)

    # Add Product
    Button(
        btn_frame,
        text="➕\nAdd Product",
        font=("Segoe UI", 18, "bold"),
        bg="#10B981",
        fg="white",
        width=18,
        height=4,
        relief="flat",
        bd=0,
        cursor="hand2",
        command=check_password_and_add
    ).grid(row=0, column=1, padx=40, pady=40)

    # Back Button
    Button(
        bottom_frame,
        text="← Back",
        font=("Segoe UI", 11, "bold"),
        bg="#EF4444",
        fg="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        command=prod_win.destroy
    ).pack(pady=20)

def add_product(parent_win):
    add_win = Toplevel(parent_win)
    add_win.title("Add Product")
    add_win.state("zoomed")
    add_win.configure(bg="#FFF8E7")
    add_win.grab_set()

    productid = int(datetime.datetime.now().timestamp())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ================= Top Banner =================
    top_frame = Frame(add_win, bg="#10B981")
    top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.22)

    Label(top_frame, text="Add New Product", bg="#10B981", fg="white",
          font=("Segoe UI", 28, "bold")).pack(pady=25)

    Label(top_frame, text=f"Product ID (auto): {productid}   |   Entry Time: {timestamp}",
          bg="#10B981", fg="white", font=("Segoe UI", 11)).pack()

    # ================= Form Section =================
    form_frame = Frame(add_win, bg="#FFF8E7")
    form_frame.place(relx=0.1, rely=0.28, relwidth=0.80, relheight=0.60)

    # Entry fields
    name_var = StringVar()
    sell_var = DoubleVar()
    wholesale_var = DoubleVar()
    qty_var = IntVar()
    mrp_var = DoubleVar()
    cat_var = StringVar()

    fields = [
        ("Product Name",    name_var,        0, 0),
        ("Sell Price",      sell_var,        0, 2),
        ("Wholesale Price", wholesale_var,   0, 4),
        ("Quantity",        qty_var,         1, 0),
        ("MRP",             mrp_var,         1, 2),
        ("Category",        cat_var,         1, 4),
    ]

    entries = {}
    for label_text, var, row, col in fields:
        Label(form_frame, text=label_text, font=("Segoe UI", 12, "bold"),
              bg="#FFF8E7", fg="#1F2937").grid(row=row, column=col, padx=15, pady=20, sticky="e")

        e = Entry(form_frame, textvariable=var, font=("Segoe UI", 12),
                  width=16, bg="white", fg="#1F2937", relief="solid", bd=1)
        e.grid(row=row, column=col+1, padx=5, pady=20, sticky="w")
        entries[label_text] = e

    # Focus on first field
    entries["Product Name"].focus_set()

    # Barcode value = product id, zero-padded to 6 digits
    barcode_value = str(productid)[-6:]  # last 6 digits of timestamp id, keeps it short

    barcode_frame = Frame(add_win, bg="#FFF8E7")
    barcode_frame.place(relx=0.1, rely=0.90, relwidth=0.80, relheight=0.08)

    Label(barcode_frame, text=f"Barcode: {barcode_value}", font=("Segoe UI", 12, "bold"),
          bg="#FFF8E7", fg="#1F2937").pack(side="left", padx=10)

    def generate_and_print_label():
        # Validate required fields first
        if not name_var.get().strip():
            messagebox.showerror("Error", "Enter Product Name first.")
            return

        # 1. Generate barcode image
        # code128 = barcode.get("code128", barcode_value, writer=ImageWriter())

        from barcode.writer import ImageWriter

        writer = ImageWriter()
        writer.set_options({
            "write_text": False,  # <-- remove built-in number
            "module_width": 0.35,
            "module_height": 18,
            "quiet_zone": 2,
            "font_size": 0
        })

        # code128 = barcode.get("code128", barcode_value, writer=writer)
        from barcode.writer import ImageWriter

        writer = ImageWriter()

        writer.set_options({
            "write_text": False,
            "module_height": 20,
            "module_width": 0.4,
            "quiet_zone": 2
        })

        code128 = barcode.get(
            "code128",
            barcode_value,
            writer=writer
        )
        barcode_folder = "barcodes"
        os.makedirs(barcode_folder, exist_ok=True)
        barcode_path = code128.save(os.path.join(barcode_folder, f"barcode_{barcode_value}"))
        # barcode_path -> e.g. "barcodes/barcode_123456.png"

        # 2. Build the label (barcode + text) using PIL
        from PIL import Image, ImageDraw, ImageFont

        barcode_img = Image.open(barcode_path)

        label_w = 304
        label_h = 304

        label = Image.new("RGB", (label_w, label_h), "white")
        draw = ImageDraw.Draw(label)

        # Barcode nearly full width
        barcode_width = 290
        barcode_height = 105

        bc_resized = barcode_img.resize(
            (barcode_width, barcode_height),
            Image.Resampling.LANCZOS
        )

        x = (label_w - barcode_width) // 2
        label.paste(bc_resized, (x, 10))

        draw = ImageDraw.Draw(label)
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 30)
            text_font = ImageFont.truetype("arialbd.ttf", 23)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Barcode Number (centered below barcode)

        barcode_text = barcode_value

        bbox = draw.textbbox((0, 0), barcode_text, font=title_font)
        text_width = bbox[2] - bbox[0]

        draw.text(
            ((label_w - text_width) // 2, 165),
            barcode_text,
            fill="black",
            font=title_font
        )

        # ---------------- Divider ----------------
        draw.line(
            [(35, 205), (270, 205)],
            fill="black",
            width=2
        )

        # ---------------- Product Details ----------------

        y = 220

        draw.text(
            (20, y),
            "BUGZY",
            font=title_font,
            fill="black"
        )

        y += 40

        draw.text(
            (20, y),
            name_var.get(),
            font=text_font,
            fill="black"
        )

        y += 35

        draw.text(
            (20, y),
            f"MRP : ₹{mrp_var.get():.2f}",
            font=text_font,
            fill="black"
        )

        y += 35

        draw.text(
            (20, y),
            f"Price : ₹{sell_var.get():.2f}",
            font=text_font,
            fill="black"
        )

        y += 35

        draw.text(
            (35, y),
            f"Qty : {qty_var.get()}",
            font=text_font,
            fill="black"
        )

        # 3. Save final label and open it (for printing via default image viewer)
        final_path = os.path.join(barcode_folder, f"label_{barcode_value}.png")
        label.save(final_path)
        # os.startfile(final_path, "print")  # sends straight to default printer
        print_tspl_label(
            barcode_value,
            name_var.get(),
            mrp_var.get(),
            sell_var.get(),
            qty_var.get()
        )
        messagebox.showinfo("Success", f"Label generated & sent to printer.\nBarcode: {barcode_value}")

    Button(barcode_frame, text="🖨 Generate & Print Barcode Label", font=("Segoe UI", 11, "bold"),
           bg="#6366F1", fg="white", relief="flat", cursor="hand2",
           command=generate_and_print_label).pack(side="left", padx=15)

    def print_image_to_printer(image_path):

        printer_name = win32print.GetDefaultPrinter()

        # hDC = win32ui.CreateDC()
        # hDC.CreatePrinterDC(printer_name)
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC("4BARCODE 4B-2054N")

        printable_area = hDC.GetDeviceCaps(8), hDC.GetDeviceCaps(10)

        bmp = Image.open(image_path)

        # Image size in pixels
        img_w, img_h = bmp.size

        dib = ImageWin.Dib(bmp)

        hDC.StartDoc("Barcode Label")
        hDC.StartPage()

        LEFT_OFFSET = 8  # adjust 5-15 pixels
        TOP_OFFSET = 0

        dib.draw(
            hDC.GetHandleOutput(),
            (
                LEFT_OFFSET,
                TOP_OFFSET,
                img_w + LEFT_OFFSET,
                img_h + TOP_OFFSET
            )
        )

        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()
    # ================= Save Button =================
    def save_product():
        if name_var.get().strip() == "":
            messagebox.showerror("Error", "Product Name is required!", parent=add_win)
            return
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("""CREATE TABLE IF NOT EXISTS product_master (
                                productid INTEGER PRIMARY KEY,
                                name TEXT,
                                sell_price REAL,
                                wholesale_price REAL,
                                quantity INTEGER,
                                mrp REAL,
                                category TEXT,
                                entry_time TEXT
                            )""")
                # c.execute("INSERT INTO product_master VALUES (?,?,?,?,?,?,?,?)",
                #           (productid, name_var.get().strip(), sell_var.get(),
                #            wholesale_var.get(), qty_var.get(), mrp_var.get(),
                #            cat_var.get().strip(), timestamp))
                c.execute("""
                    INSERT INTO product_master (productid, name, sell_price, wholesale_price, quantity, mrp, category, entry_time, barcode)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (productid, name_var.get(), sell_var.get(), wholesale_var.get(),
                      qty_var.get(), mrp_var.get(), cat_var.get(), timestamp, barcode_value))
                conn.commit()
            messagebox.showinfo("Success", f"Product '{name_var.get()}' saved successfully!")
            add_win.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to save: {e}", parent=add_win)

    btn_frame = Frame(add_win, bg="#FFF8E7")
    btn_frame.place(relx=0.1, rely=0.80, relwidth=0.80, relheight=0.12)

    Button(btn_frame, text="← Cancel", bg="#EF4444", fg="white",
           font=("Segoe UI", 16, "bold"), relief="flat", bd=0,
           cursor="hand2", width=18,
           command=add_win.destroy).pack(side="right", padx=10, pady=5)

    Button(btn_frame, text="💾  Save Product", bg="#10B981", fg="white",
           font=("Segoe UI", 16, "bold"), relief="flat", bd=0,
           cursor="hand2", width=22,
           command=save_product).pack(side="right", padx=10, pady=10)

    add_win.bind("<Return>", lambda e: save_product())

#show all products functionality
def show_all_products(parent_win):
    show_win = Toplevel(parent_win)
    show_win.title("All Products")
    show_win.geometry("700x400")
    show_win.configure(bg="#FFF8E7")
    show_win.state("zoomed")

    # Top Banner
    top_banner = Frame(show_win, bg="#6366F1")
    top_banner.pack(fill="x")
    Label(top_banner, text="📦  Product Master Table", font=("Segoe UI", 20, "bold"),
          bg="#6366F1", fg="white").pack(pady=18)

    tree = ttk.Treeview(show_win, columns=("ID", "Name", "Sell", "Wholesale", "Qty", "MRP", "Category", "Time"),
                        show="headings")
    for col in ("ID", "Name", "Sell", "Wholesale", "Qty", "MRP", "Category", "Time"):
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(fill="both", expand=True, padx=10, pady=10)
    enable_cell_copy(tree)

    # Load data
    def load_products():
        tree.delete(*tree.get_children())
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS product_master (
                                productid INTEGER PRIMARY KEY,
                                name TEXT,
                                sell_price REAL,
                                wholesale_price REAL,
                                quantity INTEGER,
                                mrp REAL,
                                category TEXT,
                                entry_time TEXT
                            )""")
            c.execute("SELECT * FROM product_master")
            rows = c.fetchall()
        for r in rows:
            tree.insert("", "end", values=r)

    load_products()
    # Delete selected row
    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No product selected")
            # return
            load_products()
            show_all_products(show_win)
        vals = tree.item(selected[0])["values"]
        productid = vals[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Product {productid}?")
        if not confirm:
            return
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM product_master WHERE productid=?", (productid,))
            conn.commit()
        messagebox.showinfo("Deleted", f"Product {productid} deleted successfully!")
        load_products()
        # todays_sell()
        show_all_products(show_win)

    def ask_password(action_func):
        pass_win = Toplevel(show_win)
        pass_win.title("Enter Password")
        pass_win.geometry("300x180")
        pass_win.resizable(False, False)
        pass_win.grab_set()
        pass_win.focus_force()

        Label(pass_win, text="Enter Admin Password:",
              font=("Arial", 11, "bold")).pack(pady=15)

        pass_var = StringVar()
        pass_entry = Entry(pass_win, textvariable=pass_var,
                           show="*", font=("Arial", 13), width=15, justify="center")
        pass_entry.pack(pady=5)
        pass_entry.focus_set()

        def verify():
            if pass_var.get() == "bugzy123":  # ← same password as Add Product
                pass_win.destroy()
                action_func()
            else:
                pass_var.set("")
                messagebox.showerror("Access Denied", "Wrong Password!", parent=pass_win)
                pass_entry.focus_set()

        Button(pass_win, text="Submit", bg="#27AE60", fg="white",
               font=("Arial", 11, "bold"), width=12,
               command=verify).pack(pady=15)

        pass_win.bind("<Return>", lambda e: verify())

    btn_bar = Frame(show_win, bg="#FFF8E7")
    btn_bar.pack(pady=10)

    Button(btn_bar, text="🗑  Delete Selected", bg="#EF4444", fg="white",
           font=("Segoe UI", 12, "bold"), relief="flat", bd=0, cursor="hand2", width=18,
           command=lambda: ask_password(delete_selected)).grid(row=0, column=0, padx=15)

    Button(btn_bar, text="✏️ Update Selected", bg="#F59E0B", fg="white",
           font=("Segoe UI", 12, "bold"), relief="flat", bd=0, cursor="hand2", width=18,
           command=lambda: ask_password(update_selected)).grid(row=0, column=1, padx=15)

    Button(btn_bar, text="← Back", bg="#6B7280", fg="white",
           font=("Segoe UI", 12, "bold"), relief="flat", bd=0, cursor="hand2", width=18,
           command=show_win.destroy).grid(row=0, column=2, padx=15)

    # Update selected row
    def update_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No product selected")
            # return
            load_products()
            show_all_products(show_win)
        vals = tree.item(selected[0])["values"]
        productid = vals[0]

        upd_win = Toplevel(show_win)
        upd_win.title("Update Product")
        upd_win.geometry("500x400")
        upd_win.configure(bg="#D1F2EB")
        upd_win.grab_set()

        # Pre-fill variables
        name_var = StringVar(value=vals[1])
        sell_var = DoubleVar(value=vals[2])
        wholesale_var = DoubleVar(value=vals[3])
        qty_var = IntVar(value=vals[4])
        mrp_var = DoubleVar(value=vals[5])
        cat_var = StringVar(value=vals[6])

        for lbl, var in [
            ("Product Name", name_var),
            ("Sell Price", sell_var),
            ("Wholesale Price", wholesale_var),
            ("Quantity", qty_var),
            ("MRP", mrp_var),
            ("Category", cat_var)
        ]:
            Label(upd_win, text=lbl, font=("arial", 12, "bold"), bg="#D1F2EB").pack()
            Entry(upd_win, textvariable=var, width=25, font=("arial", 12)).pack(pady=5)

        def save_update():
            confirm = messagebox.askyesno("Confirm Update", f"Are you sure you want to update Product {productid}?")
            if not confirm:
                return
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("""UPDATE product_master
                                 SET name=?, sell_price=?, wholesale_price=?, quantity=?, mrp=?, category=?
                                 WHERE productid=?""",
                          (name_var.get(), sell_var.get(), wholesale_var.get(),
                           qty_var.get(), mrp_var.get(), cat_var.get(), productid))
                conn.commit()
            messagebox.showinfo("Updated", f"Product {productid} updated successfully!")
            upd_win.destroy()
            load_products()
            show_all_products(show_win)

        Button(upd_win, text="Save Update", bg="#27AE60", fg="white",
               font=("arial", 12, "bold"), command=save_update).pack(pady=20)

def open_bills():
    bills_win = Toplevel(window)
    bills_win.title("Bill Records")
    bills_win.state("zoomed")
    bills_win.configure(bg="#FFF8E7")
    bills_win.grab_set()

    def day_wise_sale():
        win = Toplevel(bills_win)
        win.title("Day Wise Sale")
        win.geometry("330x180")
        win.resizable(False, False)
        win.grab_set()

        Label(
            win,
            text="Select Date",
            font=("arial", 12, "bold")
        ).pack(pady=15)

        cal=DateEntry(
            win,
            width=18,
            date_pattern="dd-mm-yyyy",
            font=("arial", 12),
            locale='en_IN',
            firstweekday='monday'
        )

        cal.pack()

        def show_sale():
            selected_date = cal.get()

            from_var.set(selected_date)
            to_var.set(selected_date)
            load_bills()
            win.destroy()
        Button(
            win,
            text="Show Bills",
            bg="#27AE60",
            fg="white",
            font=("arial", 11, "bold"),
            width=15,
            command=show_sale
        ).pack(pady=25)

    top_banner = Frame(bills_win, bg="#3B82F6")
    top_banner.pack(fill="x")
    Label(top_banner, text="📄  Bill Records", font=("Segoe UI", 20, "bold"),
          bg="#3B82F6", fg="white").pack(pady=18)

    # --- Filter Frame ---
    filter_frame = Frame(bills_win, bg="#FFF8E7")
    filter_frame.pack(fill="x", padx=10, pady=5)

    Label(filter_frame, text="From Date (DD-MM-YYYY):", font=("arial", 10, "bold"), bg="#D1F2EB").grid(row=0, column=0, padx=5, pady=5)
    from_var = StringVar(value=datetime.datetime.now().strftime("%d-%m-%Y"))
    Entry(filter_frame, textvariable=from_var, font=("arial", 10), width=12).grid(row=0, column=1, padx=5)

    Label(filter_frame, text="To Date (DD-MM-YYYY):", font=("arial", 10, "bold"), bg="#D1F2EB").grid(row=0, column=2, padx=5, pady=5)
    to_var = StringVar(value=datetime.datetime.now().strftime("%d-%m-%Y"))
    Entry(filter_frame, textvariable=to_var, font=("arial", 10), width=12).grid(row=0, column=3, padx=5)
    Button(filter_frame, text="🔍 Search", font=("Segoe UI", 10, "bold"),
           bg="#6366F1", fg="white", relief="flat", cursor="hand2",
           command=lambda: load_bills()).grid(row=0, column=4, padx=10)
    Button(filter_frame, text="📅 Today", font=("Segoe UI", 10, "bold"),
           bg="#10B981", fg="white", relief="flat", cursor="hand2",
           command=lambda: (
               from_var.set(datetime.datetime.now().strftime("%d-%m-%Y")),
               to_var.set(datetime.datetime.now().strftime("%d-%m-%Y")),
               load_bills()
           )).grid(row=0, column=5, padx=5)
    Button(filter_frame, text="📊 Day Wise", font=("Segoe UI", 10, "bold"),
           bg="#F59E0B", fg="white", relief="flat", cursor="hand2",
           command=day_wise_sale).grid(row=0, column=6, padx=5)
    selected_date_var = StringVar(value="")

    Label(
        bills_win,
        textvariable=selected_date_var,
        font=("Segoe UI", 16, "bold"),
        bg="#FFF8E7",
        fg="#1E3A8A"
    ).pack(pady=(10, 5))
    summary_frame = Frame(bills_win, bg="#FFF8E7")
    summary_frame.pack(fill="x", pady=10)
    card_frame = Frame(summary_frame, bg="#FFF8E7")
    card_frame.pack(anchor="center")
    bill_var = StringVar(value="0")
    cash_var = StringVar(value="₹0")
    upi_var = StringVar(value="₹0")
    card_var = StringVar(value="₹0")
    total_var = StringVar(value="₹0")

    create_card(card_frame, "Bills", bill_var, "#3B82F6").grid(row=0, column=0, padx=10)
    create_card(card_frame, "💵 Cash", cash_var, "#10B981").grid(row=0, column=1, padx=10)
    create_card(card_frame, "📱 UPI", upi_var, "#8B5CF6").grid(row=0, column=2, padx=10)
    create_card(card_frame, "💳 Card", card_var, "#F59E0B").grid(row=0, column=3, padx=10)
    create_card(card_frame, "Total", total_var, "#EF4444").grid(row=0, column=4, padx=10)
    # --- Bills Table ---
    cols = ("Bill No", "Customer", "Contact", "Total", "Date", "Time","Payment")
    bill_tree = ttk.Treeview(bills_win, columns=cols, show="headings", height=8)
    for col in cols:
        bill_tree.heading(col, text=col)
        bill_tree.column(col, width=160)

    # Make Payment column slightly narrower
    bill_tree.column("Payment", width=120, anchor="center")
    bill_tree.pack(fill="x", padx=10, pady=10)
    enable_cell_copy(bill_tree)

    # --- Items Table (shown on bill selection) ---
    Label(bills_win, text="Bill Items", font=("Segoe UI", 12, "bold"), bg="#FFF8E7", fg="#1F2937").pack()
    item_cols = ("Product", "Qty", "Price", "Total")
    item_tree = ttk.Treeview(bills_win, columns=item_cols, show="headings", height=3)
    for col in item_cols:
        item_tree.heading(col, text=col)
        item_tree.column(col, width=200)
    item_tree.pack(fill="both", padx=10, pady=5)
    enable_cell_copy(item_tree)

    def load_bills():
        bill_tree.delete(*bill_tree.get_children())
        try:
            from_date = datetime.datetime.strptime(from_var.get(), "%d-%m-%Y").strftime("%d-%m-%Y")
            to_date   = datetime.datetime.strptime(to_var.get(),   "%d-%m-%Y").strftime("%d-%m-%Y")
            if from_date == to_date:
                selected_date_var.set(f"📅 Business Summary - {from_date}")
            else:
                selected_date_var.set(f"📅 Business Summary ({from_date}  to  {to_date})")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY")
            return

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT bill_no, customer_name, contact, total, bill_date, bill_time,payment_mode
                FROM bill_master
                WHERE bill_date BETWEEN ? AND ?
                ORDER BY bill_id DESC
            """, (from_date, to_date))
            rows = c.fetchall()

        total_collection = 0.0
        cash_total = 0.0
        upi_total = 0.0
        card_total = 0.0

        for r in rows:

            payment = r[6]

            if payment == "Cash":
                cash_total += float(r[3])
                payment_text = "💵 Cash"

            elif payment == "UPI":
                upi_total += float(r[3])
                payment_text = "📱 UPI"

            elif payment == "Card":
                card_total += float(r[3])
                payment_text = "💳 Card"

            else:
                payment_text = payment

            bill_tree.insert(
                "",
                "end",
                values=(
                    r[0],
                    r[1],
                    r[2],
                    f"₹{float(r[3]):,.2f}",
                    r[4],
                    r[5],
                    payment_text
                )
            )

            total_collection += float(r[3])
        bill_var.set(len(rows))
        cash_var.set(f"₹{cash_total:,.2f}")
        upi_var.set(f"₹{upi_total:,.2f}")
        card_var.set(f"₹{card_total:,.2f}")
        total_var.set(f"₹{total_collection:,.2f}")

    def on_bill_select(event):
        selected = bill_tree.selection()
        if not selected:
            return
        bill_no = bill_tree.item(selected[0])["values"][0]
        item_tree.delete(*item_tree.get_children())
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT product_name, qty, price, total
                FROM bill_items
                WHERE bill_id = (SELECT bill_id FROM bill_master WHERE bill_no=?)
            """, (bill_no,))
            for row in c.fetchall():
                item_tree.insert("", "end", values=row)

    def reprint_bill():
        import os, sys
        selected = bill_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a bill to reprint.")
            return
        bill_no = bill_tree.item(selected[0])["values"][0]

        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        pdf_path = os.path.join(base_dir, "Bills", f"{bill_no}.pdf")
        if os.path.exists(pdf_path):
            os.startfile(pdf_path)
        else:
            messagebox.showerror("Not Found", f"PDF not found:\n{pdf_path}")

    bill_tree.bind("<<TreeviewSelect>>", on_bill_select)

    bottom_btn = Frame(bills_win, bg="#FFF8E7")
    bottom_btn.pack(pady=8)

    Button(bottom_btn, text="🖨  Reprint Selected Bill", font=("Segoe UI", 11, "bold"),
           bg="#3B82F6", fg="white", relief="flat", cursor="hand2", width=22,
           command=reprint_bill).grid(row=0, column=0, padx=15)

    Button(bottom_btn, text="← Back", font=("Segoe UI", 11, "bold"),
           bg="#EF4444", fg="white", relief="flat", cursor="hand2", width=15,
           command=bills_win.destroy).grid(row=0, column=1, padx=15)

    load_bills()  # load today's bills on open
def create_card(parent, title, variable, bg):

    card = Frame(
        parent,
        bg=bg,
        width=220,
        height=95,
        relief="flat",
        bd=0
    )

    card.pack_propagate(False)

    Label(
        card,
        textvariable=variable,
        bg=bg,
        fg="white",
        font=("Segoe UI", 18, "bold")
    ).pack(pady=(15, 0))

    Label(
        card,
        text=title,
        bg=bg,
        fg="white",
        font=("Segoe UI", 10)
    ).pack()

    return card
def create_clickable_card(parent, title, variable, bg, command):

    card = Frame(
        parent,
        bg=bg,
        width=220,
        height=95,
        relief="flat",
        bd=0
    )

    card.pack_propagate(False)

    value_lbl = Label(
        card,
        textvariable=variable,
        bg=bg,
        fg="white",
        cursor="hand2",
        font=("Segoe UI", 18, "bold", "underline")
    )

    value_lbl.pack(pady=(15,0))

    Label(
        card,
        text=title,
        bg=bg,
        fg="white",
        font=("Segoe UI",10)
    ).pack()

    value_lbl.bind("<Button-1>", lambda e: command())

    return card

def open_sales_report():
    sales_win = Toplevel(window)
    sales_win.title("Sales Report")
    sales_win.state("zoomed")
    sales_win.configure(bg="#FFF8E7")
    sales_win.grab_set()

    top_frame = Frame(sales_win, bg="#3B82F6")
    top_frame.pack(fill="x")

    Label(
        top_frame,
        text="💰 Sales Report",
        bg="#3B82F6",
        fg="white",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(15, 2))

    Label(
        top_frame,
        text="View sales between selected dates",
        bg="#3B82F6",
        fg="white",
        font=("Segoe UI", 10)
    ).pack(pady=(0, 12))

    Button(
        top_frame,
        text="← Back",
        bg="#EF4444",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        command=sales_win.destroy
    ).place(relx=0.98, rely=0.08, anchor="ne")

    filter_frame = Frame(sales_win, bg="#FFF8E7")
    filter_frame.pack(fill="x", padx=15, pady=15)
    summary_frame = Frame(sales_win, bg="#FFF8E7")
    summary_frame.pack(fill="x", padx=15, pady=10)
    total_sales_var = StringVar(value="₹0.00")
    bill_count_var = StringVar(value="0")
    cash_var = StringVar(value="₹0.00")
    upi_var = StringVar(value="₹0.00")
    card_var = StringVar(value="₹0.00")


    create_card(summary_frame, "Total Sales", total_sales_var, "#3B82F6")
    create_card(summary_frame, "Bills", bill_count_var, "#10B981")
    create_card(summary_frame, "Cash", cash_var, "#F59E0B")
    create_card(summary_frame, "UPI", upi_var, "#8B5CF6")
    create_card(summary_frame, "Card", card_var, "#EF4444")

    table_frame = Frame(sales_win, bg="#FFF8E7")
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Sales.Treeview",
        background="#FFFDF7",
        foreground="#374151",
        fieldbackground="#FFFDF7",
        rowheight=34,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Sales.Treeview.Heading",
        background="#3B82F6",
        foreground="white",
        font=("Segoe UI", 11, "bold")
    )

    style.map(
        "Sales.Treeview",
        background=[("selected", "#D6EFFF")],
        foreground=[("selected", "black")]
    )

    sales_tree = ttk.Treeview(
        table_frame,
        columns=(
            "Bill",
            "Customer",
            "Contact",
            "Payment",
            "Amount",
            "Date",
            "Time"
        ),
        show="headings",
        style="Sales.Treeview"
    )



    sales_tree.heading("Bill", text="Bill No")
    sales_tree.heading("Customer", text="Customer")
    sales_tree.heading("Contact", text="Contact")
    sales_tree.heading("Payment", text="Payment")
    sales_tree.heading("Amount", text="Amount")
    sales_tree.heading("Date", text="Date")
    sales_tree.heading("Time", text="Time")

    scroll = Scrollbar(
        table_frame,
        orient="vertical",
        command=sales_tree.yview
    )

    sales_tree.configure(
        yscrollcommand=scroll.set
    )

    scroll.pack(side="right", fill="y")

    sales_tree.pack(
        fill="both",
        expand=True
    )
    enable_cell_copy(sales_tree)

    def this_month_report():

        today = datetime.date.today()

        first = today.replace(day=1)

        from_cal.set_date(first)

        to_cal.set_date(today)

        load_sales_report()

    def load_sales_report():

        sales_tree.delete(*sales_tree.get_children())

        from_date = from_cal.get()
        to_date = to_cal.get()

        with sqlite3.connect(DB_PATH) as conn:

            c = conn.cursor()

            c.execute("""
                SELECT
                    bill_no,
                    customer_name,
                    contact,
                    payment_mode,
                    total,
                    bill_date,
                    bill_time
                FROM bill_master
                WHERE bill_date BETWEEN ? AND ?
                ORDER BY bill_id DESC
            """, (from_date, to_date))

            rows = c.fetchall()

        total_sales = 0
        total_bills = 0

        cash = 0
        upi = 0
        card = 0

        for row in rows:

            payment = row[3]
            amount = float(row[4])

            total_sales += amount
            total_bills += 1

            if payment == "Cash":
                cash += amount
                payment_text = "💵 Cash"

            elif payment == "UPI":
                upi += amount
                payment_text = "📱 UPI"

            elif payment == "Card":
                card += amount
                payment_text = "💳 Card"

            else:
                payment_text = payment

            sales_tree.insert(
                "",
                END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    payment_text,
                    f"₹{amount:,.2f}",
                    row[5],
                    row[6]
                )
            )

        total_sales_var.set(f"₹{total_sales:,.2f}")
        bill_count_var.set(str(total_bills))
        cash_var.set(f"₹{cash:,.2f}")
        upi_var.set(f"₹{upi:,.2f}")
        card_var.set(f"₹{card:,.2f}")





    Label(
        filter_frame,
        text="From",
        bg="#FFF8E7",
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, padx=5)

    from_cal = DateEntry(
        filter_frame,
        width=12,
        date_pattern="dd-mm-yyyy"
    )
    from_cal.grid(row=0, column=1, padx=5)

    Label(
        filter_frame,
        text="To",
        bg="#FFF8E7",
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=2, padx=5)

    to_cal = DateEntry(
        filter_frame,
        width=12,
        date_pattern="dd-mm-yyyy"
    )
    to_cal.grid(row=0, column=3, padx=5)

    Button(
        filter_frame,
        text="🔍 Search",
        bg="#3B82F6",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        command=load_sales_report,
        width=12
    ).grid(row=0, column=4, padx=10)

    Button(
        filter_frame,
        text="📅 Today",
        bg="#10B981",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        command=lambda: (
            from_cal.set_date(datetime.date.today()),
            to_cal.set_date(datetime.date.today()),
            load_sales_report()
        ),
        width=12
    ).grid(row=0, column=5, padx=5)

    Button(
        filter_frame,
        text="🗓 This Month",
        bg="#F59E0B",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        command=this_month_report,
        width=14
    ).grid(row=0, column=6, padx=5)
    Button(
        filter_frame,
        text="📆 Month wise Sell",
        bg="#8B5CF6",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        # command=open_month_wise_sales,
        width=16
    ).grid(row=0, column=7, padx=5)
    load_sales_report()

def open_stock_report():
    stock_win = Toplevel(window)
    stock_win.title("Stock Report")
    stock_win.state("zoomed")
    stock_win.configure(bg="#FFF8E7")
    stock_win.grab_set()

    top = Frame(stock_win, bg="#10B981")
    top.pack(fill="x")

    Label(
        top,
        text="📦 Stock Report",
        bg="#10B981",
        fg="white",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(15, 2))

    Label(
        top,
        text="View Current Inventory Status",
        bg="#10B981",
        fg="white",
        font=("Segoe UI", 10)
    ).pack(pady=(0, 12))

    Button(
        top,
        text="← Back",
        bg="#EF4444",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        command=stock_win.destroy
    ).place(relx=.98, rely=.08, anchor="ne")
    total_products_var = StringVar(value="0")
    inventory_var = StringVar(value="₹0")
    low_stock_var = StringVar(value="0")
    out_stock_var = StringVar(value="0")
    summary = Frame(stock_win, bg="#FFF8E7")
    summary.pack(fill="x", padx=15, pady=15)

    def show_low_stock():

        win = Toplevel(stock_win)
        win.title("Low Stock Products")
        win.geometry("900x550")
        win.configure(bg="#FFF8E7")
        win.grab_set()

        Label(
            win,
            text="🟡 Low Stock Products",
            bg="#F59E0B",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(fill="x")

        tree = ttk.Treeview(
            win,
            columns=("Name", "Category", "Qty", "Price"),
            show="headings"
        )

        tree.heading("Name", text="Product")
        tree.heading("Category", text="Category")
        tree.heading("Qty", text="Qty")
        tree.heading("Price", text="Selling Price")

        tree.column("Name", width=320)
        tree.column("Category", width=180)
        tree.column("Qty", width=100, anchor="center")
        tree.column("Price", width=120, anchor="e")

        tree.pack(fill="both", expand=True, padx=15, pady=15)

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            c.execute("""
                SELECT
                    name,
                    category,
                    quantity,
                    sell_price
                FROM product_master
                WHERE quantity > 0
                  AND quantity <= 5
                ORDER BY quantity ASC, name ASC
            """)

            rows = c.fetchall()

        for row in rows:
            tree.insert("", END, values=row)

        Button(
            win,
            text="Close",
            bg="#EF4444",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=win.destroy
        ).pack(pady=10)

    def show_out_stock():

        win = Toplevel(stock_win)
        win.title("Out Of Stock Products")
        win.geometry("900x550")
        win.configure(bg="#FFF8E7")
        win.grab_set()

        Label(
            win,
            text="🔴 Out Of Stock Products",
            bg="#EF4444",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(fill="x")

        tree = ttk.Treeview(
            win,
            columns=("Name", "Category", "Qty", "Price"),
            show="headings"
        )

        tree.heading("Name", text="Product")
        tree.heading("Category", text="Category")
        tree.heading("Qty", text="Qty")
        tree.heading("Price", text="Selling Price")

        tree.column("Name", width=320)
        tree.column("Category", width=180)
        tree.column("Qty", width=100, anchor="center")
        tree.column("Price", width=120, anchor="e")

        tree.pack(fill="both", expand=True, padx=15, pady=15)

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            c.execute("""
                SELECT
                    name,
                    category,
                    quantity,
                    sell_price
                FROM product_master
                WHERE quantity = 0
                ORDER BY name
            """)

            rows = c.fetchall()

        for row in rows:
            tree.insert("", END, values=row)

        Button(
            win,
            text="Close",
            bg="#EF4444",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=win.destroy
        ).pack(pady=10)

    # create_card(summary, "Products", total_products_var, "#3B82F6")
    create_card(summary, "Products", total_products_var, "#3B82F6").pack(side="left", padx=8)
    create_card(summary, "Inventory ₹", inventory_var, "#10B981").pack(side="left", padx=8)
    create_clickable_card(summary, "Low Stock", low_stock_var, "#F59E0B",show_low_stock).pack(side="left", padx=8)
    create_clickable_card(summary, "Out Of Stock", out_stock_var, "#EF4444",show_out_stock).pack(side="left", padx=8)


    search_frame = Frame(stock_win, bg="#FFF8E7")
    search_frame.pack(fill="x", padx=20, pady=10)

    Label(
        search_frame,
        text="🔍 Search Product :",
        bg="#FFF8E7",
        font=("Segoe UI", 11, "bold")
    ).pack(side="left")

    search_var = StringVar()

    search_entry = Entry(
        search_frame,
        textvariable=search_var,
        width=35,
        font=("Segoe UI", 11)
    )
    search_entry.pack(side="left", padx=10)

    Button(
        search_frame,
        text="Search",
        bg="#3B82F6",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=12,
        command=lambda: search_stock()
    ).pack(side="left", padx=5)

    Button(
        search_frame,
        text="Refresh",
        bg="#10B981",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=12,
        command=lambda: load_stock()
    ).pack(side="left", padx=5)
    table_frame = Frame(stock_win, bg="#FFF8E7")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Stock.Treeview",
        background="#FFFDF7",
        foreground="#374151",
        fieldbackground="#FFFDF7",
        rowheight=34,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Stock.Treeview.Heading",
        background="#10B981",
        foreground="white",
        font=("Segoe UI", 11, "bold")
    )
    stock_tree = ttk.Treeview(
        table_frame,
        columns=(
            "ID",
            "Product",
            "Category",
            "Stock",
            "MRP",
            "Selling"
        ),
        show="headings",
        style="Stock.Treeview"
    )
    stock_tree.heading("ID", text="ID")
    stock_tree.heading("Product", text="Product")
    stock_tree.heading("Category", text="Category")
    stock_tree.heading("Stock", text="Stock")
    stock_tree.heading("MRP", text="MRP")
    stock_tree.heading("Selling", text="Selling Price")
    stock_tree.column("ID", width=90, anchor="center")
    stock_tree.column("Product", width=350)
    stock_tree.column("Category", width=170)
    stock_tree.column("Stock", width=120, anchor="center")
    stock_tree.column("MRP", width=120, anchor="e")
    stock_tree.column("Selling", width=140, anchor="e")
    scroll = Scrollbar(table_frame)

    scroll.pack(side="right", fill="y")
    enable_cell_copy(stock_tree)

    stock_tree.configure(
        yscrollcommand=scroll.set
    )

    scroll.config(command=stock_tree.yview)

    stock_tree.pack(fill="both", expand=True)

    def load_stock():

        stock_tree.delete(*stock_tree.get_children())

        with sqlite3.connect(DB_PATH) as conn:

            c = conn.cursor()

            c.execute("""
                SELECT
                    productid,
                    name,
                    category,
                    quantity,
                    mrp,
                    sell_price
                FROM product_master
                ORDER BY name
            """)

            rows = c.fetchall()

        total_products = 0
        inventory = 0
        low_stock = 0
        out_stock = 0

        for row in rows:

            qty = int(row[3])
            sell = float(row[5])

            total_products += 1
            inventory += qty * sell

            if qty < 10:
                low_stock += 1

            if qty == 0:
                out_stock += 1

            stock_tree.insert("", END, values=row)

        total_products_var.set(str(total_products))
        inventory_var.set(f"₹{inventory:,.2f}")
        low_stock_var.set(str(low_stock))
        out_stock_var.set(str(out_stock))

    def search_stock():

        key = search_var.get().strip()

        stock_tree.delete(*stock_tree.get_children())

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            c.execute("""
                SELECT
                    productid,
                    name,
                    category,
                    quantity,
                    mrp,
                    sell_price
                FROM product_master
                WHERE
                    name LIKE ?
                    OR category LIKE ?
                ORDER BY name
            """, (f"%{key}%", f"%{key}%"))

            rows = c.fetchall()

        for row in rows:
            stock_tree.insert("", END, values=row)



    load_stock()
def open_customer_report():

    report_win = Toplevel(window)
    report_win.title("Customer Report")
    report_win.state("zoomed")
    report_win.configure(bg="#FFF8E7")
    report_win.grab_set()

    # ================= HEADER =================

    top = Frame(report_win, bg="#8B5CF6")
    top.pack(fill="x")

    Label(
        top,
        text="👥 Customer Report",
        bg="#8B5CF6",
        fg="white",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(12, 2))

    Label(
        top,
        text="Customer Purchase Summary",
        bg="#8B5CF6",
        fg="white",
        font=("Segoe UI", 10)
    ).pack(pady=(0, 12))

    Button(
        top,
        text="← Back",
        bg="#EF4444",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        command=report_win.destroy
    ).place(relx=.98, rely=.08, anchor="ne")

    # ================= VARIABLES =================

    total_customer_var = StringVar(value="0")
    total_sales_var = StringVar(value="₹0")
    repeat_customer_var = StringVar(value="0")
    today_customer_var = StringVar(value="0")

    # ================= SUMMARY =================

    summary = Frame(report_win, bg="#FFF8E7")
    summary.pack(fill="x", padx=20, pady=15)

    create_card(
        summary,
        "Customers",
        total_customer_var,
        "#3B82F6"
    ).pack(side="left", padx=8)

    create_card(
        summary,
        "Sales ₹",
        total_sales_var,
        "#10B981"
    ).pack(side="left", padx=8)

    create_card(
        summary,
        "Repeat",
        repeat_customer_var,
        "#F59E0B"
    ).pack(side="left", padx=8)

    create_card(
        summary,
        "Today's",
        today_customer_var,
        "#8B5CF6"
    ).pack(side="left", padx=8)

    # ================= SEARCH =================

    search_var = StringVar()

    search_frame = Frame(report_win, bg="#FFF8E7")
    search_frame.pack(fill="x", padx=20, pady=8)

    Label(
        search_frame,
        text="🔍 Search :",
        bg="#FFF8E7",
        font=("Segoe UI",11,"bold")
    ).pack(side="left")

    Entry(
        search_frame,
        textvariable=search_var,
        width=35,
        font=("Segoe UI",11)
    ).pack(side="left", padx=10)

    search_btn = Button(
        search_frame,
        text="Search",
        bg="#3B82F6",
        fg="white",
        width=12,
        font=("Segoe UI", 10, "bold"),
        command=lambda: search_customers()
    )

    search_btn.pack(side="left", padx=5)

    refresh_btn = Button(
        search_frame,
        text="Refresh",
        bg="#10B981",
        fg="white",
        width=12,
        font=("Segoe UI", 10, "bold"),
        command=lambda: (search_var.set(""), load_customers())
    )

    refresh_btn.pack(side="left", padx=5)

    # ================= TABLE =================

    table_frame = Frame(report_win, bg="#FFF8E7")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "CustomerReport.Treeview",
        background="#FFFDF7",
        foreground="#374151",
        fieldbackground="#FFFDF7",
        rowheight=34,
        font=("Segoe UI",10)
    )

    style.configure(
        "CustomerReport.Treeview.Heading",
        background="#8B5CF6",
        foreground="white",
        font=("Segoe UI",11,"bold")
    )

    customer_tree = ttk.Treeview(
        table_frame,
        columns=(
            "Name",
            "Mobile",
            "Bills",
            "Purchase",
            "Last"
        ),
        show="headings",
        style="CustomerReport.Treeview"
    )

    customer_tree.heading("Name", text="Customer")
    customer_tree.heading("Mobile", text="Mobile")
    customer_tree.heading("Bills", text="Bills")
    customer_tree.heading("Purchase", text="Total Purchase")
    customer_tree.heading("Last", text="Last Visit")

    customer_tree.column("Name", width=320)
    customer_tree.column("Mobile", width=170, anchor="center")
    customer_tree.column("Bills", width=100, anchor="center")
    customer_tree.column("Purchase", width=170, anchor="e")
    customer_tree.column("Last", width=150, anchor="center")

    scroll = Scrollbar(
        table_frame,
        orient="vertical",
        command=customer_tree.yview
    )

    customer_tree.configure(
        yscrollcommand=scroll.set
    )

    scroll.pack(side="right", fill="y")

    customer_tree.pack(fill="both", expand=True)
    enable_cell_copy(customer_tree)
    # ================= LOAD REPORT =================

    def load_customers():

        customer_tree.delete(*customer_tree.get_children())

        with sqlite3.connect(DB_PATH) as conn:

            c = conn.cursor()

            c.execute("""
                SELECT
                    cm.customer_name,
                    cm.mobile,
                    COUNT(b.bill_id),
                    IFNULL(SUM(b.total),0),
                    IFNULL(MAX(b.bill_date),'')
                FROM customer_master cm
                LEFT JOIN bill_master b
                    ON cm.customer_name=b.customer_name
                GROUP BY
                    cm.customer_id
                ORDER BY
                    cm.customer_name
            """)

            rows=c.fetchall()

        total_customers=0
        total_sales=0
        repeat_customers=0

        today=datetime.datetime.now().strftime("%d-%m-%Y")
        today_count=0

        for row in rows:

            bills=int(row[2])
            sales=float(row[3])

            total_customers+=1
            total_sales+=sales

            if bills>1:
                repeat_customers+=1

            if row[4]==today:
                today_count+=1

            customer_tree.insert(
                "",
                END,
                values=(
                    row[0],
                    row[1],
                    bills,
                    f"₹{sales:,.2f}",
                    row[4]
                )
            )

        total_customer_var.set(str(total_customers))
        total_sales_var.set(f"₹{total_sales:,.2f}")
        repeat_customer_var.set(str(repeat_customers))
        today_customer_var.set(str(today_count))

    def search_customers():

        key = search_var.get().strip()

        customer_tree.delete(*customer_tree.get_children())

        with sqlite3.connect(DB_PATH) as conn:

            c = conn.cursor()

            c.execute("""
                SELECT
                    cm.customer_name,
                    cm.mobile,
                    COUNT(b.bill_id),
                    IFNULL(SUM(b.total),0),
                    IFNULL(MAX(b.bill_date),'')
                FROM customer_master cm
                LEFT JOIN bill_master b
                    ON cm.customer_name=b.customer_name
                WHERE
                    cm.customer_name LIKE ?
                    OR cm.mobile LIKE ?
                GROUP BY
                    cm.customer_id
                ORDER BY
                    cm.customer_name
            """, (f"%{key}%", f"%{key}%"))

            rows = c.fetchall()

        for row in rows:
            customer_tree.insert(
                "",
                END,
                values=(
                    row[0],
                    row[1],
                    int(row[2]),
                    f"₹{float(row[3]):,.2f}",
                    row[4]
                )
            )

    load_customers()

    def show_customer_history(event=None):

        selected = customer_tree.selection()

        if not selected:
            return

        values = customer_tree.item(selected[0])["values"]

        customer_name = values[0]

        history = Toplevel(report_win)
        history.title(customer_name + " - Purchase History")
        history.state("zoomed")
        history.configure(bg="#FFF8E7")
        history.grab_set()

        Label(
            history,
            text=f"👤 {customer_name}",
            bg="#8B5CF6",
            fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack(fill="x", pady=(0, 10))

        hist_tree = ttk.Treeview(
            history,
            columns=(
                "Bill",
                "Date",
                "Time",
                "Payment",
                "Amount"
            ),
            show="headings"
        )

        hist_tree.heading("Bill", text="Bill No")
        hist_tree.heading("Date", text="Date")
        hist_tree.heading("Time", text="Time")
        hist_tree.heading("Payment", text="Payment")
        hist_tree.heading("Amount", text="Amount")

        hist_tree.column("Bill", width=130, anchor="center")
        hist_tree.column("Date", width=130, anchor="center")
        hist_tree.column("Time", width=120, anchor="center")
        hist_tree.column("Payment", width=140, anchor="center")
        hist_tree.column("Amount", width=150, anchor="e")

        hist_tree.pack(fill="both", expand=True, padx=15, pady=10)
        enable_cell_copy(hist_tree)
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            c.execute("""
                SELECT
                    bill_no,
                    bill_date,
                    bill_time,
                    payment_mode,
                    total
                FROM bill_master
                WHERE customer_name=?
                ORDER BY bill_id DESC
            """, (customer_name,))

            rows = c.fetchall()

        total_purchase = 0

        for row in rows:
            total_purchase += float(row[4])

            hist_tree.insert(
                "",
                END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    f"₹{row[4]:,.2f}"
                )
            )

        bottom = Frame(history, bg="#FFF8E7")
        bottom.pack(fill="x", pady=10)

        Label(
            bottom,
            text=f"Total Bills : {len(rows)}",
            bg="#FFF8E7",
            fg="#1E3A5F",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=20)

        Label(
            bottom,
            text=f"Total Purchase : ₹{total_purchase:,.2f}",
            bg="#FFF8E7",
            fg="#10B981",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=20)

        Button(
            bottom,
            text="Close",
            bg="#EF4444",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=history.destroy
        ).pack(side="right", padx=20)

    customer_tree.bind("<Double-1>", show_customer_history)

def open_business_analytics():

    analytics_win = Toplevel(window)
    analytics_win.title("Business Analytics")
    analytics_win.state("zoomed")
    analytics_win.configure(bg="#F8FAFC")
    analytics_win.grab_set()

    # ---------------- Header ----------------

    top = Frame(
        analytics_win,
        bg="#0F766E",
        height=170
    )

    top.pack(fill="x")
    top.pack_propagate(False)

    Label(
        top,
        text="📊 Business Analytics",
        bg="#0F766E",
        fg="white",
        font=("Segoe UI",26,"bold")
    ).pack(pady=(20,5))

    Label(
        top,
        text="Month Wise Sales & Profit",
        bg="#0F766E",
        fg="white",
        font=("Segoe UI",11)
    ).pack()

    Button(
        top,
        text="← Back",
        bg="#EF4444",
        fg="white",
        font=("Segoe UI",10,"bold"),
        command=analytics_win.destroy
    ).place(relx=.98,rely=.18,anchor="ne")

    # ---------------- Cards Area ----------------

    body = Frame(
        analytics_win,
        bg="#F8FAFC"
    )

    body.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    # Equal row sizes
    for r in range(3):
        body.grid_rowconfigure(
            r,
            weight=1,
            uniform="rows"
        )

    # Equal column sizes
    for c in range(4):
        body.grid_columnconfigure(
            c,
            weight=1,
            uniform="months"
        )
    months = [
        "January", "February", "March",
        "April", "May", "June",
        "July", "August", "September",
        "October", "November", "December"
    ]

    current_year = datetime.datetime.now().year

    def create_month_card(parent, month, index):

        colors = [
            "#EFF6FF", "#ECFDF5", "#FEF3C7",
            "#F3E8FF", "#FCE7F3", "#E0F2FE",
            "#DCFCE7", "#FEF9C3", "#FFE4E6",
            "#EDE9FE", "#F0FDF4", "#FFF7ED"
        ]

        card = Frame(
            parent,
            bg=colors[index],
            width=340,
            height=195,
            highlightbackground="#D1D5DB",
            highlightthickness=1,
            cursor="hand2"
        )

        card.grid_propagate(False)
        # card.grid(
        #     row=r,
        #     column=c,
        #     padx=18,
        #     pady=18
        # )

        title = Label(
            card,
            text=f"🗓 {month} {current_year}",
            bg=colors[index],
            fg="#111827",
            font=("Segoe UI", 13, "bold")
        )
        title.pack(pady=(6, 2))

        sales_var = StringVar(value="₹0")
        profit_var = StringVar(value="₹0")
        bills_var = StringVar(value="🧾 0 Bills")

        sales_lbl = Label(
            card,
            textvariable=sales_var,
            bg=colors[index],
            fg="#2563EB",
            font=("Segoe UI", 20, "bold")
        )
        sales_lbl.pack()

        Label(
            card,
            text="Sales",
            bg=colors[index],
            fg="gray35",
            font=("Segoe UI", 9)
        ).pack()

        profit_lbl = Label(
            card,
            textvariable=profit_var,
            bg=colors[index],
            fg="#059669",
            font=("Segoe UI", 17, "bold")
        )
        profit_lbl.pack(pady=(2, 0))

        Label(
            card,
            text="Profit",
            bg=colors[index],
            fg="gray35",
            font=("Segoe UI", 9)
        ).pack()

        bills_lbl = Label(
            card,
            textvariable=bills_var,
            bg=colors[index],
            fg="#7C3AED",
            font=("Segoe UI", 11, "bold")
        )
        bills_lbl.pack(pady=(2, 2))

        def enter(e):
            card.config(highlightbackground="#2563EB", highlightthickness=3)

        def leave(e):
            card.config(highlightbackground="#D1D5DB", highlightthickness=1)

        for w in (card, title, sales_lbl, profit_lbl, bills_lbl):
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)

        return card, sales_var, profit_var, bills_var

        def open_month():
            messagebox.showinfo(
                month,
                f"Detailed report for {month} {current_year}\n\nComing Soon..."
            )

        for w in (
                card,
                title,
                sales_lbl,
                profit_lbl,
                bills_lbl
        ):
            w.bind("<Button-1>", lambda e: open_month())
    cards = []

    for i, month in enumerate(months):
        card, sale, profit, bills = create_month_card(body, month,i)

        r = i // 4
        c = i % 4

        card.grid(
            row=r,
            column=c,
            padx=18,
            pady=18,
            sticky="nsew"
        )

        cards.append((month, sale, profit, bills))

    # for i in range(3):
    #     body.grid_columnconfigure(i, weight=1)
    # for i in range(4):
    #     body.grid_rowconfigure(i, weight=1, uniform="cols")


def open_reports():

    report_win = Toplevel(window)
    report_win.title("Reports")
    report_win.state("zoomed")
    report_win.configure(bg="#FFF8E7")
    report_win.grab_set()

    # ================= Background =================

    top_frame = Frame(report_win, bg="#4ECDC4", height=150)
    top_frame.pack(fill="x")
    top_frame.pack_propagate(False)

    bottom_frame = Frame(report_win, bg="#FFF8E7")
    bottom_frame.pack(fill="both", expand=True)

    Button(
        top_frame,
        text="← Back",
        bg="#EF4444",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=12,
        relief="flat",
        cursor="hand2",
        command=report_win.destroy
    ).place(relx=0.98, rely=0.12, anchor="ne")


    # ================= Header =================

    Button(
        top_frame,
        text="← Back",
        bg="#EF4444",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=12,
        relief="flat",
        cursor="hand2",
        command=report_win.destroy
    ).place(relx=0.98, rely=0.18, anchor="ne")

    Label(
        top_frame,
        text="Reports",
        bg="#4ECDC4",
        fg="white",
        font=("Segoe UI", 28, "bold")
    ).pack(pady=(30, 8))

    Label(
        top_frame,
        text="View Sales, Stock, Customer and Payment Reports",
        bg="#4ECDC4",
        fg="white",
        font=("Segoe UI", 12)
    ).pack()

    # ================= Buttons =================

    # ================= Buttons =================

    btn_frame = Frame(bottom_frame, bg="#FFF8E7")
    btn_frame.pack(expand=True)

    for i in range(3):
        btn_frame.grid_columnconfigure(i, weight=1)

    # ---------- Row 1 ----------

    Button(
        btn_frame,
        text="💰\nSales Report",
        width=16,
        height=3,
        bg="#3B82F6",
        fg="white",
        font=("Segoe UI", 18, "bold"),
        relief="flat",
        cursor="hand2",
        command=open_sales_report
    ).grid(row=0, column=0, padx=25, pady=25)

    Button(
        btn_frame,
        text="📦\nStock Report",
        width=16,
        height=3,
        bg="#10B981",
        fg="white",
        font=("Segoe UI", 18, "bold"),
        relief="flat",
        cursor="hand2",
        command=open_stock_report
    ).grid(row=0, column=1, padx=25, pady=25)

    Button(
        btn_frame,
        text="👥\nCustomer Report",
        width=16,
        height=3,
        bg="#F59E0B",
        fg="white",
        font=("Segoe UI", 18, "bold"),
        relief="flat",
        cursor="hand2",
        command=open_customer_report
    ).grid(row=0, column=2, padx=25, pady=25)

    # ---------- Row 2 ----------

    Button(
        btn_frame,
        text="🏆\nTop Selling",
        width=16,
        height=3,
        bg="#8B5CF6",
        fg="white",
        font=("Segoe UI", 18, "bold"),
        relief="flat",
        cursor="hand2"
    ).grid(row=1, column=0, padx=25, pady=25)

    Button(
        btn_frame,
        text="📊\nBusiness Analytics",
        width=16,
        height=3,
        bg="#0F766E",
        fg="white",
        font=("Segoe UI", 18, "bold"),
        relief="flat",
        cursor="hand2",
        command=open_business_analytics
    ).grid(row=1, column=1, padx=25, pady=25)
    print("Business Analytics button created")

    Button(
        btn_frame,
        text="💳\nPayment Report",
        width=16,
        height=3,
        bg="#EC4899",
        fg="white",
        font=("Segoe UI", 18, "bold"),
        relief="flat",
        cursor="hand2"
        # command=open_payment_report
    ).grid(row=1, column=2, padx=25, pady=25)
    print("Payment Report button created")



    btn_frame.pack(expand=True)

def open_newbill(search_frame=None, scan_barcode=None):
    newbill_win = Toplevel(window)
    newbill_win.title("New Bill")
    newbill_win.state("zoomed")
    newbill_win.configure(bg="#EAF4FF")
    newbill_win.grab_set()

    Label(newbill_win, text="New Bill", font=("arial",10,"bold"),
          fg="#FACE68", bg="#295F98", relief="solid").pack(pady=10)

    def remove_selected():
        selected = cart_tree.selection()

        if not selected:
            messagebox.showerror("Error", "Select item to remove")
            return

        cart_tree.delete(selected[0])

        # Recalculate serial numbers
        for i, item in enumerate(cart_tree.get_children(), start=1):
            vals = list(cart_tree.item(item)["values"])
            vals[0] = i
            cart_tree.item(item, values=vals)

        update_bill_totals()

    def increase_qty(qty_entry=None):
        selected = cart_tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select a product.")
            return
        item = selected[0]


        values = list(cart_tree.item(item)["values"])

        product_id = values[1]

        # Get latest stock from database
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT quantity FROM product_master WHERE productid=?",
                (product_id,)
            )

            stock = int(c.fetchone()[0])
        qty = int(values[3])
        price = float(values[4])

        # Prevent exceeding available stock
        # Prevent exceeding available stock
        if qty >= stock:
            messagebox.showwarning(
                "Stock Limit",
                f"Only {stock} item(s) available in stock."
            )
            return

            # qty_entry.destroy()
            return

        qty += 1
        total = qty * price
        values[3] = qty
        values[5] = f"{total:.2f}"
        cart_tree.item(item, values=values)
        update_bill_totals()
    def decrease_qty():

        selected = cart_tree.selection()

        if not selected:
            messagebox.showwarning("Select Item", "Please select a product.")
            return

        item = selected[0]

        values = list(cart_tree.item(item)["values"])

        qty = int(values[3])
        price = float(values[4])

        qty -= 1

        if qty <= 0:

            cart_tree.delete(item)

        else:

            total = qty * price

            values[3] = qty
            values[5] = f"{total:.2f}"

            cart_tree.item(item, values=values)

        update_bill_totals()
    def edit_qty(event):
        # Remove any previous qty editor
        for widget in cart_tree.winfo_children():
            if isinstance(widget, Entry):
                widget.destroy()
        # Remove any previous qty editor
        for widget in cart_tree.winfo_children():
            if isinstance(widget, Entry):
                widget.destroy()
        region = cart_tree.identify("region", event.x, event.y)

        if region != "cell":
            return

        column = cart_tree.identify_column(event.x)

        # Qty column is #4
        if column != "#4":
            return

        row = cart_tree.identify_row(event.y)

        if not row:
            return

        x, y, width, height = cart_tree.bbox(row, column)

        values = list(cart_tree.item(row)["values"])
        product_id = values[1]

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT quantity FROM product_master WHERE productid=?",
                (product_id,)
            )
            stock = c.fetchone()[0]

        def validate_qty(value):

            if value == "":
                return True

            if not value.isdigit():
                return False

            return int(value) <= stock

        qty_entry = Entry(
            cart_tree,
            justify="center",
            font=("Segoe UI", 10)
        )

        qty_entry.place(x=x, y=y, width=width, height=height)

        qty_entry.insert(0, values[3])

        qty_entry.focus()

        def save_qty(event=None):

            try:
                new_qty = int(qty_entry.get())
                product_id = values[1]

                with sqlite3.connect(DB_PATH) as conn:
                    c = conn.cursor()

                    c.execute(
                        "SELECT quantity FROM product_master WHERE productid=?",
                        (product_id,)
                    )

                    stock = c.fetchone()[0]

                if new_qty > stock:
                    messagebox.showerror(
                        "Stock Limit",
                        f"Only {stock} item(s) available in stock."
                    )

                    qty_entry.focus_set()
                    qty_entry.select_range(0, END)

                    return

                if new_qty <= 0:

                    qty_entry.destroy()

                    confirm = messagebox.askyesno(
                        "Remove Item",
                        f"Do you want to remove '{values[2]}' from the cart?"
                    )

                    if confirm:
                        cart_tree.delete(row)
                        update_bill_totals()

                    return

                price = float(values[4])

                values[3] = new_qty
                values[5] = f"{new_qty * price:.2f}"

                cart_tree.item(row, values=values)

                qty_entry.destroy()

                update_bill_totals()

            except ValueError:
                qty_entry.destroy()
        qty_entry.bind("<Return>", save_qty)
        qty_entry.bind("<FocusOut>", save_qty)


    # --- Customer Info ---
    cust_frame = Frame(newbill_win, bg="#D1F2EB")
    cust_frame.pack(fill="x", padx=10, pady=10)
    Label(cust_frame, text="Mobile No", font=("arial", 9, "bold"),
          bg="#D1F2EB").grid(row=0, column=0, padx=5)
    contact_var = StringVar()
    contact_entry = Entry(cust_frame, textvariable=contact_var,
                          font=("arial", 10), width=18)
    contact_entry.grid(row=0, column=1, padx=5)
    customer_list = Listbox(
        cust_frame,
        width=55,
        height=5,
        font=("Arial", 10)
    )

    customer_list.grid(
        row=1,
        column=1,
        columnspan=5,
        sticky="w",
        padx=5
    )

    customer_list.grid_remove()  # hide initially

    Label(cust_frame, text="Customer Name",
          font=("arial", 9, "bold"),
          bg="#D1F2EB").grid(row=0, column=2, padx=5)

    name_var = StringVar()
    name_entry = Entry(cust_frame, textvariable=name_var,
                       font=("arial", 10), width=25)
    name_entry.grid(row=0, column=3, padx=5)

    Label(cust_frame, text="City",
          font=("arial", 9, "bold"),
          bg="#D1F2EB").grid(row=0, column=4, padx=5)

    city_var = StringVar()
    city_entry = Entry(cust_frame, textvariable=city_var,
                       font=("arial", 10), width=18)
    city_entry.grid(row=0, column=5, padx=5)

    def todays_sell():
        today = datetime.datetime.now().strftime("%d-%m-%Y")

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            c.execute("""
                SELECT COUNT(*), IFNULL(SUM(total),0)
                FROM bill_master
                WHERE bill_date=?
            """, (today,))

            bills, sale = c.fetchone()

        today_bill_var.set(f"Bills : {bills}")
        today_sale_var.set(f"Sale : ₹{sale:,.2f}")

    def search_customer(event=None):

        customer_list.delete(0, END)

        mobile = contact_var.get().strip()

        if mobile == "":
            customer_list.grid_remove()
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT customer_name,mobile,address
            FROM customer_master
            WHERE mobile LIKE ?
            ORDER BY customer_name
            LIMIT 10
        """, (mobile + "%",))

        rows = cur.fetchall()

        conn.close()

        if len(rows) == 0:
            customer_list.grid_remove()
            return

        customer_list.grid()

        for row in rows:
            customer_list.insert(
                END,
                f"{row[1]}   |   {row[0]}   |   {row[2]}"
            )

    def choose_customer(event):

        if not customer_list.curselection():
            return

        text = customer_list.get(customer_list.curselection())

        parts = text.split("|")

        mobile = parts[0].strip()
        name = parts[1].strip()
        city = parts[2].strip()

        contact_var.set(mobile)
        name_var.set(name)
        city_var.set(city)

        customer_list.grid_remove()

    contact_entry.bind("<KeyRelease>", search_customer)

    customer_list.bind(
        "<<ListboxSelect>>",
        choose_customer
    )

    # --- Layout Frames ---
    left_frame = Frame(newbill_win, bg="#F0F4FF")
    left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    today_bill_var = StringVar(value="Bills : 0")
    today_sale_var = StringVar(value="Sale : ₹0.00")

    right_frame = Frame(newbill_win, bg="#E7C582")
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)


    # --- Product List (Left) ---
    Label(
        left_frame,
        text="📦  Product List",
        font=("Segoe UI", 14, "bold"),
        bg="#6366F1",
        fg="white"
    ).pack(fill="x", ipady=10)

    search_frame = Frame(left_frame, bg="#F0F4FF")
    search_frame.pack(pady=5)

    def scan_barcode(event=None):

        print("SCAN FUNCTION CALLED")
        barcode = barcode_scan_var.get().strip()

        if barcode == "":
            return

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            c.execute("""
                SELECT
                    productid,
                    name,
                    sell_price,
                    quantity
                FROM product_master
                WHERE barcode = ?
            """, (barcode,))

            row = c.fetchone()

        if row is None:
            messagebox.showerror(
                "Not Found",
                "Barcode not found."
            )
            barcode_scan_var.set("")
            barcode_scan_entry.focus_set()
            return

        productid, name, price, qty_avail = row

        if qty_avail <= 0:
            messagebox.showerror(
                "Out Of Stock",
                f"{name} is out of stock."
            )
            barcode_scan_var.set("")
            barcode_scan_entry.focus_set()
            return

        add_barcode_product(
            productid,
            name,
            price,
            qty_avail
        )
        import winsound

        winsound.MessageBeep()

        barcode_scan_var.set("")
        barcode_scan_entry.focus_set()
        # barcode_scan_entry.bind("<Return>", scan_barcode)


    # ---------- Barcode Scan ----------

    barcode_scan_var = StringVar()

    Label(
        search_frame,
        text="📷 Scan",
        font=("Segoe UI", 10, "bold"),
        bg="#F0F4FF"
    ).grid(row=0, column=0, padx=5)

    barcode_scan_entry = Entry(
        search_frame,
        textvariable=barcode_scan_var,
        font=("Segoe UI", 11),
        width=20
    )

    barcode_scan_entry.grid(row=0, column=1, padx=5)
    barcode_scan_entry.bind("<Return>", scan_barcode)

    # ---------- Product Search ----------

    Label(
        search_frame,
        text="🔍 Barcode Search",
        font=("Segoe UI", 10, "bold"),
        bg="#F0F4FF"
    ).grid(row=1, column=0, padx=5, pady=5)

    search_var = StringVar()

    search_entry = Entry(
        search_frame,
        textvariable=search_var,
        font=("Segoe UI", 11),
        width=20
    )

    search_entry.grid(row=1, column=1, padx=5, pady=5)

    barcode_scan_entry.focus_set()


    search_frame = Frame(left_frame, bg="#F0F4FF")
    search_frame.pack(pady=5)

    Label(search_frame, text="🔍 Product Search:", font=("Segoe UI", 10, "bold"), bg="#F0F4FF", fg="#1F2937").grid(row=0,
                                                                                                          column=0,
                                                                                                          padx=5)
    search_var = StringVar()
    search_entry = Entry(search_frame, textvariable=search_var, font=("arial", 10), width=25)
    search_entry.grid(row=0, column=1, padx=5)

    # Product Treeview inside its own frame
    prod_frame = Frame(left_frame, bg="#F0F4FF")
    prod_frame.pack(fill="both", expand=True)

    product_tree = ttk.Treeview(prod_frame,
                                columns=("ID", "Name", "Sell", "Qty", "MRP", "Category"),
                                show="headings", height=1)
    for col in ("ID", "Name", "Sell", "Qty", "MRP", "Category"):
        product_tree.heading(col, text=col)
        product_tree.column(col, width=100)
    product_tree.pack(fill="both", expand=True, padx=5, pady=5)
    enable_cell_copy(product_tree)

    def load_products():
        product_tree.delete(*product_tree.get_children())
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT productid,name,sell_price,quantity,mrp,category FROM product_master")
            rows = c.fetchall()
        for r in rows:
            product_tree.insert("", "end", values=r)

    def search_products(*args):
        query = search_var.get().lower()
        product_tree.delete(*product_tree.get_children())
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT productid,name,sell_price,quantity,mrp,category FROM product_master")
            rows = c.fetchall()
        for r in rows:
            # case-insensitive match, even partial
            if query == "" or query in r[1].lower():
                product_tree.insert("", "end", values=r)

    # Bind live search to typing
    search_var.trace_add("write", search_products)

    # Initial load
    load_products()
    # --- Cart ---
    Label(right_frame, text="Cart", font=("arial",10,"bold"), bg="#FDEBD0").pack(pady=5)

    cart_tree = ttk.Treeview(right_frame,
                             columns=("SNo","ID","Name","Qty","Price","Total"),
                             show="headings", height=7)
    for col in ("SNo","ID","Name","Qty","Price","Total"):
        cart_tree.heading(col, text=col)
        cart_tree.column(col, width=110)
    cart_tree.pack(fill="both", expand=True)
    cart_tree.bind("<Double-1>", edit_qty)

    def generate_bill():
        entry_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        if not cart_tree.get_children():
            messagebox.showerror("Error", "Cart is empty!")
            return

        import os, sys
        from reportlab.lib.pagesizes import mm
        from reportlab.pdfgen import canvas as pdf_canvas

        total_amount = float(final_var.get())

        # Automatically save customer if new
        mobile = contact_var.get().strip()
        customer = name_var.get().strip()
        city = city_var.get().strip()  # can be blank

        if mobile != "" and customer != "":

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            cur.execute("""
                SELECT customer_id
                FROM customer_master
                WHERE mobile=?
            """, (mobile,))

            found = cur.fetchone()

            if found is None:
                cur.execute("""
                    INSERT INTO customer_master
                    (customer_name, mobile, address,entry_time)
                    VALUES (?,?,?,?)
                """, (customer, mobile, city, entry_time))

            conn.commit()
            conn.close()

        customer_name = name_var.get().strip() if name_var.get().strip() else "Walk-in Customer"
        contact = contact_var.get().strip() if contact_var.get().strip() else "N/A"
        now = datetime.datetime.now()
        bill_date = now.strftime("%d-%m-%Y")
        bill_time = now.strftime("%H:%M:%S")
        bill_no = now.strftime("BILL%d%m%Y%H%M%S")
        payment_mode = payment_var.get()

        # Collect cart items
        cart_items = []
        for item in cart_tree.get_children():
            vals = cart_tree.item(item)["values"]
            cart_items.append(vals)  # (SNo, ID, Name, Qty, Price, Total)

        # --- Save to DB ---
        with sqlite3.connect(DB_PATH) as conn:

            c = conn.cursor()
            c.execute("""
                INSERT INTO bill_master (bill_no, customer_name, contact, total, bill_date, bill_time,payment_mode)
                VALUES (?, ?, ?, ?, ?, ?,?)
            """, (bill_no, customer_name, contact, total_amount, bill_date, bill_time,payment_mode))
            bill_id = c.lastrowid

            def get_wholesale_price(product_id):
                c.execute(
                    "SELECT wholesale_price FROM product_master WHERE productid=?",
                    (product_id,)
                )
                row = c.fetchone()
                return float(row[0]) if row else 0

            for vals in cart_items:
                product_id = vals[1]
                product_name = vals[2]
                qty = int(vals[3])
                sell_price = float(vals[4])
                total = float(vals[5])

                wholesale_price = get_wholesale_price(product_id)

                profit = (sell_price - wholesale_price) * qty

                c.execute("""
                    INSERT INTO bill_items
                    (
                        bill_id,
                        product_id,
                        product_name,
                        qty,
                        price,
                        total,
                        sell_price,
                        wholesale_price,
                        profit
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bill_id,
                    product_id,
                    product_name,
                    qty,
                    sell_price,
                    total,
                    sell_price,
                    wholesale_price,
                    profit
                ))

                c.execute("""
                    UPDATE product_master
                    SET quantity =
                        CASE
                            WHEN quantity >= ? THEN quantity - ?
                            ELSE quantity
                        END
                    WHERE productid=?
                """, (
                    qty,
                    qty,
                    product_id
                ))

            conn.commit()

        # --- PDF Save Path ---
        # Works both in .py and after building .exe
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        bills_folder = os.path.join(base_dir, "Bills")
        os.makedirs(bills_folder, exist_ok=True)

        pdf_path = os.path.join(bills_folder, f"{bill_no}.pdf")

        # --- Generate PDF ---
        page_width = 80 * mm
        margin = 5 * mm
        line_height = 5 * mm
        header_height = 50 * mm
        footer_height = 20 * mm
        items_height = (len(cart_items) + 2) * line_height
        page_height = header_height + items_height + footer_height

        c = pdf_canvas.Canvas(pdf_path, pagesize=(page_width, page_height))
        y = page_height - 5 * mm

        def draw_line():
            nonlocal y
            c.setLineWidth(0.5)
            c.line(margin, y, page_width - margin, y)
            y -= 3 * mm

        def draw_text(text, size=8, align="left", bold=False):
            nonlocal y
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            if align == "center":
                c.drawCentredString(page_width / 2, y, text)
            elif align == "right":
                c.drawRightString(page_width - margin, y, text)
            else:
                c.drawString(margin, y, text)
            y -= line_height

        # Header
        draw_text("Rashvin Enterprises (BUGZY)", size=14, align="center", bold=True)
        draw_text("GST Number : 27ABHFR6757R1Z3", size=7, align="center")
        draw_text("Shop no 7, F6, Sector 10, Vashi, NAvi Mumbai-400703", size=7, align="center")
        draw_text("8591127301(only WhatsApp)", size=7, align="center")
        draw_text(f"Bill No : {bill_no}", size=7, align="center")
        draw_text(f"Date    : {bill_date}  {bill_time}", size=7, align="center")
        draw_line()
        draw_text(f"Customer : {customer_name}", size=7, bold=True)
        draw_text(f"Contact  : {contact}", size=7)
        draw_line()

        # Column headers
        c.setFont("Helvetica-Bold", 7)
        c.drawString(margin, y, "Item")
        c.drawString(margin + 27 * mm, y, "Qty")
        c.drawString(margin + 37 * mm, y, "Rate")
        c.drawRightString(page_width - margin, y, "Amt")
        y -= line_height
        draw_line()

        # Items
        for vals in cart_items:
            name = str(vals[2])[:15]
            qty = vals[3]
            price = float(vals[4])
            total = float(vals[5])
            c.setFont("Helvetica", 7)
            c.drawString(margin, y, name)
            c.drawString(margin + 27 * mm, y, str(qty))
            c.drawString(margin + 37 * mm, y, f"{price:.0f}")
            c.drawRightString(page_width - margin, y, f"{total:.2f}")
            y -= line_height

        draw_line()

        # Total
        subtotal_amt = float(subtotal_var.get())
        disc_amt = float(discount_var.get())

        if disc_amt > 0:
            c.setFont("Helvetica", 8)
            c.drawString(margin, y, "Subtotal:")
            c.drawRightString(page_width - margin, y, f"Rs.{subtotal_amt:.2f}")
            y -= line_height

            c.setFont("Helvetica", 8)
            c.drawString(margin, y, f"Discount:")
            c.drawRightString(page_width - margin, y, f"- Rs.{disc_amt:.2f}")
            y -= line_height

        draw_line()
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, "TOTAL PAYABLE:")
        c.drawRightString(page_width - margin, y, f"Rs.{total_amount:.2f}")
        y -= line_height + 2 * mm
        draw_line()

        # Footer
        draw_text("** NO return Only EXCHANGE within 7 days! **", size=7, align="center")
        draw_text("No Guarantee on any item", size=8, align="center")
        c.save()

        # --- Open PDF directly (no save dialog) ---
        os.startfile(pdf_path)

        messagebox.showinfo("Success", f"Bill Generated!\nBill No: {bill_no}\nTotal: Rs.{total_amount:.2f}")
        # Clear everything for next bill
        cart_tree.delete(*cart_tree.get_children())
        subtotal_var.set(0.0)
        final_var.set(0.0)
        discount_var.set(0.0)
        name_var.set("")
        contact_var.set("")
        contact_entry.focus_set()
        load_products()
        todays_sell()
    def apply_discount():
        if not cart_tree.get_children():
            messagebox.showerror("Error", "Cart is empty! Add products first.")
            return

        disc_win = Toplevel(newbill_win)
        disc_win.title("Apply Discount")
        disc_win.geometry("320x200")
        disc_win.resizable(False, False)
        disc_win.grab_set()
        disc_win.focus_force()

        Label(disc_win, text="Enter Discount Amount (Rs.):",
              font=("Arial", 12, "bold")).pack(pady=20)

        disc_entry_var = DoubleVar(value=0.0)
        disc_entry = Entry(disc_win, textvariable=disc_entry_var,
                           font=("Arial", 16, "bold"), width=10, justify="center")
        disc_entry.pack(pady=5)
        disc_entry.focus_set()
        disc_entry.select_range(0, END)
        update_bill_totals()

        def confirm_discount():
            try:
                disc_amount = float(disc_entry_var.get())
                subtotal = float(subtotal_var.get())

                if disc_amount < 0:
                    messagebox.showerror("Error", "Discount cannot be negative.")
                    return
                if disc_amount > subtotal:
                    messagebox.showerror("Error", f"Discount Rs.{disc_amount} cannot exceed total Rs.{subtotal}!")
                    return

                discount_var.set(round(disc_amount, 2))
                update_bill_totals()
                disc_win.destroy()

            except ValueError:
                messagebox.showerror("Error", "Enter a valid number.")

        def remove_discount():
            discount_var.set(0.0)
            update_bill_totals()
            disc_win.destroy()

        btn_frame = Frame(disc_win)
        btn_frame.pack(pady=15)

        Button(btn_frame, text="Apply", bg="#27AE60", fg="white",
               font=("Arial", 11, "bold"), width=10,
               command=confirm_discount).grid(row=0, column=0, padx=10)

        Button(btn_frame, text="Remove Discount", bg="#E74C3C", fg="white",
               font=("Arial", 11, "bold"), width=14,
               command=remove_discount).grid(row=0, column=1, padx=5)

        disc_win.bind("<Return>", lambda e: confirm_discount())

    subtotal_var = DoubleVar(value=0.0)
    final_var = DoubleVar(value=0.0)
    discount_var = DoubleVar(value=0.0)

    def update_bill_totals():

        subtotal = 0.0

        # Calculate subtotal from cart
        for item in cart_tree.get_children():
            values = cart_tree.item(item)["values"]

            subtotal += float(values[5])

        subtotal_var.set(round(subtotal, 2))

        # Apply discount
        discount = discount_var.get()

        final = subtotal - discount

        if final < 0:
            final = 0

        final_var.set(round(final, 2))

    # --- Totals Box ---
    totals_frame = Frame(right_frame, bg="#E7C582", relief="ridge", bd=2)
    totals_frame.pack(fill="x", padx=5, pady=5)

    Label(totals_frame, text="Total Amount:", font=("arial", 9, "bold"),
          bg="#E7C582").grid(row=0, column=0, sticky="w", padx=8, pady=1)
    Label(totals_frame, textvariable=subtotal_var, font=("arial", 18, "bold"),
          bg="#E7C582").grid(row=0, column=1, sticky="e", padx=8, pady=1)

    Label(totals_frame, text="Discount (-):", font=("arial", 9, "bold"),
          fg="red", bg="#E7C582").grid(row=1, column=0, sticky="w", padx=8, pady=1)
    Label(totals_frame, textvariable=discount_var, font=("arial", 14, "bold"),
          fg="red", bg="#E7C582").grid(row=1, column=1, sticky="e", padx=8, pady=1)

    Label(totals_frame, text="Final Payable:", font=("arial", 10, "bold"),
          fg="green", bg="#E7C582").grid(row=2, column=0, sticky="w", padx=8, pady=1)
    Label(totals_frame, textvariable=final_var, font=("arial", 20, "bold"),
          fg="green", bg="#E7C582").grid(row=2, column=1, sticky="e", padx=8, pady=1)
    # ---------------- Payment Mode ----------------

    payment_var = StringVar(value="Cash")

    Label(
        right_frame,
        text="Payment Mode",
        bg="#FFF1E6",
        fg="#1E3A5F",
        font=("Segoe UI", 11, "bold")
    ).pack(pady=(10, 2))

    payment_combo = ttk.Combobox(
        right_frame,
        textvariable=payment_var,
        values=("Cash", "UPI", "Card"),
        width=18,
        state="readonly",
        font=("Segoe UI", 10)
    )
    payment_combo.pack()
    payment_combo.current(0)
    totals_frame.columnconfigure(1, weight=1)
    # --- 3 Buttons Side by Side ---
    action_frame = Frame(right_frame, bg="#E7C582")
    action_frame.pack(fill="x", padx=5, pady=5)

    qty_frame = Frame(right_frame, bg="#FFF1E6")
    qty_frame.pack(pady=8)

    Button(
        qty_frame,
        text="➖ Qty",
        bg="#EF4444",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=10,
        command=decrease_qty
    ).grid(row=0, column=0, padx=6)

    Button(
        qty_frame,
        text="➕ Qty",
        bg="#10B981",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=10,
        command=increase_qty
    ).grid(row=0, column=1, padx=6)

    Button(action_frame, text="Discount", bg="#E67E22", fg="white",
           font=("arial", 11, "bold"),
           command=apply_discount).grid(row=0, column=1, padx=3, pady=3, sticky="ew")
    Button(action_frame, text="Generate Bill", bg="#3498DB", fg="white",
           font=("arial", 11, "bold"),
           command=generate_bill).grid(row=0, column=2, padx=3, pady=3, sticky="ew")
    action_frame.columnconfigure(0, weight=1)
    action_frame.columnconfigure(1, weight=1)
    action_frame.columnconfigure(2, weight=1)

    def calculate_totals():
        subtotal = 0.0

        for item in cart_tree.get_children():
            values = cart_tree.item(item)["values"]
            subtotal += float(values[5])

        subtotal = round(subtotal, 2)
        discount = round(float(discount_var.get()), 2)
        final = round(subtotal - discount, 2)
        if final < 0:
            final = 0.0

        subtotal_var.set(subtotal)
        final_var.set(final)

    # --- Cart Logic ---
    def add_to_cart():
        selected = product_tree.selection()

        if not selected:
            messagebox.showerror("Error", "Please select a product.")
            return

        vals = product_tree.item(selected[0])["values"]
        productid, name, price, qty_avail, mrp, cat = vals
        qty_avail = int(qty_avail)
        qty_win = Toplevel(newbill_win)
        qty_win.title("Select Quantity")
        qty_win.geometry("320x220")
        qty_win.resizable(False, False)
        qty_win.grab_set()
        qty_win.focus_force()
        Label(
            qty_win,
            text=name,
            font=("Arial", 12, "bold")
        ).pack(pady=(10, 5))
        Label(
            qty_win,
            text=f"Available Stock : {qty_avail}",
            fg="blue",
            font=("Arial", 10)
        ).pack()

        qty_var = IntVar(value=1)

        frame = Frame(qty_win)
        frame.pack(pady=15)

        def minus_qty():
            if qty_var.get() > 1:
                qty_var.set(qty_var.get() - 1)

        def plus_qty():
            if qty_var.get() < qty_avail:
                qty_var.set(qty_var.get() + 1)

        Button(
            frame,
            text="-",
            width=4,
            font=("Arial", 14, "bold"),
            command=minus_qty
        ).grid(row=0, column=0, padx=10)

        Label(
            frame,
            textvariable=qty_var,
            width=5,
            relief="solid",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=1)

        Button(
            frame,
            text="+",
            width=4,
            font=("Arial", 14, "bold"),
            command=plus_qty
        ).grid(row=0, column=2, padx=10)

        def confirm_qty():

            q = qty_var.get()

            if q <= 0:
                messagebox.showerror("Error", "Invalid Quantity")
                return

            if q > qty_avail:
                messagebox.showerror("Error", "Not enough stock")
                return

            total = round(float(price) * q, 2)

            for item in cart_tree.get_children():

                values = cart_tree.item(item)["values"]

                if str(values[1]) == str(productid):

                    old_qty = int(values[3])

                    new_qty = old_qty + q

                    if new_qty > qty_avail:
                        messagebox.showerror(
                            "Stock Error",
                            f"Only {qty_avail} items available."
                        )
                        return

                    unit_price = float(values[4])

                    cart_tree.item(
                        item,
                        values=(
                            values[0],
                            values[1],
                            values[2],
                            new_qty,
                            unit_price,
                            round(unit_price * new_qty, 2)
                        )
                    )

                    update_bill_totals()
                    qty_win.destroy()

                    return

            sno = len(cart_tree.get_children()) + 1

            cart_tree.insert(
                "",
                "end",
                values=(
                    sno,
                    productid,
                    name,
                    q,
                    float(price),
                    total
                )
            )

            update_bill_totals()
            qty_win.destroy()

        Button(
            qty_win,
            text="Add To Cart",
            bg="#27AE60",
            fg="white",
            width=20,
            font=("Arial", 11, "bold"),
            command=confirm_qty
        ).pack(pady=10)

        # ----- Button Frame -----

    def add_barcode_product(productid, name, price, qty_avail):

        q = 1

        total = round(float(price) * q, 2)

        for item in cart_tree.get_children():

            values = cart_tree.item(item)["values"]

            if str(values[1]) == str(productid):

                old_qty = int(values[3])

                new_qty = old_qty + 1

                if new_qty > qty_avail:
                    messagebox.showerror(
                        "Stock Error",
                        f"Only {qty_avail} items available."
                    )
                    return

                unit_price = float(values[4])

                cart_tree.item(
                    item,
                    values=(
                        values[0],
                        values[1],
                        values[2],
                        new_qty,
                        unit_price,
                        round(unit_price * new_qty, 2)
                    )
                )

                update_bill_totals()
                return

        sno = len(cart_tree.get_children()) + 1

        cart_tree.insert(
            "",
            "end",
            values=(
                sno,
                productid,
                name,
                1,
                float(price),
                total
            )
        )

        update_bill_totals()



    button_frame = Frame(left_frame, bg="#F0F4FF")
    button_frame.pack(pady=10)
    Button(
        button_frame,
        text="🛒 Add to Cart",
        bg="#10B981",
        fg="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 12, "bold"),
        width=18,
        command=add_to_cart
    ).grid(row=0, column=0, padx=8)

    Button(
        button_frame,
        text="📄 Bill Master",
        bg="#3B82F6",
        fg="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 12, "bold"),
        width=18,
        command=open_bills
    ).grid(row=0, column=1, padx=8)

    Button(
        button_frame,
        text="💰 Today's Sale",
        bg="#F59E0B",
        fg="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 12, "bold"),
        width=18,
        command=todays_sell
    ).grid(row=0, column=2, padx=8)

    # ---------------- Selected Date Heading ----------------
    selected_date_var = StringVar()

    summary_frame = Frame(left_frame, bg="#EEF2FF", relief="ridge", bd=2)
    summary_frame.pack(fill="x", padx=10, pady=10)
    Label(summary_frame,
          text="📈 Today's Business",
          font=("Segoe UI", 12, "bold"),
          bg="#EEF2FF", fg="#6366F1").pack(pady=5)

    Label(summary_frame,
          textvariable=today_bill_var,
          font=("Segoe UI", 11, "bold"),
          bg="#EEF2FF", fg="#1F2937").pack()

    Label(summary_frame,
          textvariable=today_sale_var,
          font=("Segoe UI", 14, "bold"),
          fg="#10B981",
          bg="#EEF2FF").pack(pady=5)

with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            contact TEXT,
            total REAL,
            bill_time TEXT
        )
    """)
    conn.commit()
with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bill_master (
            bill_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no   TEXT,
            customer_name TEXT,
            contact   TEXT,
            total     REAL,
            bill_date TEXT,
            bill_time TEXT,
            payment_mode TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            item_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id   INTEGER,
            product_id INTEGER,
            product_name TEXT,
            qty       INTEGER,
            price     REAL,
            total     REAL,
            FOREIGN KEY (bill_id) REFERENCES bill_master(bill_id)
        )
    """)
    conn.commit()

with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS customer_master(
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            address TEXT,
            entry_time TEXT
        )
    """)
    conn.commit()


window = Tk()
window.geometry("600x600")
window.title("Billing App")
window.state("zoomed")
window.configure(bg="#6BADA0")

# ---------------- MAIN WINDOW THEME ----------------
top_frame = Frame(window, bg="#4ECDC4")   # Aqua Teal
top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.42)

bottom_frame = Frame(window, bg="#FFF8E7")  # Soft Ivory
bottom_frame.place(relx=0, rely=0.42, relwidth=1, relheight=0.58)

# Header
homepageLbl = Label(
    window,
    text="BUGZY BILLING SYSTEM",
    fg="#FACC15",
    bg="#1E293B",
    relief="flat",
    padx=20,
    pady=10,
    font=("Segoe UI", 26, "bold")
)
homepageLbl.pack(pady=30)

# Main Button Frame
menu_frame = Frame(window, bg="#FFFFFF")
menu_frame.pack(expand=True)

# Button Common Style
btn_font = ("Segoe UI",30, "bold")
btn_width = 12
btn_height = 2

# Row 1
Button(
    menu_frame,
    text="🧾 New Bill",
    font=btn_font,
    width=btn_width,
    height=btn_height,
    bg="#10B981",     # Royal Blue
    fg="#1F2937",
    bd=0,
    cursor="hand2",
    command=open_newbill
).grid(row=0, column=0, padx=20, pady=20)

Button(
    menu_frame,
    text="📦 Products",
    font=btn_font,
    width=btn_width,
    height=btn_height,
    bg="#6366F1",     # Modern Purple
    fg="#1F2937",
    bd=0,
    cursor="hand2",
    command=open_products
).grid(row=0, column=1, padx=20, pady=20)

# Row 2
Button(
    menu_frame,
    text="👥 Customers",
    font=btn_font,
    width=btn_width,
    height=btn_height,
    bg="#F59E0B",     # Orange
    fg="#1F2937",
    bd=0,
    cursor="hand2",
    command=open_customers
).grid(row=1, column=0, padx=20, pady=20)

Button(
    menu_frame,
    text="📊 Reports",
    font=btn_font,
    width=btn_width,
    height=btn_height,
    bg="#3B82F6",     # Emerald Green
    fg="#1F2937",
    bd=0,
    cursor="hand2",
    command=open_reports
).grid(row=1, column=1, padx=20, pady=20)

window.mainloop()
