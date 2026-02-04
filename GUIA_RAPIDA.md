# GUÍA RÁPIDA DE IMPLEMENTACIÓN

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA DE PREDICCIÓN                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 1. CAPA DE DATOS (Web Scraping)                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  FreezeOcean ──┐                                             │
│                ├──→ consolidation ──→ Precios Públicos      │
│  Selina Wamucii┤                                             │
│  FAO Index ────┘                                             │
│                                                              │
│  EXPORQUILSA ──────→ Precios de Despacho                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CAPA DE ALMACENAMIENTO (SQLite)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ precios_publicos                                      │  │
│  │ ├─ fecha                                              │  │
│  │ ├─ calibre (16/20, 21/25, ...)                       │  │
│  │ ├─ precio_usd_lb                                     │  │
│  │ └─ fuente, confiabilidad, metadata                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ precios_despacho                                      │  │
│  │ ├─ fecha                                              │  │
│  │ ├─ calibre, presentacion                             │  │
│  │ ├─ precio_usd_lb                                     │  │
│  │ └─ origen (EXPORQUILSA)                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ correlaciones                                         │  │
│  │ ├─ calibre, presentacion                             │  │
│  │ ├─ coeficiente_correlacion, r_cuadrado              │  │
│  │ ├─ formula: P_desp = α + β * P_pub                  │  │
│  │ └─ muestras, fecha_calculo                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. CAPA DE ANÁLISIS (Modelos Matemáticos)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Correlación Análisis        Predicción Pública              │
│  ├─ scipy.stats.linregress   ├─ Regresión lineal           │
│  ├─ P_desp = α + β * P_pub   ├─ P(t) = a + b*t             │
│  ├─ R² calculation            ├─ EMA smoothing              │
│  └─ Error estimation          └─ Interval confidence        │
│                                                              │
│  Predicción Despacho                                        │
│  ├─ Predict public price                                    │
│  ├─ Apply correlation formula                               │
│  ├─ Propagate error: √(σ²_pub + σ²_desp)                  │
│  └─ Return final prediction with bounds                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. CAPA DE API (FastAPI Endpoints)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  GET  /data/market-prices         → Precios públicos       │
│  POST /data/save-despacho-history → Guardar histórico      │
│  GET  /database/status            → Estado BD              │
│  POST /correlations/calculate     → Correlación            │
│  GET  /predict/future-price       → Predicción pública     │
│  GET  /predict/despacho-price     → Predicción despacho    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. RESPUESTA A USUARIO                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✓ Precios públicos actuales (6 calibres)                  │
│  ✓ Correlación histórica con R² documentado                │
│  ✓ Predicción a 30 días con intervalo confianza           │
│  ✓ Fórmulas matemáticas explícitas para tesis             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Modelos Matemáticos Implementados

### Modelo 1: Predicción de Precio Público

**Fórmula:**
```
P_público(t) = a + b*t + EMA[α=0.3]
```

**Pasos de Cálculo:**

1. **Regresión Lineal**
   ```python
   from scipy.stats import linregress
   
   # X: días desde hoy (0, -1, -2, ..., -89)
   # Y: precios históricos
   slope, intercept, r_value, p_value, std_err = linregress(X, Y)
   
   # a = intercept
   # b = slope
   # std_err = desviación estándar del error
   ```

2. **Media Móvil Exponencial (Suavizado)**
   ```python
   EMA[0] = precio[0]
   for i in 1:n:
       EMA[i] = α * precio[i] + (1-α) * EMA[i-1]
   
   Con α = 0.3 (30% peso precio actual, 70% histórico)
   ```

3. **Predicción a 30 Días**
   ```python
   t_futuro = 30
   P(30) = a + b * 30 + ajuste_EMA
   
   Intervalo: [P(30) - 1.96*std_err, P(30) + 1.96*std_err]
   Confianza: R² * 100%
   ```

### Modelo 2: Correlación Público ↔ Despacho

**Fórmula:**
```
P_despacho = α + β * P_público + ε
```

**Cálculo:**
```python
from scipy.stats import linregress

# Datos históricos coincidentes
X = [precio_publico_1, precio_publico_2, ..., precio_publico_n]
Y = [precio_despacho_1, precio_despacho_2, ..., precio_despacho_n]

slope, intercept, r_value, p_value, std_err = linregress(X, Y)

# Resultados
alpha = intercept     # Margen base
beta = slope          # Sensibilidad
r_squared = r_value²  # Calidad del ajuste (0-1)
formula = f"P_desp = {alpha:.4f} + {beta:.4f} * P_pub"
```

