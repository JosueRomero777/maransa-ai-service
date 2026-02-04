#!/bin/bash

# Script de instalación y configuración del Microservicio IA - Maransa
# Autor: Sistema de IA Maransa
# Fecha: $(date)

set -e

echo "🚀 Iniciando instalación del Microservicio de IA Maransa..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Verificar Python 3.11+
print_step "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    print_message "Python encontrado: $PYTHON_VERSION"
    if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc) -eq 1 ]]; then
        print_message "Python 3.11+ confirmado ✅"
    else
        print_error "Se requiere Python 3.11 o superior"
        exit 1
    fi
else
    print_error "Python3 no encontrado. Por favor instala Python 3.11+"
    exit 1
fi

# Crear entorno virtual
print_step "Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_message "Entorno virtual creado ✅"
else
    print_warning "Entorno virtual ya existe"
fi

# Activar entorno virtual
print_step "Activando entorno virtual..."
source venv/bin/activate
print_message "Entorno virtual activado ✅"

# Actualizar pip
print_step "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
print_step "Instalando dependencias Python..."
pip install -r requirements.txt
print_message "Dependencias instaladas ✅"

# Crear directorios necesarios
print_step "Creando estructura de directorios..."
mkdir -p models cache logs data notebooks
print_message "Directorios creados ✅"

# Configurar archivo .env
print_step "Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_message "Archivo .env creado. Por favor configura las variables necesarias."
    print_warning "Edita el archivo .env con tus claves de API reales."
else
    print_warning "Archivo .env ya existe"
fi

# Verificar Ollama
print_step "Verificando instalación de Ollama..."
if command -v ollama &> /dev/null; then
    print_message "Ollama encontrado ✅"
    
    # Verificar si el modelo está disponible
    if ollama list | grep -q "llama3.2:3b"; then
        print_message "Modelo llama3.2:3b ya está instalado ✅"
    else
        print_step "Descargando modelo llama3.2:3b..."
        print_warning "Esto puede tomar varios minutos..."
        ollama pull llama3.2:3b
        print_message "Modelo descargado ✅"
    fi
else
    print_warning "Ollama no encontrado."
    print_message "Para instalar Ollama:"
    echo "  1. Visita: https://ollama.ai"
    echo "  2. Descarga e instala para tu sistema operativo"
    echo "  3. Ejecuta: ollama pull llama3.2:3b"
fi

# Verificar Docker (opcional)
print_step "Verificando Docker..."
if command -v docker &> /dev/null; then
    print_message "Docker encontrado ✅"
    if docker --version &> /dev/null; then
        print_message "Docker funcionando correctamente"
    fi
else
    print_warning "Docker no encontrado (opcional para desarrollo)"
fi

# Crear script de inicio
print_step "Creando script de inicio..."
cat > start_service.sh << 'EOF'
#!/bin/bash

# Script para iniciar el microservicio de IA Maransa

echo "🤖 Iniciando Microservicio IA Maransa..."

# Activar entorno virtual
source venv/bin/activate

# Verificar Ollama
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Iniciando Ollama..."
    ollama serve &
    sleep 5
fi

# Iniciar el servicio
echo "Iniciando FastAPI server en http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

EOF

chmod +x start_service.sh
print_message "Script de inicio creado ✅"

# Crear script de pruebas
print_step "Creando script de pruebas..."
cat > test_service.sh << 'EOF'
#!/bin/bash

# Script para probar el microservicio de IA Maransa

echo "🧪 Ejecutando pruebas del Microservicio IA..."

source venv/bin/activate

# Ejecutar pruebas unitarias
if [ -d "tests" ]; then
    pytest tests/ -v
else
    echo "Directorio de pruebas no encontrado"
fi

# Probar endpoints básicos
echo "Probando endpoint de salud..."
curl -s http://localhost:8000/health | python -m json.tool

echo "Prueba de predicción de precios..."
curl -s -X POST "http://localhost:8000/predict/price" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_producto": "30/40",
    "mercado_destino": "CHINA",
    "provincia": "GUAYAS",
    "fecha_prediccion": "2025-01-15",
    "incluir_factores_externos": true
  }' | python -m json.tool

EOF

chmod +x test_service.sh
print_message "Script de pruebas creado ✅"

# Información final
echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo "  1. Edita el archivo .env con tus configuraciones"
echo "  2. Ejecuta: ./start_service.sh"
echo "  3. Visita: http://localhost:8000"
echo "  4. Documentación API: http://localhost:8000/docs"
echo ""
echo "🔧 Comandos útiles:"
echo "  - Iniciar servicio: ./start_service.sh"
echo "  - Probar servicio: ./test_service.sh"
echo "  - Ver logs: tail -f logs/maransa_ai.log"
echo "  - Docker: docker-compose up -d"
echo ""
echo "📊 Dashboards disponibles:"
echo "  - FastAPI Docs: http://localhost:8000/docs"
echo "  - Jupyter Lab: http://localhost:8888 (si usar Docker)"
echo ""

print_message "¡Microservicio de IA Maransa listo para usar! 🚀"