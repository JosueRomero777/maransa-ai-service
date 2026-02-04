# 🏗️ ESTRUCTURA DE CAMBIOS - Maransa AI v2.1

## 📍 UBICACIÓN DE CAMBIOS EN EL CÓDIGO

### Archivo: `maransa-ai-service/main.py`

---

## 1️⃣ CONFIGURACIÓN - RealAIConfig (Líneas ~168-208)

### ANTES:
```python
class RealAIConfig:
    # ... otras configuraciones ...
    ECUADOR_MARKETS = { ... }
```

### DESPUÉS:
```python
class RealAIConfig:
    # ... otras configuraciones ...
    
    ECUADOR_MARKETS = { ... }
    
    # ✨ NUEVO: Tabla de precios EXPORQUILSA
    SHRIMP_CALIBER_PRICES = {
        "HEADLESS": {
            "16/20": 2.90,
            "21/25": 2.50,
            # ... 8 más
        },
        "WHOLE": {
            "20": 4.60,
            "30": 3.60,
            # ... 5 más
        }
    }
    
    # ✨ NUEVO: Factor de rendimiento
    HEADLESS_RENDIMIENTO = 0.45
    
    # ✨ NUEVO: Requisitos de calidad
    QUALITY_REQUIREMENTS = { ... }
```

### Cambios Específicos:
- `+38` líneas de código
- `+17` calibres con precios
- `+4` campos de configuración

---

## 2️⃣ CLASE RealDataCollector (Líneas ~287-380)

### NUEVO MÉTODO (Líneas ~376-427):
```python
def get_caliber_base_price(self, tipo_producto: str, presentation: str = "HEADLESS") -> Dict[str, Any]:
    """
    Obtiene el precio base de EXPORQUILSA para un calibre específico
    """
    try:
        presentation_upper = presentation.upper()
        
        if presentation_upper not in config.SHRIMP_CALIBER_PRICES:
            logger.warning(f"Presentación {presentation_upper} no encontrada, usando HEADLESS")
            presentation_upper = "HEADLESS"
        
        caliber_prices = config.SHRIMP_CALIBER_PRICES[presentation_upper]
        
        if tipo_producto in caliber_prices:
            base_price = caliber_prices[tipo_producto]
            
            return {
                "calibre": tipo_producto,
                "presentacion": presentation_upper,
                "precio_base": base_price,
                "fuente": "EXPORQUILSA_Real_31_01_2026",
                "calidad_requerida": config.QUALITY_REQUIREMENTS,
                "tiene_prioridad": tipo_producto in ["21/25", "26/30", "31/35"],
                "estatus": "success"
            }
        else:
            # ... manejo de calibre no encontrado ...
```

### Cambios:
- `+52` líneas de código
- `1` nuevo método público
- Manejo robusto de errores

---

## 3️⃣ ENDPOINT `/predict/price` (Líneas ~929-1050)

### ANTES (Paso 1 - Línea ~929):
```python
async def predict_shrimp_price_real(request: MarketDataRequest):
    try:
        logger.info(f"Predicción REAL para {request.tipo_producto}...")
        
        # 1. Recopilar datos REALES
        async with RealDataCollector() as collector:
            weather_data = await collector.get_real_weather_data(...)
            # ...
```

### DESPUÉS (Pasos 1-2 - Línea ~929):
```python
async def predict_shrimp_price_real(request: MarketDataRequest):
    try:
        logger.info(f"Predicción REAL para {request.tipo_producto}...")
        
        # ✨ 1. NUEVO: Obtener precio base EXPORQUILSA
        async with RealDataCollector() as collector:
            caliber_price_info = collector.get_caliber_base_price(
                request.tipo_producto, "HEADLESS"
            )
        
        if caliber_price_info.get("estatus") == "success":
            base_price_exporquilsa = caliber_price_info["precio_base"]
            logger.info(f"Precio base EXPORQUILSA: ${base_price_exporquilsa}")
        else:
            base_price_exporquilsa = 2.5  # Fallback
            logger.warning(f"Usando fallback: ${base_price_exporquilsa}")
        
        # 2. Recopilar datos REALES
        async with RealDataCollector() as collector:
            weather_data = await collector.get_real_weather_data(...)
            # ...
```

