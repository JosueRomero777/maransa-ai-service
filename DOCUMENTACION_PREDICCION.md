# Sistema de Predicción de Precios - Documentación Completa

## 📊 Resumen del Sistema

Sistema integrado para:
1. **Scraping** de precios públicos de camarón desde múltiples fuentes
2. **Almacenamiento** en base de datos SQLite de histórico de precios
3. **Análisis** de correlación entre precios públicos y de despacho
4. **Predicción** de precios futuros con modelos matemáticos fundamentados
5. **Cálculo** de precios de despacho realistas basados en correlación histórica

---

## 🔬 Modelos Matemáticos Implementados

### 1. Predicción de Precio Público
**Fórmula Principal:**
```
P_público(t) = a + b*t + EMA[t]
```

Donde:
- **a**: Intercepto (precio base estimado)
- **b**: Pendiente (tendencia diaria en USD/lb)
- **t**: Días en el futuro
- **EMA[t]**: Media Móvil Exponencial con α=0.3

**Implementación:**
```
1. Obtener histórico de n días de precios públicos
2. Aplicar regresión lineal: scipy.stats.linregress(dias, precios)
3. Calcular EMA: EMA[i] = α * precio[i] + (1-α) * EMA[i-1]
4. Predicción: P(t+30) = a + b*(t+30) + ajuste_EMA
5. Intervalo confianza: ±1.96 * std_err
```

**R² esperado:** > 0.7 (buena correlación en tendencias cortas)

---

### 2. Correlación Precio Público ↔ Precio Despacho
**Fórmula de Regresión Lineal:**
```
P_despacho = α + β * P_público + ε
```

Donde:
- **α**: Intercepto (margen base)
- **β**: Coeficiente de correlación
- **P_público**: Precio público independiente
- **ε**: Error residual ~N(0, σ²)

**Cálculo:**
```
Using scipy.stats.linregress():
  slope (β), intercept (α), r_value, p_value, std_err = linregress(P_pub, P_desp)
  
Validación:
  r_squared = r_value² 
  formula = f"P_desp = {α:.4f} + {β:.4f} * P_pub"
```

**Interpretación R²:**
- R² > 0.9: Excelente (explica >90% variación)
- 0.7 < R² < 0.9: Buena (explica 70-90%)
- 0.5 < R² < 0.7: Moderada (explica 50-70%)
- R² < 0.5: Débil (explica <50%)

---

### 3. Predicción de Precio de Despacho
**Fórmula Integrada:**
```
1. P_público_futuro = Predicción Modelo 1
2. P_despacho_futuro = α + β * P_público_futuro
3. Error total = √(σ_público² + σ_despacho²)
```

**Ventajas:**
- Utiliza tendencia del mercado público
- Incorpora correlación histórica
- Propaga error de forma estadística

---

## 📁 Estructura Base de Datos

### Tabla: precios_publicos
```sql
CREATE TABLE precios_publicos (
    id INTEGER PRIMARY KEY,
    fecha DATE NOT NULL,
    calibre TEXT NOT NULL,
    precio_usd_lb REAL NOT NULL,
    fuente TEXT,
    cantidad_fuentes INTEGER,
    confiabilidad REAL,
    metadata JSON,
    UNIQUE(fecha, calibre, fuente)
);
```

### Tabla: precios_despacho
```sql
CREATE TABLE precios_despacho (
    id INTEGER PRIMARY KEY,
    fecha DATE NOT NULL,
    calibre TEXT NOT NULL,
    presentacion TEXT NOT NULL,
    precio_usd_lb REAL NOT NULL,
    origen TEXT DEFAULT 'EXPORQUILSA',
    metadata JSON,
    UNIQUE(fecha, calibre, presentacion)
);
```

### Tabla: correlaciones
```sql
CREATE TABLE correlaciones (
    id INTEGER PRIMARY KEY,
    calibre TEXT NOT NULL,
    presentacion TEXT NOT NULL,
    ratio_promedio REAL,
    coeficiente_correlacion REAL,
    desviacion_estandar REAL,
    muestras INTEGER,
    fecha_calculo DATE,
    formula TEXT,
    r_cuadrado REAL,
    UNIQUE(calibre, presentacion)
);
```