### Modelo 3: Predicción Despacho Futuro

**Proceso Integrado:**
```
1. P_public_future ← Predecir usando Modelo 1
2. P_despacho_future = α + β * P_public_future
3. σ_total = √(σ_público² + σ_despacho²)
4. Return: precio ± intervalo con confianza
```

---

## 🔄 Flujo de Datos

```
DÍA 1: Scraping
───────────────
├─ FreezeOcean API → 6 calibres
├─ Selina Wamucii AJAX → 1 promedio
├─ FAO Index → multiplicador
└─ → Guardado en precios_publicos


DÍA 30: Cargar Histórico
─────────────────────────
├─ Leer CSV EXPORQUILSA
├─ Validar calibres/presentaciones
└─ → Guardado en precios_despacho


ANÁLISIS: Correlación
──────────────────────
├─ Obtener 30 pares (público, despacho)
├─ Regresión lineal
├─ Calcular R²
└─ → Guardado en correlaciones
    Ejemplo: P_desp = 0.452 + 0.988 * P_pub (R²=0.764)


PREDICCIÓN: Precio Público a 30 días
──────────────────────────────────────
├─ Input: calibre="16/20", dias=30
├─ Obtener histórico 90 días
├─ Regresión + EMA + confianza
└─ Output: $3.75 ± $0.23 (85.5% confianza)


PREDICCIÓN FINAL: Precio Despacho a 30 días
─────────────────────────────────────────────
├─ Input: calibre="16/20", presentacion="HEADLESS", dias=30
├─ Precio público predicho: $3.75
├─ Aplicar correlación: $3.75 * 0.988 + 0.452 = $4.12
├─ Error total: √(0.23² + 0.25²) = $0.34
└─ Output: $4.12 ± $0.34 (82.3% confianza)
```

---

## 💾 Base de Datos - Ejemplo de Datos

### precios_publicos
```
fecha        | calibre | precio_usd_lb | fuente           | confiabilidad
─────────────┼─────────┼───────────────┼──────────────────┼──────────────
2024-02-15   | 16/20   | 3.45          | freezeocean      | 0.90
2024-02-15   | 21/25   | 4.10          | freezeocean      | 0.90
2024-02-15   | 16/20   | 3.40          | selina_wamucii   | 0.75
2024-02-14   | 16/20   | 3.42          | freezeocean      | 0.90
...
```

### precios_despacho
```
fecha        | calibre | presentacion | precio_usd_lb | origen
─────────────┼─────────┼──────────────┼───────────────┼─────────────
2024-02-15   | 16/20   | HEADLESS     | 4.50          | EXPORQUILSA
2024-02-14   | 16/20   | HEADLESS     | 4.48          | EXPORQUILSA
2024-02-13   | 16/20   | HEADLESS     | 4.55          | EXPORQUILSA
...
```

### correlaciones
```
calibre | presentacion | coeficiente | r_cuadrado | formula
────────┼──────────────┼─────────────┼────────────┼──────────────────────────────
16/20   | HEADLESS     | 0.9876      | 0.9754     | P_desp = 0.4521 + 0.9876*P_pub
21/25   | HEADLESS     | 1.0234      | 0.8642     | P_desp = 0.3890 + 1.0234*P_pub
...
```

---

## 🎯 Casos de Uso

### Caso 1: Gerente EXPORQUILSA (Decisiones Diarias)
```
1. GET /data/market-prices
   ✓ Obtiene precios públicos actuales

2. GET /predict/despacho-price?calibre=16/20&presentacion=HEADLESS&dias=7
   ✓ Predice precio despacho próxima semana
   ✓ Usa para ajustar precios de compra
```

### Caso 2: Investigador/Tesis
```
1. POST /correlations/calculate?calibre=16/20&presentacion=HEADLESS
   ✓ Obtiene R² documentado para justificar tesis

2. GET /predict/despacho-price?calibre=16/20&presentacion=HEADLESS&dias=30
   ✓ Genera datos empíricos
   ✓ Documenta fórmulas matemáticas

3. GET /database/status
   ✓ Muestra cantidad de observaciones
   ✓ Valida metodología
```

### Caso 3: Análisis Histórico
```
1. GET /database/status
   ✓ Ver rango de datos disponibles

2. POST /correlations/calculate
   ✓ Analizar correlación por calibre/presentación

3. GET /predict/future-price
   ✓ Estudiar tendencias por período
```

---

## ⚙️ Configuración Requerida

