#!/usr/bin/env python3
"""
EJEMPLOS DE USO DEL SISTEMA DE PREDICCIÓN

Cómo usar cada endpoint y obtener predicciones de precios de camarón
"""

import requests
import json
from datetime import datetime, date, timedelta

BASE_URL = "http://localhost:8000"

print("""
╔════════════════════════════════════════════════════════════════╗
║         EJEMPLOS: SISTEMA DE PREDICCIÓN DE PRECIOS              ║
║              DE CAMARÓN ECUATORIANO (MARANSA)                   ║
╚════════════════════════════════════════════════════════════════╝
""")

# ============================================================================
# EJEMPLO 1: OBTENER PRECIOS PÚBLICOS ACTUALES
# ============================================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EJEMPLO 1: Obtener Precios Públicos Actuales del Mercado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción:
  • Scraping de múltiples fuentes de internet (FreezeOcean, Selina Wamucii, FAO)
  • Consolidación con pesos por confiabilidad
  • Guardado automático en BD SQLite
  • Respuesta en USD por libra

Código:
""")

print("""
  import requests
  
  response = requests.get("http://localhost:8000/data/market-prices")
  data = response.json()
  
  print(f"Precios consolidados:")
  for calibre, precio in data['precios_consolidados'].items():
      print(f"  {calibre}: ${precio:.2f}/lb")
  
  print(f"\\nEstado BD: {data['bd_status']} ({data['bd_registros']} registros)")
""")

print("""
Respuesta esperada:
  {
    "status": "success",
    "precios_consolidados": {
      "16/20": 3.45,
      "21/25": 4.10,
      "26/30": 4.65,
      "31/35": 5.20,
      "36/40": 5.85,
      "41/50": 6.50
    },
    "bd_status": "guardado",
    "bd_registros": 6,
    "fuentes_consultadas": ["freezeocean", "selina_wamucii", "fao"]
  }
""")

# ============================================================================
# EJEMPLO 2: CARGAR HISTÓRICO DE PRECIOS DE DESPACHO
# ============================================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EJEMPLO 2: Cargar Histórico de Precios de Despacho (EXPORQUILSA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción:
  • Guardar datos históricos de EXPORQUILSA
  • Necesario para calcular correlación público-despacho
  • Formato: USD por libra

Código:
""")

print("""
  import requests
  from datetime import date, timedelta
  
  # Histórico de los últimos 30 días
  for i in range(1, 31):
      fecha = (date.today() - timedelta(days=i)).isoformat()
      
      response = requests.post(
          "http://localhost:8000/data/save-despacho-history",
          params={
              "fecha": fecha,
              "calibre": "16/20",
              "presentacion": "HEADLESS",
              "precio_usd_lb": 4.50 + (i * 0.01),
              "origen": "EXPORQUILSA"
          }
      )
      
      if response.status_code == 200:
          print(f"✓ {fecha}: ${4.50 + (i * 0.01):.2f}/lb guardado")
""")

print("""
Respuesta esperada (por cada registro):
  {
    "status": "success",
    "message": "Precio de despacho guardado: 16/20 HEADLESS = $4.50/lb",
    "fecha": "2024-02-15",
    "origen": "EXPORQUILSA"
  }
""")

# ============================================================================
# EJEMPLO 3: VERIFICAR ESTADO DE LA BASE DE DATOS
# ============================================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EJEMPLO 3: Verificar Estado de la Base de Datos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción:
  • Cantidad de registros por tabla
  • Rangos de fechas disponibles
  • Calibres/presentaciones con datos

Código:
""")

print("""
  import requests
  
  response = requests.get("http://localhost:8000/database/status")
  data = response.json()
  
  print(f"Precios Públicos: {data['precios_publicos']['total_registros']} registros")
  print(f"  Calibres: {', '.join(data['precios_publicos']['calibres'])}")
  
  print(f"\\nPrecios Despacho: {data['precios_despacho']['total_registros']} registros")
  print(f"  Combinaciones: {', '.join(data['precios_despacho']['combinaciones'][:3])}")
""")

# ============================================================================
# EJEMPLO 4: CALCULAR CORRELACIÓN PÚBLICO-DESPACHO
# ============================================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EJEMPLO 4: Calcular Correlación (Modelo de Regresión)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción:
  • Regresión lineal: P_despacho = α + β * P_público
  • Calcula R² (bondad del ajuste)
  • Sirve para predicciones futuras

Fórmula Matemática:
  
  scipy.stats.linregress(precio_publico, precio_despacho)
  
  P_despacho = intercept + slope * P_público
  
  Donde:
  - intercept (α): Margen base de despacho
  - slope (β): Sensibilidad al cambio de precio público
  - r_squared: % de variación explicada (0-1)

Código:
""")

print("""
  import requests
  
  response = requests.post(
      "http://localhost:8000/correlations/calculate",
      params={
          "calibre": "16/20",
          "presentacion": "HEADLESS"
      }
  )
  
  data = response.json()
  
  print(f"Fórmula: {data['formula']}")
  print(f"R²: {data['r_cuadrado']:.4f} ({data['interpretacion']['r_cuadrado_porcentaje']})")
  print(f"Calidad: {data['interpretacion']['calidad']}")
  print(f"Muestras: {data['muestras']}")
""")

