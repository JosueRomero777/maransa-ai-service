#!/usr/bin/env python3
"""Script de prueba del sistema - verificación rápida"""

import sys
import subprocess
import os

print("\n" + "="*70)
print("PRUEBA DEL SISTEMA MARANSA")
print("="*70)

# Verificación 1: Archivos
print("\n[1] Verificando archivos requeridos...")
files = ['main.py', 'database.py', 'predictor.py', 'market_data_scraper.py']
for f in files:
    exists = "OK" if os.path.exists(f) else "FALTA"
    print(f"  {f}: {exists}")

# Verificación 2: Dependencias
print("\n[2] Verificando dependencias...")
try:
    import numpy
    print("  numpy: OK")
except:
    print("  numpy: FALTA")

try:
    import scipy
    print("  scipy: OK")
except:
    print("  scipy: FALTA")

try:
    import fastapi
    print("  fastapi: OK")
except:
    print("  fastapi: FALTA")

try:
    import requests
    print("  requests: OK")
except:
    print("  requests: FALTA")

# Verificación 3: BD
print("\n[3] Verificando base de datos...")
try:
    from database import PriceDatabase
    db = PriceDatabase()
    print("  PriceDatabase: OK")
    
    import sqlite3
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"  Tablas en BD: {len(tables)}")
    for table in tables:
        print(f"    - {table[0]}")
    conn.close()
except Exception as e:
    print(f"  Error: {e}")

# Verificación 4: Modelos
print("\n[4] Verificando modelos matemáticos...")
try:
    from predictor import PricePredictor
    print("  PricePredictor: OK")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
print("PRUEBA COMPLETADA")
print("="*70 + "\n")