### Dependencias Python
```
fastapi==0.104.1
pydantic==2.0.0
numpy==1.24.0
scipy==1.11.0
pandas==2.0.0
aiohttp==3.9.0
requests==2.31.0
beautifulsoup4==4.12.0
```

### Variables de Entorno (.env)
```
WEATHER_API_KEY=xxx
EXCHANGE_API_KEY=xxx
DATABASE_PATH=./prices.db
SCRAPING_INTERVAL=3600
```

### Estructura de Archivos
```
maransa-ai-service/
├── main.py                          # API FastAPI
├── database.py                      # Clase PriceDatabase (SQLite)
├── predictor.py                     # Clase PricePredictor (ML)
├── market_data_scraper.py           # Scrapers (FreezeOcean, Selina, FAO)
├── prices.db                        # Base de datos SQLite
├── requirements.txt                 # Dependencias
├── DOCUMENTACION_PREDICCION.md      # Documentación completa
├── EJEMPLOS_USO.py                  # Ejemplos prácticos
└── README.md                        # Este archivo
```

---

## 🚀 Inicio Rápido

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Iniciar Servidor
```bash
python main.py
# ✓ Server running on http://localhost:8000
```

### 3. Ejecutar Scraping
```bash
curl http://localhost:8000/data/market-prices
```

### 4. Cargar Histórico
```bash
curl -X POST "http://localhost:8000/data/save-despacho-history" \
  -G --data-urlencode "fecha=2024-02-15" \
  --data-urlencode "calibre=16/20" \
  --data-urlencode "presentacion=HEADLESS" \
  --data-urlencode "precio_usd_lb=4.50"
```

### 5. Calcular Correlación
```bash
curl -X POST "http://localhost:8000/correlations/calculate" \
  -G --data-urlencode "calibre=16/20" \
  --data-urlencode "presentacion=HEADLESS"
```

### 6. Predecir Futuro
```bash
curl "http://localhost:8000/predict/despacho-price" \
  -G --data-urlencode "calibre=16/20" \
  --data-urlencode "presentacion=HEADLESS" \
  --data-urlencode "dias=30"
```

---

## 📝 Para Tu Tesis

### Capitulo: Metodología
```
2.1 Recolección de Datos

Se implementó un sistema de web scraping que obtiene precios 
públicos de camarón de tres fuentes:
- FreezeOcean (WooCommerce API)
- Selina Wamucii (AJAX + HTML parsing)
- FAO Index (análisis de tendencia)

Los precios se consolidan con pesos según confiabilidad:
  P_consolidado = w₁*P₁ + w₂*P₂ + w₃*P₃
  donde wᵢ = confiabilidad_fuente / Σ confiabilidades

2.2 Análisis de Correlación

Se aplica regresión lineal mediante scipy.stats.linregress:
  
  P_despacho = α + β * P_público + ε
  
Donde:
- α (intercept): Margen base de EXPORQUILSA
- β (slope): Sensibilidad al cambio de precio público
- ε (residual): Error aleatorio ~ N(0, σ²)
- R²: Proporción de varianza explicada

2.3 Modelo de Predicción

Se utiliza regresión lineal con suavizado exponencial:

  P(t) = a + b*t + EMA[α=0.3]
  
Donde:
- a, b: Parámetros estimados por minimos cuadrados
- EMA[i] = 0.3 * precio[i] + 0.7 * EMA[i-1]

2.4 Propagación de Errores

El error total se calcula como:
  
  σ_total = √(σ_público² + σ_despacho²)
  
Intervalo de confianza (95%):
  
  [P ± 1.96 * σ_total]

3. Resultados

Ver archivo DOCUMENTACION_PREDICCION.md
```

---

## 🐛 Troubleshooting

### Problema: "No data found"
```
Solución: 
1. Verificar que el scraping funcionó: GET /data/market-prices
2. Cargar al menos 10 registros históricos de despacho
3. Asegurar que hay datos en ambas tablas (público y despacho)
```

### Problema: "R² muy bajo" (< 0.5)
```
Solución:
1. Asegurar que hay suficientes muestras (mín 10-20)
2. Revisar que los datos sean del mismo calibre/presentación
3. Validar que las fechas coincidan entre público y despacho
```

### Problema: "Predicción poco confiable"
```
Solución:
1. Aumentar días de histórico (mín 60-90 días)
2. Verificar que no hay cambios estructurales en mercado
3. Reducir horizonte de predicción (mín 7 días, máx 30 días)
```

---

*Sistema de Predicción de Precios de Camarón - MARANSA*
*Versión 1.0 - Febrero 2024*
