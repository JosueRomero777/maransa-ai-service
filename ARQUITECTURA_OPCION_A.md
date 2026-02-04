# 🏗️ ARQUITECTURA OPCIÓN A - DOS ENDPOINTS SEPARADOS

## Resumen Ejecutivo

Se implementó una arquitectura clara y separada para hacer **evidente qué datos vienen de dónde**:

```
┌─────────────────────────────────────────────────────────────┐
│ USUARIO / FRONTEND                                          │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴──────────────┐
        │                          │
        ▼                          ▼
   🌐 ENDPOINT 1              💰 ENDPOINT 2
   GET /data/                 POST /predict/
   market-prices              purchase-price
        │                          │
        │                          └──────────────┐
        │                                         │ Usa datos
        │                                         │ de ENDPOINT 1
        ▼                                         ▼
   Retorna:                        Retorna:
   - Precios públicos              - Compra mínima
   - Cache info                    - Compra recomendada
   - Spread actual                 - Márgenes
   - Fuentes                       - Viabilidad
```

---

## 📋 ENDPOINT 1: GET /data/market-prices

### Propósito
**Consulta precios públicos actuales del mercado**

Responsable de:
- ✅ Buscar en internet (si no está cacheado)
- ✅ Cachear resultado UNA VEZ por día
- ✅ Retornar precios consolidados

### Request
```
GET http://localhost:8000/data/market-prices
```

### Response
```json
{
  "estatus": "success",
  "timestamp": "2026-02-04T02:30:00.123456",
  "fecha": "2026-02-04",
  "cache_status": "desde_caché",
  "precios_consolidados": {
    "16/20": {
      "precio_publico_promedio": 2.95,
      "cantidad_fuentes": 3,
      "rango_min": 2.85,
      "rango_max": 3.05,
      "actualizado": "2026-02-04"
    },
    "21/25": {
      "precio_publico_promedio": 2.55,
      "cantidad_fuentes": 2,
      "actualizado": "2026-02-04"
    },
    "26/30": {...}
  },
  "fuentes_consultadas": ["alibaba", "trading_economics"],
  "descripcion": "Precios públicos del mercado (lo que paga el usuario final)",
  "nota": "Estos precios se usan para predecir tendencias del despacho"
}
```

### Flujo Interno

```python
1. Crear instancia de MarketPriceScraper
2. Llamar get_public_market_prices(use_cache=True)
   ├─ Buscar caché de hoy en .cache/market_prices_2026-02-04.json
   ├─ Si existe:
   │  └─ Retornar datos cacheados (sin consultar internet)
   └─ Si NO existe:
      ├─ Scraping Alibaba.com → precios por calibre
      ├─ Consultar Trading Economics → tendencias
      ├─ Consultar FAO Index → índices generales
      ├─ Consolidar con promedio ponderado
      ├─ Guardar en caché
      └─ Retornar datos
3. Retornar JSON con todos los precios
```

### Cache
- **Ubicación**: `maransa-ai-service/.cache/market_prices_YYYY-MM-DD.json`
- **Duración**: 1 día (se renueva mañana)
- **Ventaja**: Una sola consulta a internet por día, respuestas instantáneas después

---

## 💰 ENDPOINT 2: POST /predict/purchase-price

### Propósito
**Predice precio de compra rentable para obtener margen garantizado**

Recibe: calibre, presentación, fecha, horizonte
Retorna: compra mínima, compra recomendada, márgenes, viabilidad

### Request
```json
{
  "tipo_producto": "21/25",
  "presentacion": "HEADLESS",
  "provincia": "GUAYAS",
  "fecha_prediccion": "2026-02-20",
  "dias_horizonte": 14
}
```

