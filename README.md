# 🧠 Maransa AI - Sistema Inteligente de Estimación de Precios

**Módulo de Inteligencia Artificial para la comercialización de camarón ecuatoriano**

---

## 🌟 Características Principales

### 🤖 **IA Avanzada con Ollama**
- **Modelo Local**: Llama 3.2:3b para análisis contextual
- **Análisis de Sentimientos**: Evaluación de noticias y factores del mercado
- **Procesamiento de Lenguaje Natural**: Comprensión del contexto ecuatoriano

### 📊 **Predicciones Multifactoriales**
- **Factores Climáticos**: Temperatura, humedad, precipitaciones
- **Tipos de Cambio**: USD vs CNY, EUR, KRW, JPY, VND
- **Precios Internacionales**: Monitoreo de mercados globales
- **Estacionalidad**: Patrones históricos de producción y demanda
- **Calidad Regional**: Análisis por provincia ecuatoriana

### 🌍 **Contexto Ecuatoriano Especializado**
- **5 Provincias Camaroneras**: Guayas, Manabí, El Oro, Santa Elena, Esmeraldas
- **7 Mercados Destino**: China, USA, Europa, Vietnam, Corea Sur, Japón, Nacional
- **Factores Logísticos**: Distancias, costos de transporte, puertos
- **Datos Reales**: Integración con BCE, CNA, OpenWeatherMap

### 🔮 **Algoritmos Predictivos**
- **Machine Learning**: Random Forest, XGBoost, LSTM
- **Ensemble Methods**: Combinación de múltiples algoritmos
- **Intervalos de Confianza**: Estimaciones con precisión estadística
- **Reentrenamiento Automático**: Mejora continua de los modelos

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│         Interfaz de Estimaciones Inteligentes          │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                BACKEND (NestJS)                         │
│         API Principal + Módulo de IA                    │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│             MICROSERVICIO IA (Python)                  │
│    FastAPI + ML Models + Ollama Integration            │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                  FUENTES DE DATOS                      │
│  BCE | CNA | OpenWeatherMap | ExchangeRate | Ollama    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Instalación y Configuración

### 📋 Prerrequisitos

1. **Node.js 18+** y **npm**
2. **Python 3.11+** y **pip**
3. **PostgreSQL 13+**
4. **Ollama** (para IA local)
5. **Docker** (opcional, recomendado)

### 🔧 Instalación Paso a Paso

#### 1️⃣ Configurar la Base de Datos

```bash
# Aplicar nueva migración con tablas de IA
cd maransa-back
npm run prisma:migrate:dev
npm run prisma:generate
```

#### 2️⃣ Instalar el Microservicio de IA

```bash
# Navegar al directorio del microservicio
cd maransa-ai-service

# Ejecutar script de instalación automática
chmod +x install.sh
./install.sh

# O instalación manual:
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3️⃣ Configurar Ollama

```bash
# Instalar Ollama (si no está instalado)
# Visita: https://ollama.ai

# Descargar modelo Llama 3.2
ollama pull llama3.2:3b

# Verificar instalación
ollama list
```

#### 4️⃣ Configurar Variables de Entorno

```bash
# En maransa-ai-service/
cp .env.example .env

# Editar .env con tus configuraciones:
# - DATABASE_URL (misma que el backend)
# - WEATHER_API_KEY (OpenWeatherMap)
# - EXCHANGE_API_KEY (ExchangeRate-API)
```

#### 5️⃣ Añadir Variables al Backend

```bash
# En maransa-back/.env añadir:
AI_SERVICE_URL=http://localhost:8000
```

---

## 🎮 Uso del Sistema

### 🚀 Iniciar Servicios

```bash
# Terminal 1: Backend NestJS
cd maransa-back
npm run start:dev

# Terminal 2: Microservicio IA
cd maransa-ai-service
./start_service.sh

# Terminal 3: Frontend React
cd maransa
npm run dev
```

### 📡 Endpoints de IA Disponibles

#### **Predicción de Precios**
```http
POST /ai/predict/price
{
  \"tipoProducto\": \"30/40\",
  \"mercadoDestino\": \"CHINA\",
  \"provincia\": \"GUAYAS\",
  \"fechaPrediccion\": \"2025-01-15\",
  \"incluirFactoresExternos\": true
}
```

#### **Factores de Mercado**
```http
GET /ai/market/factors
```

#### **Análisis de Sentimientos**
```http
POST /ai/analysis/sentiment
{
  \"content\": \"Las exportaciones de camarón a China aumentaron 15% este mes\"
}
```

#### **Predicción Inteligente para Pedidos**
```http
POST /ai/predict/smart-order
{
  \"tipoProducto\": \"40/50\",
  \"cantidadLibras\": 15000,
  \"proveedorId\": 1,
  \"provincia\": \"MANABI\",
  \"fechaEntrega\": \"2025-01-20\"
}
```

#### **Recomendaciones de Mercado**
```http
GET /ai/recommendations/market?tipoProducto=30/40&provincia=GUAYAS
```

#### **Estado del Servicio**
```http
GET /ai/health
```

---

## 🧪 Testing y Validación

### 🔍 Probar el Microservicio

```bash
cd maransa-ai-service

# Ejecutar todas las pruebas
./test_service.sh

# Probar endpoint específico
curl -X POST \"http://localhost:8000/predict/price\" \
  -H \"Content-Type: application/json\" \
  -d '{
    \"tipo_producto\": \"30/40\",
    \"mercado_destino\": \"CHINA\",
    \"provincia\": \"GUAYAS\",
    \"fecha_prediccion\": \"2025-01-15\"
  }'