### Tabla: predicciones
```sql
CREATE TABLE predicciones (
    id INTEGER PRIMARY KEY,
    fecha_prediccion DATE,
    fecha_objetivo DATE,
    calibre TEXT,
    presentacion TEXT,
    precio_publico_predicho REAL,
    precio_despacho_predicho REAL,
    confianza REAL,
    metodo TEXT,
    parametros JSON
);
```

---

## 🌐 Endpoints API

### 1. Obtener Precios Públicos Actuales
```
GET /data/market-prices
```
**Respuesta:**
```json
{
  "status": "success",
  "precios_consolidados": {
    "16/20": 3.50,
    "21/25": 4.20,
    ...
  },
  "bd_status": "guardado",
  "bd_registros": 6
}
```

### 2. Guardar Histórico de Despacho
```
POST /data/save-despacho-history
Parameters:
  fecha: "2024-01-15" (YYYY-MM-DD)
  calibre: "16/20"
  presentacion: "HEADLESS"
  precio_usd_lb: 4.50
  origen: "EXPORQUILSA" (default)
```

### 3. Calcular Correlación
```
POST /correlations/calculate?calibre=16/20&presentacion=HEADLESS
```
**Respuesta:**
```json
{
  "status": "success",
  "ratio_promedio": 1.3245,
  "coeficiente_correlacion": 0.8742,
  "r_cuadrado": 0.7642,
  "formula": "P_desp = 0.4521 + 0.9876 * P_pub",
  "muestras": 45,
  "interpretacion": {
    "calidad": "Buena",
    "r_cuadrado_porcentaje": "76.42%"
  }
}
```

### 4. Predecir Precio Público
```
GET /predict/future-price?calibre=16/20&dias=30
```
**Respuesta:**
```json
{
  "status": "success",
  "calibre": "16/20",
  "dias_prediccion": 30,
  "fecha_objetivo": "2024-02-15",
  "precio_predicho_usd_lb": 3.75,
  "intervalo_confianza": {
    "minimo": 3.52,
    "maximo": 3.98
  },
  "confianza_porcentaje": 85.5,
  "formula": "P(t) = a + b*t + EMA",
  "parametros": {
    "a": 3.45,
    "b": 0.0087,
    "alpha_ema": 0.3
  },
  "muestras_historicas": 60
}
```

### 5. Predecir Precio de Despacho
```
GET /predict/despacho-price?calibre=16/20&presentacion=HEADLESS&dias=30
```
**Respuesta:**
```json
{
  "status": "success",
  "calibre": "16/20",
  "presentacion": "HEADLESS",
  "dias_prediccion": 30,
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
  "muestras_correlacion": 45
}
```

### 6. Estado de la Base de Datos
```
GET /database/status
```
**Respuesta:**
```json
{
  "status": "success",
  "database_file": "prices.db",
  "precios_publicos": {
    "total_registros": 186,
    "fecha_inicio": "2024-01-01",
    "fecha_fin": "2024-02-15",
    "calibres": ["16/20", "21/25", "26/30", "31/35", "36/40", "41/50"]
  },
  "precios_despacho": {
    "total_registros": 35,
    "fecha_inicio": "2024-01-01",
    "fecha_fin": "2024-02-15",
    "combinaciones": ["16/20 HEADLESS", "21/25 HEADLESS", ...]
  },
  "correlaciones_calculadas": 6,
  "predicciones_guardadas": 12
}
```

---

## 🚀 Flujo de Uso Completo

### Paso 1: Scraping Automático
```bash
# El endpoint /data/market-prices se ejecuta automáticamente
# y guarda los precios en la BD
curl http://localhost:8000/data/market-prices
```

### Paso 2: Cargar Histórico EXPORQUILSA
```bash
# Cargar múltiples registros históricos
for i in {1..30}; do
  fecha=$(date -d "-$i days" +%Y-%m-%d)
  curl -X POST "http://localhost:8000/data/save-despacho-history" \
    -G --data-urlencode "fecha=$fecha" \
    --data-urlencode "calibre=16/20" \
    --data-urlencode "presentacion=HEADLESS" \
    --data-urlencode "precio_usd_lb=4.50"
done
```

### Paso 3: Verificar Estado BD
```bash
curl http://localhost:8000/database/status
```

