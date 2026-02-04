"""
Endpoints de predicción de precios y correlación con base de datos.

Estas funciones deben ser agregadas a main.py después de la inicialización de db y predictor.
"""

from fastapi import HTTPException, Depends
from datetime import datetime, date
import sqlite3
import logging

logger = logging.getLogger(__name__)

# Estos endpoints deben agregarse a la aplicación FastAPI en main.py


async def save_despacho_history(
    fecha: str,  # formato: YYYY-MM-DD
    calibre: str,
    presentacion: str,
    precio_usd_lb: float,
    origen: str = "EXPORQUILSA"
):
    """
    Guarda precios históricos de despacho manualmente.
    Ejemplo: POST /data/save-despacho-history
    Body: {"fecha": "2024-01-15", "calibre": "16/20", "presentacion": "HEADLESS", "precio_usd_lb": 4.50, "origen": "EXPORQUILSA"}
    """
    try:
        from main import db
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        
        db.guardar_precios_despacho(
            fecha_obj, 
            calibre, 
            presentacion, 
            precio_usd_lb, 
            origen
        )
        
        return {
            "status": "success",
            "message": f"Precio de despacho guardado: {calibre} {presentacion} = ${precio_usd_lb}/lb",
            "fecha": fecha,
            "origen": origen
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {e}")
    except Exception as e:
        logger.error(f"Error guardando precio despacho: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def predict_future_public_price(
    calibre: str,
    dias: int = 30
):
    """
    Predice el precio público futuro usando regresión lineal y EMA.
    
    Fórmula base: P(t) = a + b*t
    Con ajuste EMA: EMA[t] = α * precio[t] + (1-α) * EMA[t-1]
    
    Ejemplo: GET /predict/future-price?calibre=16/20&dias=30
    """
    try:
        from main import predictor
        resultado = predictor.predecir_precio_publico(calibre, dias)
        
        if not resultado:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay datos históricos suficientes para {calibre}"
            )
        
        return {
            "status": "success",
            "calibre": calibre,
            "dias_prediccion": dias,
            "fecha_objetivo": resultado["fecha_objetivo"].isoformat(),
            "precio_predicho_usd_lb": round(resultado["precio_predicho"], 4),
            "intervalo_confianza": {
                "minimo": round(resultado["precio_minimo"], 4),
                "maximo": round(resultado["precio_maximo"], 4)
            },
            "confianza_porcentaje": round(resultado["confianza"] * 100, 2),
            "metodo": "Regresión Lineal + EMA",
            "formula": resultado["formula"],
            "parametros": resultado["parametros"],
            "muestras_historicas": resultado["muestras"],
            "nota": "Esta predicción se basa en tendencias históricas del mercado público"
        }
    except Exception as e:
        logger.error(f"Error prediciendo precio público: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def predict_despacho_price(
    calibre: str,
    presentacion: str,
    dias: int = 30
):
    """
    Predice el precio de despacho futuro basándose en:
    1. Predicción del precio público futuro
    2. Correlación histórica entre precio público y despacho
    
    Fórmula: P_despacho = α + β * P_publico
    
    Ejemplo: GET /predict/despacho-price?calibre=16/20&presentacion=HEADLESS&dias=30
    """
    try:
        from main import predictor
        resultado = predictor.predecir_precio_despacho(calibre, presentacion, dias)
        
        if not resultado:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay datos suficientes para {calibre} {presentacion}"
            )
        
        return {
            "status": "success",
            "calibre": calibre,
            "presentacion": presentacion,
            "dias_prediccion": dias,
            "fecha_objetivo": resultado["fecha_objetivo"].isoformat(),
            "precio_publico_predicho_usd_lb": round(resultado["precio_publico_predicho"], 4),
            "precio_despacho_predicho_usd_lb": round(resultado["precio_despacho_predicho"], 4),
            "intervalo_confianza_despacho": {
                "minimo": round(resultado["precio_despacho_minimo"], 4),
                "maximo": round(resultado["precio_despacho_maximo"], 4)
            },
            "confianza_porcentaje": round(resultado["confianza"] * 100, 2),
            "correlacion": {
                "coeficiente": round(resultado["coeficiente_correlacion"], 4),
                "formula": resultado["formula_correlacion"],
                "r_cuadrado": round(resultado["r_cuadrado"], 4)
            },
            "metodo": "Predicción Público + Correlación Histórica",
            "muestras_correlacion": resultado["muestras_correlacion"],
            "nota": "Precio de despacho calculado a partir del precio público predicho usando correlación histórica"
        }
    except Exception as e:
        logger.error(f"Error prediciendo precio despacho: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def calculate_correlation(
    calibre: str,
    presentacion: str
):
    """
    Calcula la correlación entre precios públicos y despacho para un calibre/presentación.
    
    Usa regresión lineal: P_despacho = α + β * P_publico
    
    Ejemplo: POST /correlations/calculate?calibre=16/20&presentacion=HEADLESS
    """
    try:
        from main import db
        correlacion = db.calcular_correlacion(calibre, presentacion)
        
        if not correlacion:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay datos suficientes para calcular correlación de {calibre} {presentacion}"
            )
        
        return {
            "status": "success",
            "calibre": calibre,
            "presentacion": presentacion,
            "ratio_promedio": round(correlacion["ratio_promedio"], 4),
            "coeficiente_correlacion": round(correlacion["coeficiente_correlacion"], 4),
            "r_cuadrado": round(correlacion["r_cuadrado"], 4),
            "desviacion_estandar": round(correlacion["desviacion_estandar"], 4),
            "formula": correlacion["formula"],
            "muestras": correlacion["muestras"],
            "fecha_calculo": correlacion["fecha_calculo"].isoformat(),
            "interpretacion": {
                "calidad_correlacion": "Excelente" if correlacion["r_cuadrado"] > 0.9 else 
                                      "Buena" if correlacion["r_cuadrado"] > 0.7 else
                                      "Moderada" if correlacion["r_cuadrado"] > 0.5 else "Débil",
                "explicacion": f"El modelo explica {round(correlacion['r_cuadrado'] * 100, 1)}% de la variación en precios de despacho"
            },
            "nota": "Esta correlación se usa para predecir precios de despacho a partir de precios públicos"
        }
    except Exception as e:
        logger.error(f"Error calculando correlación: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_database_status():
    """
    Muestra el estado de la base de datos: cantidad de registros, rangos de fechas, etc.
    """
    try:
        conn = sqlite3.connect('prices.db')
        cursor = conn.cursor()
        
        # Precios públicos
        cursor.execute("SELECT COUNT(*), MIN(fecha), MAX(fecha) FROM precios_publicos")
        publicos = cursor.fetchone()
        
        cursor.execute("SELECT DISTINCT calibre FROM precios_publicos")
        calibres_publicos = [row[0] for row in cursor.fetchall()]
        
        # Precios despacho
        cursor.execute("SELECT COUNT(*), MIN(fecha), MAX(fecha) FROM precios_despacho")
        despacho = cursor.fetchone()
        
        cursor.execute("SELECT DISTINCT calibre, presentacion FROM precios_despacho")
        despacho_combos = [f"{row[0]} {row[1]}" for row in cursor.fetchall()]
        
        # Correlaciones
        cursor.execute("SELECT COUNT(*) FROM correlaciones")
        correlaciones = cursor.fetchone()[0]
        
        # Predicciones
        cursor.execute("SELECT COUNT(*) FROM predicciones")
        predicciones = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "success",
            "database_file": "prices.db",
            "precios_publicos": {
                "total_registros": publicos[0],
                "fecha_inicio": publicos[1],
                "fecha_fin": publicos[2],
                "calibres": calibres_publicos
            },
            "precios_despacho": {
                "total_registros": despacho[0],
                "fecha_inicio": despacho[1],
                "fecha_fin": despacho[2],
                "combinaciones": despacho_combos
            },
            "correlaciones_calculadas": correlaciones,
            "predicciones_guardadas": predicciones
        }
    except Exception as e:
        logger.error(f"Error consultando estado BD: {e}")
        raise HTTPException(status_code=500, detail=str(e))