```

### 📊 Verificar Precisión de Predicciones

```bash
# Ver logs del microservicio
tail -f maransa-ai-service/logs/maransa_ai.log

# Monitorear métricas
curl http://localhost:8000/health
```

---

## 📈 Características Avanzadas

### 🔄 **Actualización Automática de Datos**

El sistema actualiza automáticamente:
- ✅ Datos climáticos cada hora
- ✅ Tipos de cambio cada hora  
- ✅ Precios internacionales cada 6 horas
- ✅ Reentrenamiento de modelos semanalmente

### 🎯 **Algoritmos Implementados**

1. **Linear Regression**: Tendencias básicas
2. **Random Forest**: Factores no lineales
3. **XGBoost**: Optimización gradient boosting
4. **LSTM**: Patrones temporales (opcional)
5. **Ensemble**: Combinación ponderada

### 🌡️ **Factores Monitoreados**

| Factor | Fuente | Impacto | Actualización |
|--------|--------|---------|---------------|
| Temperatura | OpenWeatherMap | Alto | 1h |
| Humedad | OpenWeatherMap | Medio | 1h |
| Tipo Cambio USD/CNY | ExchangeRate-API | Alto | 1h |
| Precios Internacionales | Market Data | Muy Alto | 6h |
| Sentimiento Noticias | Ollama + Web Scraping | Medio | 24h |
| Producción Nacional | CNA/Manual | Alto | Semanal |

---

## 🔒 Seguridad y Autenticación

- 🔐 **JWT Authentication** requerida para todos los endpoints
- 👥 **Role-based Access Control**:
  - `ADMIN`: Acceso completo
  - `GERENCIA`: Predicciones y análisis
  - `COMPRAS`: Predicciones básicas
  - `LABORATORIO`: Solo factores de mercado

---

## 📊 Monitoreo y Logging

### 📝 Logs Disponibles
```bash
# Backend NestJS
tail -f maransa-back/logs/application.log

# Microservicio IA
tail -f maransa-ai-service/logs/maransa_ai.log

# Base de datos
tail -f /var/log/postgresql/postgresql.log
```

### 📈 Métricas de Rendimiento
- ⏱️ Tiempo de respuesta de predicciones
- 🎯 Precisión de modelos (RMSE, MAE)
- 📊 Uso de recursos del sistema
- 🔄 Tasa de actualización de datos

---

## 🐳 Deployment con Docker

### 🚀 Desarrollo Local

```bash
cd maransa-ai-service
docker-compose up -d
```

### 🌐 Producción

```bash
# Build imagen de producción
docker build -t maransa-ai:latest .

# Deploy con Docker Swarm
docker stack deploy -c docker-compose.prod.yml maransa-ai
```

---

## 🤝 Contribución y Desarrollo

### 🔧 Añadir Nuevos Algoritmos

1. Crear clase en `maransa-ai-service/algorithms/`
2. Implementar interface `BasePredictor`
3. Registrar en `ModelRegistry`
4. Añadir tests en `tests/algorithms/`

### 📊 Añadir Nuevas Fuentes de Datos

1. Crear colector en `maransa-ai-service/collectors/`
2. Implementar interface `DataCollector`
3. Registrar en configuración
4. Actualizar schema de base de datos si es necesario

---

## 🆘 Solución de Problemas

### ❌ Errores Comunes

**Error: \"Ollama not available\"**
```bash
# Verificar que Ollama está corriendo
ollama serve

# Verificar modelo
ollama list
ollama pull llama3.2:3b
```

**Error: \"Database connection failed\"**
```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
sudo systemctl start postgresql

# Verificar variables de entorno
echo $DATABASE_URL
```

**Error: \"Weather API rate limit\"**
```bash
# Obtener API key gratuita en:
# https://openweathermap.org/api

# Añadir a .env
WEATHER_API_KEY=tu_api_key_aqui
```

### 📞 Soporte

- 📧 **Email**: support@maransa.com
- 📖 **Documentación**: http://localhost:8000/docs
- 🐛 **Issues**: GitHub Issues
- 💬 **Discord**: Canal #maransa-ai

---

## 📄 Licencia

**Propietary Software** - Maransa © 2025

Este sistema está diseñado específicamente para la comercialización de camarón ecuatoriano y contiene algoritmos propietarios optimizados para el contexto local.

---

## 🙏 Agradecimientos

- 🇪🇨 **Cámara Nacional de Acuacultura (CNA)** - Datos del sector
- 🏛️ **Banco Central del Ecuador (BCE)** - Indicadores económicos  
- 🤖 **Ollama Team** - IA local de código abierto
- 🌦️ **OpenWeatherMap** - Datos meteorológicos
- 🏭 **Comunidad Camaronera Ecuatoriana** - Feedback y validación

---

## 🚀 Próximas Características

- [ ] **Predicción de Demanda** por mercado
- [ ] **Optimización de Rutas Logísticas** con IA
- [ ] **Análisis de Riesgo** por cliente/mercado
- [ ] **Dashboard de BI** con Power BI
- [ ] **API GraphQL** para consultas complejas
- [ ] **Mobile App** para productores
- [ ] **Blockchain** para trazabilidad
- [ ] **Computer Vision** para clasificación automática

---

*¡Transformando la comercialización de camarón ecuatoriano con Inteligencia Artificial! 🦐🧠*