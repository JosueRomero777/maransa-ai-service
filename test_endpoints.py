#!/usr/bin/env python3
"""
Script para probar el sistema completo
Prueba el flujo: scraping -> BD -> correlación -> predicción
"""

import requests
import json
import time
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server(max_attempts=30):
    """Espera a que el servidor esté listo"""
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("[OK] Servidor listo")
                return True
        except:
            print(f"[{attempt+1}/{max_attempts}] Esperando servidor...")
            time.sleep(1)
    return False

def test_scraping():
    """Prueba 1: Obtener precios públicos"""
    print("\n" + "="*70)
    print("[TEST 1] Obtener precios públicos (Scraping)")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/data/market-prices?force_refresh=true")
        data = response.json()
        
        if response.status_code == 200:
            print("[OK] Status 200")
            precios = data.get('precios_consolidados', {})
            print(f"[OK] {len(precios)} calibres obtenidos:")
            for calibre, precio in precios.items():
                print(f"  - {calibre}: ${precio:.2f}/lb")
            
            bd_status = data.get('bd_status')
            bd_registros = data.get('bd_registros', 0)
            print(f"[OK] BD Status: {bd_status} ({bd_registros} registros)")
            return precios
        else:
            print(f"[ERROR] Status {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def test_save_despacho(calibre="16/20"):
    """Prueba 2: Guardar histórico despacho"""
    print("\n" + "="*70)
    print("[TEST 2] Guardar histórico despacho (últimos 30 días)")
    print("="*70)
    
    try:
        # Guardar 30 días de histórico
        count = 0
        for i in range(1, 31):
            fecha = (date.today() - timedelta(days=i)).isoformat()
            precio = 4.50 + (i * 0.01)
            
            response = requests.post(
                f"{BASE_URL}/data/save-despacho-history",
                params={
                    "fecha": fecha,
                    "calibre": calibre,
                    "presentacion": "HEADLESS",
                    "precio_usd_lb": precio,
                    "origen": "EXPORQUILSA"
                }
            )
            
            if response.status_code == 200:
                count += 1
        
        print(f"[OK] {count} registros guardados")
        return count > 0
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_db_status():
    """Prueba 3: Verificar estado BD"""
    print("\n" + "="*70)
    print("[TEST 3] Estado de la base de datos")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/database/status")
        data = response.json()
        
        if response.status_code == 200:
            print("[OK] Status 200")
            
            pub = data.get('precios_publicos', {})
            print(f"[OK] Precios públicos: {pub.get('total_registros', 0)} registros")
            print(f"     Calibres: {pub.get('calibres', [])}")
            
            desp = data.get('precios_despacho', {})
            print(f"[OK] Precios despacho: {desp.get('total_registros', 0)} registros")
            print(f"     Combinaciones: {desp.get('combinaciones', [])}")
            
            return True
        else:
            print(f"[ERROR] Status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_correlation(calibre="16/20", presentacion="HEADLESS"):
    """Prueba 4: Calcular correlación"""
    print("\n" + "="*70)
    print("[TEST 4] Calcular correlación (público vs despacho)")
    print("="*70)
    
    try:
        response = requests.post(
            f"{BASE_URL}/correlations/calculate",
            params={
                "calibre": calibre,
                "presentacion": presentacion
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Status 200")
            print(f"[OK] Fórmula: {data.get('formula')}")
            print(f"[OK] R²: {data.get('r_cuadrado', 0):.4f} ({data.get('interpretacion', {}).get('r_cuadrado_porcentaje')})")
            print(f"[OK] Muestras: {data.get('muestras')}")
            return data
        else:
            print(f"[ERROR] Status {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def test_predict_public(calibre="16/20", dias=30):
    """Prueba 5: Predecir precio público"""
    print("\n" + "="*70)
    print("[TEST 5] Predecir precio público (30 días)")
    print("="*70)
    
    try:
        response = requests.get(
            f"{BASE_URL}/predict/future-price",
            params={
                "calibre": calibre,
                "dias": dias
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Status 200")
            print(f"[OK] Calibre: {data.get('calibre')}")
            print(f"[OK] Fecha objetivo: {data.get('fecha_objetivo')}")
            print(f"[OK] Precio predicho: ${data.get('precio_predicho_usd_lb'):.2f}/lb")
            ic = data.get('intervalo_confianza', {})
            print(f"[OK] Intervalo: ${ic.get('minimo', 0):.2f} - ${ic.get('maximo', 0):.2f}")
            print(f"[OK] Confianza: {data.get('confianza_porcentaje'):.1f}%")
            return data
        else:
            print(f"[ERROR] Status {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def test_predict_despacho(calibre="16/20", presentacion="HEADLESS", dias=30):
    """Prueba 6: Predecir precio despacho"""
    print("\n" + "="*70)
    print("[TEST 6] Predecir precio despacho (30 días) - FÓRMULA FINAL")
    print("="*70)
    
    try:
        response = requests.get(
            f"{BASE_URL}/predict/despacho-price",
            params={
                "calibre": calibre,
                "presentacion": presentacion,
                "dias": dias
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Status 200")
            print(f"[OK] Calibre: {data.get('calibre')}")
            print(f"[OK] Presentacion: {data.get('presentacion')}")
            print(f"[OK] Fecha objetivo: {data.get('fecha_objetivo')}")
            print(f"\n*** RESULTADO FINAL ***")
            print(f"[OK] Precio público predicho: ${data.get('precio_publico_predicho_usd_lb'):.2f}/lb")
            print(f"[OK] Precio despacho predicho: ${data.get('precio_despacho_predicho_usd_lb'):.2f}/lb")
            ic = data.get('intervalo_confianza_despacho', {})
            print(f"[OK] Intervalo: ${ic.get('minimo', 0):.2f} - ${ic.get('maximo', 0):.2f}")
            print(f"[OK] Confianza: {data.get('confianza_porcentaje'):.1f}%")
            
            corr = data.get('correlacion', {})
            print(f"\n*** CORRELACIÓN USADA ***")
            print(f"[OK] Fórmula: {corr.get('formula')}")
            print(f"[OK] R²: {corr.get('r_cuadrado'):.4f}")
            
            return data
        else:
            print(f"[ERROR] Status {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PRUEBA COMPLETA DEL SISTEMA MARANSA")
    print("="*70)
    
    # Esperar a que el servidor esté listo
    print("\nEsperando servidor FastAPI...")
    if not wait_for_server():
        print("[ERROR] Servidor no responde")
        exit(1)
    
    time.sleep(2)
    
    # Ejecutar pruebas
    precios = test_scraping()
    
    if precios:
        # Usar el primer calibre disponible
        calibre = list(precios.keys())[0] if precios else "16/20"
        
        test_save_despacho(calibre)
        test_db_status()
        test_correlation(calibre, "HEADLESS")
        test_predict_public(calibre)
        test_predict_despacho(calibre, "HEADLESS")
    
    print("\n" + "="*70)
    print("PRUEBAS COMPLETADAS")
    print("="*70 + "\n")
