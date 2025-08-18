#!/bin/bash
#
# LogiDroid Test Cleanup - Pulizia file di test
# Rimuove tutti i file generati durante il testing
#

# Colori
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Menu di opzioni
if [ $# -eq 0 ]; then
    echo -e "${BLUE}LogiDroid Test Cleanup${NC}"
    echo ""
    echo "Opzioni disponibili:"
    echo "  all        - Rimuove tutta la cartella test/"
    echo "  json       - Rimuove solo i file JSON"
    echo "  xml        - Rimuove solo i file XML"
    echo "  screenshots - Rimuove solo gli screenshot"
    echo "  prompts    - Rimuove solo la cronologia azioni"
    echo "  legacy     - Rimuove file nelle cartelle legacy"
    echo ""
    echo "Uso: $0 <opzione>"
    exit 1
fi

case "$1" in
    "all")
        print_info "🧹 Rimuovendo tutta la cartella test/..."
        if [ -d "test" ]; then
            rm -rf test/
            print_success "Cartella test/ rimossa completamente"
        else
            print_warning "Cartella test/ non esiste"
        fi
        ;;
    "json")
        print_info "🧹 Rimuovendo file JSON..."
        if [ -d "test/json" ]; then
            rm -f test/json/*
            print_success "File JSON rimossi"
        else
            print_warning "Cartella test/json/ non esiste"
        fi
        ;;
    "xml")
        print_info "🧹 Rimuovendo file XML..."
        if [ -d "test/xml" ]; then
            rm -f test/xml/*
            print_success "File XML rimossi"
        else
            print_warning "Cartella test/xml/ non esiste"
        fi
        ;;
    "screenshots")
        print_info "🧹 Rimuovendo screenshot..."
        if [ -d "test/screenshots" ]; then
            rm -f test/screenshots/*
            print_success "Screenshot rimossi"
        else
            print_warning "Cartella test/screenshots/ non esiste"
        fi
        ;;
    "prompts")
        print_info "🧹 Rimuovendo cronologia azioni..."
        if [ -d "test/prompts" ]; then
            rm -f test/prompts/*
            print_success "Cronologia azioni rimossa"
        else
            print_warning "Cartella test/prompts/ non esiste"
        fi
        ;;
    "legacy")
        print_info "🧹 Rimuovendo file nelle cartelle legacy..."
        
        # Rimuovi file nelle cartelle legacy
        if [ -d "screenshots" ]; then
            rm -f screenshots/screen_*.png
            print_success "Screenshot legacy rimossi"
        fi
        
        if [ -d "ui_captures" ]; then
            rm -f ui_captures/current_*.xml
            print_success "File XML legacy rimossi"
        fi
        
        if [ -d "prompts" ]; then
            rm -f prompts/action_history.json prompts/last_action.txt
            print_success "Cronologia legacy rimossa"
        fi
        
        # Rimuovi file JSON nella root
        rm -f result_current_*.json
        print_success "File JSON legacy rimossi"
        ;;
    *)
        print_error "Opzione non riconosciuta: $1"
        echo "Usa: $0 per vedere le opzioni disponibili"
        exit 1
        ;;
esac

echo ""
print_info "💡 Per ricreare la struttura: mkdir -p test/{json,xml,screenshots,prompts}"
