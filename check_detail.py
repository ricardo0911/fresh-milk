#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT id, name, detail FROM products")
rows = cursor.fetchall()

with open('detail_output.txt', 'w', encoding='utf-8') as f:
    for row in rows:
        f.write(f"ID: {row[0]}\n")
        f.write(f"名称: {row[1]}\n")
        f.write(f"详情: {row[2]}\n")
        f.write("-" * 40 + "\n")

conn.close()
print("Done")
