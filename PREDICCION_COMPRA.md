# 🆕 Nuevo Endpoint: Predicción de Precio de Compra Rentable

## Cambio Fundamental en la Arquitectura

**Antes**: Sistema predecía precio de despacho de forma teórica
**Ahora**: Sistema predice **cuánto DEBES COMPRAR** para obtener margen garantizado

---

## Endpoint: `POST /predict/purchase-price`

### Descripción
Predice el precio de compra recomendado para obtener margen rentable cuando venda a la empacadora (EXPORQUILSA).

### Flujo de Predicción

```
1. Consulta precios públicos del mercado
   ↓ (con caché diario)
2. Predice variación del mercado en N días usando ML
   ↓
3. Estima impacto en precio de despacho EXPORQUILSA
   ↓
4. Calcula precio de compra para margen mínimo/recomendado
   ↓
5. Retorna estrategia de compra rentable
```

### Request

```json
{
  "tipo_producto": "16/20",
  "presentacion": "HEADLESS",
  "provincia": "GUAYAS",
  "fecha_prediccion": "2026-02-15",
  "dias_horizonte": 30
}
```

**Parámetros:**
- `tipo_producto` (string, required): Calibre comercial (16/20, 21/25, 26/30, etc.)
- `presentacion` (string, default: HEADLESS): HEADLESS, WHOLE, o LIVE
- `provincia` (string, default: GUAYAS): GUAYAS o EL_ORO (para precios locales)
- `fecha_prediccion` (date, required): Fecha para la cual predecir
- `dias_horizonte` (int, default: 30): Días hasta que hagas la compra (afecta margen de riesgo)

### Response

```json
{
  "calibre": "16/20",
  "presentacion": "HEADLESS",
  "provincia": "GUAYAS",
  "fecha_despacho_predicho": "2026-02-15",
  
  "precio_despacho_predicho": 2.87,
  "intervalo_confianza_despacho": {
    "min": 2.73,
    "max": 3.01,
    "confianza": 0.85
  },
  
  "precio_compra_minimo": 2.77,
  "precio_compra_recomendado": 2.72,
  "margen_minimo_garantizado": 0.10,
  "margen_recomendado": 0.15,
  
  "dias_horizonte": 30,
  
  "recomendacion": "💰 Estrategia de compra para 16/20 (HEADLESS):\n  • Despacho esperado: $2.87/lb\n  • Compra MÍNIMA: $2.77/lb (margen $0.10)\n  • Compra RECOMENDADA: $2.72/lb (margen $0.15)\n  • Horizonte: 30 días | Confianza: 85%",
  
  "spread_mercado_despacho": {
    "caliber": "16/20",
    "presentacion": "HEADLESS",
    "precio_exporquilsa": 2.90,
    "precio_publico_promedio": 2.95,
    "spread_absoluto": 0.05,
    "spread_porcentaje": 1.72,
    "ratio_mercado_despacho": 1.017
  },
  
  "viabilidad_economica": {
    "precio_base_exporquilsa": 2.90,
    "precio_predicho_despacho": 2.87,
    "margen_minimo_rentable": 0.10,
    "margen_recomendado": 0.15,
    "dias_prediccion": 11,
    "spread_mercado_despacho": 1.72,
    "factor_ajuste_horizonte": 1.0,
    "estatus": "viable"
  }
}
```

### Campos de Respuesta Explicados

| Campo | Significado |
|-------|-------------|
| `precio_despacho_predicho` | Precio que EXPORQUILSA pagará por tu camarón |
| `precio_compra_minimo` | Máximo que debes pagar para NO perder dinero |
| `precio_compra_recomendado` | Precio ideal: +$0.15 margen sobre mínimo |
| `margen_minimo_garantizado` | Ganancia mínima por libra |
| `margen_recomendado` | Ganancia objetivo por libra |
| `spread_mercado_despacho` | Diferencia entre precio público y despacho |
| `viabilidad_economica` | Resumen de viabilidad del negocio |

---

## Ejemplo de Uso

### Request cURL

```bash
curl -X POST "http://localhost:8000/predict/purchase-price" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "16/20",
    "presentacion": "HEADLESS",
    "provincia": "GUAYAS",
    "fecha_prediccion": "2026-02-15",
    "dias_horizonte": 30
  }'
```

### Interpretación

Si el resultado muestra:
- **Despacho predicho**: $2.87/lb
- **Compra recomendada**: $2.72/lb
- **Margen**: $0.15/lb

**Significa:**
- En ~30 días, EXPORQUILSA te pagará ~$2.87 por libra de 16/20 HEADLESS
- Debes comprar a productor local a $2.72 o menos
- Ganancias: $2.87 - $2.72 = $0.15/lb ✓ Rentable

---

## Tecnología Detrás

### 1. **Web Scraping con Caché Diario**
- Consulta precios públicos de Alibaba, Trading Economics, FAO
- **Caché**: Solo consulta internet UNA VEZ por día
- **Fallback**: Si falla scraping, usa últimos datos válidos

### 2. **Machine Learning para Predicción de Tendencias**
- Ensemble de modelos (RandomForest + GradientBoosting + XGBoost)
- Entrena con datos históricos reales de producción, clima, tipos de cambio
- Predice cómo varía el mercado público en N días

### 3. **Ajuste por Volatilidad**
- Mercado público: ±25% volatilidad (muy variable)
- Despacho EXPORQUILSA: ±5% volatilidad (negociado, estable)
- Sistema amortigua cambios del mercado (60% factor) antes de aplicar a despacho

### 4. **Márgenes Inteligentes por Horizonte**
- 7-30 días: Margen $0.10-0.15 (riesgo bajo)
- 30-60 días: Margen +10% por riesgo adicional
- 60+ días: Margen +25% por incertidumbre

---

## Comparativa: Viejo vs Nuevo Sistema

### ❌ Viejo Sistema
```
Predicción genérica de "precio de mercado"
Resultado: $4.89 para 16/20 HEADLESS NACIONAL (68% sobre base)
Problema: No alineado con realidad EXPORQUILSA ($2.90)
Uso: No servía para decisiones de compra
```

### ✅ Nuevo Sistema
```
Predicción de "precio de compra rentable"
Resultado: Comprar a $2.72-2.77 para vender a $2.87
Margen: $0.10-0.15/lb garantizado
Uso: Decisión clara: "Busca productor que venda a <$2.72"
```

---

## Próximos Pasos Recomendados

1. **Validar con datos reales**
   - Hacer predicción para hoy
   - Comparar precio predicho vs precio real despacho

2. **Refinar márgenes**
   - Si márgenes son muy apretados: aumentar a $0.20
   - Si son muy holgados: reducir a $0.08

3. **Agregar factores locales**
   - Precios pueden variar por provincia
   - Costos de transporte
   - Demanda local

4. **Historial de precisión**
   - Guardar predicciones
   - Comparar vs resultados reales
   - Ajustar modelos mensualmente

---

## Troubleshooting

### "Calibre no encontrado"
- Verifica que uses calibres válidos: 16/20, 21/25, 26/30, etc.
- Consulta `/data/exporquilsa-prices` para lista completa

### "Sin datos públicos disponibles"
- Scraping de internet falló (sitios podrían estar offline)
- Sistema usa caché de días anteriores si existe
- Si persiste: aumentar `dias_horizonte` para menos volatilidad

### "No viable"
- Precio de compra > precio de despacho
- Mercado muy alcista vs base EXPORQUILSA
- Esperar días mejores o negociar margen con empacadora

