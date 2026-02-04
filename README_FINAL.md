# 📊 SISTEMA DE PREDICCIÓN DE PRECIOS DE CAMARÓN ECUATORIANO

**Maransa - Sistema Inteligente de Estimaciones**  
*Versión 1.0 - Febrero 2024*

---

## 🎯 Descripción General

Sistema completo de **scraping, almacenamiento, análisis y predicción** de precios de camarón ecuatoriano con fundamentación matemática para tesis académica.

**Características principales:**
- ✅ Scraping de 3 fuentes públicas de precios (FreezeOcean, Selina Wamucii, FAO)
- ✅ Base de datos SQLite con histórico de precios
- ✅ Análisis de correlación público-despacho con regresión lineal
- ✅ Predicción de precios a 30 días con intervalos de confianza
- ✅ API REST con 6 endpoints funcionales
- ✅ Documentación completa para tesis académica

---

## 📁 Estructura del Proyecto

```
maransa-ai-service/
│
├── 📄 main.py                           # API FastAPI con 6 endpoints
├── 📄 database.py                       # Clase PriceDatabase (SQLite)
├── 📄 predictor.py                      # Clase PricePredictor (modelos ML)
├── 📄 market_data_scraper.py            # Scrapers de precios públicos
│
├── 🗄️  prices.db                        # Base de datos SQLite (auto-creada)
│
├── 📚 DOCUMENTACION_PREDICCION.md       # Fórmulas matemáticas + schema BD
├── 📚 GUIA_RAPIDA.md                    # Arquitectura, flujo, troubleshooting
├── 📚 EJEMPLOS_USO.py                   # 7 ejemplos prácticos con código
├── 📚 IMPLEMENTACION_RESUMIDA.md        # Resumen de implementación
├── 📚 README.md                         # Este archivo
│
├── 🧪 test_prediction_system.py         # Script de prueba completo
├── 🔍 verificar_sistema.py              # Verificación de setup
│
└── 📦 requirements.txt                  # Dependencias Python
```

---

## 🚀 Instalación Rápida

### 1. Clonar/Descargar el Proyecto
```bash
cd maransa-ai-service
```

### 2. Crear Entorno Virtual (Recomendado)
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Verificar Sistema
```bash
python verificar_sistema.py
```

Deberías ver ✅ en todos los checks.

---

## 🔧 Uso Rápido

### Iniciar Servidor
```bash
python main.py
# ✓ Uvicorn running on http://0.0.0.0:8000
```

### Obtener Precios Actuales
```bash
curl http://localhost:8000/data/market-prices
```

**Respuesta:**
```json
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
  "bd_registros": 6
}
```

### Predecir Precio Despacho (30 días)
```bash
curl "http://localhost:8000/predict/despacho-price?calibre=16/20&presentacion=HEADLESS&dias=30"
```

**Respuesta:**
```json
{
  "status": "success",
  "calibre": "16/20",
  "precio_despacho_predicho_usd_lb": 4.12,
  "intervalo_confianza_despacho": {
    "minimo": 3.87,
    "maximo": 4.37
  },
  "confianza_porcentaje": 82.3,
  "correlacion": {
    "formula": "P_desp = 0.4521 + 0.9876 * P_pub",
    "r_cuadrado": 0.7642
  }
}
```

---

## 📊 Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/data/market-prices` | Obtener precios públicos actuales |
| POST | `/data/save-despacho-history` | Guardar histórico despacho |
| GET | `/database/status` | Estado de la base de datos |
| POST | `/correlations/calculate` | Calcular correlación público-despacho |
| GET | `/predict/future-price` | Predecir precio público futuro |
| GET | `/predict/despacho-price` | Predecir precio despacho futuro |

**Ver documentación completa:** [DOCUMENTACION_PREDICCION.md](DOCUMENTACION_PREDICCION.md)

---

## 🔬 Modelos Matemáticos

### 1️⃣ Predicción Precio Público
```
P_público(t) = a + b*t + EMA[α=0.3]
```
- Regresión lineal: `scipy.stats.linregress`
- Media Móvil Exponencial para suavizado
- Intervalo confianza: ±1.96 * std_err

### 2️⃣ Correlación Público-Despacho
```
P_despacho = α + β * P_público + ε
```
- Regresión bivariada
- R² como métrica de calidad
- Validación p-value < 0.05

### 3️⃣ Predicción Despacho Integrada
```
P_despacho(futuro) = α + β * P_público(futuro)
σ_total = √(σ_pub² + σ_desp²)
```
- Combina ambos modelos
- Propaga error estadísticamente
- Intervalo final documentado

