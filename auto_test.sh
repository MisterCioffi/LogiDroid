#!/bin/bash
#
# LogiDroid Auto Test - Esegue test automatici con Activity Coverage
#

# Colori
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
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

print_coverage() {
    echo -e "${CYAN}📊 $1${NC}"
}

# File per activity coverage
COVERAGE_DIR="test/coverage"
ALL_ACTIVITIES_FILE="$COVERAGE_DIR/all_activities.txt"
EXPLORED_ACTIVITIES_FILE="$COVERAGE_DIR/explored_activities.txt"
MANIFEST_FILE="$COVERAGE_DIR/AndroidManifest.xml"

# Inizializza activity coverage
init_activity_coverage() {
    print_step "📊 Inizializzando Activity Coverage..."
    
    # Crea directory
    mkdir -p "$COVERAGE_DIR"
    
    # Trova app corrente
    print_info "🔍 Rilevando app corrente..."
    local current_focus=$(adb shell dumpsys window | grep -E 'mCurrentFocus' | head -1 2>/dev/null)
    local package=$(echo "$current_focus" | grep -oE '[a-zA-Z0-9_.]+/[a-zA-Z0-9_.]+' | head -1 | cut -d'/' -f1)
    
    if [ -z "$package" ]; then
        print_error "Impossibile rilevare app corrente. Assicurati che un'app sia aperta."
        exit 1
    fi
    
    print_success "Package rilevato: $package"
    echo "$package" > "$COVERAGE_DIR/current_package.txt"
    
    # Estrai AndroidManifest.xml
    print_info "📱 Estraendo AndroidManifest.xml..."
    local apk_path=$(adb shell pm path "$package" | head -1 | cut -d':' -f2)
    
    if [ -z "$apk_path" ]; then
        print_error "Impossibile trovare APK per $package"
        exit 1
    fi
    
    # Estrai APK e manifest
    adb pull "$apk_path" "$COVERAGE_DIR/app.apk" >/dev/null 2>&1
    
    # Estrai tutte le activity usando dumpsys package (più affidabile)
    print_info "📋 Estraendo lista activity..."
    adb shell dumpsys package "$package" | grep -A 1000 "Activity Resolver Table:" | grep -B 1000 "Receiver Resolver Table:" | grep -oE "$package/[a-zA-Z0-9_.$]*" | sort | uniq > "$ALL_ACTIVITIES_FILE" 2>/dev/null
    
    # Se non trova activity, prova metodo alternativo
    if [ ! -s "$ALL_ACTIVITIES_FILE" ]; then
        print_info "Metodo alternativo per activity..."
        adb shell dumpsys package "$package" | grep -i "activity" | grep -oE "$package[a-zA-Z0-9_./]*" | grep -v "Receiver\|Service\|Provider" | sort | uniq > "$ALL_ACTIVITIES_FILE"
    fi
    
    local total_activities=$(wc -l < "$ALL_ACTIVITIES_FILE" | tr -d ' ')
    
    if [ "$total_activities" -eq 0 ]; then
        print_error "Nessuna activity trovata per $package"
        exit 1
    fi
    
    print_success "Trovate $total_activities activity totali"
    
    # Inizializza file activity esplorate
    > "$EXPLORED_ACTIVITIES_FILE"
    
    print_success "Activity Coverage inizializzato"
}

