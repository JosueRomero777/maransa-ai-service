#!/bin/bash
# Script de Pruebas - Maransa AI Service v2.1 con Tabla EXPORQUILSA
# Uso: Copiar y pegar los comandos en terminal para probar los nuevos endpoints

API_URL="http://localhost:8000"
TOKEN="tu_token_jwt_aqui"  # Si requiere autenticación

echo "=================================================="
echo "PRUEBAS - MARANSA AI SERVICE v2.1"
echo "Tabla de Precios EXPORQUILSA Integrada"
echo "=================================================="
echo ""

# ============= 1. VER INFORMACIÓN DEL SERVICIO =============
echo "1️⃣  INFORMACIÓN DEL SERVICIO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -X GET "$API_URL/" | jq .
echo ""
echo ""

# ============= 2. VER TABLA COMPLETA EXPORQUILSA =============
echo "2️⃣  TABLA COMPLETA DE PRECIOS EXPORQUILSA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Solicitud: GET /data/exporquilsa-prices"
echo ""
curl -X GET "$API_URL/data/exporquilsa-prices" | jq .
echo ""
echo ""

# ============= 3. PRECIO ESPECÍFICO - CALIBRE 36/40 =============
echo "3️⃣  PRECIO ESPECÍFICO: Calibre 36/40 (Sin Cabeza)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Solicitud: GET /data/caliber-price/36%2F40?presentation=HEADLESS"
echo ""
curl -X GET "$API_URL/data/caliber-price/36%2F40?presentation=HEADLESS" | jq .
echo ""
echo ""

# ============= 4. PRECIO ESPECÍFICO - CALIBRE 50 ENTERO =============
echo "4️⃣  PRECIO ESPECÍFICO: Calibre 50 (Con Cabeza)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Solicitud: GET /data/caliber-price/50?presentation=WHOLE"
echo ""
curl -X GET "$API_URL/data/caliber-price/50?presentation=WHOLE" | jq .
echo ""
echo ""

# ============= 5. PREDICCIÓN: Calibre 36/40 para China =============
echo "5️⃣  PREDICCIÓN: Calibre 36/40 para Mercado China"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Solicitud: POST /predict/price"
echo ""
curl -X POST "$API_URL/predict/price" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "36/40",
    "mercado_destino": "CHINA",
    "provincia": "GUAYAS",
    "fecha_prediccion": "2026-02-03",
    "incluir_factores_externos": true
  }' | jq .
echo ""
echo ""

# ============= 6. PREDICCIÓN: Calibre 21/25 para USA =============
echo "6️⃣  PREDICCIÓN: Calibre 21/25 para Mercado USA (Con Prioridad)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Solicitud: POST /predict/price"
echo ""
curl -X POST "$API_URL/predict/price" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "21/25",
    "mercado_destino": "USA",
    "provincia": "GUAYAS",
    "fecha_prediccion": "2026-02-03",
    "incluir_factores_externos": true
  }' | jq .
echo ""
echo ""

# ============= 7. PREDICCIÓN: Calibre 91/110 para Nacional =============
echo "7️⃣  PREDICCIÓN: Calibre 91/110 para Mercado Nacional"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Solicitud: POST /predict/price"
echo ""
curl -X POST "$API_URL/predict/price" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "91/110",
    "mercado_destino": "NACIONAL",
    "provincia": "MACHALA",
    "fecha_prediccion": "2026-02-03",
    "incluir_factores_externos": true
  }' | jq .
echo ""
echo ""

# ============= 8. FACTORES DE MERCADO =============
echo "8️⃣  FACTORES DE MERCADO EN TIEMPO REAL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Solicitud: GET /data/market-factors"
echo ""
curl -X GET "$API_URL/data/market-factors" | jq '.factors | sort_by(-.impact_score) | .[0:5]'
echo ""
echo "(Mostrando top 5 factores)"
echo ""
echo ""

# ============= 9. INFORMACIÓN DEL MODELO =============
echo "9️⃣  INFORMACIÓN DEL MODELO ML"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Solicitud: GET /models/info"
echo ""
curl -X GET "$API_URL/models/info" | jq .
echo ""
echo ""

# ============= 10. ESTADO DE SALUD =============
echo "🔟 ESTADO DE SALUD DEL SERVICIO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Solicitud: GET /health"
echo ""
curl -X GET "$API_URL/health" | jq .
echo ""
echo ""

echo "=================================================="
echo "✅ PRUEBAS COMPLETADAS"
echo "=================================================="
echo ""
echo "📊 RESUMEN DE ENDPOINTS NUEVOS:"
echo "1. GET  /data/exporquilsa-prices"
echo "   → Tabla completa EXPORQUILSA"
echo ""
echo "2. GET  /data/caliber-price/{caliber}"
echo "   → Precio específico por calibre"
echo ""
echo "3. POST /predict/price (mejorado)"
echo "   → Predicciones con precios EXPORQUILSA reales"
echo ""
echo "📚 DOCUMENTACIÓN:"
echo "   - MEJORAS_EXPORQUILSA_v2.1.md"
echo "   - RESUMEN_CAMBIOS_v2.1.md"
echo ""