print("""
Respuesta esperada:
  {
    "status": "success",
    "calibre": "16/20",
    "presentacion": "HEADLESS",
    "ratio_promedio": 1.3245,
    "coeficiente_correlacion": 0.8742,
    "r_cuadrado": 0.7642,
    "formula": "P_despacho = 0.4521 + 0.9876 * P_publico",
    "muestras": 45,
    "interpretacion": {
      "calidad": "Buena",
      "r_cuadrado_porcentaje": "76.42%"
    }
  }
  
Interpretación:
  • R² = 0.7642 significa que el modelo explica 76.42% de la variación
  • Esto es una correlación "Buena" (70-90% de variación explicada)
  • La fórmula P_desp = 0.4521 + 0.9876 * P_pub es estadísticamente válida
""")

# ============================================================================
# EJEMPLO 5: PREDECIR PRECIO PÚBLICO FUTURO
# ============================================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EJEMPLO 5: Predecir Precio Público a 30 Días
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción:
  • Predice tendencia futura del mercado público
  • Basado en regresión lineal + media móvil exponencial
  • Incluye intervalo de confianza (±1.96σ)

Modelo Matemático:
  
  1. Obtener histórico de n días
  2. Aplicar regresión lineal: P(t) = a + b*t
  3. Calcular EMA: EMA[i] = 0.3 * precio[i] + 0.7 * EMA[i-1]
  4. Predicción: P(30) = a + b*30 + ajuste_EMA
  5. Intervalo: [P(30) - 1.96σ, P(30) + 1.96σ]

Código:
""")

print("""
  import requests
  
  response = requests.get(
      "http://localhost:8000/predict/future-price",
      params={
          "calibre": "16/20",
          "dias": 30
      }
  )
  
  data = response.json()
  
  print(f"Predicción para {data['dias_prediccion']} días ({data['fecha_objetivo']})")
  print(f"Precio predicho: ${data['precio_predicho_usd_lb']:.2f}/lb")
  print(f"Rango confianza: ${data['intervalo_confianza']['minimo']:.2f} - ${data['intervalo_confianza']['maximo']:.2f}/lb")
  print(f"Confianza: {data['confianza_porcentaje']:.1f}%")
  print(f"Fórmula: {data['formula']}")
  print(f"Parámetros: a={data['parametros']['a']:.4f}, b={data['parametros']['b']:.6f}")
""")

print("""
Respuesta esperada:
  {
    "status": "success",
    "calibre": "16/20",
    "dias_prediccion": 30,
    "fecha_objetivo": "2024-03-16",
    "precio_predicho_usd_lb": 3.75,
    "intervalo_confianza": {
      "minimo": 3.52,
      "maximo": 3.98
    },
    "confianza_porcentaje": 85.5,
    "metodo": "Regresión Lineal + EMA",
    "formula": "P(t) = a + b*t + EMA[α=0.3]",
    "parametros": {
      "a": 3.45,
      "b": 0.0087,
      "alpha_ema": 0.3
    },
    "muestras_historicas": 60
  }
  
Lectura:
  • "Mañana (promedio)" + 30 días ≈ 15 de marzo
  • Precio esperado: $3.75/lb
  • Rango probable: $3.52-$3.98/lb (95% confianza)
  • Tendencia: +0.0087 USD/lb por día (ligeramente al alza)
""")

# ============================================================================
# EJEMPLO 6: PREDECIR PRECIO DE DESPACHO (FÓRMULA COMPLETA)
# ============================================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EJEMPLO 6: Predecir Precio de Despacho a 30 Días (FÓRMULA FINAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción:
  • Combina predicción de precio público + correlación histórica
  • Resultado final: precio realista de despacho

Proceso Integrado:
  
  1. Predecir P_público(30) usando Ejemplo 5
  2. Obtener correlación: P_desp = α + β * P_pub
  3. Calcular: P_despacho(30) = α + β * P_público(30)
  4. Propagar error: σ_total = √(σ_pub² + σ_desp²)

Código:
""")

print("""
  import requests
  
  response = requests.get(
      "http://localhost:8000/predict/despacho-price",
      params={
          "calibre": "16/20",
          "presentacion": "HEADLESS",
          "dias": 30
      }
  )
  
  data = response.json()
  
  print(f"PREDICCIÓN A 30 DÍAS ({data['fecha_objetivo']})")
  print(f"\\n═══════ MERCADO PÚBLICO ═══════")
  print(f"Precio predicho: ${data['precio_publico_predicho_usd_lb']:.2f}/lb")
  
  print(f"\\n═════ DESPACHO EXPORQUILSA ═════")
  print(f"Precio predicho: ${data['precio_despacho_predicho_usd_lb']:.2f}/lb")
  print(f"Rango confianza: ${data['intervalo_confianza_despacho']['minimo']:.2f} - ${data['intervalo_confianza_despacho']['maximo']:.2f}/lb")
  
  print(f"\\n════ CORRELACIÓN HISTÓRICA ════")
  print(f"Fórmula: {data['correlacion']['formula']}")
  print(f"R²: {data['correlacion']['r_cuadrado']:.4f}")
  print(f"Confianza predicción: {data['confianza_porcentaje']:.1f}%")
""")