# Rileva activity corrente e aggiorna coverage
update_activity_coverage() {
    local iteration=$1
    
    # Rileva activity corrente
    local current_activity=$(adb shell dumpsys activity activities | grep -E 'mResumedActivity' | head -1 | grep -oE '[a-zA-Z0-9_.]+/[a-zA-Z0-9_.$]+' | head -1 2>/dev/null)
    
    if [ -z "$current_activity" ]; then
        # Metodo alternativo
        current_activity=$(adb shell dumpsys window | grep -E 'mCurrentFocus' | head -1 | grep -oE '[a-zA-Z0-9_.]+/[a-zA-Z0-9_.$]+' | head -1 2>/dev/null)
    fi
    
    if [ ! -z "$current_activity" ]; then
        # Controlla se è una nuova activity
        if ! grep -q "^$current_activity$" "$EXPLORED_ACTIVITIES_FILE" 2>/dev/null; then
            echo "$current_activity" >> "$EXPLORED_ACTIVITIES_FILE"
            print_success "🆕 Nuova activity: $current_activity"
        fi
        
        # Calcola e mostra coverage
        local total_activities=$(wc -l < "$ALL_ACTIVITIES_FILE" | tr -d ' ')
        local explored_activities=$(wc -l < "$EXPLORED_ACTIVITIES_FILE" | tr -d ' ')
        local coverage_percent=0
        
        if [ "$total_activities" -gt 0 ]; then
            coverage_percent=$(echo "scale=1; $explored_activities * 100 / $total_activities" | bc -l)
        fi
        
        print_coverage "Activity Coverage: $explored_activities/$total_activities (${coverage_percent}%)"
        
        # Mostra barra di progresso semplice
        local progress_bars=$((explored_activities * 20 / total_activities))
        local progress_empty=$((20 - progress_bars))
        local bar=""
        for ((i=1; i<=progress_bars; i++)); do bar+="█"; done
        for ((i=1; i<=progress_empty; i++)); do bar+="░"; done
        echo -e "${CYAN}[$bar] ${coverage_percent}%${NC}"
    fi
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
    
    # Aggiorna activity coverage PRIMA del test
    update_activity_coverage $iteration
    
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
    print_info "🤖 Chiamata LLM con rate limiting..."
    python3 llm_api.py "$json_file"
    local llm_result=$?
    
    if [ $llm_result -ne 0 ]; then
        print_error "Errore LLM (iterazione $iteration)"
        return 1
    fi
    
    # Pausa per permettere all'app di reagire
    sleep 1
    
    # Aggiorna activity coverage DOPO il test per catturare cambiamenti
    update_activity_coverage $iteration
    
    print_success "Iterazione $iteration completata"
    
    # Pausa tra le iterazioni (già coperta dal rate limiting, ma manteniamo per sicurezza UI)
    sleep 2
    
    return 0
}

# Main
main() {
    echo -e "${YELLOW}🤖 LogiDroid Auto Test con Activity Coverage${NC}"
    echo "================================================="
    
    # Verifica prerequisiti
    print_step "🔍 Verificando prerequisiti..."
    check_prerequisites
    print_success "Prerequisiti OK"
    
    # Inizializza Activity Coverage
    init_activity_coverage
    
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
    
    # Report finale Activity Coverage
    print_step "📊 Report Finale Activity Coverage"
    
    local total_activities=$(wc -l < "$ALL_ACTIVITIES_FILE" | tr -d ' ')
    local explored_activities=$(wc -l < "$EXPLORED_ACTIVITIES_FILE" | tr -d ' ')
    local coverage_percent=0
    
    if [ "$total_activities" -gt 0 ]; then
        coverage_percent=$(echo "scale=1; $explored_activities * 100 / $total_activities" | bc -l)
    fi
    
    print_coverage "🎯 ACTIVITY COVERAGE FINALE"
    print_coverage "Activity totali nell'app: $total_activities"
    print_coverage "Activity esplorate: $explored_activities"
    print_coverage "Copertura: ${coverage_percent}%"
    
    # Barra di progresso finale
    local progress_bars=$((explored_activities * 30 / total_activities))
    local progress_empty=$((30 - progress_bars))
    local bar=""
    for ((i=1; i<=progress_bars; i++)); do bar+="█"; done
    for ((i=1; i<=progress_empty; i++)); do bar+="░"; done
    echo -e "${CYAN}[${bar}] ${coverage_percent}%${NC}"
    
    # Mostra activity esplorate
    if [ -s "$EXPLORED_ACTIVITIES_FILE" ]; then
        echo ""
        print_coverage "✅ Activity Esplorate:"
        cat "$EXPLORED_ACTIVITIES_FILE" | while read -r activity; do
            echo -e "${GREEN}  ✓ $activity${NC}"
        done
    fi
    
    # Salva report JSON
    local package=$(cat "$COVERAGE_DIR/current_package.txt" 2>/dev/null)
    cat > "$COVERAGE_DIR/final_report.json" << EOF
{
  "package": "$package",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "test_iterations": $((successes + failures)),
  "successful_iterations": $successes,
  "failed_iterations": $failures,
  "success_rate": $(echo "scale=2; $successes * 100 / (successes + failures)" | bc -l),
  "total_activities": $total_activities,
  "explored_activities": $explored_activities,
  "coverage_percentage": $coverage_percent,
  "explored_activity_list": $(cat "$EXPLORED_ACTIVITIES_FILE" | jq -R . | jq -s . 2>/dev/null || echo "[]")
}
EOF
    
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
    echo "  Coverage: test/coverage/"
    echo ""
    print_success "Report coverage salvato: test/coverage/final_report.json"
    
    # Rimuovi marker di test in corso
    rm -f test/prompts/.test_in_progress
}

# Esegui se chiamato direttamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
