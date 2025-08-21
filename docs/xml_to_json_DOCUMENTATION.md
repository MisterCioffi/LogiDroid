# 📱 xml_to_json.py - Documentazione Completa

## 🎯 **Scopo del Modulo**

Il file `xml_to_json.py` è il **convertitore principale** del sistema LogiDroid che trasforma i file XML generati da UIAutomator (Android) in formato JSON strutturato e pulito, ottimizzato per l'analisi da parte dell'LLM.

## 🔧 **Funzionalità Principali**

### 1. **Parsing XML Android**
- Legge file XML di UIAutomator (`adb shell uiautomator dump`)
- Estrae elementi dell'interfaccia utente Android
- Identifica automaticamente Button, EditText e TextView

### 2. **Classificazione Intelligente**
- **Button**: Elementi cliccabili per azioni
- **EditText**: Campi di input dove inserire testo
- **TextView**: Etichette di solo lettura

### 3. **Associazione Etichette**
- Trova automaticamente le etichette per i campi EditText
- Associa TextView vicini ai campi di input
- Calcola distanze spaziali per trovare l'etichetta più appropriata

## 📋 **Struttura del Codice**

### 🔍 **Funzioni Principali**

#### `parse_bounds(bounds_str)`
```python
def parse_bounds(bounds_str):
    """
    Converte coordinate '[x1,y1][x2,y2]' in dizionario con centro e dimensioni
    Input: '[100,200][300,400]'
    Output: {'x': 200, 'y': 300, 'width': 200, 'height': 200}
    """
```
- **Input**: Stringa coordinate Android `'[x1,y1][x2,y2]'`
- **Output**: Dizionario con coordinate centro e dimensioni
- **Uso**: Calcolare dove cliccare su un elemento

#### `extract_elements(node, elements, text_nodes)`
```python
def extract_elements(node, elements=[], text_nodes=[]):
    """
    Funzione ricorsiva che attraversa l'albero XML
    e classifica ogni nodo come Button, EditText o TextView
    """
```
- **Attraversamento ricorsivo** dell'albero XML
- **Classificazione automatica** basata su:
  - `class` attribute (es. `android.widget.Button`)
  - `clickable` attribute
  - `editable` attribute
- **Raccolta** elementi utili in liste separate

#### `find_label_for_edittext(edittext, text_nodes)`
```python
def find_label_for_edittext(edittext, text_nodes):
    """
    Algoritmo intelligente per trovare l'etichetta di un campo EditText
    Cerca TextView nelle vicinanze con priorità a quelli sopra
    """
```
- **Calcolo distanze** spaziali tra EditText e TextView
- **Priorità elementi sopra** (bonus 0.7x alla distanza)
- **Soglie** di vicinanza: verticale <150px, orizzontale <300px
- **Fallback**: hint → text → "Campo senza etichetta"

#### `find_label_for_button(button, text_nodes)`
```python
def find_label_for_button(button, text_nodes):
    """
    Trova etichetta per Button senza testo
    (es. ImageButton con TextView vicino)
    """
```
- **Prima**: Usa il testo del Button se presente
- **Alternativo**: Cerca TextView molto vicino (≤50px)
- **Uso**: Button con icone ma senza testo

#### `xml_to_json(xml_file)`
```python
def xml_to_json(xml_file):
    """
    Funzione principale che coordina tutto il processo
    XML → Parsing → Classificazione → Etichettatura → JSON
    """
```
- **Parsing XML** con ElementTree
- **Estrazione elementi** con `extract_elements()`
- **Aggiunta etichette** automatiche
- **Creazione JSON** strutturato finale

## 📊 **Formato Output JSON**

```json
{
  "source_file": "current_123456.xml",
  "timestamp": "2025-08-21T10:30:45.123456",
  "total_buttons": 8,
  "total_inputs": 3,
  "elements": [
    {
      "type": "button",
      "text": "Salva",
      "hint": "",
      "content_desc": "",
      "resource_id": "com.app:id/save_btn",
      "bounds": {"x": 200, "y": 300, "width": 100, "height": 50},
      "clickable": true,
      "editable": false,
      "label": "Salva"
    },
    {
      "type": "edit_text",
      "text": "",
      "hint": "Inserisci nome",
      "content_desc": "",
      "resource_id": "com.app:id/name_field",
      "bounds": {"x": 150, "y": 200, "width": 200, "height": 40},
      "clickable": false,
      "editable": true,
      "label": "Nome"
    }
  ]
}
```

