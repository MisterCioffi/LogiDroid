#!/bin/bash
#
# LogiDroid Automator - Automazione UI Android tramite ADB
# Usa i dati JSON per automatizzare click, input testo, ecc.
#

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Funzioni base ADB per automazione
adb_click() {
    local x=$1
    local y=$2
    local description=${3:-""}
    
    print_info "Click su ($x, $y) ${description}"
    adb shell input tap $x $y
    
    if [ $? -eq 0 ]; then
        print_success "Click eseguito"
        sleep 1  # Pausa per animazioni
    else
        print_error "Errore durante il click"
        return 1
    fi
}

adb_type_text() {
    local text="$1"
    local description=${2:-""}
    
    print_info "Digitando testo: '$text' ${description}"
    
    # Assicurati che ci sia focus
    sleep 0.5
    
    # Escape caratteri speciali per ADB
    local escaped_text=$(echo "$text" | sed 's/ /%s/g')
    adb shell input text "$escaped_text"
    
    if [ $? -eq 0 ]; then
        print_success "Testo inserito"
        sleep 1  # Pausa più lunga dopo inserimento
    else
        print_error "Errore durante inserimento testo"
        return 1
    fi
}

adb_clear_field() {
    local x=$1
    local y=$2
    local description=${3:-""}
    
    print_info "Cancellando campo ($x, $y) ${description}"
    
    # Click sul campo per assicurare focus
    adb shell input tap $x $y
    sleep 0.8  # Pausa più lunga per focus
    
    # Seleziona tutto e cancella (metodo 1)
    adb shell input keyevent KEYCODE_CTRL_A
    sleep 0.3
    adb shell input keyevent KEYCODE_DEL
    sleep 0.3
    
    # Metodo alternativo: cancella carattere per carattere se necessario
    adb shell input keyevent KEYCODE_MOVE_END
    sleep 0.2
    for i in {1..50}; do
        adb shell input keyevent KEYCODE_DEL
    done
    
    print_success "Campo cancellato"
}

adb_long_click() {
    local x=$1
    local y=$2
    local description=${3:-""}
    
    print_info "Long click su ($x, $y) ${description}"
    adb shell input swipe $x $y $x $y 1000  # Long press
    
    if [ $? -eq 0 ]; then
        print_success "Long click eseguito"
        sleep 1
    else
        print_error "Errore durante long click"
        return 1
    fi
}

adb_scroll() {
    local direction=$1  # up, down, left, right
    local steps=${2:-3}
    
    case $direction in
        "up")
            print_info "Scroll verso l'alto ($steps steps)"
            for i in $(seq 1 $steps); do
                adb shell input swipe 500 800 500 400 300
                sleep 0.5
            done
            ;;
        "down")
            print_info "Scroll verso il basso ($steps steps)"
            for i in $(seq 1 $steps); do
                adb shell input swipe 500 400 500 800 300
                sleep 0.5
            done
            ;;
        "left")
            print_info "Scroll verso sinistra ($steps steps)"
            for i in $(seq 1 $steps); do
                adb shell input swipe 800 500 400 500 300
                sleep 0.5
            done
            ;;
        "right")
            print_info "Scroll verso destra ($steps steps)"
            for i in $(seq 1 $steps); do
                adb shell input swipe 400 500 800 500 300
                sleep 0.5
            done
            ;;
        *)
            print_error "Direzione non valida: $direction (usa: up, down, left, right)"
            return 1
            ;;
    esac
    
    print_success "Scroll completato"
}

adb_back() {
    print_info "Premendo tasto Indietro"
    adb shell input keyevent KEYCODE_BACK
    print_success "Tasto Indietro premuto"
    sleep 1
}

adb_home() {
    print_info "Premendo tasto Home"
    adb shell input keyevent KEYCODE_HOME
    print_success "Tasto Home premuto"
    sleep 1
}

adb_menu() {
    print_info "Premendo tasto Menu"
    adb shell input keyevent KEYCODE_MENU
    print_success "Tasto Menu premuto"
    sleep 1
}

