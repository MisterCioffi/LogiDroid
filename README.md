# 🧠 LogiDroid - Sistema Completo di Automazione Android con LLM

LogiDroid è un sistema avanzato che combina cattura UI, analisi intelligente e automazione Android tramite ADB, con integrazione LLM per automazione guidata da linguaggio naturale.

## 🌟 Caratteristiche

- **🔍 Cattura UI**: Estrae automaticamente la struttura dell'interfaccia Android
- **📊 Analisi Intelligente**: Converte XML UIAutomator in JSON strutturato con etichette contestuali
- **🤖 Integrazione LLM**: Genera prompt ottimizzati per Large Language Models
- **⚡ Automazione ADB**: Esegue azioni sui dispositivi Android basandosi sui dati estratti
- **🎯 Workflow Completo**: Pipeline automatica da cattura a esecuzione

## 📁 Struttura del Progetto

```
LogiDroid/
├── xml_to_json.py           # Conversione XML → JSON (183 righe, ottimizzato)
├── prompt_generator.py       # Generatore prompt per LLM
├── adb_automator.sh         # Automazione ADB
├── llm_integration.sh       # Script integrazione completa
├── llm_simulator.py         # Simulatore LLM per testing
├── demo.sh                 # Script demo workflow completo
├── config.sh               # Configurazioni
├── ui_captures/            # Directory catture UI
├── prompts/               # Directory prompt generati
└── README.md              # Questa documentazione
```

## 🚀 Quick Start

### 1. Prerequisiti
```bash
# Android Debug Bridge
brew install android-platform-tools  # macOS
# oppure installa Android SDK

# Python 3
python3 --version  # Verifica installazione

# Dispositivo Android in modalità sviluppatore
adb devices
```

### 2. Workflow Completo
```bash
# Connetti dispositivo Android e naviga alla schermata desiderata
# Esegui workflow completo
./llm_integration.sh workflow "Aggiungi nuovo contatto con nome Mario Rossi"

# Output:
# - ui_captures/session_YYYYMMDD_HHMMSS.xml
# - session_YYYYMMDD_HHMMSS.json  
# - prompts/session_YYYYMMDD_HHMMSS_task.md
```

### 3. Invia Prompt al LLM
```bash
# Copia il prompt generato
cat prompts/session_YYYYMMDD_HHMMSS_task.md

# Incolla nel tuo LLM preferito (ChatGPT, Claude, ecc.)
# Ottieni risposta JSON con steps di automazione
```

### 4. Esegui Automazione
```bash
# Usa la risposta LLM per automazione
./adb_automator.sh session_YYYYMMDD_HHMMSS.json click_button "Salva"
./adb_automator.sh session_YYYYMMDD_HHMMSS.json fill_field "Nome" "Mario Rossi"
```

## 🛠️ Utilizzo Avanzato

### Modalità Interattiva
```bash
./llm_integration.sh interactive
```
Menu interattivo per tutte le funzionalità.

### Cattura UI Manuale
```bash
# Cattura UI corrente
./llm_integration.sh capture my_screen
# Genera: ui_captures/my_screen.xml
```

### Conversione XML Esistente
```bash
# Converte file XML esistente
./llm_integration.sh convert ui_captures/my_screen.xml my_data.json
```

### Generazione Prompt Specifici

#### Task Automation
```bash
./llm_integration.sh prompt my_data.json task "Compila form registrazione utente"
```

#### UI Understanding
```bash
./llm_integration.sh prompt my_data.json understand
```

#### Troubleshooting
```bash
./llm_integration.sh prompt my_data.json troubleshoot "Campo email non accetta input"
```

#### Test Scenarios
```bash
python3 prompt_generator.py my_data.json test
```

## 📊 Formato Dati

### JSON Output Esempio
```json
{
  "source_file": "2.xml",
  "timestamp": "2025-08-17T15:23:23.520761",
  "total_buttons": 6,
  "total_inputs": 4,
  "elements": [
    {
      "type": "edit_text",
      "text": "",
      "hint": "",
      "resource_id": "com.samsung.android.app.contacts:id/nameEdit",
      "bounds": { "x": 501, "y": 680, "width": 715, "height": 92 },
      "clickable": true,
      "editable": true,
      "label": "Nome"
    }
  ]
}
```

### Formato Risposta LLM Attesa
```json
{
  "steps": [
    {
      "action": "fill_field",
      "target": "Nome",
      "value": "Mario Rossi",
      "description": "Inserisce il nome del contatto"
    },
    {
      "action": "click_button", 
      "target": "Salva",
      "description": "Salva il nuovo contatto"
    }
  ],
  "confidence": "high",
  "notes": "Verifica che tutti i campi obbligatori siano compilati"
}
```

## 🎯 Tipi di Prompt

