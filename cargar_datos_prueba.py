#!/usr/bin/env python3
"""Cargar datos de prueba en la BD para hacer predicciones"""
import sqlite3
from datetime import date, timedelta
import random

DB_PATH = "data/precios_historicos.db"

def cargar_datos_prueba():
    """Cargar 90 días de datos históricos de prueba"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Crear tablas si no existen
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS precios_publicos (
        id INTEGER PRIMARY KEY,
        fecha TEXT,
        calibre TEXT,
        precio_usd_lb REAL,
        fuente TEXT,
        confiabilidad TEXT,
        cantidad_muestras INTEGER,
        desviacion_estandar REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS precios_despacho (
        id INTEGER PRIMARY KEY,
        fecha TEXT,
        calibre TEXT,
        presentacion TEXT,
        precio_usd_lb REAL,
        origen TEXT,
        cantidad_sacos INTEGER,
        costo_operativo REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS correlaciones (
        id INTEGER PRIMARY KEY,
        calibre TEXT,
        presentacion TEXT,
        coeficiente_a REAL,
        coeficiente_b REAL,
        r_cuadrado REAL,
        muestras_utilizadas INTEGER,
        fecha_calculo TEXT,
        formula TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predicciones (
        id INTEGER PRIMARY KEY,
        calibre TEXT,
        presentacion TEXT,
        fecha_prediccion TEXT,
        dias_adelante INTEGER,
        precio_predicho REAL,
        intervalo_minimo REAL,
        intervalo_maximo REAL,
        confianza_porcentaje REAL,
        created_at TEXT
    )
    ''')
    
    conn.commit()
    
    # Calibres disponibles
    calibres = ['16/20', '21/25', '26/30', '31/35', '36/40', '41/50']
    
    # Generar datos históricos (90 días atrás)
    print("Cargando datos históricos de prueba...")
    today = date.today()
    
    # Precios base por calibre (basados en datos reales)
    precios_base = {
        '16/20': 5.92,
        '21/25': 5.37,
        '26/30': 5.07,
        '31/35': 4.24,
        '36/40': 4.59,
        '41/50': 4.46
    }
    
    for i in range(90, 0, -1):
        fecha = (today - timedelta(days=i)).isoformat()
        
        for calibre in calibres:
            precio_base = precios_base[calibre]
            
            # Agregar variación aleatoria
            variacion = random.uniform(-0.15, 0.15)
            precio_publico = precio_base + variacion
            
            # Guardar en precios_publicos
            cursor.execute('''
            INSERT INTO precios_publicos 
            (fecha, calibre, precio_usd_lb, fuente, confiabilidad, cantidad_muestras, desviacion_estandar)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha, calibre, precio_publico, 'freezeocean', 'alta', 1, 0.05))
            
            # Precio despacho es correlacionado con precio público
            # Fórmula simplificada: P_desp ≈ 0.85 * P_pub - 0.5
            precio_despacho = 0.85 * precio_publico - 0.5
            
            cursor.execute('''
            INSERT INTO precios_despacho
            (fecha, calibre, presentacion, precio_usd_lb, origen, cantidad_sacos, costo_operativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha, calibre, 'HEADLESS', precio_despacho, 'EXPORQUILSA', 200, 0.30))
    
    # Insertar correlaciones calculadas
    for calibre in calibres:
        cursor.execute('''
        INSERT INTO correlaciones
        (calibre, presentacion, coeficiente_a, coeficiente_b, r_cuadrado, muestras_utilizadas, fecha_calculo, formula)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (calibre, 'HEADLESS', -0.5, 0.85, 0.92, 90, today.isoformat(), 'P_desp = 0.85 * P_pub - 0.50'))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Cargados datos de prueba en {DB_PATH}")
    print(f"✓ {90 * len(calibres)} registros de precios públicos")
    print(f"✓ {90 * len(calibres)} registros de precios despacho")
    print(f"✓ {len(calibres)} correlaciones calculadas")

if __name__ == "__main__":
    cargar_datos_prueba()
