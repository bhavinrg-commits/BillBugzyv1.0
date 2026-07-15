import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "store.db")
from auth import login_user
#
# print(login_user("admin", "admin123"))
# print(login_user("employee", "1234"))

# import sqlite3
# conn = sqlite3.connect("store.db")
# c = conn.cursor()
# c.execute("PRAGMA table_info(bill_items)")
# print(c.fetchall())
# conn.close()
#

# import sqlite3
#
# conn = sqlite3.connect("store.db")
# c = conn.cursor()
#
# c.execute("PRAGMA table_info(expense_master)")
#
# print(c.fetchall())
#
# conn.close()
import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM bill_details")
print(c.fetchone())

conn.close()
# import sqlite3
# from config import DB_PATH
#
# conn = sqlite3.connect(DB_PATH)
# c = conn.cursor()
#
# c.execute("PRAGMA table_info(bill_master)")
# print("bill_master")
# for row in c.fetchall():
#     print(row)
#
# conn.close()
# import sqlite3
# conn = sqlite3.connect(DB_PATH)
# c = conn.cursor()
# c.execute("SELECT expense_date FROM expense_master")
# print(c.fetchall())
# conn.close()
# conn = sqlite3.connect("store.db")
# c = conn.cursor()
#
# c.execute("SELECT * FROM expense_master")
#
# print(c.fetchall())
#
# conn.close()
# import sqlite3
#
# conn = sqlite3.connect("store.db")
# c = conn.cursor()
#
# c.execute("""
# INSERT INTO expense_master
# (
# expense_date,
# category,
# description,
# amount,
# payment_mode,
# created_by
# )
#
# VALUES
# (
# '10-07-2026',
# 'Tea & Snacks',
# 'Evening Tea',
# 150,
# 'Cash',
# 'admin'
# )
# """)
#
# conn.commit()
#
# print("Sample expense inserted.")
#
# conn.close()
# import sqlite3
#
# conn = sqlite3.connect("store.db")
# c = conn.cursor()
#
# c.execute("""
# CREATE TABLE IF NOT EXISTS expense_master
# (
#     expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
#
#     expense_date TEXT NOT NULL,
#
#     category TEXT NOT NULL,
#
#     description TEXT,
#
#     amount REAL NOT NULL,
#
#     payment_mode TEXT DEFAULT 'Cash',
#
#     created_by TEXT,
#
#     created_on TEXT DEFAULT CURRENT_TIMESTAMP
# )
# """)
#
# conn.commit()
#
# print("expense_master table created successfully.")
#
# conn.close()


# import sqlite3
#
# conn = sqlite3.connect("store.db")
# c = conn.cursor()
#
# c.execute("SELECT username,password FROM user_master")
#
# print(c.fetchall())
#
# conn.close()

# import sqlite3
# conn = sqlite3.connect(DB_PATH)
# c = conn.cursor()
#
# c.execute("SELECT * FROM user_master")
#
# rows = c.fetchall()
#
# for row in rows:
#     print(row)
#
# conn.close()




# import win32print
#
# printers = win32print.EnumPrinters(2)
#
# for p in printers:
#     print(p[2])
#
#
# conn = sqlite3.connect(DB_PATH)
# c = conn.cursor()
#
# c.execute("SELECT * FROM user_master")
#
# rows = c.fetchall()
#
# for row in rows:
#     print(row)
#
# conn.close()
# import sqlite3
#
# conn = sqlite3.connect(DB_PATH)
# c = conn.cursor()
#
# c.execute("""
# INSERT INTO user_master
# (username, password, fullname, role, active)
# VALUES
# (?, ?, ?, ?, ?)
# """,
# ("employee", "1234", "Employee User", "EMPLOYEE", 1))
#
# conn.commit()
# conn.close()
#
# print("✅ Employee user created.")
# import sqlite3
#
# conn = sqlite3.connect(DB_PATH)
# c = conn.cursor()
#
# c.execute("""
# INSERT INTO user_master
# (username, password, fullname, role, active)
# VALUES
# (?, ?, ?, ?, ?)
# """,
# ("admin", "admin123", "Bhavin", "ADMIN", 1))
#
# conn.commit()
# conn.close()
#
# print("✅ Admin user created.")
#
# import sqlite3
#
# conn = sqlite3.connect(DB_PATH)
# c = conn.cursor()
#
# c.execute("""
# CREATE TABLE IF NOT EXISTS user_master (
#     userid INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT UNIQUE NOT NULL,
#     password TEXT NOT NULL,
#     fullname TEXT NOT NULL,
#     role TEXT NOT NULL,
#     active INTEGER DEFAULT 1,
#     created_on DATETIME DEFAULT CURRENT_TIMESTAMP
# )
# """)
#
# conn.commit()
# conn.close()
#
# print("✅ user_master table created successfully.")


# import sqlite3
# conn = sqlite3.connect(DB_PATH)
# c = conn.cursor()
# c.execute("ALTER TABLE product_master ADD COLUMN barcode TEXT UNIQUE")
# conn.commit()
# conn.close()





# import sqlite3
# import sqlite3
# conn = sqlite3.connect(DB_PATH)  # use the exact DB_PATH your app uses
# c = conn.cursor()
# c.execute("SELECT name,barcode FROM product_master")
# print(c.fetchall())
#
# # c.execute("PRAGMA table_info(product_master)")  # replace with real table name
# # print(c.fetchall())
# #
# # import sqlite3
# # conn = sqlite3.connect(DB_PATH)
# # c = conn.cursor()
# # c.execute("ALTER TABLE product_master ADD COLUMN barcode TEXT UNIQUE")
# # conn.commit()
# # conn.close()
# #
# # import sqlite3
# #
# # conn = sqlite3.connect(DB_PATH)
# # c = conn.cursor()
# #
# # # 1. Add the column without UNIQUE
# # c.execute("ALTER TABLE product_master ADD COLUMN barcode TEXT")
# #
# # # 2. Create a unique index on it instead
# # c.execute("CREATE UNIQUE INDEX idx_product_barcode ON product_master(barcode)")
# #
# # conn.commit()
# # conn.close()



# import win32print
#
# print(win32print.GetDefaultPrinter())
#
# import win32print
#
# for flags, desc, name, comment in win32print.EnumPrinters(2):
#     print(name)