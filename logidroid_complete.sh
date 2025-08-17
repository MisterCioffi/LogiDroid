#!/bin/bash
#
# LogiDroid Complete - Workflow completo con LLM locale
# Cattura schermata → Genera JSON → Esegue azione tramite LLM
#

# Colori
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Controlla se Ollama è disponibile
check_ollama() {
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "❌ Ollama non disponibile!"
        echo "Avvialo con: brew services start ollama"
        exit 1
    fi
}

# Uso
if [ $# -gt 0 ]; then
    echo -e "${YELLOW}LogiDroid Complete - Automazione Android con LLM locale${NC}"
    echo ""
    echo "Uso: $0"
    echo ""
    echo "Lo script catturerà automaticamente l'interfaccia corrente e l'LLM deciderà cosa fare."
    exit 1
fi

# Verifica prerequisiti
print_step "🔍 Verificando prerequisiti..."
check_ollama
print_success "Ollama disponibile"

if ! adb devices | grep -q "device$"; then
    echo "❌ Dispositivo Android non connesso!"
    echo "Connetti il dispositivo e abilita Debug USB"
    exit 1
fi
print_success "Dispositivo Android connesso"

# 1. Cattura schermata corrente
print_step "📱 Catturando interfaccia corrente..."
TIMESTAMP=$(date +%s)
XML_FILE="ui_captures/current_${TIMESTAMP}.xml"
JSON_FILE="result_current_${TIMESTAMP}.json"
SCREENSHOT_FILE="screenshots/screen_${TIMESTAMP}.png"

# Crea cartelle se non esistono
mkdir -p ui_captures
mkdir -p screenshots

# Cattura screenshot
print_step "📸 Catturando screenshot..."
adb exec-out screencap -p > "$SCREENSHOT_FILE"

if [ ! -f "$SCREENSHOT_FILE" ]; then
    echo "❌ Errore nella cattura dello screenshot"
    exit 1
fi
print_success "Screenshot salvato: $SCREENSHOT_FILE"

# Cattura UI XML
adb shell uiautomator dump /sdcard/ui_dump.xml
adb pull /sdcard/ui_dump.xml "$XML_FILE"

if [ ! -f "$XML_FILE" ]; then
    echo "❌ Errore nella cattura dell'interfaccia"
    exit 1
fi
print_success "Interfaccia catturata: $XML_FILE"

# 2. Converti in JSON
print_step "🔄 Convertendo in JSON..."
python3 xml_to_json.py "$XML_FILE" "$JSON_FILE"

if [ ! -f "$JSON_FILE" ]; then
    echo "❌ Errore nella conversione JSON"
    exit 1
fi
print_success "JSON generato: $JSON_FILE"

# 3. Analisi tramite LLM
print_step "🤖 Analizzando interfaccia con LLM locale..."

python3 llm_local.py "$JSON_FILE"

# 4. Cleanup opzionale
echo ""
echo -e "${BLUE}📁 File generati:${NC}"
echo "  Screenshot: $SCREENSHOT_FILE"
echo "  XML: $XML_FILE"
echo "  JSON: $JSON_FILE"
echo ""
echo -e "${YELLOW}💡 Per rivedere l'interfaccia: python3 prompt_generator.py $JSON_FILE${NC}"
