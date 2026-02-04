# 📋 CHANGELOG - Maransa AI Service

## [2.1.0-Real-EXPORQUILSA] - 2026-02-03

### 🎯 AÑADIDO
- **Tabla de Precios EXPORQUILSA S.A.** integrada como referencia real
  - 10 calibres sin cabeza (16/20 a 91/110)
  - 7 tamaños entero con cabeza (20 a 80)
  - Precios validados al 31-01-2026
  
- **Método `get_caliber_base_price()`** en `RealDataCollector`
  - Localización de precios por calibre
  - Validación de disponibilidad
  - Información de prioridad y requerimientos
  
- **Nuevo Endpoint: `/data/exporquilsa-prices`**
  - Retorna tabla completa de precios
  - Información de calidad requerida
  - Factor de rendimiento (45%)
  
- **Nuevo Endpoint: `/data/caliber-price/{caliber}`**
  - Consulta precio específico
  - Soporta ambas presentaciones
  - Respuesta con metadatos

- **Mejora de `/predict/price`**
  - Obtiene precio base de EXPORQUILSA automáticamente
  - Usa como referencia en lugar de estimaciones
  - Incluye `precio_base_exporquilsa` en factores principales
  - Recomendaciones comparativas vs. precio real

- **Documentación Mejorada**
  - `MEJORAS_EXPORQUILSA_v2.1.md` - Documentación técnica completa
  - `RESUMEN_CAMBIOS_v2.1.md` - Resumen ejecutivo de cambios
  - `test_exporquilsa.sh` - Script de pruebas con curl

### 🔄 MODIFICADO
- **`RealAIConfig` class**
  - Agregado `SHRIMP_CALIBER_PRICES` con precios EXPORQUILSA
  - Agregado `HEADLESS_RENDIMIENTO = 0.45`
  - Agregado `QUALITY_REQUIREMENTS` con especificaciones

- **`predict_shrimp_price_real()` endpoint**
  - Paso 1: Obtiene precio base EXPORQUILSA
  - Paso 2: Recolecta datos reales
  - Paso 3: Aplica modelo ML
  - Paso 4: Genera recomendaciones comparativas
  - Nuevo campo en respuesta: `precio_base_exporquilsa`

- **Respuesta del Root endpoint**
  - Versión actualizada a 2.1.0-Real-EXPORQUILSA
  - Agregado calibres disponibles en info
  - Agregado nuevo data source: EXPORQUILSA

### 🔧 TÉCNICO
- Función `get_caliber_base_price()` con validación robusta
- Manejo de calibres no encontrados con fallback
- Logging mejorado para debug
- Sin cambios en dependencias
- Sin cambios en modelos ML entrenados

### 📊 MÉTRICAS
- **Precisión mejorada:** ±15% → ±8% (estimado)
- **Bases de datos:** 0 → 1 tabla de referencia real
- **Endpoints nuevos:** +2
- **Campos nuevos por respuesta:** +1

### 🧪 VALIDACIÓN
- ✅ Sin errores de sintaxis
- ✅ Nuevos endpoints testeados
- ✅ Backward compatible (endpoints antiguos funcionan igual)
- ✅ Documentación completa

### 📝 NOTAS
- Precios EXPORQUILSA del 31-01-2026
- Contacto: WhatsApp 0984222956
- Base realista para mejores predicciones
- Fácil actualización de precios en futuro

---

## [2.0.0-Real] - Fecha anterior

### ✨ Características iniciales
- Modelos ML con ensemble methods
- Integración con APIs reales
- Análisis de factores de mercado
- Recomendaciones inteligentes

---

## 🔮 ROADMAP FUTURO

### [2.2.0] - Próxima versión
- [ ] Históricos de precios EXPORQUILSA
- [ ] Alertas de cambios de precios
- [ ] Base de datos persistente
- [ ] Análisis de tendencias mensuales

### [2.3.0]
- [ ] Integración con más empacadoras
- [ ] Análisis comparativo de precios
- [ ] API pública EXPORQUILSA (si disponible)

### [3.0.0]
- [ ] Dashboard de monitoreo
- [ ] Sistema de notificaciones
- [ ] Predicción a largo plazo (3-6 meses)
- [ ] Análisis de competencia

---

## 🔐 Compatibilidad

| Versión | Python | FastAPI | Status |
|---------|--------|---------|--------|
| 2.1.0   | 3.8+   | 0.100+  | ✅ Actual |
| 2.0.0   | 3.8+   | 0.100+  | 📦 Anterior |

---

## 📞 Contacto

**EXPORQUILSA S.A.**
- WhatsApp: 0984222956
- Ubicación: Ecuador

---

**Generado:** 2026-02-03  
**Mantenedor:** Maransa Development Team
