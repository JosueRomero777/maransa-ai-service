#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('data/precios_historicos.db')
cur = conn.cursor()
cur.execute(
    "SELECT fecha, precio_usd_lb, origen "
    "FROM precios_despacho "
    "WHERE calibre = '16/20' AND presentacion = 'HEADLESS' "
    "ORDER BY fecha DESC LIMIT 5"
)
rows = cur.fetchall()
conn.close()
print(rows)