### Paso 4: Calcular Correlaciones
```bash
# Para cada combinación calibre/presentación disponible
curl -X POST "http://localhost:8000/correlations/calculate?calibre=16/20&presentacion=HEADLESS"
```

### Paso 5: Generar Predicciones
```bash
# Predicción precio público
curl "http://localhost:8000/predict/future-price?calibre=16/20&dias=30"

# Predicción precio despacho
curl "http://localhost:8000/predict/despacho-price?calibre=16/20&presentacion=HEADLESS&dias=30"
```

---

## 📋 Calibres Disponibles

Calibres normalizados en la BD:

| Rango | Descripción |
|-------|-------------|
| 16/20 | Camarón pequeño |
| 21/25 | Camarón pequeño-medio |
| 26/30 | Camarón medio |
| 31/35 | Camarón medio-grande |
| 36/40 | Camarón grande |
| 41/50 | Camarón muy grande |

---

## 💡 Justificación para Tesis

### Ventajas del Sistema:

1. **Fundamentación Matemática:**
   - Regresión lineal con intervalos de confianza
   - Media Móvil Exponencial para capturar tendencias recientes
   - Correlación bivariada con R² documentado

2. **Datos Históricos Reales:**
   - Precios públicos de múltiples fuentes (FreezeOcean, Selina Wamucii, etc.)
   - Datos de despacho de EXPORQUILSA
   - Validación de correlación en datos reales

3. **Propagación de Errores:**
   - Error total = √(error_público² + error_correlación²)
   - Intervalos de confianza ±1.96 * std_err

4. **Reproducibilidad:**
   - Todos los parámetros guardados en BD
   - Fórmulas documentadas en cada predicción
   - Metodología claramente especificada

---

## 🔍 Variables Críticas para Documentación

### Parámetros de Regresión Pública
```
Variable           Descripción                    Unidad
─────────────────────────────────────────────────────
a (intercept)      Precio base estimado           USD/lb
b (slope)          Tendencia diaria               USD/(lb·día)
std_err            Error estándar                 USD/lb
r_squared          Calidad del ajuste             %
```

### Parámetros de Correlación
```
Variable                   Descripción                    Unidad
──────────────────────────────────────────────────────────
α (intercept)              Margen base despacho           USD/lb
β (slope)                  Sensibilidad a precio público   -
r_squared                  Explicación de variación       %
σ (std dev)                Dispersión de residuos         USD/lb
```

---

## ⚠️ Limitaciones y Consideraciones

1. **Datos Insuficientes:**
   - Sistema requiere mínimo 10-20 observaciones por calibre
   - Correlación requiere mínimo 5-10 puntos históricos coincidentes

2. **Cambios de Mercado:**
   - Modelo asume continuidad
   - Cambios estructurales pueden invalidar predicción

3. **Horizontes de Predicción:**
   - Óptimo: 7-30 días
   - Riesgoso: > 60 días

4. **Calibres/Presentaciones:**
   - Predicción solo posible con datos previos
   - Nuevas combinaciones requieren período de observación

---

## 📞 Soporte Técnico

### Debugging

**Problema:** No hay datos en BD
```bash
# Verificar último scraping
curl http://localhost:8000/database/status

# Verificar precios públicos scrapeados
curl http://localhost:8000/data/market-prices

# Verificar registro manual
curl -X POST "http://localhost:8000/data/save-despacho-history" \
  -G --data-urlencode "fecha=2024-02-15" \
  --data-urlencode "calibre=16/20" \
  --data-urlencode "presentacion=HEADLESS" \
  --data-urlencode "precio_usd_lb=4.50"
```

**Problema:** Correlación sin datos suficientes
```
Solución: Asegurar mínimo de 5 registros en ambas tablas (público y despacho) 
con fechas coincidentes
```

---

## 📚 Referencias Bibliográficas

- Montgomery, D. C., & Runger, G. C. (2013). Applied Statistics and Probability for Engineers. Wiley.
- Cipra, T. (2010). Time Series Forecasting. Karlin, Charles University.
- FAO Fisheries. (2023). Market Reports on Shrimp - Global Overview.

---

*Documento generado para Sistema de Predicción de Precios - Camarón Ecuatoriano*
*Versión 1.0 - Febrero 2024*
