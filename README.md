# 🧠 LogiDroid - Sistema Avanzato di Automazione Android con LLM


<div align="center">
  <img src="imm/IconaLogi.png" alt="LogiDroid Logo" width="600" height="600">
  <br><br>



<div align="center">
  <img sr├── 📚 Documentation
│   ├── complete_instructions.txt # 🤖 Istruzioni menu-based per Gemini
│   ├── docs/                     # 📖 Documentazione dettagliata
│   ├── README.md                 # 📚 Questa documentazione
│   └── .gitignore               # 🚫 File ignorati da Git
├── ⚙️ Configuration
│   ├── config.json              # 🔑 API Key Gemini (NON condividere!)
│   └── config_example.json      # 📋 Template configurazione
└── 🎨 Assets
    └── imm/Icona.png            # 🎨 Logo del progettoIconaLogiDroid.png" alt="LogiDroid Logo" width="500" height="500">
  <br><br>
  
  ![Version](https://img.shields.io/badge/version-3.0-blue.svg)
  ![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)
  ![License](https://img.shields.io/badge/license-MIT-orange.svg)
  ![Android](https://img.shields.io/badge/platform-Android-green.svg)
  ![AI](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-purple.svg)
  
</div>

LogiDroid è un sistema all'avanguardia che combina cattura UI, analisi intelligente e automazione Android tramite ADB, con integrazione **Gemini 2.0 Flash** per esplorazione autonoma e automazione guidata da intelligenza artificiale di nuova generazione.

## 🌟 Caratteristiche Principali

- **🔍 Cattura Completa**: Screenshot PNG + struttura UI XML in formato JSON
- **🧠 Memoria Intelligente**: Sistema di cronologia azioni con 20 azioni di contesto
- **🤖 Gemini 2.0 Flash**: Integrazione con l'AI più avanzata di Google, completamente gratuita
- **💡 Menu-Based Commands**: Sistema rivoluzionario di comandi a lettera (A, B, C) per eliminare errori di parsing
- **⚡ Automazione Precisa**: Click centrati e gestione dinamica delle interfacce
- **🎯 Esplorazione Autonoma**: Gemini esplora le app con logica superiore e strategia intelligente
- **🔧 Targeting Avanzato**: Riconoscimento intelligente dei controlli Android
- **🆓 Completamente Gratuito**: 15 richieste/minuto, 1500/giorno, 1M token/mese

## 🌐 Architettura Cloud-First con Privacy

### 🧠 **Sistema Gemini 2.0 Flash Gratuito**
```
🌐 CONNESSIONE SICURA A GOOGLE AI 🌐

┌─────────────────┐    HTTPS Sicure     ┌─────────────────┐
│   LogiDroid     │◄──────────────────►│  Gemini 2.0 API │
│                 │ generativelanguage  │   (Google AI)   │
└─────────────────┘    .googleapis.com  └─────────────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │ Gemini 2.0 Flash│
                                        │   VELOCISSIMO   │
                                        │  🆓 GRATUITO    │
                                        └─────────────────┘
```

### 🛡️ **Privacy e Sicurezza**
- ✅ **API Sicure**: Connessioni HTTPS crittografate
- ✅ **Zero Costi**: 15 richieste/minuto, 1500/giorno completamente gratis
- ✅ **Intelligenza Superiore**: Gemini 2.0 Flash > modelli locali
- ✅ **Velocità**: Risposta istantanea vs lag modelli locali
- ✅ **Context Window**: 1M+ token vs 4K dei modelli locali
- 🔒 **API Key Sicura**: File `config.json` escluso dal git per proteggere le credenziali

### ⚡ **Perché Gemini invece di Ollama Locale?**
- **Intelligenza**: Gemini 2.0 Flash è drasticamente più intelligente per UI testing
- **Velocità**: Istantaneo vs 5-10 secondi con 8GB RAM
- **Affidabilità**: Zero crash, sempre disponibile
- **Gratuito**: Nessun costo hardware aggiuntivo
- **Aggiornamenti**: Sempre l'ultima versione senza installazioni

## 🆕 Novità v3.0

### 🚀 Gemini 2.0 Flash Integration
- **AI di Nuova Generazione**: Sostituito Ollama con Gemini 2.0 Flash
- **Completamente Gratuito**: 15 richieste/minuto, 1500/giorno, 1M token/mese
- **Intelligenza Superiore**: Scelte molto più logiche e strategiche
- **Velocità Istantanea**: Risposta immediata vs lag modelli locali

### 💡 Sistema Menu-Based Rivoluzionario
- **Comandi a Lettera**: L'AI sceglie A, B, C invece di costruire risposte
- **Zero Errori di Parsing**: Elimina errori di formato e interpretazione
- **Testo Personalizzato**: Supporto F:MarioRossi per input custom
- **Esempi Dinamici**: Generati specificamente per ogni schermata

### � Memoria Estesa
- **20 Azioni di Contesto**: Cronologia molto ampia per decisioni strategiche
- **Rilevamento Vicoli Ciechi**: Gemini riconosce quando tornare indietro
- **Pattern Recognition**: Identifica loop e comportamenti ripetitivi

## 📁 Struttura del Progetto

```
LogiDroid/
├── 🚀 Core System (6 file essenziali)
│   ├── start_test.sh             # ⭐ Script principale cattura + test
│   ├── llm_api.py                # 🧠 Gemini 2.0 Flash integration
│   ├── prompt_generator.py       # 📝 Menu-based commands + memoria 20 azioni
│   ├── adb_automator.sh          # ⚡ Automazione ADB precisa
│   ├── xml_to_json.py            # 🔄 Convertitore interfacce
│   └── cleanup_test.sh           # 🧹 Utility pulizia test
├── 📁 Generated at Runtime
│   └── test/                     # 🧪 Cartella test centralizzata
│       ├── json/                 # 📋 File JSON generati
│       ├── xml/                  # 📱 File XML interfacce
│       ├── screenshots/          # 📸 Screenshot PNG
│       └── prompts/              # 🧠 Sistema memoria 20 azioni
├── � Documentation
│   ├── complete_instructions.txt # 🤖 Istruzioni menu-based per Gemini
│   ├── docs/                     # 📖 Documentazione dettagliata
│   ├── README.md                 # 📚 Questa documentazione
│   └── .gitignore               # 🚫 File ignorati da Git
└── 🎨 Assets
    └── imm/Icona.png            # 🎨 Logo del progetto
```

## 🚀 Quick Start

### 1. Prerequisiti

#### Software Richiesto
```bash
# Android Debug Bridge
brew install android-platform-tools  # macOS
# oppure installa Android SDK

# Python 3.7+
python3 --version

# Google Gemini API Key (gratuita)
# Ottieni da: https://makersuite.google.com/app/apikey
```

#### Setup Dispositivo Android
```bash
# Abilita Opzioni Sviluppatore e Debug USB
adb devices  # Verifica connessione

# Autorizza il computer quando richiesto dal dispositivo
```

### 2. Configurazione API

#### 🔑 Setup Gemini API Key
```bash
# 1. Copia il file di esempio
cp config_example.json config.json

# 2. Modifica config.json e inserisci la tua API key
# Cambia "your-google-gemini-api-key-here" con la tua chiave
# Ottieni la chiave gratis da: https://makersuite.google.com/app/apikey

# 3. Test connessione
python3 llm_api.py  # Dovrebbe connettersi a Gemini
```

### 3. Utilizzo Immediato

#### 🎯 Test Automatico con Menu
```bash
# Naviga all'app che vuoi testare sul dispositivo
# Avvia il test automatico
./start_test.sh

# ✨ Il sistema fa tutto automaticamente:
# 📸 Cattura screenshot + interfaccia XML
# 🔄 Converte in JSON strutturato  
# 🧠 Gemini 2.0 Flash analizza e presenta menu
# ⚡ Esegue l'azione scelta via ADB
# 💾 Memorizza azione (memoria fino a 20 azioni)
```

#### 📋 Sistema Menu-Based
Il sistema ora presenta opzioni a menu:
```
Gemini analizza la schermata e presenta:
A. Clicca su "Login"
B. Digita nel campo username  
C. Scorri verso il basso
```

Gemini risponde con una lettera (es: "A") per eliminare errori di parsing.
Per testo personalizzato: `F:Testo da scrivere`

#### 🔧 Componenti Individuali (Uso Avanzato)
```bash
# Cattura e conversione
python3 xml_to_json.py test/xml/input.xml test/json/output.json

# Generazione prompt con memoria (20 azioni)
python3 prompt_generator.py test/json/result.json

# Gemini 2.0 Flash API call
# Gemini API call
python3 llm_api.py test/json/result.json

# Automazione ADB diretta
./adb_automator.sh test/json/result.json click_button "Nome Bottone"
./adb_automator.sh test/json/result.json fill_field "Nome Campo" "Valore"
```

## 📊 Output del Sistema

### File Generati (Cartella test/)
```
📸 test/screenshots/screen_TIMESTAMP.png    # Screenshot PNG dell'interfaccia
📱 test/xml/current_TIMESTAMP.xml           # Struttura UI in formato XML
📋 test/json/result_current_TIMESTAMP.json  # Dati strutturati per Gemini
🧠 test/prompts/action_history.json         # Cronologia azioni (max 20)
📝 test/prompts/last_action.txt             # Ultima azione eseguita
```

### Gestione File di Test
```bash
# Pulizia rapida di tutti i file di test
rm -rf test/

# Pulizia selettiva
rm -rf test/json/*          # Solo file JSON
rm -rf test/xml/*           # Solo file XML  
rm -rf test/screenshots/*   # Solo screenshot
rm -rf test/prompts/*       # Solo cronologia azioni
```

### Esempio JSON Generato
```json
{
  "source_file": "current_1234567890.xml",
  "timestamp": "2025-08-17T19:30:00.000000",
  "total_buttons": 15,
  "total_inputs": 3,
  "elements": [
    {
      "type": "button",
      "text": "Salva",
      "content_desc": "Salva contatto",
      "bounds": {"x": 540, "y": 2020, "width": 325, "height": 147},
      "clickable": true,
      "label": "Salva"
    },
    {
      "type": "input",
      "text": "",
      "hint": "Inserisci nome",
      "bounds": {"x": 159, "y": 491, "width": 800, "height": 92},
      "editable": true,
      "label": "Nome (VUOTO) [pos:159,491]"
    }
  ]
}
```

## 🧠 Sistema di Memoria Avanzato

### Cronologia delle Azioni (20 Azioni Max)
```json
[
  {
    "timestamp": "2025-08-17T19:30:00.000000",
    "action": "CLICK:Aggiungi",
    "screen": "Schermata lista contatti"
  },
  {
    "timestamp": "2025-08-17T19:30:15.000000", 
    "action": "FILL:Nome:Mario Rossi",
    "screen": "Schermata di creazione contatto"
  },
  {
    "timestamp": "2025-08-17T19:30:30.000000",
    "action": "CLICK:Salva", 
    "screen": "Schermata di creazione contatto"
  }
]
```

### Prompt Generato con Memoria per Gemini
```
🤖 ESPLORAZIONE AUTONOMA ANDROID - MENU COMMANDS

📱 AZIONI PRECEDENTI (mantieni la logica!):
1. CLICK:Aggiungi → Schermata di creazione contatto
2. FILL:Nome:Mario Rossi → Schermata di creazione contatto

📍 SCHERMATA ATTUALE: Schermata di creazione contatto

🎯 COMANDI DISPONIBILI:
A. Clicca su "Salva"
B. Compila campo "Email"  
C. Torna indietro

🤖 RISPONDI CON UNA SOLA LETTERA (A, B, C)
Per testo personalizzato: F:Testo da digitare
```

## 🔧 API e Comandi

### 🎯 Sistema Semplificato (v3.0)
```bash
# Setup una volta sola  
brew install android-platform-tools
# Configura API Key Gemini in config.json

# Uso quotidiano - UN SOLO COMANDO!
./start_test.sh     # ⭐ Fa tutto automaticamente con Gemini
```

### 🧹 Gestione File Test
```bash
./cleanup_test.sh all      # Rimuove tutti i file test
./cleanup_test.sh json     # Solo file JSON
./cleanup_test.sh xml      # Solo file XML
./cleanup_test.sh screenshots # Solo screenshot
```

### 🔧 Componenti Individuali (Opzionale)
```bash
# Conversione manuale
python3 xml_to_json.py test/xml/input.xml test/json/output.json

# Generazione prompt con menu
python3 prompt_generator.py test/json/result.json

# Gemini API call
python3 llm_api.py test/json/result.json

# Automazione ADB
./adb_automator.sh test/json/result.json click_button "Nome"
./adb_automator.sh test/json/result.json fill_field "Campo" "Valore"
```

## ⚙️ Configurazione Gemini API

### Setup API Key
```json
// In config.json
{
  "gemini_api_key": "your-google-gemini-api-key-here",
  "model": "gemini-2.0-flash-exp", 
  "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent",
  "max_output_tokens": 50,
  "temperature": 0.7,
  "top_p": 0.9
}
```

### Parametri Gemini Ottimizzati
```json
{
  "model": "gemini-2.0-flash-exp",
  "temperature": 0.7,        // Bilanciamento decisioni
  "max_output_tokens": 50,   // Risposte brevi (solo lettere)
  "top_p": 0.9              // Diversità nelle scelte
}
```

### Formato Risposte Menu-Based
```
A                           # Scelta menu semplice
F:Testo da digitare         # Testo personalizzato
```

## 🔍 Risoluzione Problemi

### Gemini API Non Risponde
```bash
# Test connessione diretta
curl -H "Content-Type: application/json" \
     -H "x-goog-api-key: YOUR_API_KEY" \
     -d '{"contents":[{"parts":[{"text":"Test"}]}]}' \
     https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent

# Verifica quota API (15 req/min free tier)
```

### Dispositivo Non Connesso
```bash
# Verifica connessione ADB
adb devices
adb kill-server && adb start-server
```

### Click Non Precisi
Il sistema ora usa **click centrati** automaticamente:
- Calcola centro elemento: `center_x = x + width/2`
- Filtra elementi troppo piccoli: `width > 10 && height > 10`

### Memoria Non Funziona
```bash
# Verifica cartelle
ls -la prompts/
# Deve essere scrivibile per action_history.json e last_action.txt
```

## 🎯 Esempi d'Uso

### Esplorazione App Contatti
```bash
# 1. Apri app Contatti
# 2. Esegui LogiDroid
./start_test.sh

# Output esempio con menu:
# 📱 AZIONI PRECEDENTI:
# 1. CLICK:Aggiungi → Schermata di creazione contatto
# 2. FILL:Nome:Mario Rossi → Schermata di creazione contatto
# 
# 🎯 COMANDI DISPONIBILI:
# A. Clicca su "Salva"
# B. Compila campo "Email"
# C. Torna indietro
#
# Gemini risponde: A
```

### Debug Interfaccia
```bash
# Cattura interfaccia problematica
python3 xml_to_json.py test/xml/problem.xml test/json/debug.json
python3 prompt_generator.py test/json/debug.json

# Analizza elementi disponibili con menu
./adb_automator.sh test/json/debug.json list_elements
```

### Gestione File di Test
```bash
# Pulizia completa
./cleanup_test.sh all

# Pulizia selettiva
./cleanup_test.sh json        # Solo file JSON
./cleanup_test.sh xml         # Solo file XML
./cleanup_test.sh screenshots # Solo screenshot
./cleanup_test.sh prompts     # Solo cronologia
./cleanup_test.sh legacy      # File cartelle vecchie

# Ricreare struttura dopo pulizia completa
mkdir -p test/{json,xml,screenshots,prompts}
```

## 📚 Documentazione Tecnica

### Struttura JSON Elemento
```json
{
  "type": "button|input",
  "text": "Testo visibile",
  "content_desc": "Descrizione accessibilità", 
  "resource_id": "com.app.id:id/element",
  "bounds": {"x": 0, "y": 0, "width": 100, "height": 50},
  "clickable": true,
  "editable": false,
  "label": "Etichetta generata per menu"
}
```

### Sistema Menu-Based v3.0
- **Input automatici**: Sistema genera menu con opzioni A, B, C
- **Risposte lettere**: Gemini risponde solo con lettere (A, B, C)
- **Testo personalizzato**: Formato `F:Testo da scrivere`
- **Zero parsing errors**: Eliminati errori di interpretazione

### Gemini 2.0 Flash Integration
- **Model**: `gemini-2.0-flash-exp` (sperimentale, performance superiori)
- **Free Tier**: 15 richieste/minuto gratuito
- **Context**: 20 azioni precedenti per decisioni intelligenti
- **Latency**: Cloud-based, ~1-2 secondi per risposta

## 🔐 Sicurezza e Best Practices

### ⚠️ IMPORTANTE - Sicurezza API Key

### 🔒 **NON CONDIVIDERE MAI LA TUA API KEY**
- ✅ La tua API key è in `config.json` (escluso dal git)
- ❌ **NON** committare mai `config.json` nel repository
- ❌ **NON** condividere screenshot con la tua API key visibile
- ✅ Usa sempre `config_example.json` come template per altri

### 🛡️ **Verifiche di Sicurezza**
```bash
# Verifica che config.json sia nel .gitignore
git status  # config.json NON deve apparire

# Se config.json appare in git status:
git reset config.json  # Rimuovilo dal staging
echo "config.json" >> .gitignore  # Assicurati sia nel .gitignore
```
