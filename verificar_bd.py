#!/usr/bin/env python3
"""Verificar estado de la BD"""
import sqlite3

conn = sqlite3.connect('data/precios_historicos.db')
cursor = conn.cursor()

# Ver tablas
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tablas = cursor.fetchall()
print(f"Tablas en BD: {[t[0] for t in tablas]}")

# Contar registros
cursor.execute('SELECT COUNT(*) FROM precios_publicos')
pub = cursor.fetchone()[0]
print(f"Precios públicos: {pub} registros")

cursor.execute('SELECT COUNT(*) FROM precios_despacho')
desp = cursor.fetchone()[0]
print(f"Precios despacho: {desp} registros")

# Ver últimos 5 registros públicos
cursor.execute('SELECT fecha, calibre, precio_usd_lb, fuente FROM precios_publicos ORDER BY fecha DESC LIMIT 5')
print("\nÚltimos 5 precios públicos:")
for row in cursor.fetchall():
    print(f"  {row[0]} - {row[1]}: ${row[2]:.2f}/lb ({row[3]})")

# Ver últimos 5 registros despacho
cursor.execute('SELECT fecha, calibre, presentacion, precio_usd_lb, origen FROM precios_despacho ORDER BY fecha DESC LIMIT 5')
print("\nÚltimos 5 precios despacho:")
for row in cursor.fetchall():
    print(f"  {row[0]} - {row[1]} {row[2]}: ${row[3]:.2f}/lb ({row[4]})")

conn.close()
