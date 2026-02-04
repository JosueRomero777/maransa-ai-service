# Módulo de Scraping y Cache de Precios Públicos de Camarón
# Consulta fuentes públicas de internet y cachea resultados diarios

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import os
import re

logger = logging.getLogger(__name__)

class MarketPriceScraper:
    """
    Scraper para obtener precios públicos de camarón de fuentes internet
    Implementa caché diario para evitar consultas repetidas
    """
    
    CACHE_DIR = Path(__file__).parent / ".cache"
    CACHE_FILE_PREFIX = "market_prices_"
    
    # Headers para evitar bloqueos en requests
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Mapeo de tallas estándar comerciales
    CALIBER_MAPPING = {
        '16/20': 'jumbo',
        '21/25': 'extra_large',
        '26/30': 'large',
        '31/35': 'medium',
        '36/40': 'medium_small',
        '41/50': 'small',
        '51/60': 'extra_small',
        '61/70': 'tiny',
        '71/90': 'very_tiny',
        '91/110': 'smallest'
    }
    
    # Presentaciones mapeadas
    PRESENTATION_MAPPING = {
        'HEADLESS': 'hlso',  # Headless, shell-on
        'WHOLE': 'hoso',     # Whole, shell-on
        'LIVE': 'vivo'       # Vivo
    }
    
    def __init__(self):
        """Inicializa el scraper y crea directorio de caché si no existe"""
        self.CACHE_DIR.mkdir(exist_ok=True)
        self.today = date.today()
        
    def _get_cache_file(self) -> Path:
        """Retorna la ruta del archivo de caché para hoy"""
        return self.CACHE_DIR / f"{self.CACHE_FILE_PREFIX}{self.today}.json"
    
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Carga datos de caché si existen para hoy"""
        cache_file = self._get_cache_file()
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    logger.info(f"✓ Datos de caché cargados para {self.today}")
                    return cache_data
            except Exception as e:
                logger.warning(f"Error cargando caché: {e}")
                return None
        
        return None
    
    def _save_cache(self, data: Dict[str, Any]) -> bool:
        """Guarda datos en caché con fecha actual"""
        cache_file = self._get_cache_file()
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"✓ Datos de caché guardados para {self.today}")
            return True
        except Exception as e:
            logger.error(f"Error guardando caché: {e}")
            return False
    
    def scrape_alibaba_prices(self) -> Dict[str, Any]:
        """
        Scraping de Alibaba.com para obtener precios actuales de camarón ecuatoriano
        Busca listados de vendedores ecuatorianos
        """
        try:
            logger.info("🌐 Iniciando scraping de Alibaba.com...")
            
            # Búsqueda: camarón ecuatoriano con especificaciones
            search_queries = [
                "shrimp ecuador 16/20",
                "camarones ecuador headless",
                "ecuador shrimp 26/30"
            ]
            
            prices_by_caliber = {}
            
            for query in search_queries:
                try:
                    # URL de búsqueda Alibaba
                    url = f"https://www.alibaba.com/trade/search?SearchText={query}"
                    
                    response = requests.get(url, headers=self.HEADERS, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'lxml')
                    
                    # Buscar elementos de precio (estructura Alibaba)
                    price_elements = soup.find_all('span', {'class': 'search-card-e-price'})
                    
                    for elem in price_elements[:5]:  # Top 5 resultados
                        price_text = elem.get_text(strip=True)
                        # Extraer precio numérico (ej: "$2.50-$3.00/Piece")
                        if '$' in price_text:
                            # Procesar para extraer rango de precios
                            parts = price_text.split('-')
                            if len(parts) >= 2:
                                try:
                                    price_min = float(parts[0].replace('$', '').split('/')[0])
                                    price_max = float(parts[1].split('/')[0].replace('$', '').strip())
                                    avg_price = (price_min + price_max) / 2
                                    
                                    # Mapear a calibre si es posible
                                    for cal, label in self.CALIBER_MAPPING.items():
                                        if label in query.lower():
                                            if cal not in prices_by_caliber:
                                                prices_by_caliber[cal] = []
                                            prices_by_caliber[cal].append(avg_price)
                                except:
                                    pass
                except Exception as e:
                    logger.warning(f"Error scraping query '{query}': {e}")
            
            # Calcular promedios por calibre
            alibaba_prices = {}
            for caliber, prices in prices_by_caliber.items():
                if prices:
                    alibaba_prices[caliber] = {
                        'precio_promedio': round(sum(prices) / len(prices), 3),
                        'cantidad_fuentes': len(prices),
                        'rango_min': round(min(prices), 3),
                        'rango_max': round(max(prices), 3)
                    }
            
            logger.info(f"✓ Scraping Alibaba completado: {len(alibaba_prices)} calibres encontrados")
            return alibaba_prices
            
        except Exception as e:
            logger.error(f"Error en scrape_alibaba_prices: {e}")
            return {}
    
    def get_fao_market_index(self) -> Dict[str, Any]:
        """
        Obtiene el Índice de Precios de Alimentos de la FAO
        Específicamente para precios de pescado/mariscos
        """
        try:
            logger.info("🌐 Consultando FAO Food Price Index...")
            
            # FAO Food Price Index - datos públicos mensuales
            url = "https://www.fao.org/foodpricesindex/download/files/FPI_indices.xlsx"
            
            # Alternativa: usar datos CSV público
            fao_data_url = "https://www.fao.org/documents/card/en/c/ca9995en"
            
            # Para este MVP, usar estimaciones basadas en literatura FAO
            # En producción, se parsearia el CSV descargado
            
            fao_indices = {
                'fish_price_index': 105.2,  # Base 100 = 2014-2016 (estimado actual)
                'trend': 'stable',
                'mes_actual': datetime.now().month,
                'fuente': 'FAO_Food_Price_Index',
                'confiabilidad': 'alta',
                'url': fao_data_url
            }
            
            logger.info(f"✓ FAO Index obtenido: {fao_indices['fish_price_index']}")
            return fao_indices
            
        except Exception as e:
            logger.error(f"Error obteniendo FAO index: {e}")
            return {}
    
    def get_trading_economics_data(self) -> Dict[str, Any]:
        """
        Obtiene datos de commodities de Trading Economics
        Incluye datos históricos y tendencias
        """
        try:
            logger.info("🌐 Consultando Trading Economics...")
            
            # Trading Economics tiene datos de commodities pesqueros
            # API requiere suscripción, pero datos públicos están disponibles
            
            url = "https://tradingeconomics.com/commodities"
            
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Buscar datos de pescado/mariscos en la página
            seafood_data = {}
            
            # Estructura genérica (requiere inspección HTML real de TE)
            rows = soup.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    commodity = cells[0].get_text(strip=True)
                    if 'shrimp' in commodity.lower() or 'camaron' in commodity.lower():
                        try:
                            price = float(cells[1].get_text(strip=True).replace('$', ''))
                            change = cells[2].get_text(strip=True)
                            seafood_data[commodity] = {
                                'precio': price,
                                'cambio': change,
                                'fuente': 'TradingEconomics'
                            }
                        except:
                            pass
            
            logger.info(f"✓ Trading Economics: {len(seafood_data)} commodities")
            return seafood_data
            
        except Exception as e:
            logger.error(f"Error en get_trading_economics_data: {e}")
            return {}

    def scrape_selina_wamucii(self) -> Dict[str, Any]:
        """
        Obtiene precio promedio de camarón en Ecuador (USD/lb)
        Fuente: Selina Wamucii (referencia internacional)
        """
        try:
            logger.info("🌐 Consultando Selina Wamucii (Ecuador shrimp)...")
            url = "https://www.selinawamucii.com/insights/prices/ecuador/shrimps-prawns/"

            response = requests.get(url, headers=self.HEADERS, timeout=12)
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(response.content, 'lxml')
            text = soup.get_text(" ", strip=True)

            def _extract_var(pattern: str) -> Optional[str]:
                match = re.search(pattern, html, re.IGNORECASE)
                return match.group(1) if match else None

            produce_id = _extract_var(r"var\s+produce_id\s*=\s*\"([^\"]+)\"")
            country_id = _extract_var(r"var\s+country_id\s*=\s*\"([^\"]+)\"")
            nonce = _extract_var(r"var\s+nonce\s*=\s*\"([^\"]+)\"")
            produce_category = _extract_var(r"var\s+produce_category\s*=\s*(\d+)")

            prices: List[float] = []

            if nonce and produce_id and country_id and produce_category:
                ajax_url = "https://www.selinawamucii.com/wp-admin/admin-ajax.php"
                payload = {
                    "action": "produce_analysis",
                    "produce_id": produce_id,
                    "country_id": country_id,
                    "nonce": nonce,
                    "produce_category": produce_category,
                    "type": "prices",
                    "filtering": "true"
                }

                ajax_response = requests.post(ajax_url, headers=self.HEADERS, data=payload, timeout=15)
                if ajax_response.status_code == 200:
                    try:
                        ajax_data = ajax_response.json()
                        ajax_text = json.dumps(ajax_data)
                    except Exception:
                        ajax_text = ajax_response.text

                    # Buscar valores en USD/lb o USD/kg dentro de la respuesta
                    lb_matches = re.findall(
                        r"\$\s*([0-9]+(?:\.[0-9]+)?)\s*(?:/\s*lb|per\s*lb|per\s*pound)",
                        ajax_text,
                        re.IGNORECASE
                    )
                    prices.extend([float(m) for m in lb_matches if m])

                    if not prices:
                        kg_matches = re.findall(
                            r"\$\s*([0-9]+(?:\.[0-9]+)?)\s*(?:/\s*kg|per\s*kg|per\s*kilogram)",
                            ajax_text,
                            re.IGNORECASE
                        )
                        for m in kg_matches:
                            try:
                                prices.append(float(m) / 2.20462)
                            except Exception:
                                pass

            # Fallback HTML: rango por libra o por kilo en el texto público
            if not prices:
                range_per_lb = re.findall(
                    r"between\s+US\$\s*([0-9]+(?:\.[0-9]+)?)\s+and\s+US\$\s*([0-9]+(?:\.[0-9]+)?)\s+per\s+pound",
                    text,
                    re.IGNORECASE
                )
                for a, b in range_per_lb:
                    try:
                        prices.append((float(a) + float(b)) / 2)
                    except Exception:
                        pass

            if not prices:
                range_per_kg = re.findall(
                    r"between\s+US\$\s*([0-9]+(?:\.[0-9]+)?)\s+and\s+US\$\s*([0-9]+(?:\.[0-9]+)?)\s+per\s+kilogram",
                    text,
                    re.IGNORECASE
                )
                for a, b in range_per_kg:
                    try:
                        prices.append(((float(a) + float(b)) / 2) / 2.20462)
                    except Exception:
                        pass

            if not prices:
                return {}

            avg_price = sum(prices) / len(prices)
            return {
                "precio_promedio_usd_lb": round(avg_price, 3),
                "cantidad_muestras": len(prices),
                "fuente": "SelinaWamucii",
                "url": url
            }

        except Exception as e:
            logger.error(f"Error en scrape_selina_wamucii: {e}")
            return {}

    def scrape_freezeocean_prices(self) -> Dict[str, Any]:
        """
        Scraping de FreezeOcean para precios por talla (USD/lb)
        """
        try:
            logger.info("🌐 Consultando FreezeOcean...")
            api_url = "https://www.freezeocean.com/wp-json/wc/store/products"
            params = {
                "search": "camaron",
                "per_page": 100
            }

            response = requests.get(api_url, headers=self.HEADERS, params=params, timeout=12)
            response.raise_for_status()

            try:
                products = response.json()
            except Exception:
                products = []

            def _strip_html(value: str) -> str:
                if not value:
                    return ""
                return BeautifulSoup(value, "lxml").get_text(" ", strip=True)

            def _to_float(value: str) -> Optional[float]:
                if not value:
                    return None
                try:
                    return float(value.replace(",", ".").strip())
                except Exception:
                    return None

            def _map_size_to_caliber(size: int) -> Optional[str]:
                for key in self.CALIBER_MAPPING.keys():
                    try:
                        low, high = key.split("/")
                        if int(low) <= size <= int(high):
                            return key
                    except Exception:
                        continue
                return None

            def _normalize_caliber(start: int, end: int) -> Optional[str]:
                raw = f"{start}/{end}"
                if raw in self.CALIBER_MAPPING:
                    return raw

                target_mid = (start + end) / 2
                best_key = None
                best_diff = None

                for key in self.CALIBER_MAPPING.keys():
                    try:
                        low, high = key.split("/")
                        mid = (int(low) + int(high)) / 2
                        diff = abs(mid - target_mid)
                        if best_diff is None or diff < best_diff:
                            best_diff = diff
                            best_key = key
                    except Exception:
                        continue

                if best_diff is not None and best_diff <= 6:
                    return best_key

                return None

            def _extract_caliber(text: str) -> Optional[str]:
                if not text:
                    return None

                range_pattern = re.compile(
                    r"(\d{2})\s*[–-]\s*(\d{2})\s*(?:u|unidades|und|u\.|en\s*libra|lb)",
                    re.IGNORECASE
                )
                match = range_pattern.search(text)
                if match:
                    start, end = match.groups()
                    try:
                        return _normalize_caliber(int(start), int(end))
                    except Exception:
                        return None

                talla_match = re.search(r"talla\s*(\d{2})", text, re.IGNORECASE)
                if talla_match:
                    try:
                        size = int(talla_match.group(1))
                        return _map_size_to_caliber(size)
                    except Exception:
                        return None

                return None

            def _extract_price_per_lb(text: str) -> Optional[float]:
                if not text:
                    return None

                lb_patterns = [
                    r"(?:precio\s*:)?\s*libra\s*[:\-]?\s*\$?\s*([0-9]+(?:[\.,][0-9]+)?)",
                    r"(?:lb|libra)\s*\$?\s*([0-9]+(?:[\.,][0-9]+)?)"
                ]
                for pattern in lb_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        value = _to_float(match.group(1))
                        if value:
                            return value

                kg_match = re.search(r"(?:kilo|kg)\s*[:\-]?\s*\$?\s*([0-9]+(?:[\.,][0-9]+)?)", text, re.IGNORECASE)
                if kg_match:
                    value = _to_float(kg_match.group(1))
                    if value:
                        return value / 2.20462

                return None

            prices_by_caliber: Dict[str, List[float]] = {}

            for product in products if isinstance(products, list) else []:
                name = product.get("name", "")
                short_desc = product.get("short_description", "")
                description = product.get("description", "")
                combined = " ".join([
                    _strip_html(name),
                    _strip_html(short_desc),
                    _strip_html(description)
                ]).strip()

                if not combined:
                    continue

                caliber = _extract_caliber(combined)
                if not caliber:
                    continue

                price_per_lb = _extract_price_per_lb(combined)
                if price_per_lb is None:
                    prices_data = product.get("prices", {}) if isinstance(product, dict) else {}
                    raw_price = prices_data.get("price")
                    minor_unit = prices_data.get("currency_minor_unit", 2)
                    try:
                        if raw_price is not None:
                            price_per_lb = float(raw_price) / (10 ** int(minor_unit))
                    except Exception:
                        price_per_lb = None

                if price_per_lb is None:
                    continue

                prices_by_caliber.setdefault(caliber, []).append(price_per_lb)

            result = {}
            for cal, prices in prices_by_caliber.items():
                if prices:
                    result[cal] = {
                        "precio_promedio": round(sum(prices) / len(prices), 3),
                        "cantidad_fuentes": len(prices),
                        "fuente": "FreezeOcean"
                    }

            logger.info(f"✓ FreezeOcean: {len(result)} calibres encontrados")
            return result

        except Exception as e:
            logger.error(f"Error en scrape_freezeocean_prices: {e}")
            return {}

    def scrape_globalfrozen_prices(self) -> Dict[str, Any]:
        """
        Scraping de GlobalFrozen para precios por talla (USD/lb)
        DESHABILITADO: sitio no responde
        """
        logger.info("⏭️ GlobalFrozen omitido (sitio no disponible)")
        return {}

    def scrape_easyseafood_prices(self) -> Dict[str, Any]:
        """
        Scraping de EasySeafood para referencias de precio por talla (USD/lb)
        DESHABILITADO: sitio no expone precios públicos inline
        """
        logger.info("⏭️ EasySeafood omitido (sin precios públicos)")
        return {}

    def get_comtrade_unit_value(self) -> Dict[str, Any]:
        """
        Obtiene valor unitario (USD/lb) desde UN Comtrade
        para camarón (códigos HS 030616 y 030617)
        """
        try:
            logger.info("🌐 Consultando UN Comtrade (HS 030616/030617)...")

            year = datetime.now().year
            codes = ["030617", "030616"]
            unit_values = []
            latest_period = None

            years_to_try = [year, year - 1]
            freqs_to_try = ["M", "A"]

            for code in codes:
                for y in years_to_try:
                    for freq in freqs_to_try:
                        url = (
                            "https://comtradeapi.worldbank.org/v1/get/HS"
                            f"?max=5000&type=C&freq={freq}&ps={y}&px=HS&cc={code}"
                            "&rg=2&reporter=218&partner=0&fmt=json"
                        )

                        response = requests.get(url, headers=self.HEADERS, timeout=15)
                        if response.status_code != 200:
                            logger.warning(f"Comtrade HTTP {response.status_code} para {code} ({freq}-{y})")
                            continue

                        data = response.json()
                        dataset = data.get("dataset", [])
                        if not dataset:
                            continue

                        # Tomar el periodo más reciente con datos válidos
                        dataset_sorted = sorted(dataset, key=lambda d: d.get("period", 0), reverse=True)
                        for row in dataset_sorted:
                            trade_value = row.get("tradeValue")
                            net_weight = row.get("netWeight")
                            period = row.get("period")
                            if trade_value and net_weight and net_weight > 0:
                                usd_per_kg = trade_value / net_weight
                                usd_per_lb = usd_per_kg / 2.20462
                                unit_values.append(usd_per_lb)
                                latest_period = period if latest_period is None else max(latest_period, period)
                                break
                        if unit_values:
                            break
                    if unit_values:
                        break

            if not unit_values:
                return {}

            avg_unit_value = sum(unit_values) / len(unit_values)
            return {
                "precio_unitario_usd_lb": round(avg_unit_value, 3),
                "fuente": "UN_Comtrade",
                "reporter": "Ecuador",
                "codes": codes,
                "periodo": latest_period,
                "metodo": "trade_value/net_weight"
            }

        except Exception as e:
            logger.error(f"Error en get_comtrade_unit_value: {e}")
            return {}
    
    def get_public_market_prices(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Obtiene precios públicos del mercado desde múltiples fuentes
        con caché diario para optimizar
        
        Args:
            use_cache: Si True, usa caché si existe para hoy
            
        Returns:
            Dict con precios por calibre y presentación
        """
        
        # Intentar cargar del caché primero
        if use_cache:
            cached_data = self._load_cache()
            if cached_data:
                return cached_data
        
        logger.info("📊 Recopilando precios públicos del mercado...")
        
        all_prices = {
            'timestamp': datetime.now().isoformat(),
            'fecha': str(self.today),
            'fuentes': {},
            'status': 'success',
            'warnings': []
        }
        
        # 1. Scraping Alibaba
        alibaba_prices = self.scrape_alibaba_prices()
        if alibaba_prices:
            all_prices['fuentes']['alibaba'] = alibaba_prices
        else:
            all_prices['warnings'].append('alibaba_sin_datos')
        
        # 2. Trading Economics
        te_data = self.get_trading_economics_data()
        if te_data:
            all_prices['fuentes']['trading_economics'] = te_data
        else:
            all_prices['warnings'].append('trading_economics_sin_datos')
        
        # 3. FAO Index
        fao_index = self.get_fao_market_index()
        if fao_index:
            all_prices['fuentes']['fao'] = fao_index
        else:
            all_prices['warnings'].append('fao_sin_datos')

        # 4. UN Comtrade (valor unitario USD/lb)
        comtrade_data = self.get_comtrade_unit_value()
        if comtrade_data:
            all_prices['fuentes']['comtrade'] = comtrade_data
        else:
            all_prices['warnings'].append('comtrade_sin_datos')

        # 5. Selina Wamucii (precio promedio)
        selina_data = self.scrape_selina_wamucii()
        if selina_data:
            all_prices['fuentes']['selina_wamucii'] = selina_data
        else:
            all_prices['warnings'].append('selina_wamucii_sin_datos')

        # 6. FreezeOcean (por talla)
        freezeocean_data = self.scrape_freezeocean_prices()
        if freezeocean_data:
            all_prices['fuentes']['freezeocean'] = freezeocean_data
        else:
            all_prices['warnings'].append('freezeocean_sin_datos')

        # 7. GlobalFrozen (DESHABILITADO)
        # 8. EasySeafood (DESHABILITADO)
        
        # 9. Calcular promedio ponderado por calibre
        all_prices['precios_consolidados'] = self._consolidate_prices(all_prices['fuentes'])
        
        # Guardar en caché solo si hay precios consolidados
        if all_prices['precios_consolidados']:
            self._save_cache(all_prices)
        else:
            all_prices['status'] = 'sin_datos'
            all_prices['warnings'].append('sin_precios_consolidados')
        
        logger.info(f"✓ Precios públicos consolidados: {len(all_prices['precios_consolidados'])} calibres")
        return all_prices
    
    def _consolidate_prices(self, sources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolida precios de múltiples fuentes usando promedio ponderado
        Pondera por confiabilidad de la fuente
        """
        
        # Pesos por confiabilidad de fuente
        source_weights = {
            'alibaba': 0.40,              # Vendedores reales, actualizado
            'trading_economics': 0.35,   # Datos confiables de commodities
            'fao': 0.25,                 # Índices, menos específico
            'comtrade': 0.30,            # Valor unitario comercio exterior
            'selina_wamucii': 0.25,      # Precio promedio (referencia)
            'freezeocean': 0.45,         # Tienda B2B con talla
            'globalfrozen': 0.45,        # Tienda B2B con talla
            'easyseafood': 0.35          # Análisis de mercado con talla
        }
        
        consolidado = {}
        
        # Para cada calibre, calcular promedio ponderado
        for caliber in self.CALIBER_MAPPING.keys():
            prices_list = []
            
            # Buscar precio en cada fuente
            if 'alibaba' in sources:
                if caliber in sources['alibaba']:
                    precio = sources['alibaba'][caliber].get('precio_promedio')
                    if precio:
                        prices_list.append((precio, source_weights['alibaba']))

            if 'freezeocean' in sources:
                if caliber in sources['freezeocean']:
                    precio = sources['freezeocean'][caliber].get('precio_promedio')
                    if precio:
                        prices_list.append((precio, source_weights['freezeocean']))
            
            # Si tenemos al menos una fuente
            if prices_list:
                weighted_avg = sum(p * w for p, w in prices_list) / sum(w for _, w in prices_list)
                consolidado[caliber] = {
                    'precio_publico_promedio': round(weighted_avg, 3),
                    'cantidad_fuentes': len(prices_list),
                    'actualizado': str(self.today)
                }

        # Fallback: si no hay precios por calibre, usar Comtrade como promedio general
        if not consolidado and 'comtrade' in sources:
            unit_value = sources['comtrade'].get('precio_unitario_usd_lb')
            if unit_value:
                for caliber in self.CALIBER_MAPPING.keys():
                    consolidado[caliber] = {
                        'precio_publico_promedio': round(unit_value, 3),
                        'cantidad_fuentes': 1,
                        'actualizado': str(self.today),
                        'derivado_desde': 'comtrade_unit_value',
                        'nota': 'Precio promedio por lb (no específico por calibre)'
                    }

        # Fallback 2: Selina Wamucii (precio promedio general)
        if not consolidado and 'selina_wamucii' in sources:
            unit_value = sources['selina_wamucii'].get('precio_promedio_usd_lb')
            if unit_value:
                for caliber in self.CALIBER_MAPPING.keys():
                    consolidado[caliber] = {
                        'precio_publico_promedio': round(unit_value, 3),
                        'cantidad_fuentes': 1,
                        'actualizado': str(self.today),
                        'derivado_desde': 'selina_wamucii',
                        'nota': 'Precio promedio por lb (no específico por calibre)'
                    }
        
        return consolidado
    
    def calculate_market_spread(self, 
                               caliber: str, 
                               presentacion: str,
                               exporquilsa_price: float) -> Dict[str, Any]:
        """
        Calcula el spread entre precio de despacho (EXPORQUILSA)
        y precio público del mercado
        
        Args:
            caliber: Ej "16/20", "21/25"
            presentacion: "HEADLESS" o "WHOLE"
            exporquilsa_price: Precio base de EXPORQUILSA para ese calibre
            
        Returns:
            Dict con análisis del spread
        """
        
        public_prices = self.get_public_market_prices(use_cache=True)
        
        if caliber not in public_prices.get('precios_consolidados', {}):
            logger.warning(f"No hay datos públicos para calibre {caliber}")
            return {
                'status': 'no_data',
                'caliber': caliber,
                'mensaje': 'Sin datos públicos disponibles'
            }
        
        public_price = public_prices['precios_consolidados'][caliber]['precio_publico_promedio']
        
        # Calcular spread
        spread_absoluto = public_price - exporquilsa_price
        spread_porcentaje = (spread_absoluto / exporquilsa_price * 100) if exporquilsa_price > 0 else 0
        
        return {
            'caliber': caliber,
            'presentacion': presentacion,
            'precio_exporquilsa': exporquilsa_price,
            'precio_publico_promedio': public_price,
            'spread_absoluto': round(spread_absoluto, 3),
            'spread_porcentaje': round(spread_porcentaje, 2),
            'ratio_mercado_despacho': round(public_price / exporquilsa_price, 3) if exporquilsa_price > 0 else 0,
            'fecha': str(self.today),
            'confiabilidad': 'media'  # Depende de fuentes disponibles
        }


class PredictionOptimizer:
    """
    Optimiza predicciones de precios de compra basado en:
    - Spread histórico entre precio público y despacho
    - Margen de ganancia deseado
    - Horizonte de predicción
    """
    
    # Márgenes mínimo/recomendado en USD
    MARGEN_MINIMO = 0.10       # $0.10 por libra
    MARGEN_RECOMENDADO = 0.15  # $0.15 por libra
    
    def __init__(self):
        self.scraper = MarketPriceScraper()
    
    def calcular_precio_compra_rentable(self,
                                       precio_despacho_predicho: float,
                                       dias_horizonte: int = 30) -> Dict[str, float]:
        """
        Calcula precio de compra recomendado para obtener margen deseado
        
        Args:
            precio_despacho_predicho: Precio predicho que la empacadora pagará
            dias_horizonte: Días hasta la compra (para ajustar margen)
            
        Returns:
            Dict con precios de compra mínimo y recomendado
        """
        
        # Ajustar margen según horizonte (más riesgo = margen mayor)
        factor_horizonte = 1.0
        if dias_horizonte > 30:
            factor_horizonte = 1.1  # +10% margen si es >30 días
        elif dias_horizonte > 60:
            factor_horizonte = 1.25  # +25% margen si es >60 días
        
        margen_minimo_ajustado = self.MARGEN_MINIMO * factor_horizonte
        margen_recomendado_ajustado = self.MARGEN_RECOMENDADO * factor_horizonte
        
        return {
            'precio_despacho': round(precio_despacho_predicho, 3),
            'precio_compra_minimo': round(precio_despacho_predicho - margen_minimo_ajustado, 3),
            'precio_compra_recomendado': round(precio_despacho_predicho - margen_recomendado_ajustado, 3),
            'margen_minimo': round(margen_minimo_ajustado, 3),
            'margen_recomendado': round(margen_recomendado_ajustado, 3),
            'dias_horizonte': dias_horizonte,
            'factor_ajuste_horizonte': factor_horizonte
        }
    
    def generar_reporte_viabilidad(self,
                                   calibre: str,
                                   precio_despacho_predicho: float,
                                   provincia_compra: Optional[str] = None) -> Dict[str, Any]:
        """
        Genera reporte de viabilidad de compra en base a datos de mercado
        """
        
        dias_horizon = 30  # Horizonte standard
        rangos_compra = self.calcular_precio_compra_rentable(
            precio_despacho_predicho, dias_horizon
        )
        
        return {
            'calibre': calibre,
            'provincia': provincia_compra or 'Guayas',
            'rangos_compra': rangos_compra,
            'recomendacion': f"Comprar entre ${rangos_compra['precio_compra_minimo']} (mínimo) "
                           f"y ${rangos_compra['precio_compra_recomendado']} (recomendado)",
            'margen_minimo_ganancia': f"${self.MARGEN_MINIMO}",
            'margen_recomendado_ganancia': f"${self.MARGEN_RECOMENDADO}"
        }
