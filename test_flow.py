#!/usr/bin/env python3
"""Test complete prediction flow"""
import requests
import json

# Prueba el flujo completo
calibre = '16/20'
presentacion = 'HEADLESS'
dias = 30

print('[FLUJO COMPLETO DE PREDICCIÓN]')
print('='*60)

# 1. Obtener precios públicos
print('\n[PASO 1] Obtener precios públicos...')
r1 = requests.get('http://127.0.0.1:8000/data/market-prices')
d1 = r1.json()
precio_pub = d1['precios_consolidados'][calibre]['precio_publico_promedio']
print(f'✓ Precio público {calibre}: ${precio_pub:.2f}/lb')

# 2. Calcular correlación
print(f'\n[PASO 2] Calcular correlación {calibre} vs {presentacion}...')
r2 = requests.post(f'http://127.0.0.1:8000/correlations/calculate?calibre={calibre}&presentacion={presentacion}')
d2 = r2.json()
formula = d2.get('formula', '')
r2_val = d2.get('r_cuadrado', 0)
print(f'✓ Fórmula correlación: {formula}')
print(f'✓ R²: {r2_val:.4f}')

# 3. Predecir precio público futuro
print(f'\n[PASO 3] Predecir precio público en {dias} días...')
r3 = requests.get(f'http://127.0.0.1:8000/predict/future-price?calibre={calibre}&dias={dias}')
d3 = r3.json()
precio_pub_pred = d3.get('precio_predicho_usd_lb', 0)
print(f'✓ Precio público predicho: ${precio_pub_pred:.2f}/lb')

# 4. Obtener predicción final de despacho
print(f'\n[PASO 4] Obtener predicción final despacho...')
r4 = requests.get(f'http://127.0.0.1:8000/predict/despacho-price?calibre={calibre}&presentacion={presentacion}&dias={dias}')
d4 = r4.json()
precio_desp = d4.get('precio_despacho_predicho_usd_lb', 0)
confianza = d4.get('confianza_porcentaje', 0)

print(f'\n' + '='*60)
print('*** RESULTADO FINAL ***')
print(f'Calibre: {calibre}')
print(f'Presentación: {presentacion}')
print(f'Días predicción: {dias}')
print(f'Precio despacho: ${precio_desp:.2f}/lb')
print(f'Confianza: {confianza:.1f}%')
print('='*60)
