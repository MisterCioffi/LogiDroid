#!/bin/bash
#
# LogiDroid LLM Integration
# Sistema completo: UI Capture → JSON → Prompt → LLM → Automation
#

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}LogiDroid - Automazione Android${NC}"
}

print_info() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_step() {
    echo -e "${PURPLE}$1${NC}"
}

# Verifica prerequisiti
check_requirements() {
    if ! command -v adb &> /dev/null; then
        print_error "ADB non trovato. Installa Android SDK"
        return 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 non trovato"
        return 1
    fi
    
    if [ ! -f "xml_to_json.py" ]; then
        print_error "File xml_to_json.py mancante"
        return 1
    fi
    
    return 0
}

# Cattura UI corrente
capture_ui() {
    local output_name=${1:-"current_ui"}
    
    print_step "Catturando UI corrente..."
    
    # Verifica connessione ADB
    if ! adb devices | grep -q "device$"; then
        print_error "Nessun dispositivo Android connesso"
        return 1
    fi
    
    # Crea directory se non esiste
    mkdir -p ui_captures
    
    # Cattura UI dump
    adb shell uiautomator dump /sdcard/ui_dump.xml
    if [ $? -ne 0 ]; then
        print_error "Errore nella cattura UI"
        return 1
    fi
    
    # Scarica il file
    adb pull /sdcard/ui_dump.xml "ui_captures/${output_name}.xml"
    if [ $? -ne 0 ]; then
        print_error "Errore nel download UI dump"
        return 1
    fi
    
    # Pulisci il dispositivo
    adb shell rm /sdcard/ui_dump.xml
    
    print_success "UI catturata: ui_captures/${output_name}.xml"
    return 0
}

# Converte XML in JSON
convert_to_json() {
    local xml_file=$1
    local json_file=${2:-"${xml_file%.*}.json"}
    
    print_step "Convertendo XML in JSON..."
    
    if [ ! -f "$xml_file" ]; then
        print_error "File XML non trovato: $xml_file"
        return 1
    fi
    
    python3 xml_to_json.py "$xml_file" "$json_file"
    if [ $? -ne 0 ]; then
        print_error "Errore nella conversione XML→JSON"
        return 1
    fi
    
    print_success "JSON creato: $json_file"
    return 0
}

# Genera prompt per LLM
generate_prompt() {
    local json_file=$1
    local output_file=${2:-""}
    
    print_step "Generando prompt semplice..."
    
    if [ ! -f "$json_file" ]; then
        print_error "File JSON non trovato: $json_file"
        return 1
    fi
    
    local prompt_content
    prompt_content=$(python3 prompt_generator.py "$json_file")
    
    if [ $? -ne 0 ]; then
        print_error "Errore nella generazione prompt"
        return 1
    fi
    
    if [ -n "$output_file" ]; then
        echo "$prompt_content" > "$output_file"
        print_success "Prompt salvato: $output_file"
    else
        echo "$prompt_content"
    fi
    
    return 0
}

# Workflow completo
full_workflow() {
    local session_name=${1:-"session_$(date +%Y%m%d_%H%M%S)"}
    
    print_header
    echo "Sessione: $session_name"
    echo ""
    
    # Step 1: Cattura UI
    if ! capture_ui "$session_name"; then
        return 1
    fi
    
    # Step 2: Converti in JSON
    if ! convert_to_json "ui_captures/${session_name}.xml" "${session_name}.json"; then
        return 1
    fi
    
    # Step 3: Genera prompt semplice
    mkdir -p prompts
    if ! generate_prompt "${session_name}.json" "prompts/${session_name}_prompt.txt"; then
        return 1
    fi
    
    # Step 4: Mostra riassunto
    print_success "Completato!"
    echo ""
    echo "File generati:"
    echo "  XML: ui_captures/${session_name}.xml"
    echo "  JSON: ${session_name}.json"
    echo "  Prompt: prompts/${session_name}_prompt.txt"
    echo ""
    echo "Prossimi passi:"
    echo "1. cat prompts/${session_name}_prompt.txt"
    echo "2. ./adb_automator.sh ${session_name}.json [azione]"
}

# Modalità interattiva
interactive_mode() {
    print_header
    echo "Modalità interattiva"
    echo ""
    
    while true; do
        echo -e "${YELLOW}Opzioni:${NC}"
        echo "1. Cattura UI"
        echo "2. XML → JSON"
        echo "3. JSON → Prompt"
        echo "4. Workflow completo"
        echo "5. Esci"
        echo ""
        read -p "Scegli (1-5): " choice
        
        case $choice in
            1)
                read -p "Nome file (senza estensione): " name
                capture_ui "$name"
                ;;
            2)
                read -p "File XML: " xml_file
                read -p "File JSON output: " json_file
                convert_to_json "$xml_file" "$json_file"
                ;;
            3)
                read -p "File JSON: " json_file
                generate_prompt "$json_file"
                ;;
            4)
                full_workflow
                ;;
            5)
                print_info "Uscita..."
                break
                ;;
            *)
                print_error "Scelta non valida"
                ;;
        esac
        echo ""
    done
}

# Mostra esempi
show_examples() {
    echo -e "${BLUE}ESEMPI:${NC}"
    echo ""
    echo "./llm_integration.sh workflow"
    echo "./llm_integration.sh capture screen1"
    echo "./llm_integration.sh convert ui.xml data.json"
    echo "./llm_integration.sh prompt data.json"
    echo "./llm_integration.sh interactive"
}

# Main
case ${1:-""} in
    "workflow")
        if ! check_requirements; then
            exit 1
        fi
        full_workflow "$2"
        ;;
    "capture")
        if ! check_requirements; then
            exit 1
        fi
        capture_ui "$2"
        ;;
    "convert")
        if [ -z "$2" ]; then
            print_error "Specificare file XML"
            exit 1
        fi
        convert_to_json "$2" "$3"
        ;;
    "prompt")
        if [ -z "$2" ]; then
            print_error "Specificare file JSON"
            exit 1
        fi
        generate_prompt "$2" "$3"
        ;;
    "interactive")
        if ! check_requirements; then
            exit 1
        fi
        interactive_mode
        ;;
    "examples"|"help"|"--help"|"-h")
        print_header
        show_examples
        ;;
    *)
        print_header
        echo "Sistema semplificato di automazione Android"
        echo ""
        echo "Uso: $0 <comando> [parametri]"
        echo ""
        echo "Comandi disponibili:"
        echo "  workflow [name]         - Workflow completo (capture→convert→prompt)"
        echo "  capture [name]          - Solo cattura UI"
        echo "  convert <xml> [json]    - Solo conversione XML→JSON"  
        echo "  prompt <json> [output]  - Solo generazione prompt"
        echo "  interactive             - Modalità interattiva"
        echo "  examples               - Mostra esempi d'uso"
        echo ""
        echo "Per maggiori dettagli: $0 examples"
        ;;
esac
