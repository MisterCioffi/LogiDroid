#!/bin/bash

echo "=== LogiDroid: Configurazione ambiente di testing ==="

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi colorati
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

# Flag per errori
HAS_ERRORS=false

echo "Verifica dei prerequisiti minimi..."
echo "================================="

# Controlla ADB (ESSENZIALE)
print_info "Verifica ADB..."
if ! command -v adb &> /dev/null; then
    print_error "ADB non trovato nel PATH"
    print_info "Scarica Android SDK Platform Tools da:"
    print_info "https://developer.android.com/studio/releases/platform-tools"
    print_info "Estrai e aggiungi platform-tools/ al PATH"
    HAS_ERRORS=true
else
    ADB_VERSION=$(adb version | head -n1)
    print_success "ADB trovato: $(which adb)"
    print_info "Versione: $ADB_VERSION"
fi

# Controlla UIAutomator (ESSENZIALE per analisi UI)
print_info "Verifica UIAutomator..."
UIAUTOMATOR_FOUND=false

# Verifica se uiautomator è disponibile via ADB sui dispositivi connessi
if command -v adb &> /dev/null; then
    DEVICES=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l | tr -d ' ')
    if [ "$DEVICES" -gt 0 ]; then
        # Test diretto con dump UI
        FIRST_DEVICE=$(adb devices | grep "device$" | head -n1 | cut -f1)
        if adb -s $FIRST_DEVICE shell uiautomator dump /sdcard/logidroid_test.xml &> /dev/null; then
            print_success "UIAutomator funziona correttamente sui dispositivi connessi"
            # Pulisci file di test
            adb -s $FIRST_DEVICE shell rm -f /sdcard/logidroid_test.xml &> /dev/null
            UIAUTOMATOR_FOUND=true
        fi
    fi
fi

if [ "$UIAUTOMATOR_FOUND" = false ]; then
    print_error "UIAutomator non disponibile"
    print_info "Soluzioni:"
    print_info "• Connetti un dispositivo Android con API 16+ (Android 4.1+)"
    print_info "• Abilita 'Opzioni sviluppatore' e 'Debug USB'"
    print_info "• Verifica che il dispositivo sia autorizzato per ADB"
    HAS_ERRORS=true
fi

# Verifica connessione dispositivi (IMPORTANTE per testing)
print_info "Verifica dispositivi connessi..."
if command -v adb &> /dev/null; then
    # Avvia server ADB se necessario
    adb start-server &> /dev/null
    
    DEVICES=$(adb devices | grep -v "List of devices" | grep -v "^$" | wc -l | tr -d ' ')
    if [ "$DEVICES" -eq 0 ]; then
        print_warning "Nessun dispositivo Android connesso"
        print_info "Per il testing avrai bisogno di:"
        print_info "• Un dispositivo fisico con USB debugging abilitato"
        print_info "• OPPURE un emulatore Android (da Android Studio o Genymotion)"
    else
        print_success "$DEVICES dispositivo/i connesso/i"
        echo "Dispositivi rilevati:"
        adb devices | grep -v "List of devices" | grep -v "^$" | while read line; do
            DEVICE_ID=$(echo $line | cut -d' ' -f1)
            DEVICE_STATUS=$(echo $line | cut -d' ' -f2)
            # Ottieni info device se possibile
            if [ "$DEVICE_STATUS" = "device" ]; then
                DEVICE_MODEL=$(adb -s $DEVICE_ID shell getprop ro.product.model 2>/dev/null | tr -d '\r')
                ANDROID_VERSION=$(adb -s $DEVICE_ID shell getprop ro.build.version.release 2>/dev/null | tr -d '\r')
                API_LEVEL=$(adb -s $DEVICE_ID shell getprop ro.build.version.sdk 2>/dev/null | tr -d '\r')
                echo "  • $DEVICE_ID ($DEVICE_STATUS) - $DEVICE_MODEL (Android $ANDROID_VERSION, API $API_LEVEL)"
                
                # Test UIAutomator su questo dispositivo
                if [ "$API_LEVEL" -ge 16 ] 2>/dev/null; then
                    print_info "    ✓ UIAutomator supportato (API $API_LEVEL >= 16)"
                else
                    print_warning "    ⚠ UIAutomator potrebbe non funzionare (API $API_LEVEL < 16)"
                fi
            else
                echo "  • $DEVICE_ID ($DEVICE_STATUS)"
            fi
        done
        
        # Test pratico di UIAutomator
        print_info "Test funzionalità UIAutomator..."
        FIRST_DEVICE=$(adb devices | grep "device$" | head -n1 | cut -f1)
        if [ -n "$FIRST_DEVICE" ]; then
            print_info "Test dump UI su dispositivo $FIRST_DEVICE..."
            if adb -s $FIRST_DEVICE shell uiautomator dump /sdcard/test_ui.xml &> /dev/null; then
                print_success "UIAutomator dump funziona correttamente"
                # Pulisci file di test
                adb -s $FIRST_DEVICE shell rm -f /sdcard/test_ui.xml &> /dev/null
            else
                print_warning "UIAutomator dump non riuscito - verifica permessi o API level"
            fi
        fi
    fi
fi

# Controlli opzionali (NON bloccanti)
print_info "Controlli opzionali..."

# Java (utile ma non essenziale)
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n1)
    print_success "Java disponibile: $JAVA_VERSION"
else
    print_warning "Java non trovato (opzionale per la maggior parte dei test)"
fi

# Python (se vuoi scripting avanzato)
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python3 disponibile: $PYTHON_VERSION"
else
    print_warning "Python3 non trovato (opzionale per scripting avanzato)"
fi

echo "================================="

if [ "$HAS_ERRORS" = true ]; then
    print_error "Configurazione incompleta. Risolvi i problemi sopra indicati."
    print_info ""
    print_info "GUIDA RAPIDA per macOS:"
    print_info "1. Scarica platform-tools: https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
    print_info "2. Estrai e aggiungi al PATH:"
    print_info "   unzip platform-tools-latest-darwin.zip"
    print_info "   echo 'export PATH=\$PATH:$(pwd)/platform-tools' >> ~/.zshrc"
    print_info "   source ~/.zshrc"
    print_info "3. Connetti dispositivo Android con USB debugging abilitato"
    print_info ""
    print_info "UIAutomator è integrato nei dispositivi Android moderni (API 16+)"
    exit 1
else
    print_success "Ambiente configurato correttamente per testing ADB + UIAutomator!"
    print_info "LogiDroid è pronto per il testing Android con analisi UI"
    print_info ""
    print_info "Funzionalità disponibili:"
    print_info "• ADB per gestione dispositivi e app"
    print_info "• UIAutomator per analisi interfaccia utente"
    print_info "• Estrazione layout XML delle schermate"
    print_info ""
    print_info "Prossimi passi:"
    print_info "• Abilita 'USB Debugging' sui dispositivi di test"
    print_info "• Testa: adb shell uiautomator dump /sdcard/ui.xml"
    print_info "• Considera di installare app comuni per i test"
fi

echo "=== Configurazione completata ==="
