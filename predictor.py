# Sistema de Predicción de Precios
# Implementa modelos matemáticos fundamentados para predecir precios futuros
# Basado en análisis de series temporales, tendencias y correlaciones

import numpy as np
from scipy import stats, optimize
from datetime import date, timedelta
from typing import Dict, Any, List, Tuple, Optional
import logging
from database import PriceDatabase

logger = logging.getLogger(__name__)

class PricePredictor:
    """
    Predictor de precios de camarón basado en modelos matemáticos
    
    Modelos implementados:
    1. Regresión Lineal Simple (tendencia histórica)
    2. Media Móvil Ponderada (suavizado exponencial)
    3. Correlación Precio Público → Precio Despacho
    """
    
    def __init__(self, db: Optional[PriceDatabase] = None):
        """Inicializa el predictor con conexión a base de datos"""
        self.db = db or PriceDatabase()
    
    def predecir_precio_publico(self, 
                                calibre: str,
                                dias_adelante: int = 30,
                                dias_historial: int = 90) -> Dict[str, Any]:
        """
        Predice precio público futuro usando regresión lineal + tendencia
        
        Modelo matemático:
        P(t) = a + b*t + ε
        
        Donde:
        - P(t): Precio en el tiempo t
        - a: Intercepto (precio base)
        - b: Pendiente (tendencia diaria)
        - t: Días desde hoy
        - ε: Error residual
        
        Args:
            calibre: Calibre a predecir (ej: "16/20")
            dias_adelante: Días en el futuro a predecir
            dias_historial: Ventana de datos históricos
            
        Returns:
            Dict con predicción y estadísticas
        """
        # Obtener historial
        historial = self.db.obtener_historial_publico(calibre, dias_historial)
        
        if len(historial) < 5:
            return {
                'status': 'datos_insuficientes',
                'calibre': calibre,
                'mensaje': f'Solo {len(historial)} muestras disponibles'
            }
        
        # Preparar datos para regresión
        fechas = np.array([(f - historial[0][0]).days for f, _ in historial])
        precios = np.array([p for _, p in historial])
        
        # Regresión lineal: precio = a + b*t
        slope, intercept, r_value, p_value, std_err = stats.linregress(fechas, precios)
        
        # Calcular volatilidad (desviación estándar de residuos)
        precios_ajustados = intercept + slope * fechas
        residuos = precios - precios_ajustados
        volatilidad = np.std(residuos)
        
        # Predicción
        dias_desde_inicio = (date.today() - historial[0][0]).days + dias_adelante
        precio_predicho = intercept + slope * dias_desde_inicio
        
        # Intervalo de confianza 95% (±1.96 * error_estandar)
        intervalo_confianza = 1.96 * std_err * np.sqrt(1 + 1/len(fechas))
        
        # Aplicar suavizado exponencial para ajustar tendencia reciente
        # EMA = α * precio_actual + (1-α) * EMA_anterior
        alpha = 0.3  # Factor de suavizado
        precios_ema = self._calcular_ema(precios, alpha)
        ajuste_reciente = precios_ema[-1] - precios[-1]
        precio_predicho_ajustado = precio_predicho + ajuste_reciente * 0.5
        
        return {
            'calibre': calibre,
            'fecha_objetivo': str(date.today() + timedelta(days=dias_adelante)),
            'precio_predicho': round(float(precio_predicho_ajustado), 3),
            'precio_predicho_base': round(float(precio_predicho), 3),
            'intervalo_inferior': round(float(precio_predicho - intervalo_confianza), 3),
            'intervalo_superior': round(float(precio_predicho + intervalo_confianza), 3),
            'tendencia': 'creciente' if slope > 0 else 'decreciente',
            'pendiente_diaria': round(float(slope), 5),
            'r_cuadrado': round(float(r_value ** 2), 4),
            'volatilidad': round(float(volatilidad), 3),
            'confianza': self._calcular_confianza(r_value, len(historial)),
            'muestras': len(historial),
            'metodo': 'regresion_lineal_ema',
            'formula': f'P(t) = {intercept:.3f} + {slope:.5f}*t + EMA_ajuste'
        }
    
    def predecir_precio_despacho(self,
                                 calibre: str,
                                 presentacion: str,
                                 dias_adelante: int = 30,
                                 dias_historial: int = 90) -> Dict[str, Any]:
        """
        Predice precio de despacho basado en predicción pública + correlación histórica
        
        Modelo matemático en 2 etapas:
        
        Etapa 1 - Predicción precio público:
        P_pub(t) = a + b*t
        
        Etapa 2 - Conversión a precio despacho:
        P_desp(t) = α + β * P_pub(t)
        
        Donde α, β se obtienen de correlación histórica
        
        Args:
            calibre: Calibre a predecir
            presentacion: HEADLESS o WHOLE
            dias_adelante: Días a futuro
            dias_historial: Ventana histórica
            
        Returns:
            Dict con predicción completa
        """
        # Paso 1: Predecir precio público
        calibre_publico = calibre
        if presentacion == "WHOLE":
            mapping = {
                "20": "16/20",
                "30": "26/30",
                "40": "36/40",
                "50": "41/50",
                "60": "51/60",
                "70": "61/70",
                "80": "71/90",
            }
            calibre_publico = mapping.get(calibre, calibre)

        prediccion_publico = self.predecir_precio_publico(calibre_publico, dias_adelante, dias_historial)
        
        if prediccion_publico.get('status') == 'datos_insuficientes':
            return prediccion_publico
        
        # Paso 2: Obtener correlación público → despacho
        correlacion = self.db.calcular_correlacion(calibre, presentacion, dias_historial, calibre_publico=calibre_publico)
        
        if correlacion.get('status') in ['sin_datos', 'datos_insuficientes']:
            # Fallback: usar ratio promedio histórico general o estimado
            ratio_fallback = 0.65 if presentacion == 'HEADLESS' else 0.70
            precio_despacho = prediccion_publico['precio_predicho'] * ratio_fallback
            
            return {
                'calibre': calibre,
                'presentacion': presentacion,
                'fecha_objetivo': prediccion_publico['fecha_objetivo'],
                'precio_publico_predicho': prediccion_publico['precio_predicho'],
                'precio_despacho_predicho': round(precio_despacho, 3),
                'metodo': 'ratio_estimado',
                'ratio_usado': ratio_fallback,
                'confianza': 'baja',
                'nota': 'Predicción basada en ratio estimado por falta de datos históricos',
                'prediccion_publico': prediccion_publico
            }
        
        # Aplicar modelo de correlación
        # P_desp = intercepto + pendiente * P_pub
        precio_publico_pred = prediccion_publico['precio_predicho']
        
        if 'pendiente' in correlacion and 'intercepto' in correlacion:
            # Modelo de regresión lineal
            precio_despacho = correlacion['intercepto'] + correlacion['pendiente'] * precio_publico_pred
        else:
            # Fallback a ratio simple
            precio_despacho = correlacion['ratio_promedio'] * precio_publico_pred
        
        # Calcular margen de error propagado
        # Error_total = sqrt(Error_publico^2 + Error_correlacion^2)
        error_publico = (prediccion_publico['intervalo_superior'] - 
                        prediccion_publico['intervalo_inferior']) / 2
        error_correlacion = correlacion.get('desviacion_estandar', 0.1) * precio_publico_pred
        error_total = np.sqrt(error_publico**2 + error_correlacion**2)
        
        return {
            'calibre': calibre,
            'presentacion': presentacion,
            'fecha_objetivo': prediccion_publico['fecha_objetivo'],
            'precio_publico_predicho': prediccion_publico['precio_predicho'],
            'precio_despacho_predicho': round(float(precio_despacho), 3),
            'intervalo_inferior': round(float(precio_despacho - error_total), 3),
            'intervalo_superior': round(float(precio_despacho + error_total), 3),
            'confianza': self._calcular_confianza_compuesta(
                prediccion_publico.get('confianza', 0.5),
                correlacion.get('coeficiente_correlacion', 0.5)
            ),
            'correlacion': {
                'ratio_promedio': correlacion['ratio_promedio'],
                'r_cuadrado': correlacion.get('r_cuadrado', correlacion['coeficiente_correlacion']**2),
                'muestras': correlacion['muestras'],
                'formula': correlacion.get('formula', f"ratio={correlacion['ratio_promedio']}")
            },
            'tendencia': prediccion_publico['tendencia'],
            'metodo': 'regresion_lineal_correlacionada',
            'prediccion_publico': prediccion_publico
        }
    
    def _calcular_ema(self, precios: np.ndarray, alpha: float) -> np.ndarray:
        """
        Calcula Media Móvil Exponencial (EMA)
        
        Formula: EMA[t] = α * precio[t] + (1-α) * EMA[t-1]
        
        Args:
            precios: Array de precios históricos
            alpha: Factor de suavizado (0-1), mayor = más peso al presente
            
        Returns:
            Array con valores EMA
        """
        ema = np.zeros_like(precios)
        ema[0] = precios[0]
        
        for i in range(1, len(precios)):
            ema[i] = alpha * precios[i] + (1 - alpha) * ema[i-1]
        
        return ema
    
    def _calcular_confianza(self, r_value: float, n_muestras: int) -> float:
        """
        Calcula nivel de confianza basado en R² y tamaño de muestra
        
        Confianza = R² * factor_muestras
        
        Args:
            r_value: Coeficiente de correlación
            n_muestras: Cantidad de muestras
            
        Returns:
            Valor entre 0 y 1
        """
        r_cuadrado = r_value ** 2
        
        # Factor de ajuste por tamaño de muestra
        if n_muestras < 10:
            factor = 0.5
        elif n_muestras < 30:
            factor = 0.7
        elif n_muestras < 60:
            factor = 0.85
        else:
            factor = 1.0
        
        confianza = r_cuadrado * factor
        return round(float(confianza), 3)
    
    def _calcular_confianza_compuesta(self, conf1: float, conf2: float) -> float:
        """
        Calcula confianza compuesta de dos predicciones encadenadas
        
        Formula: Conf_total = conf1 * conf2 (probabilidad conjunta)
        
        Args:
            conf1: Confianza de predicción pública
            conf2: Confianza de correlación
            
        Returns:
            Confianza total
        """
        return round(float(conf1 * conf2), 3)
    
    def generar_predicciones_multiples(self,
                                       calibres: List[str],
                                       presentaciones: List[str],
                                       dias_adelante: int = 30) -> Dict[str, Any]:
        """
        Genera predicciones para múltiples calibres y presentaciones
        
        Args:
            calibres: Lista de calibres
            presentaciones: Lista de presentaciones
            dias_adelante: Días a futuro
            
        Returns:
            Dict con todas las predicciones
        """
        predicciones = {}
        
        for calibre in calibres:
            for presentacion in presentaciones:
                key = f"{calibre}_{presentacion}"
                try:
                    pred = self.predecir_precio_despacho(calibre, presentacion, dias_adelante)
                    predicciones[key] = pred
                except Exception as e:
                    logger.error(f"Error prediciendo {key}: {e}")
                    predicciones[key] = {'status': 'error', 'mensaje': str(e)}
        
        return {
            'fecha_prediccion': str(date.today()),
            'fecha_objetivo': str(date.today() + timedelta(days=dias_adelante)),
            'dias_adelante': dias_adelante,
            'predicciones': predicciones,
            'total': len(predicciones)
        }
