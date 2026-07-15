import sqlite3
from config import DB_PATH


def login_user(username, password):

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT
            userid,
            fullname,
            role
        FROM user_master
        WHERE
            username=?
            AND password=?
            AND active=1
    """, (username, password))

    row = c.fetchone()

    conn.close()

    if row:
        return {
            "success": True,
            "userid": row[0],
            "name": row[1],
            "role": row[2]
        }

    return {
        "success": False
    }