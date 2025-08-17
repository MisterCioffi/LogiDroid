#!/bin/bash

echo "=== LogiDroid: Cattura UI delle app Android ==="

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni per output colorato
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Configurazione cartelle
UI_CAPTURES_DIR="ui_captures"
SCREENSHOTS_DIR="screenshots"

# Crea cartelle se non esistono
create_directories() {
    if [ ! -d "$UI_CAPTURES_DIR" ]; then
        mkdir -p "$UI_CAPTURES_DIR"
        print_success "Creata cartella: $UI_CAPTURES_DIR"
    fi
    
    if [ ! -d "$SCREENSHOTS_DIR" ]; then
        mkdir -p "$SCREENSHOTS_DIR"
        print_success "Creata cartella: $SCREENSHOTS_DIR"
    fi
}

# Trova il prossimo numero disponibile
get_next_number() {
    local max_num=0
    
    # Controlla i file XML
    for file in "$UI_CAPTURES_DIR"/*.xml; do
        if [ -f "$file" ]; then
            filename=$(basename "$file" .xml)
            if [[ "$filename" =~ ^[0-9]+$ ]]; then
                if [ "$filename" -gt "$max_num" ]; then
                    max_num=$filename
                fi
            fi
        fi
    done
    
    # Controlla anche gli screenshot
    for file in "$SCREENSHOTS_DIR"/*.png; do
        if [ -f "$file" ]; then
            filename=$(basename "$file" .png)
            if [[ "$filename" =~ ^[0-9]+$ ]]; then
                if [ "$filename" -gt "$max_num" ]; then
                    max_num=$filename
                fi
            fi
        fi
    done
    
    echo $((max_num + 1))
}

# Verifica dispositivo connesso
check_device() {
    if ! command -v adb &> /dev/null; then
        print_error "ADB non trovato nel PATH"
        exit 1
    fi
    
    DEVICE_COUNT=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l | tr -d ' ')
    
    if [ "$DEVICE_COUNT" -eq 0 ]; then
        print_error "Nessun dispositivo Android connesso"
        print_info "Connetti un dispositivo con USB debugging abilitato"
        exit 1
    elif [ "$DEVICE_COUNT" -gt 1 ]; then
        print_warning "Più dispositivi connessi, uso il primo disponibile"
    fi
    
    DEVICE_ID=$(adb devices | grep "device$" | head -n1 | cut -f1)
    print_success "Dispositivo selezionato: $DEVICE_ID"
}

# Cattura UI e screenshot
capture_ui() {
    local next_num=$(get_next_number)
    local xml_file="$UI_CAPTURES_DIR/${next_num}.xml"
    local png_file="$SCREENSHOTS_DIR/${next_num}.png"
    
    print_info "Cattura #$next_num in corso..."
    
    # 1. Cattura layout UI
    print_info "Estrazione layout UI..."
    if adb -s "$DEVICE_ID" shell uiautomator dump /sdcard/logidroid_ui.xml; then
        if adb -s "$DEVICE_ID" pull /sdcard/logidroid_ui.xml "$xml_file"; then
            print_success "Layout UI salvato: $xml_file"
            # Pulisci file temporaneo dal dispositivo
            adb -s "$DEVICE_ID" shell rm -f /sdcard/logidroid_ui.xml
        else
            print_error "Errore nel trasferimento del file UI"
            return 1
        fi
    else
        print_error "Errore nella cattura UI"
        return 1
    fi
    
    # 2. Cattura screenshot
    print_info "Cattura screenshot..."
    if adb -s "$DEVICE_ID" shell screencap -p /sdcard/logidroid_screenshot.png; then
        if adb -s "$DEVICE_ID" pull /sdcard/logidroid_screenshot.png "$png_file"; then
            print_success "Screenshot salvato: $png_file"
            # Pulisci file temporaneo dal dispositivo
            adb -s "$DEVICE_ID" shell rm -f /sdcard/logidroid_screenshot.png
        else
            print_error "Errore nel trasferimento dello screenshot"
        fi
    else
        print_error "Errore nella cattura screenshot"
    fi
    
    # 3. Mostra informazioni cattura
    show_capture_info "$xml_file" "$next_num"
}

# Mostra informazioni sulla cattura
show_capture_info() {
    local xml_file="$1"
    local capture_num="$2"
    
    if [ -f "$xml_file" ]; then
        # Estrai informazioni base dall'XML
        local package=$(grep -o 'package="[^"]*"' "$xml_file" | head -n1 | sed 's/package="\([^"]*\)"/\1/')
        local total_nodes=$(grep -o '<node ' "$xml_file" | wc -l | tr -d ' ')
        local clickable_nodes=$(grep -o 'clickable="true"' "$xml_file" | wc -l | tr -d ' ')
        
        echo ""
        echo "=== Informazioni Cattura #$capture_num ==="
        echo "App package: $package"
        echo "Nodi totali: $total_nodes"
        echo "Elementi cliccabili: $clickable_nodes"
        echo "File XML: $xml_file"
        echo "File PNG: $SCREENSHOTS_DIR/${capture_num}.png"
        echo "======================================"
        echo ""
    fi
}

# Lista tutte le catture
list_captures() {
    echo ""
    echo "=== Elenco Catture UI ==="
    
    local count=0
    for xml_file in "$UI_CAPTURES_DIR"/*.xml; do
        if [ -f "$xml_file" ]; then
            local num=$(basename "$xml_file" .xml)
            local png_file="$SCREENSHOTS_DIR/${num}.png"
            local size_xml=$(ls -lh "$xml_file" | awk '{print $5}')
            local size_png=""
            
            if [ -f "$png_file" ]; then
                size_png=$(ls -lh "$png_file" | awk '{print $5}')
                echo "  #$num: XML ($size_xml) + PNG ($size_png)"
            else
                echo "  #$num: XML ($size_xml) - NO screenshot"
            fi
            count=$((count + 1))
        fi
    done
    
    if [ "$count" -eq 0 ]; then
        print_warning "Nessuna cattura trovata"
    else
        print_success "$count catture totali"
    fi
    echo ""
}

# Analizza un file UI specifico
analyze_capture() {
    local capture_num="$1"
    local xml_file="$UI_CAPTURES_DIR/${capture_num}.xml"
    
    if [ ! -f "$xml_file" ]; then
        print_error "Cattura #$capture_num non trovata"
        return 1
    fi
    
    echo ""
    echo "=== Analisi Cattura #$capture_num ==="
    
    # Informazioni base
    local package=$(grep -o 'package="[^"]*"' "$xml_file" | head -n1 | sed 's/package="\([^"]*\)"/\1/')
    local rotation=$(grep -o 'rotation="[^"]*"' "$xml_file" | head -n1 | sed 's/rotation="\([^"]*\)"/\1/')
    
    echo "Package: $package"
    echo "Rotazione: ${rotation}°"
    
    # Statistiche elementi
    echo ""
    echo "Statistiche elementi:"
    echo "- Nodi totali: $(grep -o '<node ' "$xml_file" | wc -l | tr -d ' ')"
    echo "- Elementi cliccabili: $(grep -o 'clickable="true"' "$xml_file" | wc -l | tr -d ' ')"
    echo "- Elementi con testo: $(grep -o 'text="[^"]\+' "$xml_file" | wc -l | tr -d ' ')"
    echo "- Bottoni: $(grep -o 'class="[^"]*Button[^"]*"' "$xml_file" | wc -l | tr -d ' ')"
    echo "- TextView: $(grep -o 'class="[^"]*TextView[^"]*"' "$xml_file" | wc -l | tr -d ' ')"
    
    # Elementi cliccabili con testo
    echo ""
    echo "Elementi cliccabili principali:"
    grep 'clickable="true"' "$xml_file" | grep -o 'text="[^"]\+"' | sed 's/text="\([^"]*\)"/- \1/' | head -10
    
    echo "=========================="
    echo ""
}

# Funzione main
main() {
    case "$1" in
        "capture"|"")
            check_device
            create_directories
            capture_ui
            ;;
        "list")
            list_captures
            ;;
        "analyze")
            if [ -z "$2" ]; then
                print_error "Specificare il numero della cattura: $0 analyze <numero>"
                exit 1
            fi
            analyze_capture "$2"
            ;;
        "help")
            echo "Uso: $0 [comando] [opzioni]"
            echo ""
            echo "Comandi:"
            echo "  capture     Cattura UI corrente (default)"
            echo "  list        Elenca tutte le catture"
            echo "  analyze N   Analizza la cattura numero N"
            echo "  help        Mostra questo aiuto"
            echo ""
            echo "Esempi:"
            echo "  $0              # Cattura UI corrente"
            echo "  $0 capture      # Cattura UI corrente"
            echo "  $0 list         # Elenca catture"
            echo "  $0 analyze 3    # Analizza cattura #3"
            ;;
        *)
            print_error "Comando sconosciuto: $1"
            echo "Usa '$0 help' per vedere i comandi disponibili"
            exit 1
            ;;
    esac
}

# Esegui funzione main con tutti i parametri
main "$@"