**Fórmulas detalladas:** [DOCUMENTACION_PREDICCION.md](DOCUMENTACION_PREDICCION.md)

---

## 💾 Base de Datos

### Tablas SQLite
- **precios_publicos**: Datos scrapeados (6 calibres)
- **precios_despacho**: Histórico EXPORQUILSA
- **correlaciones**: Modelos de regresión calculados
- **predicciones**: Histórico de predicciones generadas

### Esquema completo:
Ver [DOCUMENTACION_PREDICCION.md](DOCUMENTACION_PREDICCION.md#-base-de-datos)

---

## 📚 Documentación

### Para Entender el Sistema
1. **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** ← Comienza aquí
   - Arquitectura visual
   - Flujo de datos
   - Casos de uso

### Para la Tesis
2. **[DOCUMENTACION_PREDICCION.md](DOCUMENTACION_PREDICCION.md)**
   - Fórmulas matemáticas detalladas
   - Schema de base de datos
   - Endpoints documentados

### Para Programar
3. **[EJEMPLOS_USO.py](EJEMPLOS_USO.py)**
   - 7 ejemplos prácticos
   - Código ejecutable
   - Explicaciones detalladas

### Para Testing
4. **[verificar_sistema.py](verificar_sistema.py)**
   - Verifica instalación
   - Prueba dependencias
   - Prepara datos de prueba

---

## 🧪 Testing y Validación

### Test Completo del Sistema
```bash
python test_prediction_system.py
```

Este script ejecuta:
1. ✅ Scraping de precios públicos
2. ✅ Carga de histórico despacho
3. ✅ Verificación estado BD
4. ✅ Cálculo de correlación
5. ✅ Predicción de precios públicos
6. ✅ Predicción de precios despacho

### Verificación de Setup
```bash
python verificar_sistema.py
```

Verifica:
- ✅ Archivos requeridos
- ✅ Dependencias instaladas
- ✅ Importaciones funcionales
- ✅ Base de datos
- ✅ Modelos matemáticos
- ✅ Documentación

---

## 🎓 Uso para Tesis

### Paso 1: Generar Datos Empíricos
```bash
# Ejecutar el sistema 30+ días
python main.py
# En otra terminal: curl http://localhost:8000/data/market-prices
# Cada día se guardan precios automáticamente
```

### Paso 2: Cargar Histórico EXPORQUILSA
```bash
# Agregar datos históricos manualmente
curl -X POST "http://localhost:8000/data/save-despacho-history" \
  -G --data-urlencode "fecha=2024-02-15" \
  --data-urlencode "calibre=16/20" \
  --data-urlencode "presentacion=HEADLESS" \
  --data-urlencode "precio_usd_lb=4.50"
```

### Paso 3: Generar Resultados
```bash
# Calcular correlación
curl -X POST "http://localhost:8000/correlations/calculate?calibre=16/20&presentacion=HEADLESS"

# Generar predicciones
curl "http://localhost:8000/predict/despacho-price?calibre=16/20&presentacion=HEADLESS&dias=30"
```

### Paso 4: Documentar
- Copiar fórmulas de responses JSON a tu tesis
- Crear tablas con resultados
- Generar gráficos de tendencias

**Ejemplo para Capítulo 2 (Metodología):**
```
2.1 Recolección de Datos
- Scraping de FreezeOcean, Selina Wamucii y FAO Index
- Consolidación con pesos: P_cons = w₁P₁ + w₂P₂ + w₃P₃
- Histórico EXPORQUILSA: carga manual de precios despacho

2.2 Análisis Estadístico
- Correlación bivariada: P_desp = α + β*P_pub (scipy.stats.linregress)
- R² = 0.7642 (explica 76.42% de variación)
- Validación: p-value < 0.05

2.3 Modelos de Predicción
- Regresión lineal: P(t) = a + b*t
- Suavizado exponencial: EMA[i] = 0.3*P[i] + 0.7*EMA[i-1]
- Propagación de error: σ_total = √(σ_pub² + σ_desp²)

2.4 Resultados
[Ver tabla de resultados por calibre]
```

---

## 🐛 Troubleshooting

### "No data found" Error
```
Solución:
1. Verificar scraping: GET /data/market-prices
2. Cargar histórico: POST /data/save-despacho-history
3. Asegurar mín 5-10 registros en cada tabla
```

### "R² muy bajo" (< 0.5)
```
Solución:
1. Verificar suficientes muestras (mín 10-20)
2. Confirmar calibres iguales en ambas tablas
3. Revisar fechas coincidentes
```

### "Predicción poco confiable"
```
Solución:
1. Aumentar histórico (mín 60-90 días)
2. Reducir horizonte de predicción (máx 30 días)
3. Validar que no hay cambios estructurales
```

---

## 📊 Ejemplos de Respuesta

### Predicción Despacho (Ejemplo Completo)
```json
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
```

### Interpretación
```
- Precio esperado despacho: $4.12/lb
- Rango probable: $3.87-$4.37/lb (95% confianza)
- Tendencia precio público: +0.87% diario
- Modelo explica 76.42% de variación
- Basado en 45 observaciones históricas
```

---

## 📈 Características del Sistema

✅ **Web Scraping**
- FreezeOcean WooCommerce API
- Selina Wamucii AJAX + HTML parsing
- FAO Index como multiplicador
- Consolidación inteligente

✅ **Base de Datos**
- SQLite persistente
- 4 tablas normalizadas
- Métodos CRUD completos
- Transacciones validadas

✅ **Análisis Matemático**
- Regresión lineal (scipy.stats.linregress)
- Media móvil exponencial
- Propagación de errores
- Intervalos de confianza

✅ **API REST**
- FastAPI con validación Pydantic
- 6 endpoints funcionales
- Respuestas JSON documentadas
- CORS habilitado

✅ **Documentación**
- Fórmulas matemáticas explícitas
- Ejemplos de código ejecutable
- Schema de base de datos
- Troubleshooting completo

---

## 💡 Casos de Uso

### Gerente de EXPORQUILSA
```
GET /data/market-prices
→ Obtiene precios públicos actuales para decisiones diarias

GET /predict/despacho-price?calibre=16/20&dias=7
→ Predice precio despacho próxima semana para ajustar compras
```

### Investigador/Tesis
```
POST /correlations/calculate
→ Obtiene R² documentado para justificar tesis

GET /predict/despacho-price
→ Genera datos empíricos de predicciones
```

### Analista de Mercado
```
GET /database/status
→ Consulta rango de datos disponibles

GET /predict/future-price?dias=30
→ Estudia tendencias futuras del mercado
```

---

## 🔒 Requisitos Técnicos

### Mínimos
- Python 3.8+
- SQLite 3.0+
- 100MB disco libre

### Recomendados
- Python 3.10+
- 4GB RAM
- Conexión internet estable (para scraping)

### Dependencias Python
Ver [requirements.txt](requirements.txt)

---

## 📞 Soporte y Contacto

### Debugging
```bash
# Ver estado actual
curl http://localhost:8000/database/status

# Verificar instalación
python verificar_sistema.py

# Ejecutar tests completos
python test_prediction_system.py
```

### Documentación
- Fórmulas: Ver [DOCUMENTACION_PREDICCION.md](DOCUMENTACION_PREDICCION.md)
- Arquitectura: Ver [GUIA_RAPIDA.md](GUIA_RAPIDA.md)
- Ejemplos: Ver [EJEMPLOS_USO.py](EJEMPLOS_USO.py)

---

## 📝 Licencia y Uso Académico

Este sistema fue desarrollado para investigación académica en economía de mercados de camarón ecuatoriano.

**Para tu tesis, puedes:**
- ✅ Usar las fórmulas matemáticas
- ✅ Documentar la metodología
- ✅ Incluir resultados como datos empíricos
- ✅ Compartir código en apéndices

**Por favor incluir en tesis:**
- Referencia a este sistema en metodología
- Fórmulas con derivación matemática
- Validación de supuestos (R², p-value)
- Limitaciones del modelo

---

## 🎯 Próximos Pasos

1. **Setup**
   ```bash
   python verificar_sistema.py
   ```

2. **Iniciar**
   ```bash
   python main.py
   ```

3. **Probar**
   ```bash
   python test_prediction_system.py
   ```

4. **Documentar**
   - Copiar fórmulas a tesis
   - Agregar gráficos
   - Validar metodología

---

## ✅ Checklist Final

- [ ] Verificación de sistema pasada
- [ ] Servidor FastAPI iniciado
- [ ] Endpoints probados manualmente
- [ ] Datos de prueba cargados
- [ ] Correlación calculada
- [ ] Predicción generada
- [ ] Respuesta JSON validada
- [ ] Fórmulas documentadas
- [ ] Ready para tesis

---

## 📄 Versión e Información

**Maransa v1.0**
- Creado: Febrero 2024
- Estado: Production Ready ✅
- Mantenimiento: Activo
- Licencia: Academic Use

---

*Sistema de Predicción de Precios de Camarón Ecuatoriano*
*Desarrollado para investigación académica de precios de mercado*

**¿Preguntas?** Ver documentación en carpeta `docs/`
