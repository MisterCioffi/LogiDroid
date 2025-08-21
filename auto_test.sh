#!/bin/bash
#
# LogiDroid Auto Test - Esegue 50 iterazioni automatiche di test
#

# Colori
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Controlla prerequisiti
check_prerequisites() {
    # Verifica Ollama
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_error "Ollama non disponibile!"
        echo "Avvialo con: brew services start ollama"
        exit 1
    fi
    
    # Verifica dispositivo Android
    if ! adb devices | grep -q "device$"; then
        print_error "Dispositivo Android non connesso!"
        echo "Connetti il dispositivo e abilita Debug USB"
        exit 1
    fi
}

# Singola iterazione di test
run_test_iteration() {
    local iteration=$1
    
    print_step "🔄 Iterazione $iteration/50"
    
    # 1. Cattura schermata corrente
    local timestamp=$(date +%s)
    local xml_file="test/xml/current_${timestamp}.xml"
    local json_file="test/json/result_current_${timestamp}.json"
    local screenshot_file="test/screenshots/screen_${timestamp}.png"
    
    # Crea cartelle se non esistono
    mkdir -p test/xml test/json test/screenshots test/prompts
    
    # Cattura screenshot
    adb exec-out screencap -p > "$screenshot_file" 2>/dev/null
    
    # Cattura UI XML
    adb shell uiautomator dump /sdcard/ui_dump.xml 2>/dev/null
    adb pull /sdcard/ui_dump.xml "$xml_file" 2>/dev/null
    
    if [ ! -f "$xml_file" ]; then
        print_error "Errore nella cattura dell'interfaccia (iterazione $iteration)"
        return 1
    fi
    
    # 2. Converti in JSON
    python3 xml_to_json.py "$xml_file" "$json_file" 2>/dev/null
    
    if [ ! -f "$json_file" ]; then
        print_error "Errore nella conversione JSON (iterazione $iteration)"
        return 1
    fi
    
    # 3. Esegui azione tramite LLM
    python3 llm_api.py "$json_file"
    local llm_result=$?
    
    if [ $llm_result -ne 0 ]; then
        print_error "Errore LLM (iterazione $iteration)"
        return 1
    fi
    
    print_success "Iterazione $iteration completata"
    
    # Piccola pausa tra le iterazioni
    sleep 2
    
    return 0
}

# Main
main() {
    echo -e "${YELLOW}🤖 LogiDroid Auto Test - 50 Iterazioni${NC}"
    echo "================================================="
    
    # Verifica prerequisiti
    print_step "🔍 Verificando prerequisiti..."
    check_prerequisites
    print_success "Prerequisiti OK"
    
    # Pulisci cronologia precedente per nuovo test (solo all'inizio)
    if [ ! -f "test/prompts/.test_in_progress" ]; then
        rm -f test/prompts/action_history.json
        rm -f test/prompts/last_action.txt
        rm -f test/prompts/test_strategy.txt
        touch test/prompts/.test_in_progress
        print_info "Cronologia pulita per nuovo test"
    fi
    
    # Esegui 50 iterazioni
    local successes=0
    local failures=0
    
    for i in $(seq 1 50); do
        if run_test_iteration $i; then
            ((successes++))
        else
            ((failures++))
            # Se ci sono troppi errori consecutivi, fermati
            if [ $failures -gt 5 ]; then
                print_error "Troppi errori consecutivi, test interrotto"
                break
            fi
        fi
        
        # Mostra progresso ogni 10 iterazioni
        if [ $((i % 10)) -eq 0 ]; then
            print_info "Progresso: $i/50 - Successi: $successes, Fallimenti: $failures"
        fi
    done
    
    # Risultati finali
    echo ""
    echo "================================================="
    echo -e "${GREEN}🎯 TEST COMPLETATO${NC}"
    echo -e "Iterazioni riuscite: ${GREEN}$successes${NC}"
    echo -e "Iterazioni fallite: ${RED}$failures${NC}"
    echo -e "Tasso di successo: $(( successes * 100 / (successes + failures) ))%"
    echo ""
    echo "📁 File generati in:"
    echo "  Screenshots: test/screenshots/"
    echo "  XML: test/xml/"
    echo "  JSON: test/json/"
    echo "  Cronologia: test/prompts/"
    
    # Rimuovi marker di test in corso
    rm -f test/prompts/.test_in_progress
}

# Esegui se chiamato direttamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