print("""
Respuesta esperada:
  {
    "status": "success",
    "calibre": "16/20",
    "presentacion": "HEADLESS",
    "dias_prediccion": 30,
    "fecha_objetivo": "2024-03-16",
    "precio_publico_predicho_usd_lb": 3.75,
    "precio_despacho_predicho_usd_lb": 4.12,
    "intervalo_confianza_despacho": {
      "minimo": 3.87,
      "maximo": 4.37
    },
    "confianza_porcentaje": 82.3,
    "correlacion": {
      "coeficiente": 0.8742,
      "formula": "P_desp = 0.4521 + 0.9876 * P_pub",
      "r_cuadrado": 0.7642
    },
    "metodo": "Predicción Público + Correlación Histórica",
    "muestras_correlacion": 45
  }
  
Interpretación Final para Tesis:
  
  Dada la correlación histórica entre precios públicos y de despacho:
    P_despacho = 0.4521 + 0.9876 * P_público  (R² = 76.42%)
  
  Y sabiendo que el precio público predicho a 30 días es $3.75/lb:
  
    P_despacho = 0.4521 + 0.9876 * 3.75
    P_despacho = 0.4521 + 3.6535
    P_despacho ≈ $4.12/lb
  
  Con intervalo de confianza (95%): [$3.87, $4.37]
  
  Esta predicción tiene 82.3% de confianza porque:
    - La correlación explica 76.42% de variación
    - El modelo público tiene error ±0.23
    - Error total: √(0.23² + 0.25²) ≈ ±0.34
""")

# ============================================================================
# EJEMPLO 7: FLUJO COMPLETO DE USO
# ============================================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EJEMPLO 7: Flujo Completo de Uso del Sistema
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Script Completo:
""")

print("""
  import requests
  from datetime import date, timedelta
  
  BASE_URL = "http://localhost:8000"
  
  print("Step 1: Obtener precios públicos actuales")
  market_prices = requests.get(f"{BASE_URL}/data/market-prices").json()
  print(f"  ✓ {len(market_prices['precios_consolidados'])} calibres scrapeados")
  
  print("\\nStep 2: Cargar histórico despacho (últimos 30 días)")
  for i in range(1, 31):
      fecha = (date.today() - timedelta(days=i)).isoformat()
      requests.post(
          f"{BASE_URL}/data/save-despacho-history",
          params={
              "fecha": fecha,
              "calibre": "16/20",
              "presentacion": "HEADLESS",
              "precio_usd_lb": 4.50 + (i * 0.01)
          }
      )
  print(f"  ✓ 30 registros de despacho cargados")
  
  print("\\nStep 3: Verificar estado BD")
  status = requests.get(f"{BASE_URL}/database/status").json()
  print(f"  ✓ {status['precios_publicos']['total_registros']} precios públicos")
  print(f"  ✓ {status['precios_despacho']['total_registros']} precios despacho")
  
  print("\\nStep 4: Calcular correlación")
  corr = requests.post(
      f"{BASE_URL}/correlations/calculate",
      params={"calibre": "16/20", "presentacion": "HEADLESS"}
  ).json()
  print(f"  ✓ R² = {corr['r_cuadrado']:.4f}")
  print(f"  ✓ Fórmula: {corr['formula']}")
  
  print("\\nStep 5: Predecir precios a 30 días")
  pred = requests.get(
      f"{BASE_URL}/predict/despacho-price",
      params={"calibre": "16/20", "presentacion": "HEADLESS", "dias": 30}
  ).json()
  
  print(f"  ✓ Fecha predicción: {pred['fecha_objetivo']}")
  print(f"  ✓ Precio público: ${pred['precio_publico_predicho_usd_lb']:.2f}/lb")
  print(f"  ✓ Precio despacho: ${pred['precio_despacho_predicho_usd_lb']:.2f}/lb")
  print(f"  ✓ Rango: ${pred['intervalo_confianza_despacho']['minimo']:.2f} - ${pred['intervalo_confianza_despacho']['maximo']:.2f}/lb")
  print(f"  ✓ Confianza: {pred['confianza_porcentaje']:.1f}%")
""")

print("""
╔════════════════════════════════════════════════════════════════╗
║                    EJEMPLO COMPLETADO                           ║
║                                                                 ║
║  Ahora puedes usar estos ejemplos para:                         ║
║  1. Validar el sistema funcionando                              ║
║  2. Generar datos para tu tesis                                 ║
║  3. Explicar la metodología matemática                          ║
║  4. Documentar las fórmulas y resultados                        ║
╚════════════════════════════════════════════════════════════════╝
""")
