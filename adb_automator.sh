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
    
    # Pausa più lunga per assicurarsi che il campo sia pronto
    sleep 1
    
    # Inserimento diretto del testo
    adb shell input text "$text"
    
    if [ $? -eq 0 ]; then
        print_success "Testo inserito"
        sleep 1  # Pausa dopo inserimento
    else
        print_error "Errore durante inserimento testo"
        # Metodo backup: inserimento carattere per carattere solo in caso di errore
        print_info "Tentativo con metodo alternativo carattere per carattere..."
        for (( i=0; i<${#text}; i++ )); do
            char="${text:$i:1}"
            if [ "$char" = " " ]; then
                adb shell input keyevent KEYCODE_SPACE
            else
                adb shell input text "$char"
            fi
            sleep 0.15  # Pausa più lunga tra caratteri
        done
        print_success "Testo inserito (metodo alternativo)"
        sleep 1
    fi
    
    # Verifica finale che il testo sia stato inserito
    sleep 0.5
}

adb_clear_field() {
    local x=$1
    local y=$2
    local description=${3:-""}
    
    print_info "Cancellando campo ($x, $y) ${description}"
    
    # Strategia di focus intensiva per assicurare che il campo sia attivo
    # Click multipli con pause per garantire focus
    adb shell input tap $x $y
    sleep 0.4
    adb shell input tap $x $y
    sleep 0.4
    adb shell input tap $x $y
    sleep 0.6
    
    # Assicurati che la tastiera sia nascosta prima di procedere
    adb shell input keyevent KEYCODE_ESCAPE
    sleep 0.2
    
    # Riattiva il campo
    adb shell input tap $x $y
    sleep 0.8
    
    # Metodo 1: Seleziona tutto e cancella
    adb shell input keyevent KEYCODE_CTRL_A
    sleep 0.3
    adb shell input keyevent KEYCODE_DEL
    sleep 0.3
    
    # Metodo 2: Vai alla fine e cancella carattere per carattere (più affidabile)
    adb shell input keyevent KEYCODE_MOVE_END
    sleep 0.2
    
    # Cancella fino a 50 caratteri (dovrebbe essere sufficiente)
    for i in {1..50}; do
        adb shell input keyevent KEYCODE_DEL
        sleep 0.02  # Pausa molto breve tra le cancellazioni
    done
    
    # Metodo 3: Alternativo con BACKSPACE
    for i in {1..20}; do
        adb shell input keyevent KEYCODE_BACKSPACE
        sleep 0.02
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

# Normalizza target ricevuto (rimuovi eventuali parentesi quadre e spazi, case-insensitive)
target = '$target'
target = target.strip()
if target.startswith('[') and target.endswith(']'):
    target = target[1:-1]
target_norm = target.lower()

for elem in data['elements']:
    if not elem.get('editable', False):
        text = (elem.get('text') or '').lower()
        content_desc = (elem.get('content_desc') or '').lower()
        resource_id = (elem.get('resource_id') or '').lower()
        resource_last = resource_id.split(':')[-1] if resource_id else ''

        # Confronti: testo, content_desc, resource_id completo o solo l'ultima parte
        if (target_norm in text) or (target_norm in content_desc) or (target_norm in resource_id) or (target_norm in resource_last) or (resource_last and resource_last in target_norm):
            bounds = elem.get('bounds', {})
            x = bounds.get('x', 0)
            y = bounds.get('y', 0)
            print(f\"{x} {y}\")
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

# Prima cerca il campo corretto per Nome: deve avere il resource_id specifico
for elem in data['elements']:
    if elem['editable'] and '$target' in elem.get('label', ''):
        resource_id = elem.get('resource_id', '')
        bounds = elem.get('bounds', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        # Per il campo Nome, cerca quello con nameEdit (campo principale)
        if '$target' == 'Nome' and 'nameEdit' in resource_id and width > 50 and height > 20:
            center_x = bounds['x'] + width // 2
            center_y = bounds['y'] + height // 2
            print(f\"{center_x} {center_y}\")
            sys.exit(0)

# Per altri campi o come fallback, usa la logica standard con dimensioni grandi
for elem in data['elements']:
    if elem['editable'] and '$target' in elem.get('label', ''):
        bounds = elem.get('bounds', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        # Priorità ai campi con dimensioni significative (almeno 50x20)
        if width > 50 and height > 20:  # Campo con dimensioni ragionevoli
            center_x = bounds['x'] + width // 2
            center_y = bounds['y'] + height // 2
            print(f\"{center_x} {center_y}\")
            sys.exit(0)

# ULTIMA OPZIONE: Se non trova campi grandi, prova anche i piccoli (per E-mail, etc.)
for elem in data['elements']:
    if elem['editable'] and '$target' in elem.get('label', ''):
        bounds = elem.get('bounds', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        center_x = bounds['x'] + width // 2
        center_y = bounds['y'] + height // 2
        print(f\"{center_x} {center_y}\")
        sys.exit(0)
")
            if [ -n "$coords" ]; then
                local x=$(echo $coords | cut -d' ' -f1)
                local y=$(echo $coords | cut -d' ' -f2)
                
                print_info "Focusing campo ($x, $y) - campo '$target'"
                
                # Click semplice per dare focus
                adb shell input tap $x $y
                sleep 1
                
                # Cancellazione robusta - seleziona tutto e poi cancella carattere per carattere
                adb shell input keyevent KEYCODE_CTRL_A
                sleep 0.3
                adb shell input keyevent KEYCODE_DEL
                sleep 0.3
                
                # Vai alla fine e cancella carattere per carattere per sicurezza
                adb shell input keyevent KEYCODE_MOVE_END
                sleep 0.2
                
                # Cancella fino a 30 caratteri per essere sicuri
                for i in {1..30}; do
                    adb shell input keyevent KEYCODE_DEL
                    sleep 0.01
                done
                
                # Cancella anche con BACKSPACE per sicurezza
                for i in {1..15}; do
                    adb shell input keyevent KEYCODE_BACKSPACE
                    sleep 0.01
                done
                
                # Inserimento testo semplice
                adb shell input text "$value"
                sleep 0.5
                
                print_success "Testo inserito"
            else
                print_warning "Campo editabile '$target' non trovato o troppo piccolo"
                print_info "Tentativo di attivare il campo cliccando sul bottone '$target'..."
                
                # Cerca un bottone con lo stesso nome per attivare il campo
                local button_coords=$(python3 -c "
import json, sys
with open('$json_file') as f:
    data = json.load(f)

# Cerca un bottone clickable con il nome del target
for elem in data['elements']:
    if elem['clickable'] and not elem.get('editable', False):
        # Controlla text, content_desc, o label
    button_text = (elem.get('text') or '') or (elem.get('content_desc') or '') or (elem.get('label') or '')
    bt = button_text.lower()
    tgt = '$target'.lower()
    resource_last = (elem.get('resource_id') or '').split(':')[-1].lower()
    if (tgt in bt) or (tgt in resource_last) or (resource_last in tgt):
            bounds = elem.get('bounds', {})
            width = bounds.get('width', 0)
            height = bounds.get('height', 0)
            if width > 20 and height > 20:  # Bottone con dimensioni ragionevoli
                center_x = bounds['x'] + width // 2
                center_y = bounds['y'] + height // 2
                print(f\"{center_x} {center_y}\")
                sys.exit(0)
")
                
                if [ -n "$button_coords" ]; then
                    local btn_x=$(echo $button_coords | cut -d' ' -f1)
                    local btn_y=$(echo $button_coords | cut -d' ' -f2)
                    
                    print_info "Cliccando bottone '$target' su ($btn_x, $btn_y)..."
                    adb shell input tap $btn_x $btn_y
                    sleep 2  # Attendi che appaia il campo
                    
                    print_info "Catturando nuova schermata dopo attivazione..."
                    
                    # Cattura nuova schermata per riflettere i cambiamenti UI
                    local timestamp=$(date +%s)
                    local new_xml="test/xml/current_post_click_${timestamp}.xml"
                    local new_json="test/json/result_post_click_${timestamp}.json"
                    
                    adb shell uiautomator dump /sdcard/ui_dump_new.xml
                    adb pull /sdcard/ui_dump_new.xml "$new_xml"
                    python3 xml_to_json.py "$new_xml" "$new_json"
                    
                    print_info "Ritentando ricerca campo editabile con nuova schermata..."
                    
                    # Riprova a cercare il campo editabile con il nuovo JSON
                    local retry_coords=$(python3 -c "
import json, sys
with open('$new_json') as f:
    data = json.load(f)

# Logica speciale per il telefono: dopo click, trova il campo che si è appena attivato
if '$target' == 'Telefono':
    # Strategia Samsung: il campo non si espande, ma diventa scrivibile nella stessa posizione
    # Prova a scrivere direttamente sul campo telefono originale anche se piccolo
    for elem in data['elements']:
        if elem['editable'] and 'Telefono' in elem.get('label', ''):
            bounds = elem.get('bounds', {})
            width = bounds.get('width', 0)
            height = bounds.get('height', 0)
            center_x = bounds['x'] + width // 2
            center_y = bounds['y'] + height // 2
            print(f\"{center_x} {center_y}\")
            sys.exit(0)
    
    # Se non trova il campo telefono editable, usa la posizione appena sotto il bottone
    # Spesso su Samsung il campo input appare sotto il bottone attivatore
    estimated_x = $btn_x
    estimated_y = $btn_y + 50  # 50px sotto il bottone
    print(f\"{estimated_x} {estimated_y}\")
    sys.exit(0)
else:
    # Per altri campi, usa la logica normale
    # 1. Prima cerca con il nome esatto e dimensioni grandi
    for elem in data['elements']:
        if elem['editable'] and '$target' in elem.get('label', ''):
            bounds = elem.get('bounds', {})
            width = bounds.get('width', 0)
            bounds = elem.get('bounds', {})
            width = bounds.get('width', 0)
            height = bounds.get('height', 0)
            if width > 50 and height > 20:  # Campo con dimensioni ragionevoli
                center_x = bounds['x'] + width // 2
                center_y = bounds['y'] + height // 2
                print(f\"{center_x} {center_y}\")
                sys.exit(0)

# 2. Se non trova, cerca campi editabili con dimensioni grandi (probabilmente l'ultimo aggiunto)
largest_field = None
largest_size = 0
for elem in data['elements']:
    if elem['editable']:
        bounds = elem.get('bounds', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        size = width * height
        if size > largest_size and width > 100 and height > 30:  # Campo significativo
            largest_size = size
            largest_field = elem

if largest_field:
    bounds = largest_field.get('bounds', {})
    center_x = bounds['x'] + bounds['width'] // 2
    center_y = bounds['y'] + bounds['height'] // 2
    print(f\"{center_x} {center_y}\")
    sys.exit(0)

# 3. Come ultima risorsa, cerca per resource_id correlati al telefono
for elem in data['elements']:
    if elem['editable']:
        resource_id = elem.get('resource_id', '').lower()
        if 'phone' in resource_id or 'number' in resource_id or 'edit' in resource_id:
            bounds = elem.get('bounds', {})
            width = bounds.get('width', 0)
            height = bounds.get('height', 0)
            if width > 50 and height > 20:
                center_x = bounds['x'] + width // 2
                center_y = bounds['y'] + height // 2
                print(f\"{center_x} {center_y}\")
                sys.exit(0)
")
                    
                    if [ -n "$retry_coords" ]; then
                        local retry_x=$(echo $retry_coords | cut -d' ' -f1)
                        local retry_y=$(echo $retry_coords | cut -d' ' -f2)
                        
                        print_success "Campo '$target' trovato dopo attivazione!"
                        print_info "Compilando campo su ($retry_x, $retry_y)..."
                        
                        # Compila il campo trovato
                        adb shell input tap $retry_x $retry_y
                        sleep 1
                        
                        # Cancella contenuto esistente
                        adb shell input keyevent KEYCODE_CTRL_A
                        sleep 0.3
                        adb shell input keyevent KEYCODE_DEL
                        
                        # Inserisci il nuovo testo
                        adb shell input text "$value"
                        sleep 0.5
                        
                        print_success "Campo '$target' compilato con successo!"
                    else
                        print_error "Campo '$target' ancora non trovato dopo attivazione"
                        return 1
                    fi
                else
                    print_error "Bottone '$target' non trovato per attivare il campo"
                    return 1
                fi
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
