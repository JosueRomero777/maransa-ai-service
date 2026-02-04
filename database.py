# Sistema de Base de Datos para Precios Históricos y Predicciones
# Almacena precios públicos scrapeados y precios de despacho históricos
# Permite entrenar modelos de predicción basados en datos reales

import sqlite3
import json
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

class PriceDatabase:
    """
    Base de datos SQLite para almacenar precios históricos
    Estructura optimizada para análisis de series temporales y predicciones
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Inicializa conexión a base de datos"""
        if db_path is None:
            db_path = Path(__file__).parent / "data" / "precios_historicos.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Crear tablas si no existen
        self._init_database()
        
    def _init_database(self):
        """Crea las tablas necesarias en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de precios públicos (scrapeados)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS precios_publicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                calibre TEXT NOT NULL,
                precio_usd_lb REAL NOT NULL,
                fuente TEXT NOT NULL,
                cantidad_fuentes INTEGER DEFAULT 1,
                confiabilidad TEXT DEFAULT 'media',
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fecha, calibre, fuente)
            )
        """)
        
        # Tabla de precios de despacho históricos (EXPORQUILSA)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS precios_despacho (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                calibre TEXT NOT NULL,
                presentacion TEXT NOT NULL,
                precio_usd_lb REAL NOT NULL,
                origen TEXT DEFAULT 'EXPORQUILSA',
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fecha, calibre, presentacion, origen)
            )
        """)
        
        # Tabla de correlaciones calculadas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS correlaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calibre TEXT NOT NULL,
                presentacion TEXT NOT NULL,
                ratio_promedio REAL NOT NULL,
                coeficiente_correlacion REAL,
                desviacion_estandar REAL,
                muestras INTEGER NOT NULL,
                fecha_calculo DATE NOT NULL,
                formula TEXT,
                UNIQUE(calibre, presentacion, fecha_calculo)
            )
        """)
        
        # Tabla de predicciones generadas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predicciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_prediccion DATE NOT NULL,
                fecha_objetivo DATE NOT NULL,
                calibre TEXT NOT NULL,
                presentacion TEXT NOT NULL,
                precio_publico_predicho REAL NOT NULL,
                precio_despacho_predicho REAL NOT NULL,
                confianza REAL,
                metodo TEXT NOT NULL,
                parametros TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para optimizar consultas
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_publicos_fecha ON precios_publicos(fecha)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_publicos_calibre ON precios_publicos(calibre)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_despacho_fecha ON precios_despacho(fecha)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_despacho_calibre ON precios_despacho(calibre)")
        
        conn.commit()
        conn.close()
        logger.info(f"✓ Base de datos inicializada en {self.db_path}")
    
    def guardar_precios_publicos(self, fecha: date, precios_consolidados: Dict[str, Any]) -> int:
        """
        Guarda precios públicos scrapeados en la base de datos
        
        Args:
            fecha: Fecha de los precios
            precios_consolidados: Dict con estructura {calibre: {precio_publico_promedio, cantidad_fuentes, ...}}
            
        Returns:
            Cantidad de registros guardados
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        registros_guardados = 0
        
        for calibre, datos in precios_consolidados.items():
            precio = datos.get('precio_publico_promedio')
            cantidad_fuentes = datos.get('cantidad_fuentes', 1)
            
            if precio is None or precio <= 0:
                continue
            
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO precios_publicos 
                    (fecha, calibre, precio_usd_lb, fuente, cantidad_fuentes, confiabilidad, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(fecha),
                    calibre,
                    precio,
                    'consolidado',
                    cantidad_fuentes,
                    'alta' if cantidad_fuentes >= 2 else 'media',
                    json.dumps(datos)
                ))
                registros_guardados += 1
            except Exception as e:
                logger.error(f"Error guardando precio público {calibre}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Guardados {registros_guardados} precios públicos para {fecha}")
        return registros_guardados
    
    def guardar_precios_despacho(self, fecha: date, precios: List[Dict[str, Any]]) -> int:
        """
        Guarda precios de despacho históricos de EXPORQUILSA
        
        Args:
            fecha: Fecha de los precios
            precios: Lista de dicts con {calibre, presentacion, precio_usd_lb}
            
        Returns:
            Cantidad de registros guardados
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        registros_guardados = 0
        
        for precio_data in precios:
            calibre = precio_data.get('calibre')
            presentacion = precio_data.get('presentacion')
            precio = precio_data.get('precio_usd_lb')
            
            if not all([calibre, presentacion, precio]):
                continue
            
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO precios_despacho 
                    (fecha, calibre, presentacion, precio_usd_lb, origen, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(fecha),
                    calibre,
                    presentacion,
                    precio,
                    'EXPORQUILSA',
                    json.dumps(precio_data)
                ))
                registros_guardados += 1
            except Exception as e:
                logger.error(f"Error guardando precio despacho {calibre}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Guardados {registros_guardados} precios de despacho para {fecha}")
        return registros_guardados
    
    def obtener_historial_publico(self, 
                                   calibre: str, 
                                   dias: int = 90) -> List[Tuple[date, float]]:
        """
        Obtiene historial de precios públicos para un calibre
        
        Args:
            calibre: Calibre a consultar (ej: "16/20")
            dias: Días hacia atrás
            
        Returns:
            Lista de tuplas (fecha, precio)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        fecha_inicio = date.today() - timedelta(days=dias)
        
        cursor.execute("""
            SELECT fecha, precio_usd_lb
            FROM precios_publicos
            WHERE calibre = ? AND fecha >= ?
            ORDER BY fecha ASC
        """, (calibre, str(fecha_inicio)))
        
        resultados = [(datetime.strptime(row[0], '%Y-%m-%d').date(), row[1]) 
                     for row in cursor.fetchall()]
        
        conn.close()
        return resultados
    
    def obtener_historial_despacho(self, 
                                    calibre: str, 
                                    presentacion: str,
                                    dias: int = 90) -> List[Tuple[date, float]]:
        """
        Obtiene historial de precios de despacho para un calibre/presentación
        
        Args:
            calibre: Calibre a consultar
            presentacion: HEADLESS o WHOLE
            dias: Días hacia atrás
            
        Returns:
            Lista de tuplas (fecha, precio)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        fecha_inicio = date.today() - timedelta(days=dias)
        
        cursor.execute("""
            SELECT fecha, precio_usd_lb
            FROM precios_despacho
            WHERE calibre = ? AND presentacion = ? AND fecha >= ?
            ORDER BY fecha ASC
        """, (calibre, presentacion, str(fecha_inicio)))
        
        resultados = [(datetime.strptime(row[0], '%Y-%m-%d').date(), row[1]) 
                     for row in cursor.fetchall()]
        
        conn.close()
        return resultados
    
    def calcular_correlacion(self, 
                            calibre: str, 
                            presentacion: str,
                            dias: int = 90,
                            calibre_publico: str = None) -> Dict[str, Any]:
        """
        Calcula correlación entre precio público y precio de despacho
        Utiliza regresión lineal y ratio promedio
        
        Args:
            calibre: Calibre a analizar
            presentacion: HEADLESS o WHOLE
            dias: Ventana de análisis
            
        Returns:
            Dict con estadísticas de correlación
        """
        # Obtener historiales
        calibre_pub = calibre_publico or calibre
        hist_publico = self.obtener_historial_publico(calibre_pub, dias)
        hist_despacho = self.obtener_historial_despacho(calibre, presentacion, dias)
        
        if not hist_publico or not hist_despacho:
            return {
                'status': 'sin_datos',
                'calibre': calibre,
                'calibre_publico': calibre_pub,
                'presentacion': presentacion
            }
        
        # Alinear fechas (intersección)
        fechas_publico = {f: p for f, p in hist_publico}
        fechas_despacho = {f: p for f, p in hist_despacho}
        
        fechas_comunes = set(fechas_publico.keys()) & set(fechas_despacho.keys())
        
        if len(fechas_comunes) < 5:
            return {
                'status': 'datos_insuficientes',
                'calibre': calibre,
                'calibre_publico': calibre_pub,
                'presentacion': presentacion,
                'muestras': len(fechas_comunes)
            }
        
        # Crear arrays alineados
        fechas_ordenadas = sorted(fechas_comunes)
        precios_publicos = np.array([fechas_publico[f] for f in fechas_ordenadas])
        precios_despacho = np.array([fechas_despacho[f] for f in fechas_ordenadas])
        
        # Calcular estadísticas
        ratio_array = precios_despacho / precios_publicos
        ratio_promedio = np.mean(ratio_array)
        desviacion = np.std(ratio_array)
        
        # Regresión lineal: precio_despacho = a + b * precio_publico
        slope, intercept, r_value, p_value, std_err = stats.linregress(precios_publicos, precios_despacho)
        
        correlacion = {
            'calibre': calibre,
            'presentacion': presentacion,
            'ratio_promedio': round(float(ratio_promedio), 4),
            'desviacion_estandar': round(float(desviacion), 4),
            'coeficiente_correlacion': round(float(r_value), 4),
            'pendiente': round(float(slope), 4),
            'intercepto': round(float(intercept), 4),
            'r_cuadrado': round(float(r_value ** 2), 4),
            'p_value': round(float(p_value), 6),
            'muestras': len(fechas_comunes),
            'formula': f"precio_despacho = {intercept:.4f} + {slope:.4f} * precio_publico",
            'metodo': 'regresion_lineal',
            'fecha_calculo': date.today()
        }
        
        # Guardar en BD
        self._guardar_correlacion(correlacion)
        
        return correlacion
    
    def _guardar_correlacion(self, correlacion: Dict[str, Any]):
        """Guarda correlación calculada en BD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO correlaciones 
                (calibre, presentacion, ratio_promedio, coeficiente_correlacion, 
                 desviacion_estandar, muestras, fecha_calculo, formula)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                correlacion['calibre'],
                correlacion['presentacion'],
                correlacion['ratio_promedio'],
                correlacion['coeficiente_correlacion'],
                correlacion['desviacion_estandar'],
                correlacion['muestras'],
                str(date.today()),
                correlacion['formula']
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error guardando correlación: {e}")
        finally:
            conn.close()
    
    def obtener_correlacion(self, calibre: str, presentacion: str) -> Optional[Dict[str, Any]]:
        """Obtiene la correlación más reciente calculada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ratio_promedio, coeficiente_correlacion, desviacion_estandar, 
                   muestras, fecha_calculo, formula
            FROM correlaciones
            WHERE calibre = ? AND presentacion = ?
            ORDER BY fecha_calculo DESC
            LIMIT 1
        """, (calibre, presentacion))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'calibre': calibre,
            'presentacion': presentacion,
            'ratio_promedio': row[0],
            'coeficiente_correlacion': row[1],
            'desviacion_estandar': row[2],
            'muestras': row[3],
            'fecha_calculo': row[4],
            'formula': row[5]
        }