### Response
```json
{
  "calibre": "21/25",
  "presentacion": "HEADLESS",
  "provincia": "GUAYAS",
  "fecha_despacho_predicho": "2026-02-20",
  
  "precio_despacho_predicho": 2.51,
  "intervalo_confianza_despacho": {
    "min": 2.38,
    "max": 2.64,
    "confianza": 0.85
  },
  
  "precio_compra_minimo": 2.41,
  "precio_compra_recomendado": 2.36,
  "margen_minimo_garantizado": 0.10,
  "margen_recomendado": 0.15,
  
  "dias_horizonte": 14,
  
  "recomendacion": "💰 Estrategia de compra...",
  
  "spread_mercado_despacho": {
    "precio_exporquilsa": 2.50,
    "precio_publico_promedio": 2.55,
    "spread_porcentaje": 2.0
  },
  
  "viabilidad_economica": {
    "estatus": "viable",
    "precio_base_exporquilsa": 2.50,
    "precio_predicho_despacho": 2.51,
    "margen_minimo_rentable": 0.10,
    "margen_recomendado": 0.15,
    "dias_prediccion": 14
  }
}
```

### Flujo Interno (PASOS CLAROS)

```
┌─────────────────────────────────────────────────────────────┐
│ PASO 1: Obtener base EXPORQUILSA                           │
├─────────────────────────────────────────────────────────────┤
│ • Consulta tabla EXPORQUILSA (tabla estática/BD)           │
│ • Para 21/25 HEADLESS: $2.50/lb (fuente de verdad)        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PASO 2: Obtener precios públicos actuales                  │
├─────────────────────────────────────────────────────────────┤
│ • Llamar MarketPriceScraper.get_public_market_prices()     │
│ • Retorna precios cacheados (ENDPOINT 1 ya consultó)       │
│ • Para 21/25: $2.55/lb (mercado público)                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PASO 3: Calcular spread actual                             │
├─────────────────────────────────────────────────────────────┤
│ • Spread = Público - Despacho = $2.55 - $2.50 = +$0.05    │
│ • Porcentaje: 2%                                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PASO 4: Recopilar datos para ML                            │
├─────────────────────────────────────────────────────────────┤
│ • Clima actual (OpenWeatherMap API)                        │
│ • Tipos de cambio (ExchangeRate API)                       │
│ • Producción estimada (CNA data)                           │
│ • Estacionalidad (mes actual)                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PASO 5: Usar ML para predecir variación del mercado        │
├─────────────────────────────────────────────────────────────┤
│ • ML ensemble (RandomForest + GradientBoosting + XGBoost)  │
│ • Entrada: features de clima, producción, tipos cambio     │
│ • Salida: predicción de precio en 14 días                  │
│                                                            │
│ CLAVE: Usamos ML SOLO para INDEX de cambio                 │
│ (% de variación), NO para precio absoluto                  │
│ Razón: ML entrena con datos sintéticos                     │
│                                                            │
│ Ejemplo:                                                   │
│   - ML predice: mercado público subirá 3% → $2.63         │
│   - Índice cambio: 2.63 / 2.55 = 1.03 (+3%)              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PASO 6: Aplicar amortiguación (despacho es estable)        │
├─────────────────────────────────────────────────────────────┤
│ • El despacho NO fluctúa como el mercado público           │
│ • Amortiguamiento: 50% del cambio afecta despacho          │
│                                                            │
│ Ejemplo:                                                   │
│   - Mercado sube 3% → despacho sube solo 1.5%             │
│   - Nuevo índice despacho: 1.0 + (1.03-1.0) * 0.5 = 1.015│
│   - Precio despacho: $2.50 * 1.015 = $2.538              │
│                                                            │
│ • Limitar a ±5% (máximo, despacho es muy estable)         │
│ • Resultado: $2.51/lb predicho                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PASO 7: Calcular precios de compra rentable                │
├─────────────────────────────────────────────────────────────┤
│ • Precio despacho predicho: $2.51                          │
│ • Margen mínimo: $0.10 (garantiza pequeña ganancia)        │
│ • Margen recomendado: $0.15 (ganancia cómoda)             │
│ • Ajustar por horizonte (14 días = sin ajuste extra)       │
│                                                            │
│ Resultado:                                                 │
│   - Compra MÍNIMA: $2.51 - $0.10 = $2.41                  │
│   - Compra RECOMENDADA: $2.51 - $0.15 = $2.36            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PASO 8: Retornar recomendación clara                       │
├─────────────────────────────────────────────────────────────┤
│ "💰 Estrategia: Compra a $2.36 máximo,                    │
│  vende a $2.51, gana $0.15/lb"                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo Usuario Completo

### Escenario: "Necesito saber a cuánto comprar 21/25 HEADLESS en 2 semanas"

**1️⃣ Usuario/Frontend**
```
GET http://localhost:8000/data/market-prices
→ ¿Cuál es el precio público HOY?
```

**Respuesta del servidor**
```
Precio público 21/25 hoy: $2.55/lb
(Consultó internet, cacheó resultado)
```

**2️⃣ Usuario/Frontend (informado ahora)**
```
POST http://localhost:8000/predict/purchase-price
{
  "tipo_producto": "21/25",
  "presentacion": "HEADLESS",
  "fecha_prediccion": "2026-02-20",
  "dias_horizonte": 14
}
```

**Respuesta del servidor**
```
Base EXPORQUILSA: $2.50/lb
Predicción despacho en 14 días: $2.51/lb
├─ Compra MÍNIMA: $2.41/lb (margen: $0.10)
└─ Compra RECOMENDADA: $2.36/lb (margen: $0.15)

