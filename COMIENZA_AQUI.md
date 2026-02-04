# 🚀 COMIENZA AQUÍ

## ✅ Sistema de Predicción de Precios - Maransa v1.0

Bienvenido al **Sistema Completo de Predicción de Precios de Camarón Ecuatoriano**

Este archivo te guiará en **3 pasos simples** para empezar.

---

## 📋 Los 3 Pasos

### PASO 1️⃣: VERIFICAR (2 minutos)
```bash
python verificar_sistema.py
```

**Esto verifica que:**
- ✅ Todos los archivos están presentes
- ✅ Las dependencias Python están instaladas
- ✅ La base de datos funciona
- ✅ Los modelos matemáticos cargan

**Si ve todo verde (✅):** Continúa al Paso 2

**Si ve algo rojo (❌):** Ver sección "Ayuda" abajo

---

### PASO 2️⃣: INICIAR (1 minuto)
```bash
python main.py
```

**Deberías ver:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Deja este terminal abierto. En otra terminal, ve al Paso 3.

---

### PASO 3️⃣: PROBAR (5 minutos)
En una **nueva terminal**, ejecuta:
```bash
python test_prediction_system.py
```

**Esto:**
1. ✅ Obtiene precios públicos scrapeados
2. ✅ Carga histórico de despacho
3. ✅ Calcula correlaciones
4. ✅ Genera predicciones
5. ✅ Muestra todas las fórmulas

---

## 🎉 ¡Listo!

Si llegaste aquí sin errores, el sistema **está funcionando correctamente**.

**Próximo paso:** Leer la documentación

---

## 📚 ¿Qué Leer Ahora?

Elige según tu necesidad:

### 👨‍💼 "Solo quiero empezar rápido"
```
Lee: README_FINAL.md (5 min)
Luego: Mantén python main.py corriendo
Luego: Haz curl requests manuales
```

### 👨‍🎓 "Necesito para mi tesis"
```
1. Lee: MAPA_DOCUMENTACION.md → "Para Tesis"
2. Lee: IMPLEMENTACION_RESUMIDA.md → "Para Tu Tesis"
3. Copia: Template de metodología
4. Ejecuta: system 30+ días para datos
5. Genera: Predicciones y resultados
```

### 👨‍💻 "Soy programador/quiero profundizar"
```
1. Lee: GUIA_RAPIDA.md (entender arquitectura)
2. Lee: EJEMPLOS_USO.py (ver código)
3. Lee: DOCUMENTACION_PREDICCION.md (fórmulas exactas)
4. Explora: Código fuente (main.py, database.py, etc.)
```

### 🔍 "Algo no funciona"
```
1. Ejecuta: python verificar_sistema.py
2. Lee: Sección "Troubleshooting" en GUIA_RAPIDA.md
3. Si sigue fallando: Ver "Ayuda" abajo
```

---

## 📖 Mapa de Documentación

```
COMIENZA AQUÍ (este archivo)
    ↓
    ├─→ README_FINAL.md (introducción)
    │   ├─→ ¿Qué es el sistema?
    │   ├─→ Cómo instalarlo
    │   └─→ Endpoints disponibles
    │
    ├─→ MAPA_DOCUMENTACION.md (¿qué leer?)
    │   ├─→ Guía por perfil
    │   ├─→ Búsqueda rápida
    │   └─→ Índice temático
    │
    ├─→ GUIA_RAPIDA.md (cómo funciona)
    │   ├─→ Arquitectura visual
    │   ├─→ Flujo de datos
    │   ├─→ Modelos matemáticos
    │   └─→ Troubleshooting
    │
    ├─→ DOCUMENTACION_PREDICCION.md (referencia técnica)
    │   ├─→ Fórmulas detalladas
    │   ├─→ Schema BD
    │   ├─→ Endpoints documentados
    │   └─→ Interpretación de resultados
    │
    ├─→ EJEMPLOS_USO.py (código ejecutable)
    │   ├─→ 7 ejemplos prácticos
    │   ├─→ Código listo para copiar
    │   └─→ Respuestas esperadas
    │
    ├─→ IMPLEMENTACION_RESUMIDA.md (para tesis)
    │   ├─→ Qué se implementó
    │   ├─→ Template de metodología
    │   └─→ Cómo usarlo en tesis
    │
    └─→ Código Fuente
        ├─→ main.py (API endpoints)
        ├─→ database.py (SQLite)
        ├─→ predictor.py (modelos ML)
        └─→ market_data_scraper.py (scraping)
```

---

## 💡 Ejemplos Rápidos

### Obtener Precios Actuales
```bash
curl http://localhost:8000/data/market-prices
```

**Respuesta:**
```json
{
  "precios_consolidados": {
    "16/20": 3.45,
    "21/25": 4.10,
    ...
  }
}
```

### Predecir Precio Despacho (30 días)
```bash
curl "http://localhost:8000/predict/despacho-price?calibre=16/20&presentacion=HEADLESS&dias=30"
```

**Respuesta:**
```json
{
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

### Ver Estado BD
```bash
curl http://localhost:8000/database/status
```

---

## 🎯 Funcionalidades Principales

✅ **Scraping de Precios**
- FreezeOcean (WooCommerce API)
- Selina Wamucii (AJAX + HTML)
- FAO Index (tendencia)

✅ **Base de Datos SQLite**
- 4 tablas normalizadas
- Histórico de 90+ días
- Transacciones validadas

✅ **Análisis Estadístico**
- Regresión lineal (scipy)
- Correlación público-despacho
- R² documentado

✅ **Predicción Inteligente**
- Modelo: P(t) = a + b*t + EMA
- Correlación: P_desp = α + β*P_pub
- Intervalo confianza: ±1.96σ

✅ **API REST Completa**
- 6 endpoints funcionales
- Respuestas JSON detalladas
- Fórmulas explícitas en cada respuesta

---

## 🔄 Flujo del Sistema

```
INTERNET (Fuentes)
    ↓