### CAMBIOS EN FEATURES (Línea ~963):
```python
# ✨ CAMBIO: Usar precio EXPORQUILSA como base
features = {
    'precio_historico_1m': base_price_exporquilsa,  # ← ANTES: market_prices.get(...)
    'precio_historico_3m': base_price_exporquilsa * 0.98,  # ← NUEVO
    'volumen_produccion': ...,
    'precio_nacional_base': base_price_exporquilsa,  # ← ANTES: market_prices.get(...)
    # ... resto igual ...
}
```

### CAMBIOS EN FACTORES (Línea ~1000):
```python
factores_principales = {
    'precio_base_exporquilsa': round(base_price_exporquilsa, 4),  # ← NUEVO
    'precio_historico': round(features['precio_historico_1m'] * ..., 4),
    # ... resto igual ...
}
```

### CAMBIOS EN RECOMENDACIONES (Línea ~1010):
```python
# ✨ NUEVO: Comparación inteligente con EXPORQUILSA
precio_vs_base = final_price / base_price_exporquilsa

if precio_vs_base > 1.1:
    recomendaciones.append(
        f"Precio proyectado superior al base EXPORQUILSA (+{(precio_vs_base-1)*100:.1f}%)"
    )
elif precio_vs_base < 0.9:
    recomendaciones.append(
        f"Precio proyectado inferior al base EXPORQUILSA ({(precio_vs_base-1)*100:.1f}%)"
    )
else:
    recomendaciones.append(
        f"Precio proyectado estable respecto a base EXPORQUILSA"
    )

# ... resto de recomendaciones ...
```

### CAMBIOS EN RESPUESTA (Línea ~1045):
```python
return PredictionResponse(
    # ... campos anteriores ...
    modelo_usado=f"{...}_EXPORQUILSA_Real_v1.1",  # ← ACTUALIZADO
    recomendaciones=recomendaciones
)
```

### Cambios Totales en Endpoint:
- `+120` líneas de código
- `1` nuevo paso de procesamiento
- `+1` campo en factores
- `+1` sección de recomendaciones
- Versión actualizada

---

## 4️⃣ ENDPOINT ROOT `/` (Líneas ~875-910)

### CAMBIOS:
```python
@app.get("/")
async def root():
    return {
        "service": "...",
        "version": "2.1.0-Real-EXPORQUILSA",  # ← ACTUALIZADO
        "description": "...con tabla de precios EXPORQUILSA",  # ← ACTUALIZADO
        "data_sources": {
            # ... anteriores ...
            "caliber_prices": "EXPORQUILSA S.A. Ecuador (31-01-2026)"  # ← NUEVO
        },
        "ml_models": [...],
        "scientific_basis": [
            # ...
            "EXPORQUILSA Real Market Data"  # ← NUEVO
        ],
        "endpoints": [
            # ... anteriores ...
            "/data/exporquilsa-prices - Tabla completa EXPORQUILSA",  # ← NUEVO
            "/data/caliber-price/{caliber} - Precio específico por calibre",  # ← NUEVO
        ],
        "calibres_disponibles": {  # ← NUEVO
            "headless": list(config.SHRIMP_CALIBER_PRICES["HEADLESS"].keys()),
            "whole": list(config.SHRIMP_CALIBER_PRICES["WHOLE"].keys())
        }
    }
```

### Cambios:
- `+8` líneas
- `+2` referencias a EXPORQUILSA
- `+2` nuevos endpoints en documentación
- Nueva sección de calibres

---

## 5️⃣ NUEVOS ENDPOINTS (Líneas ~1200-1246)