### 1. Task Completion
**Scopo**: Automazione guidata per completare task specifici
**Input**: Descrizione task in linguaggio naturale
**Output**: Sequenza di azioni JSON per automazione

### 2. UI Understanding  
**Scopo**: Analisi e comprensione dell'interfaccia corrente
**Input**: Stato UI corrente
**Output**: Analisi funzionalità, workflow, problemi UX

### 3. Troubleshooting
**Scopo**: Risoluzione problemi di automazione
**Input**: Descrizione errore/problema
**Output**: Analisi cause, soluzioni, prevenzione

### 4. Test Scenarios
**Scopo**: Generazione scenari di test completi
**Input**: Stato UI
**Output**: Happy path, edge cases, error scenarios

## 🔧 Comandi ADB Disponibili

### Automazione Basica
```bash
./adb_automator.sh <json_file> click_button <nome>
./adb_automator.sh <json_file> fill_field <nome> <valore>
./adb_automator.sh <json_file> list_elements
```

### Azioni Manuali Avanzate
```bash
# Funzioni disponibili nel terminal:
adb_click 500 300 "centro schermo"
adb_type_text "Hello World"
adb_clear_field 400 200
adb_long_click 600 400
adb_scroll up 3
adb_back
adb_home
```

## 📱 App Supportate

Il sistema riconosce automaticamente:
- Samsung Contacts
- Android Contacts
- WhatsApp
- Instagram
- Facebook
- Gmail
- Settings Android
- App generiche Android

## 🔍 Esempi Pratici

### Esempio 1: Aggiunta Contatto
```bash
# 1. Apri app Contatti e vai a "Nuovo Contatto"
# 2. Cattura UI
./llm_integration.sh workflow "Aggiungi contatto Mario Rossi telefono 123-456-789"
# 3. Invia prompt al LLM
# 4. Esegui automazione risultante
```

### Esempio 2: Debugging Campo Input
```bash
# 1. Cattura UI con problema
./llm_integration.sh capture debug_session
./llm_integration.sh convert ui_captures/debug_session.xml debug.json
# 2. Genera prompt troubleshooting
./llm_integration.sh prompt debug.json troubleshoot "Campo email non risponde ai click"
# 3. Analizza con LLM la risposta
```

### Esempio 3: Test Completo Form
```bash
# 1. Cattura form da testare
./llm_integration.sh capture test_form
./llm_integration.sh convert ui_captures/test_form.xml test.json
# 2. Genera scenari test
python3 prompt_generator.py test.json test
# 3. Usa LLM per pianificare test completi
```

## 🚨 Troubleshooting

### Dispositivo Non Connesso
```bash
# Verifica connessione
adb devices

# Se nessun dispositivo:
# 1. Abilita "Opzioni sviluppatore" su Android
# 2. Abilita "Debug USB"
# 3. Autorizza computer quando richiesto
```

### Errori di Permessi
```bash
# Rendi eseguibili gli script
chmod +x *.sh
chmod +x *.py
```

### Cattura UI Fallisce
```bash
# Verifica che UIAutomator sia disponibile
adb shell uiautomator dump --help

# Se non disponibile, aggiorna Android SDK
```

## 🔬 Architettura Tecnica

### 1. Cattura UI (UIAutomator)
- Dump XML della struttura UI corrente
- Estrazione elementi clickable ed editabili
- Coordinate precise per automazione

### 2. Processamento Intelligente
- Parser XML ottimizzato (ElementTree)
- Analisi contestuale per etichette automatiche
- Filtro elementi rilevanti (bottoni, campi input)

### 3. Generazione Prompt
- Template strutturati per diversi use case
- Context injection basato su package app
- Formato output standardizzato JSON

### 4. Automazione ADB
- Comandi touch, input testo, navigazione
- Error handling e feedback utente
- Timing intelligente per animazioni

## 📈 Ottimizzazioni

- **Codice ridotto del 73%**: Da 670 a 183 righe nel parser principale
- **Parser efficiente**: ElementTree con XPath ottimizzati
- **Cache intelligente**: Riutilizzo dati JSON tra sessioni
- **Error resilience**: Handling robusto errori ADB e parsing

## 🤝 Contribuire

1. Fork del repository
2. Crea feature branch
3. Commit con messaggi descrittivi
4. Push e crea Pull Request

## 📄 Licenza

MIT License - Vedi file LICENSE per dettagli

## 🔗 Collegamenti

- [Android Debug Bridge](https://developer.android.com/studio/command-line/adb)
- [UIAutomator](https://developer.android.com/training/testing/ui-automator)
- [Android Accessibility](https://developer.android.com/guide/topics/ui/accessibility)

---

**🎯 LogiDroid**: Dove l'automazione Android incontra l'intelligenza artificiale 🚀

# LogiDroid
LogiDroid: tool di testing per applicazioni Android basato sul prompt engineering, che guida le interazioni con l’app tramite intelligenza artificiale.
