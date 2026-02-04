# Mejoras al Microservicio de IA - Versión 2.1
## Integración de Tabla de Precios Real EXPORQUILSA S.A. Ecuador

**Fecha:** 31-01-2026  
**Versión:** 2.1.0-Real-EXPORQUILSA  
**Fuente de Precios:** EXPORQUILSA S.A. Ecuador  
**Contacto:** WhatsApp 0984222956

---

## 📊 Tabla de Precios Integrada

### Precios Despachos (Sin Cabeza/Headless) - USD por libra

| Calibre | Precio | Prioridad | Calidad Requerida |
|---------|--------|-----------|-------------------|
| 16/20   | $2.90  | -         | No picado, No sabor |
| 21/25   | $2.50  | ✓         | No picado, No sabor |
| 26/30   | $2.30  | ✓         | No picado, No sabor |
| 31/35   | $2.05  | ✓         | No picado, No sabor |
| 36/40   | $2.00  | -         | No picado, No sabor |
| 41/50   | $1.85  | -         | No picado, No sabor |
| 51/60   | $1.75  | -         | No picado, No sabor |
| 61/70   | $1.60  | -         | No picado, No sabor |
| 71/90   | $1.30  | -         | No picado, No sabor |
| 91/110  | $0.90  | -         | No picado, No sabor |

### Precios Entero (Con Cabeza/Whole) - USD por libra

| Tamaño | Precio | Equivalencia | Calidad Requerida |
|--------|--------|--------------|-------------------|
| 20     | $4.60  | 16/20        | No picado, No branquias oscuras |
| 30     | $3.60  | 26/30        | No picado, No branquias oscuras |
| 40     | $3.15  | 36/40        | No picado, No branquias oscuras |
| 50     | $3.00  | 41/50        | No picado, No branquias oscuras |
| 60     | $2.70  | 51/60        | No picado, No branquias oscuras |
| 70     | $2.60  | 61/70        | No picado, No branquias oscuras |
| 80     | $2.40  | 71/90        | No picado, No branquias oscuras |

---

## 🔄 Cambios Implementados

### 1. **Tabla de Precios Base (SHRIMP_CALIBER_PRICES)**
- Integrado directamente en `RealAIConfig`
- Dos presentaciones: HEADLESS (sin cabeza) y WHOLE (entero)
- Precios reales validados con EXPORQUILSA
- Fácil actualización futura de precios

```python
SHRIMP_CALIBER_PRICES = {
    "HEADLESS": {
        "16/20": 2.90,
        "21/25": 2.50,
        # ... etc
    },
    "WHOLE": {
        "20": 4.60,
        # ... etc
    }
}
```

### 2. **Nuevo Método: get_caliber_base_price()**
- Localiza en la clase `RealDataCollector`
- Retorna precio base para cualquier calibre
- Valida disponibilidad del calibre
- Incluye información de prioridad y calidad

```python
async with RealDataCollector() as collector:
    caliber_info = collector.get_caliber_base_price("36/40", "HEADLESS")
    # Retorna: precio_base, calibre, presentacion, fuente, etc.
```

### 3. **Actualización del Endpoint /predict/price**
- **Paso 1:** Obtiene precio base de EXPORQUILSA para el calibre solicitado
- **Paso 2:** Usa este precio como referencia en lugar de estimaciones genéricas
- **Paso 3:** Aplica factores ML (clima, mercado, estacionalidad, etc.)
- **Paso 4:** Genera recomendaciones comparando con precio base

**Flujo:**
```
Calibre (36/40) → EXPORQUILSA ($2.00) → Factores ML → Precio Predicho
                                      ↓
                        Factor Mercado (CHINA x1.15) → $2.30
```

### 4. **Nuevos Endpoints**

#### **GET /data/exporquilsa-prices**
Retorna la tabla completa de precios EXPORQUILSA:
- Precios despachos (sin cabeza)
- Precios entero (con cabeza)
- Requisitos de calidad
- Factor de rendimiento (45%)
- Calibres con prioridad

**Respuesta:**
```json
{
  "fuente": "EXPORQUILSA S.A. - Ecuador",
  "fecha_actualizacion": "31-01-2026",
  "precios": {
    "despachos_sin_cabeza": {...},
    "entero_con_cabeza": {...}
  },
  "calibres_con_prioridad": ["21/25", "26/30", "31/35"]
}
```

