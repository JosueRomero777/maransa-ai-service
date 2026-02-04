# 🔄 GUÍA DE ACTUALIZACIÓN DE PRECIOS EXPORQUILSA

## 📋 ¿Cómo actualizar los precios cuando EXPORQUILSA cambie?

### 🎯 Objetivo
Mantener la tabla de precios actualizada sin necesidad de redeploy del servicio.

### 📍 Ubicación del Código
Archivo: `maransa-ai-service/main.py`  
Línea: ~168-208 (dentro de la clase `RealAIConfig`)

---

## 🔧 Método 1: Actualización Manual Directa (RÁPIDO)

### Paso 1: Abrir el archivo main.py
```bash
# En el editor o terminal
nano maransa-ai-service/main.py
# o usar VS Code
code maransa-ai-service/main.py
```

### Paso 2: Localizar la tabla SHRIMP_CALIBER_PRICES
```python
SHRIMP_CALIBER_PRICES = {
    "HEADLESS": {
        "16/20": 2.90,    # ← Actualizar este valor
        "21/25": 2.50,
        # ... etc
    },
    "WHOLE": {
        "20": 4.60,       # ← O este valor
        # ... etc
    }
}
```

### Paso 3: Reemplazar con nuevos precios
**Ejemplo:**
```python
"36/40": 2.00,  # Cambiar a nuevo precio

# Si EXPORQUILSA dice: 36/40 = $2.05
# Cambiar a:
"36/40": 2.05,
```

### Paso 4: Guardar y reiniciar el servicio
```bash
# Opción A: Con Docker
docker-compose restart maransa-ai-service

# Opción B: Manual (si no usa Docker)
# 1. Presionar Ctrl+C para detener el servicio
# 2. Ejecutar: python main.py
```

### Verificación
```bash
# Verificar que los nuevos precios se cargan
curl http://localhost:8000/data/exporquilsa-prices | jq .

# Debe mostrar los precios actualizados
```

---

## 📊 Método 2: Usando JSON Externo (PROFESIONAL)

Para no editar el código cada vez, crear archivo de configuración:

### Paso 1: Crear archivo de precios JSON
Archivo: `maransa-ai-service/data/exporquilsa_prices.json`

```json
{
  "fecha_actualizacion": "2026-02-03",
  "fuente": "EXPORQUILSA S.A.",
  "contacto": "0984222956",
  "headless": {
    "16/20": 2.90,
    "21/25": 2.50,
    "26/30": 2.30,
    "31/35": 2.05,
    "36/40": 2.00,
    "41/50": 1.85,
    "51/60": 1.75,
    "61/70": 1.60,
    "71/90": 1.30,
    "91/110": 0.90
  },
  "whole": {
    "20": 4.60,
    "30": 3.60,
    "40": 3.15,
    "50": 3.00,
    "60": 2.70,
    "70": 2.60,
    "80": 2.40
  }
}
```

### Paso 2: Modificar main.py para cargar desde JSON
```python
import json
from pathlib import Path

class RealAIConfig:
    def __init__(self):
        # Cargar precios desde JSON
        json_path = Path(__file__).parent / "data" / "exporquilsa_prices.json"
        
        if json_path.exists():
            with open(json_path, 'r') as f:
                prices_data = json.load(f)
                self.SHRIMP_CALIBER_PRICES = {
                    "HEADLESS": prices_data.get("headless", {}),
                    "WHOLE": prices_data.get("whole", {})
                }
        else:
            # Fallback a precios hardcoded si JSON no existe
            self.SHRIMP_CALIBER_PRICES = { ... }
```

### Ventaja
Ahora solo necesita:
1. Actualizar el archivo JSON
2. Reiniciar el servicio (sin tocar código)

---

## 🤖 Método 3: API Automática (AVANZADO)

Si EXPORQUILSA tiene API pública (futuro):

```python
async def load_exporquilsa_prices_from_api():
    """Carga precios directamente de API EXPORQUILSA"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.exporquilsa.com/prices") as response:
                if response.status == 200:
                    data = await response.json()
                    return data  # Usar directamente
    except Exception as e:
        logger.error(f"Error cargando precios API: {e}")
        # Fallback a precios locales
        return PRECIOS_LOCALES
```

---

## 📝 CHECKLIST DE ACTUALIZACIÓN

### Cuando Reciba Nuevos Precios de EXPORQUILSA:

- [ ] Registrar fecha de vigencia (ej: 31-01-2026)
- [ ] Verificar que incluya:
  - [ ] Precios sin cabeza
  - [ ] Precios entero
  - [ ] Calibres completos
  - [ ] Condiciones de calidad
  
- [ ] Comparar con precios anteriores:
  - [ ] ¿Aumentaron?
  - [ ] ¿Bajaron?
  - [ ] ¿Nuevos calibres?
  
- [ ] Actualizar en main.py o JSON
  
- [ ] Reiniciar servicio
  
- [ ] Verificar con endpoint:
  ```bash
  curl http://localhost:8000/data/exporquilsa-prices
  ```
  
- [ ] Hacer una predicción de prueba:
  ```bash
  curl -X POST http://localhost:8000/predict/price \
    -H "Content-Type: application/json" \
    -d '{"tipo_producto": "36/40", "mercado_destino": "CHINA", ...}'
  ```
  
- [ ] Verificar que la predicción use nuevos precios
  - [ ] `precio_base_exporquilsa` actualizado
  - [ ] Comparativas correctas

---

## 🔍 VALIDACIÓN DE CAMBIOS

### Ver precios actuales
```bash
curl http://localhost:8000/data/exporquilsa-prices | jq '.precios'
```

### Ver precio específico
```bash
curl http://localhost:8000/data/caliber-price/36%2F40?presentation=HEADLESS
```

### Verificar en predicción
```bash
curl -X POST http://localhost:8000/predict/price \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "36/40",
    "mercado_destino": "CHINA",
    "provincia": "GUAYAS",
    "fecha_prediccion": "2026-02-03"
  }' | jq '.factores_principales.precio_base_exporquilsa'
```

Debe mostrar el precio actualizado.

---

## 📅 REGISTRO DE CAMBIOS

| Fecha | Versión | Precios De | Precios Hasta | Cambios |
|-------|---------|-----------|--------------|---------|
| 31-01-2026 | 2.1.0 | - | Versión inicial | Primera integración |
| [Próxima] | 2.1.1 | 31-01 | ?? | ?? cambios |

---

## 💡 TIPS

1. **Respaldos:** Antes de cambiar, copiar precios viejos a comentario
2. **Pruebas:** Siempre hacer una predicción después de actualizar
3. **Historial:** Mantener registro de cambios de precios
4. **Alertas:** Considerar notificar a usuarios si hay cambios significativos
5. **Automático:** Futuro - Integrar webhook de EXPORQUILSA

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Afecta a datos antiguos?**  
R: No, solo afecta predicciones nuevas. Datos históricos se guardan en DB.

**P: ¿Necesito redeploy?**  
R: Solo reinicio del servicio. Con método JSON, ni eso.

**P: ¿Y si se equivoco en un precio?**  
R: Revisar y corregir. Los usuarios verán el nuevo precio en siguiente predicción.

**P: ¿Cuándo actualizar?**  
R: Cuando EXPORQUILSA envíe nuevos precios (generalmente mensual).

---

## 📞 CONTACTO

**EXPORQUILSA S.A.**
- WhatsApp: 0984222956
- Pedirles que notifiquen cambios de precios

---

**Última actualización:** 2026-02-03  
**Versión de Referencia:** 2.1.0-Real-EXPORQUILSA
