import sqlite3

from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("Starting migration...")

# Get all bill items with their bill number
c.execute("""
SELECT
    bm.bill_no,
    bi.product_id,
    bi.product_name,
    bi.qty,
    bi.sell_price,
    bi.total
FROM bill_items bi
JOIN bill_master bm
ON bi.bill_id = bm.bill_id
""")

rows = c.fetchall()

print(f"Found {len(rows)} bill items.")

inserted = 0

for row in rows:

    bill_no = row[0]
    productid = row[1]
    product_name = row[2]
    qty = row[3]
    sell_price = row[4]
    line_total = row[5]

    # Prevent duplicates
    c.execute("""
        SELECT COUNT(*)
        FROM bill_details
        WHERE bill_no=?
        AND productid=?
        AND product_name=?
        AND qty=?
    """, (
        bill_no,
        productid,
        product_name,
        qty
    ))

    exists = c.fetchone()[0]

    if exists == 0:

        c.execute("""
            INSERT INTO bill_details
            (
                bill_no,
                productid,
                barcode,
                product_name,
                qty,
                mrp,
                sell_price,
                line_total
            )
            VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            bill_no,
            productid,
            "",
            product_name,
            qty,
            sell_price,
            sell_price,
            line_total
        ))

        inserted += 1

conn.commit()

print(f"Migration Completed.")
print(f"{inserted} records inserted into bill_details.")

conn.close()