#### **GET /data/caliber-price/{caliber}**
Obtiene precio específico para un calibre:
- `/data/caliber-price/36%2F40?presentation=HEADLESS` → $2.00
- `/data/caliber-price/50?presentation=WHOLE` → $3.00

**Respuesta:**
```json
{
  "calibre": "36/40",
  "presentacion": "HEADLESS",
  "precio_base": 2.00,
  "fuente": "EXPORQUILSA_Real_31_01_2026",
  "tiene_prioridad": false
}
```

### 5. **Factores Principales Mejorados**
Ahora incluyen referencia EXPORQUILSA:

```json
{
  "precio_base_exporquilsa": 2.00,  // Nuevo campo
  "precio_historico": 0.46,
  "volumen_produccion": 0.18,
  "estacionalidad": 0.15,
  // ... otros factores
}
```

### 6. **Recomendaciones Inteligentes Mejoradas**
Comparan automáticamente con precios EXPORQUILSA:

- "Precio proyectado superior al base EXPORQUILSA (+15%)"
- "Precio proyectado inferior al base EXPORQUILSA (-8%)"
- "Precio proyectado estable respecto a base EXPORQUILSA"

---

## 📈 Beneficios de la Integración

1. **Precisión Mejorada:** Usa precios reales de mercado como base
2. **Validación Real:** Compara predicciones con datos verificados
3. **Contexto Local:** Entiende la realidad del mercado ecuatoriano
4. **Decisiones Informadas:** Los usuarios ven comparaciones vs. precios reales
5. **Actualización Sencilla:** Tabla de precios fácil de actualizar cuando EXPORQUILSA cambie precios

---

## 🔧 Ejemplo de Uso

### Predicción con Precio EXPORQUILSA

**Request:**
```bash
POST /predict/price
{
  "tipo_producto": "36/40",
  "mercado_destino": "CHINA",
  "provincia": "GUAYAS",
  "fecha_prediccion": "2026-02-03",
  "incluir_factores_externos": true
}
```

**Response:**
```json
{
  "precio_predicho": 2.30,
  "intervalo_confianza": {
    "min": 2.15,
    "max": 2.45,
    "confianza": 0.85
  },
  "factores_principales": {
    "precio_base_exporquilsa": 2.00,
    "estacionalidad": 1.05,
    "mercado_destino": 0.115,
    // ... más factores
  },
  "recomendaciones": [
    "Precio proyectado superior al base EXPORQUILSA (+15%)",
    "Precio favorable para venta en CHINA (+15%)",
    "Condiciones climáticas favorables para producción"
  ],
  "modelo_usado": "Ensemble_EXPORQUILSA_Real_v1.1"
}
```

### Consultar Precios EXPORQUILSA

**Request:**
```bash
GET /data/exporquilsa-prices
```

**Request para Calibre Específico:**
```bash
GET /data/caliber-price/41%2F50?presentation=HEADLESS
```

---

## 📝 Requisitos de Calidad (EXPORQUILSA)

### General (Ambas presentaciones)
- ✓ No picado
- ✓ No sabor

### Específico Entero (Con Cabeza)
- ✓ No branquias oscuras

---

## 🚀 Próximas Mejoras Sugeridas

1. **Base de Datos de Históricos:** Guardar precios históricos de EXPORQUILSA para tendencias
2. **Notificaciones de Cambios:** Alertar cuando EXPORQUILSA cambie precios
3. **Integración con Más Empacadoras:** Agregar precios de otras empacadoras ecuatorianas
4. **Análisis Comparativo:** Comparar precios entre empacadoras
5. **Tendencias Mensuales:** Gráficos de evolución de precios por calibre
6. **API de EXPORQUILSA:** Si ellos lanzan API pública, integrar directamente

---

## 📞 Contacto EXPORQUILSA

- **Empresa:** EXPORQUILSA S.A.
- **WhatsApp:** 0984222956
- **Última Actualización de Precios:** 31-01-2026
- **Condiciones:** No picado, No sabor, No ataque bacteriano

---

## 🔐 Versionado

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 2.0.0   | -     | Versión base con ML real |
| 2.1.0   | 31-01-2026 | **Integración EXPORQUILSA** |

---

**Generado:** 03-02-2026  
**Sistema:** Maransa AI Price Prediction Service  
**Estado:** ✅ Activo y Operativo