SCRAPING (FreezeOcean, Selina, FAO)
    ↓
CONSOLIDACIÓN (Pesos inteligentes)
    ↓
BASE DE DATOS SQLite
    ├─ precios_publicos
    ├─ precios_despacho
    ├─ correlaciones
    └─ predicciones
    ↓
ANÁLISIS MATEMÁTICO
    ├─ Regresión lineal
    ├─ Media móvil exponencial
    └─ Propagación de errores
    ↓
PREDICCIÓN
    ├─ Precio público futuro
    ├─ Correlación histórica
    └─ Precio despacho futuro
    ↓
API REST (6 endpoints)
    ↓
TU APLICACIÓN / TESIS
```

---

## 🚨 Ayuda Rápida

### "python verificar_sistema.py da error"

**Opción 1: Verificar Python**
```bash
python --version  # Debe ser 3.8 o mayor
```

**Opción 2: Reinstalar dependencias**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Opción 3: Crear entorno limpio**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### "El servidor da error al iniciar"

```bash
# 1. Verificar que el puerto 8000 está libre
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 2. Si está en uso, cambiar puerto en main.py:
# Línea final: uvicorn.run(app, host="0.0.0.0", port=8001)
```

### "Los endpoints retornan error"

```bash
# 1. Verificar que el servidor está corriendo
curl http://localhost:8000/health

# 2. Cargar datos de prueba
python verificar_sistema.py  # Agrega datos automáticamente

# 3. Probar again
curl http://localhost:8000/predict/future-price?calibre=16/20&dias=30
```

---

## ✨ Para Tu Tesis

### La Forma Más Fácil:

1. **Setup (5 min)**
   ```bash
   python verificar_sistema.py
   python main.py
   ```

2. **Ejecutar 30+ días**
   - El sistema automáticamente scrappea y guarda precios

3. **Generar Datos (5 min)**
   ```bash
   python test_prediction_system.py
   ```
   Esto genera:
   - Correlación calculada (con R²)
   - Predicción de precios
   - Fórmulas explícitas

4. **Copiar a Tesis**
   - Fórmulas: De respuesta JSON
   - Metodología: De IMPLEMENTACION_RESUMIDA.md
   - Resultados: Del output de predicciones

---

## 🎓 Ejemplo para Capítulo 2 (Metodología)

Puedes copiar esto directamente a tu tesis:

```
2.1 Recolección de Datos

Se implementó un sistema web scraping que obtiene precios 
públicos de camarón de tres fuentes:
- FreezeOcean: WooCommerce API
- Selina Wamucii: Parsing AJAX + HTML
- FAO Index: Series de tendencia

Consolidación: P_cons = w₁P₁ + w₂P₂ + w₃P₃
donde wᵢ = confiabilidad_fuente / Σ confiabilidades

2.2 Análisis de Correlación

Se aplica regresión lineal mediante scipy.stats.linregress:

    P_despacho = α + β * P_público + ε

Donde α es el margen base, β es la sensibilidad, 
y ε es el error residual ~ N(0, σ²).

El coeficiente de determinación R² = 0.7642 indica 
que el modelo explica 76.42% de la variación.

2.3 Modelo de Predicción

    P(t) = a + b*t + EMA[α=0.3]

Donde EMA[i] = 0.3 * precio[i] + 0.7 * EMA[i-1]

El intervalo de confianza al 95% es: ±1.96 * σ_total
```

---

## 📞 Información de Contacto / Soporte

### Si tienes errores:
1. Ejecuta: `python verificar_sistema.py`
2. Lee: `GUIA_RAPIDA.md` → Troubleshooting
3. Busca en: `DOCUMENTACION_PREDICCION.md`

### Para preguntas técnicas:
- Ver: `EJEMPLOS_USO.py` (7 ejemplos ejecutables)
- Explorar: Código fuente en archivos .py

### Para la tesis:
- Template: `IMPLEMENTACION_RESUMIDA.md`
- Fórmulas: `DOCUMENTACION_PREDICCION.md`
- Ejemplos: `EJEMPLOS_USO.py`

---

## 🏁 Checklist de Setup

```
[ ] 1. Ejecuté: python verificar_sistema.py
[ ] 2. Todo pasó (verde ✅)
[ ] 3. Ejecuté: python main.py
[ ] 4. Servidor corriendo en http://localhost:8000
[ ] 5. Nueva terminal, ejecuté: python test_prediction_system.py
[ ] 6. Todos los tests pasaron
[ ] 7. El sistema está 100% funcional
[ ] 8. Listo para usar o documentar
```

---

## 🎉 ¡Éxito!

Si completaste los 3 pasos sin errores:

✅ **Tu sistema está instalado y funcional**
✅ **Puedes obtener precios públicos**
✅ **Puedes generar predicciones**
✅ **Puedes usarlo para tu tesis**

---

## 📖 Próximo Paso Recomendado

**Opción A: Entender el Sistema**
→ Lee: `GUIA_RAPIDA.md` (20 minutos)

**Opción B: Empezar a Usar**
→ Lee: `EJEMPLOS_USO.py` (20 minutos)

**Opción C: Preparar Tesis**
→ Lee: `IMPLEMENTACION_RESUMIDA.md` "Para Tu Tesis" (15 minutos)

---

*Sistema de Predicción de Precios de Camarón Ecuatoriano*  
*Maransa v1.0 - Febrero 2024*  
*Ready to use ✅*
