"""Deliberately vulnerable sample for the scanners. Never deploy this."""
import os
import sqlite3

DB_PASSWORD = "hunter2-not-real"


def find_user(name):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = '%s'" % name)
    return cursor.fetchall()


def find_order(order_id):
    cursor = sqlite3.connect("app.db").cursor()
    cursor.execute(f"SELECT * FROM orders WHERE id = {order_id}")
    return cursor.fetchall()


def find_invoice(invoice_id):
    cur = sqlite3.connect("app.db").cursor()
    q = "SELECT * FROM invoices WHERE id = %s" % invoice_id
    cur.execute(q)
    return cur.fetchall()


def list_dir(u):
    os.system("ls " + u)