# Funzione per automatizzare usando JSON
automate_from_json() {
    local json_file=$1
    local action=$2
    local target=$3
    local value=${4:-""}
    
    if [ ! -f "$json_file" ]; then
        print_error "File JSON non trovato: $json_file"
        return 1
    fi
    
    case $action in
        "click_button")
            # Cerca pulsante per testo, content_desc o resource_id
            local coords=$(python3 -c "
import json, sys
with open('$json_file') as f:
    data = json.load(f)
for elem in data['elements']:
    if not elem['editable']:
        text = elem.get('text', '')
        content_desc = elem.get('content_desc', '')
        resource_id = elem.get('resource_id', '')
        if ('$target' in text or '$target' in content_desc or '$target' in resource_id):
            print(f\"{elem['bounds']['x']} {elem['bounds']['y']}\")
            break
")
            if [ -n "$coords" ]; then
                local x=$(echo $coords | cut -d' ' -f1)
                local y=$(echo $coords | cut -d' ' -f2)
                adb_click $x $y "pulsante '$target'"
            else
                print_error "Pulsante '$target' non trovato"
                return 1
            fi
            ;;
            
        "fill_field")
            # Cerca campo per label, priorità ai campi vuoti
            local coords=$(python3 -c "
import json, sys
with open('$json_file') as f:
    data = json.load(f)

# Prima cerca campi vuoti con il nome specificato E dimensioni ragionevoli
for elem in data['elements']:
    if elem['editable'] and '$target' in elem.get('label', ''):
        current_text = elem.get('text', '').strip()
        bounds = elem.get('bounds', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        if width > 10 and height > 10:  # Campo vuoto e dimensioni ragionevoli
            center_x = bounds['x'] + width // 2
            center_y = bounds['y'] + height // 2
            print(f\"{center_x} {center_y}\")
            sys.exit(0)

# Se non trova campi vuoti, cerca qualsiasi campo con quel nome E dimensioni ragionevoli
for elem in data['elements']:
    if elem['editable'] and '$target' in elem.get('label', ''):
        bounds = elem.get('bounds', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        if width > 10 and height > 10:  # Dimensioni ragionevoli
            center_x = bounds['x'] + width // 2
            center_y = bounds['y'] + height // 2
            print(f\"{center_x} {center_y}\")
            break
")
            if [ -n "$coords" ]; then
                local x=$(echo $coords | cut -d' ' -f1)
                local y=$(echo $coords | cut -d' ' -f2)
                
                print_info "Focusing campo ($x, $y) - campo '$target'"
                # Click esplicito per dare focus
                adb shell input tap $x $y
                sleep 1  # Pausa per focus
                
                adb_clear_field $x $y "campo '$target'"
                adb_type_text "$value" "nel campo '$target'"
            else
                print_error "Campo '$target' non trovato"
                return 1
            fi
            ;;
            
        "list_elements")
            print_info "Elementi disponibili:"
            python3 -c "
import json
with open('$json_file') as f:
    data = json.load(f)
print('PULSANTI:')
for i, elem in enumerate([e for e in data['elements'] if not e['editable']], 1):
    text = elem['text'] if elem['text'] else '(senza testo)'
    resource = elem['resource_id'].split(':')[-1] if elem['resource_id'] else 'no-id'
    print(f'  {i}. \"{text}\" - {resource}')
print('\nCAMPI DI TESTO:')
for i, elem in enumerate([e for e in data['elements'] if e['editable']], 1):
    print(f'  {i}. \"{elem[\"label\"]}\" - {elem[\"resource_id\"].split(\":\")[-1] if elem[\"resource_id\"] else \"no-id\"}')
"
            ;;
            
        *)
            print_error "Azione non valida: $action"
            echo "Azioni disponibili:"
            echo "  click_button <nome/id>     - Clicca su un pulsante"
            echo "  fill_field <nome/id> <testo> - Riempie un campo"
            echo "  list_elements              - Lista tutti gli elementi"
            return 1
            ;;
    esac
}

# Esempi di uso
show_examples() {
    echo -e "${BLUE}ESEMPI:${NC}"
    echo ""
    echo "./adb_automator.sh data.json list_elements"
    echo "./adb_automator.sh data.json click_button Salva"
    echo "./adb_automator.sh data.json fill_field Nome 'Mario Rossi'"
}

# Main
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}LogiDroid Automator${NC}"
    echo "Automazione Android via ADB"
    echo ""
    echo "Uso: $0 <json_file> <action> [target] [value]"
    echo ""
    show_examples
    exit 1
fi

# Verifica connessione ADB
if ! adb devices | grep -q "device$"; then
    print_error "Nessun dispositivo Android connesso via ADB"
    exit 1
fi

print_success "Dispositivo Android connesso"

# Esegui azione
automate_from_json "$@"