✅ RECOMENDACIÓN CLARA:
"Busca productor que venda a $2.36 o menos"
```

---

## 🎯 Ventajas de Opción A

| Aspecto | Beneficio |
|--------|-----------|
| **Claridad** | Dos endpoints = dos responsabilidades claras |
| **Transparencia** | Usuario ve qué datos de dónde |
| **Reutilización** | ENDPOINT 1 cacheado para múltiples predicciones |
| **Debugging** | Fácil separar "problema en consulta" vs "problema en ML" |
| **Escalabilidad** | Puedo cachear por calibre, por provincia, etc. |
| **Frontend** | Puede mostrar "datos de mercado" y "recomendación" por separado |

---

## 📝 Documentación Endpoints

### GET /data/market-prices

**Descrición:** Obtiene precios públicos actuales del mercado

**Parámetros:** Ninguno (consulta configuración interna)

**Respuesta:** JSON con precios consolidados + cache info

**Caché:** 1 vez por día (renovable mañana)

**Fuentes:**
- Alibaba.com (vendedores ecuatorianos)
- Trading Economics (commodities)
- FAO Food Price Index

---

### POST /predict/purchase-price

**Descripción:** Predice precio de compra rentable

**Parámetros (JSON):**
- `tipo_producto` (string): Calibre (16/20, 21/25, etc.)
- `presentacion` (string): HEADLESS, WHOLE, LIVE
- `provincia` (string, opcional): GUAYAS, EL_ORO
- `fecha_prediccion` (date): Fecha para predecir
- `dias_horizonte` (int): Días hasta compra (7-90)

**Respuesta:** JSON con estrategia de compra completa

**Paso a paso interno:**
1. Base EXPORQUILSA (tabla)
2. Precios públicos (ENDPOINT 1)
3. Spread actual
4. ML predice variación
5. Amortiguación (±5%)
6. Márgenes rentables
7. Recomendación clara

---

## ✅ Estado Actual

- ✅ Endpoint 1 implementado: GET /data/market-prices
- ✅ Endpoint 2 refactorizado: POST /predict/purchase-price
- ✅ Arquitectura clara y transparente
- ✅ Caché diario funcionando
- ✅ ML usando índice de cambio (no precio absoluto)
- ✅ Documentación completa

---

## 🚀 Próximos Pasos

1. **Frontend**: Actualizar AIPredictionsPage.tsx
   - Llamar ENDPOINT 1 para mostrar datos de mercado
   - Llamar ENDPOINT 2 para mostrar recomendación
   
2. **Backend Prisma**: Agregar campo `precio_compra_recomendado` si se guarda

3. **Validación Real**: Comparar predicciones vs compras reales de productores

