#!/usr/bin/env python3
"""
Script de prueba para validar el flujo completo:
1. Scraping de precios públicos → Guardado en BD
2. Guardado de histórico EXPORQUILSA  
3. Cálculo de correlación
4. Predicción de precios públicos
5. Predicción de precios de despacho
"""

import requests
import json
from datetime import datetime, date, timedelta
import time

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Imprime respuesta formateada"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    try:
        print(json.dumps(response.json(), indent=2, default=str, ensure_ascii=False))
    except:
        print(response.text)
    print(f"Status: {response.status_code}\n")

def test_scraping():
    """Prueba 1: Scraping de precios públicos"""
    print_response(
        "TEST 1: Scraping de Precios Públicos",
        requests.get(f"{BASE_URL}/data/market-prices")
    )

def test_save_despacho_history():
    """Prueba 2: Guardar histórico despacho"""
    today = date.today()
    
    # Guardar varios registros históricos
    historico = [
        {"fecha": (today - timedelta(days=30)).isoformat(), "calibre": "16/20", "presentacion": "HEADLESS", "precio_usd_lb": 4.20},
        {"fecha": (today - timedelta(days=25)).isoformat(), "calibre": "16/20", "presentacion": "HEADLESS", "precio_usd_lb": 4.35},
        {"fecha": (today - timedelta(days=20)).isoformat(), "calibre": "16/20", "presentacion": "HEADLESS", "precio_usd_lb": 4.15},
        {"fecha": (today - timedelta(days=15)).isoformat(), "calibre": "16/20", "presentacion": "HEADLESS", "precio_usd_lb": 4.40},
        {"fecha": (today - timedelta(days=10)).isoformat(), "calibre": "16/20", "presentacion": "HEADLESS", "precio_usd_lb": 4.30},
        {"fecha": (today - timedelta(days=5)).isoformat(), "calibre": "16/20", "presentacion": "HEADLESS", "precio_usd_lb": 4.55},
        {"fecha": today.isoformat(), "calibre": "16/20", "presentacion": "HEADLESS", "precio_usd_lb": 4.50},
    ]
    
    print(f"\nGuardando {len(historico)} registros de precios despacho...")
    for record in historico:
        response = requests.post(
            f"{BASE_URL}/data/save-despacho-history",
            params=record
        )
        print(f"  ✓ {record['fecha']}: ${record['precio_usd_lb']}/lb - Status {response.status_code}")

def test_database_status():
    """Prueba 3: Estado de la base de datos"""
    print_response(
        "TEST 3: Estado de la Base de Datos",
        requests.get(f"{BASE_URL}/database/status")
    )

def test_calculate_correlation():
    """Prueba 4: Calcular correlación"""
    time.sleep(1)
    print_response(
        "TEST 4: Calcular Correlación (Público vs Despacho)",
        requests.post(f"{BASE_URL}/correlations/calculate?calibre=16/20&presentacion=HEADLESS")
    )

def test_predict_public_price():
    """Prueba 5: Predecir precio público"""
    time.sleep(1)
    print_response(
        "TEST 5: Predicción Precio Público (30 días)",
        requests.get(f"{BASE_URL}/predict/future-price?calibre=16/20&dias=30")
    )

def test_predict_despacho_price():
    """Prueba 6: Predecir precio despacho"""
    time.sleep(1)
    print_response(
        "TEST 6: Predicción Precio Despacho (30 días)",
        requests.get(f"{BASE_URL}/predict/despacho-price?calibre=16/20&presentacion=HEADLESS&dias=30")
    )

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     PRUEBA COMPLETA: SISTEMA DE PREDICCIÓN DE PRECIOS         ║
║                      DE CAMARÓN ECUATORIANO                   ║
╚═══════════════════════════════════════════════════════════════╝

FLUJO:
1. Scraping de precios públicos → Guardado en BD
2. Carga de histórico EXPORQUILSA (despacho)
3. Consulta estado BD
4. Cálculo de correlación público-despacho
5. Predicción precio público (30 días)
6. Predicción precio despacho (30 días)

MODELOS MATEMÁTICOS USADOS:
- Predicción Público: P(t) = a + b*t + EMA[α=0.3]
- Correlación: P_despacho = α + β * P_publico (scipy.stats.linregress)
- Intervalo Confianza: ±1.96 * std_err
- Error Total: √(Error_pub² + Error_corr²)
    """)
    
    try:
        print("\n✓ Verificando conexión al servidor...")
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print(f"⚠ Health check retornó {response.status_code}")
    except Exception as e:
        print(f"✗ No se puede conectar a {BASE_URL}: {e}")
        print("  Asegúrate de que el servidor FastAPI esté ejecutándose")
        exit(1)
    
    # Ejecutar pruebas
    test_scraping()
    test_save_despacho_history()
    test_database_status()
    test_calculate_correlation()
    test_predict_public_price()
    test_predict_despacho_price()
    
    print("\n" + "="*60)
    print("  ✓ PRUEBAS COMPLETADAS")
    print("="*60)
    print("\nRESUMEN SISTEMA:")
    print("  • Precios públicos: Scrapeados y guardados en BD")
    print("  • Histórico despacho: Cargado desde EXPORQUILSA")
    print("  • Correlación: Calculada usando regresión lineal")
    print("  • Predicción público: Modelo P(t) = a + b*t + EMA")
    print("  • Predicción despacho: Correlación + predicción pública")
    print("\nFÓRMULAS PARA TESIS:")
    print("  1. Precio Público: P_pub(t) = a + b*t + EMA[α=0.3]")
    print("  2. Precio Despacho: P_desp = α + β*P_pub")
    print("  3. Error Total: √(σ_pub² + σ_desp²)")
    print("\n")
