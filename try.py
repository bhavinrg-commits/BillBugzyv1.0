# import os
# import sys
#
# if getattr(sys, "frozen", False):
#     BASE_DIR = os.path.dirname(sys.executable)
# else:
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#
# DB_PATH = os.path.join(BASE_DIR, "store.db")
#
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

import win32print

for flags, desc, name, comment in win32print.EnumPrinters(2):
    print(name)