### ENDPOINT 1: GET /data/exporquilsa-prices
```python
@app.get("/data/exporquilsa-prices")
async def get_exporquilsa_prices():
    """Obtiene la tabla de precios actuales de EXPORQUILSA S.A."""
    try:
        return {
            "fuente": "EXPORQUILSA S.A. - Ecuador",
            "fecha_actualizacion": "31-01-2026",
            "contacto": "WhatsApp 0984222956",
            "requisitos_calidad": { ... },
            "precios": {
                "despachos_sin_cabeza": config.SHRIMP_CALIBER_PRICES["HEADLESS"],
                "entero_con_cabeza": config.SHRIMP_CALIBER_PRICES["WHOLE"]
            },
            "factor_rendimiento": { ... },
            "calibres_con_prioridad": ["21/25", "26/30", "31/35"],
            "moneda": "USD",
            "unidad": "por libra"
        }
```

### ENDPOINT 2: GET /data/caliber-price/{caliber}
```python
@app.get("/data/caliber-price/{caliber}")
async def get_caliber_base_price_endpoint(
    caliber: str, 
    presentation: str = "HEADLESS"
):
    """
    Obtiene el precio base para un calibre específico de EXPORQUILSA
    
    Ejemplos:
    - /data/caliber-price/36%2F40?presentation=HEADLESS
    - /data/caliber-price/50?presentation=WHOLE
    """
    try:
        async with RealDataCollector() as collector:
            result = collector.get_caliber_base_price(caliber, presentation)
        
        return result
```

### Cambios:
- `+47` líneas de código
- `2` nuevos endpoints
- Documentación inline

---

## 📊 RESUMEN DE CAMBIOS

| Sección | Líneas | Tipo | Descripción |
|---------|--------|------|-------------|
| Config | +38 | Nuevo | Tabla precios EXPORQUILSA |
| RealDataCollector | +52 | Nuevo | Método get_caliber_base_price() |
| /predict/price | +120 | Modificado | Usa precios EXPORQUILSA |
| / (root) | +8 | Modificado | Documentación actualizada |
| /data/exporquilsa-prices | +28 | Nuevo | Endpoint tabla precios |
| /data/caliber-price | +19 | Nuevo | Endpoint precio específico |
| **TOTAL** | **+265** | - | Líneas de código nuevas |

---

## 🎯 FLUJO DE EJECUCIÓN

```
Request: POST /predict/price
    ↓
1. get_caliber_base_price("36/40", "HEADLESS")
    → Busca en config.SHRIMP_CALIBER_PRICES
    → Retorna: { precio_base: 2.00, ... }
    ↓
2. Recolectar datos (clima, tipos cambio, etc.)
    ↓
3. Preparar features con base_price_exporquilsa
    ↓
4. Aplicar modelo ML
    ↓
5. Ajustar por mercado
    ↓
6. Generar recomendaciones comparativas
    ↓
Response: {
    precio_predicho: 2.30,
    precio_base_exporquilsa: 2.00,
    recomendaciones: ["Precio superior al base..."]
}
```

---

## ✨ CARACTERÍSTICAS NUEVAS

| Feature | Ubicación | Línea |
|---------|-----------|-------|
| Tabla precios EXPORQUILSA | RealAIConfig | ~173 |
| Método get_caliber_base_price | RealDataCollector | ~376 |
| Endpoint /data/exporquilsa-prices | Main | ~1200 |
| Endpoint /data/caliber-price | Main | ~1220 |
| Comparativa con base EXPORQUILSA | /predict/price | ~1010 |
| Campo precio_base_exporquilsa | Respuesta | ~1000 |

---

## 🔄 COMPATIBILIDAD

- ✅ Backward compatible (endpoints antiguos funcionan igual)
- ✅ No requiere cambios en base de datos
- ✅ No requiere cambios en dependencias
- ✅ No requiere cambios en modelos entrenados

---

**Generado:** 2026-02-03  
**Versión:** 2.1.0-Real-EXPORQUILSA  
**Líneas totales modificadas/agregadas:** 265