## 🧠 **Algoritmo di Classificazione**

### **Identificazione Tipo Elemento**
```python
class_name = attrs.get('class', '').lower()
is_button = ('button' in class_name or clickable) and 'edittext' not in class_name
is_edittext = 'edittext' in class_name
is_textview = 'textview' in class_name and text and not clickable
```

### **Logica di Classificazione**
1. **EditText**: Contiene "edittext" nel class name
2. **Button**: Contiene "button" o è `clickable=true` (ma non EditText)
3. **TextView**: Contiene "textview", ha testo e non è cliccabile

## 🎯 **Algoritmo Associazione Etichette**

### **Per Campi EditText**
1. **Cerca TextView** nelle vicinanze (150px verticale, 300px orizzontale)
2. **Calcola distanza**: `distanza = v_dist + (h_dist * 0.5)`
3. **Bonus sopra**: Se TextView è sopra EditText → `distanza *= 0.7`
4. **Seleziona più vicino** con distanza minima
5. **Fallback**: hint → text → "Campo senza etichetta"

### **Per Button senza Testo**
1. **Cerca TextView** molto vicino (≤50px)
2. **Distanza Manhattan**: `|x1-x2| + |y1-y2|`
3. **Prima corrispondenza** valida

## 🚀 **Utilizzo**

### **Comando Diretto**
```bash
python3 xml_to_json.py input.xml [output.json]
```

### **Dal Sistema LogiDroid**
```bash
# Chiamato automaticamente da start_test.sh
adb shell uiautomator dump /sdcard/ui_dump.xml
adb pull /sdcard/ui_dump.xml test/xml/current_123456.xml
python3 xml_to_json.py test/xml/current_123456.xml test/json/result_123456.json
```

## 📈 **Output Statistiche**
```
Convertendo test/xml/current_123456.xml...
✓ Completato: test/json/result_123456.json
  - 8 pulsanti
  - 3 campi di testo
```

## 🔧 **Parametri Configurabili**

### **Soglie di Vicinanza**
```python
# In find_label_for_edittext()
v_dist < 150    # Distanza verticale massima
h_dist < 300    # Distanza orizzontale massima

# In find_label_for_button()
distance <= 50  # Distanza massima per Button
```

### **Pesi Algoritmo**
```python
distance = v_dist + (h_dist * 0.5)  # Peso orizzontale ridotto
if text_pos['y'] <= edit_pos['y']:  # Bonus per elementi sopra
    distance *= 0.7
```

## 🎯 **Integrazione Sistema LogiDroid**

### **Input da**
- `adb shell uiautomator dump` (XML Android UI)

### **Output per**
- `prompt_generator.py` (genera prompt per LLM)
- `adb_automator.sh` (coordinate per click/fill)

### **Dati Utilizzati**
- **bounds**: Coordinate per automazione ADB
- **label**: Nomi comprensibili per LLM
- **editable**: Distingue campi input da bottoni
- **resource_id**: Identificazione precisa elementi

## 🛠️ **Gestione Errori**

### **File Non Trovato**
```python
if not os.path.exists(xml_file):
    print(f"Errore: File {xml_file} non trovato")
    sys.exit(1)
```

### **XML Malformato**
```python
try:
    tree = ET.parse(xml_file)
except Exception as e:
    raise Exception(f"Errore: {e}")
```

### **Coordinate Invalide**
```python
def parse_bounds(bounds_str):
    try:
        # parsing...
    except:
        return None  # Gestione sicura
```

## 📚 **Dipendenze**

```python
import xml.etree.ElementTree as ET  # Parsing XML
import json                         # Output JSON
import sys                          # Argomenti CLI
import os                          # Gestione file
from datetime import datetime      # Timestamp
```

## 🔄 **Flusso Dati Completo**

```
Android UI
    ↓ (uiautomator dump)
XML File
    ↓ (xml_to_json.py)
JSON Strutturato
    ↓ (prompt_generator.py)  
Prompt LLM
    ↓ (llm_local.py)
Comando Azione
    ↓ (adb_automator.sh)
Esecuzione su Dispositivo
```

Questo convertitore è il **cuore dell'analisi UI** del sistema LogiDroid! 🎯
