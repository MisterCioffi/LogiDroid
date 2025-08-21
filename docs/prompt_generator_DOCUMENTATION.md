# 🤖 prompt_generator.py - Documentazione Completa

## 🎯 **Scopo del Modulo**

Il file `prompt_generator.py` è il **generatore di prompt intelligenti** del sistema LogiDroid che trasforma i dati JSON dell'interfaccia Android in prompt ottimizzati per l'LLM, mantenendo la memoria delle azioni precedenti e fornendo contesto per decisioni intelligenti.

## 🔧 **Funzionalità Principali**

### 1. **Generazione Prompt Strutturati**
- Converte JSON UI Android in prompt comprensibili per LLM
- Separa chiaramente CAMPI (EditText) da BOTTONI (Button)
- Mostra stato dei campi (VUOTO/COMPILATO)

### 2. **Sistema di Memoria**
- Carica cronologia ultime 10 azioni
- Evita ripetizioni con sistema anti-loop
- Mantiene contesto per decisioni sequenziali

### 3. **Contesto Intelligente**
- Riconosce tipo di schermata (contatto, ricerca, etc.)
- Fornisce suggerimenti contestuali
- Prioritizza azioni logiche

### 4. **Integrazione Stateless LLM**
- Include sempre istruzioni complete
- Compensa mancanza di memoria LLM
- Formato standardizzato per parsing

## 📋 **Struttura del Codice**

### 🔍 **Funzioni Principali**

#### `load_action_history(history_file)`
```python
def load_action_history(history_file: str = "test/prompts/action_history.json") -> list:
    """
    Carica cronologia azioni precedenti per sistema anti-ripetizione
    File JSON con lista azioni: [{"action": "CLICK:Salva", "timestamp": "..."}, ...]
    """
```
- **Input**: Path file cronologia JSON
- **Output**: Lista azioni precedenti
- **Fallback**: Lista vuota se file non esiste
- **Uso**: Sistema anti-ripetizione per LLM

#### `get_screen_context(data)`
```python
def get_screen_context(data: dict) -> str:
    """
    Analizza elementi UI per determinare tipo di schermata
    Riconosce: contatto, ricerca, salvataggio, generica
    """
```
- **Analisi campi**: Cerca "Nome", "Cognome", etc.
- **Analisi bottoni**: Cerca "Cerca", "Salva", etc.
- **Classificazione automatica**: Determina contesto schermata
- **Output**: Stringa descrittiva tipo schermata

#### `generate_simple_prompt(json_file, is_first_iteration)`
```python
def generate_simple_prompt(json_file: str, is_first_iteration: bool = False) -> str:
    """
    FUNZIONE PRINCIPALE - Genera prompt completo per LLM
    Combina: istruzioni + cronologia + elementi UI + esempi
    """
```
- **Caricamento dati**: JSON → dizionario Python
- **Separazione elementi**: Campi vs Bottoni
- **Aggiunta cronologia**: Solo se non prima iterazione
- **Assemblaggio finale**: Prompt strutturato completo

## 📊 **Formato Output Prompt**

### **Struttura Completa Prompt**
```
🤖 SISTEMA DI TEST AUTOMATICO ANDROID
[ISTRUZIONI COMPLETE DA complete_instructions.txt]

🚫 ULTIME 10 AZIONI (NON RIPETERE QUESTE):
• CLICK:Galleria
• FILL:Nome:Marco
• CLICK:Salva

📱 INTERFACCIA CORRENTE:

CAMPI IN CUI INSERIRE TESTO:
1. Nome (VUOTO)
2. Email (COMPILATO)
3. Telefono (VUOTO)

BOTTONI:
1. Salva
2. Annulla
3. Galleria
4. Fotocamera
```

## 🧠 **Algoritmo di Classificazione Elementi**

### **Identificazione Campi di Testo**
```python
if elem['editable']:  # Campo EditText
    label = elem.get('label', elem.get('text', elem.get('content_desc', 'Campo')))
    current_value = elem.get('text', '').strip()
    
    if current_value:
        field_id = f"{label} (COMPILATO)"
    else:
        field_id = f"{label} (VUOTO)"
```

### **Identificazione Bottoni**
```python
elif elem['clickable']:  # Elemento cliccabile
    button_text = elem.get('text', '').strip()
    if not button_text:
        content_desc = elem.get('content_desc', '').strip()
        if content_desc:
            button_text = content_desc
        else:
            resource_id = elem.get('resource_id', '')
            if resource_id:
                button_text = f"[{resource_id.split(':')[-1]}]"
            else:
                button_text = "[bottone]"
```

### **Priorità Nomi Bottoni**
1. **text** attribute (testo visibile)
2. **content_desc** (descrizione accessibilità) 
3. **resource_id** (ID sviluppatore)
4. **"[bottone]"** (fallback generico)

## 🎯 **Sistema Anti-Ripetizione**

### **Meccanismo di Memoria**
```python
if not is_first_iteration and history:
    prompt += "🚫 ULTIME 10 AZIONI (NON RIPETERE QUESTE):\n"
    for action_data in history[-10:]:
        action = action_data.get('action', 'N/A')
        prompt += f"• {action}\n"
```

### **Logica Prima Iterazione**
- **Prima volta**: `is_first_iteration = True` → Nessuna cronologia
- **Iterazioni successive**: Mostra ultime 10 azioni da evitare
- **Emoji 🚫**: Segnale visivo forte per LLM

## 🔍 **Riconoscimento Contesto Schermata**

### **Algoritmo di Classificazione**
```python
if "Nome" in text_fields or "Cognome" in text_fields:
    context = "Schermata di creazione contatto"
elif "Cerca" in buttons or "cerca" in str(buttons).lower():
    context = "Schermata di ricerca"
elif any("salva" in btn.lower() for btn in buttons):
    context = "Schermata di conferma/salvataggio"
else:
    context = f"Schermata con {len(buttons)} bottoni disponibili"
```

### **Tipi di Schermate Riconosciute**
- ✅ **Creazione Contatto**: Campi Nome/Cognome
- ✅ **Ricerca**: Bottone "Cerca"
- ✅ **Salvataggio**: Bottone "Salva"
- ✅ **Generica**: Conta bottoni disponibili

## 🚀 **Utilizzo e Integrazione**

### **Chiamata Diretta**
```bash
python3 prompt_generator.py test/json/result_123456.json
python3 prompt_generator.py test/json/result_123456.json true  # Prima iterazione
```

### **Dal Sistema LogiDroid**
```python
# In llm_api.py
cmd = ["python3", "prompt_generator.py", json_file, str(is_first_iteration).lower()]
result = subprocess.run(cmd, capture_output=True, text=True)
ui_prompt = result.stdout
```

### **Parametri**
- **json_file**: Path file JSON da xml_to_json.py
- **is_first_iteration**: "true"/"false" per controllo cronologia

## 📈 **Ottimizzazioni Performance**

### **Limitazioni Elementi**
```python
for i, field in enumerate(text_fields[:5], 1):  # Max 5 campi
for i, button in enumerate(buttons[:8], 1):     # Max 8 bottoni
```
- **Campi**: Massimo 5 per evitare overload
- **Bottoni**: Massimo 8 per prompt concisi
- **Cronologia**: Ultime 10 azioni

### **Pulizia Nomi**
```python
clean_field = field.split(' [pos:')[0]  # Rimuove coordinate
```
- Rimuove informazioni tecniche non necessarie per LLM
- Mantiene solo nomi comprensibili

## 🔧 **Gestione Errori**

### **File JSON Mancante**
```python
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    raise Exception(f"Errore nel caricamento JSON: {e}")
```

### **Cronologia Corrotta**
```python
try:
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
except Exception:
    pass
return []  # Fallback sicuro
```

## 🎭 **Esempi Prompt Generati**

### **Prima Iterazione (Senza Cronologia)**
```
🤖 SISTEMA DI TEST AUTOMATICO ANDROID
[...istruzioni complete...]

📱 INTERFACCIA CORRENTE:

CAMPI IN CUI INSERIRE TESTO:
1. Nome (VUOTO)
2. Email (VUOTO)

BOTTONI:
1. Salva
2. Annulla
```

### **Iterazione Successiva (Con Cronologia)**
```
🤖 SISTEMA DI TEST AUTOMATICO ANDROID
[...istruzioni complete...]

🚫 ULTIME 10 AZIONI (NON RIPETERE QUESTE):
• FILL:Nome:Marco
• CLICK:Galleria

📱 INTERFACCIA CORRENTE:

CAMPI IN CUI INSERIRE TESTO:
1. Nome (COMPILATO)
2. Email (VUOTO)

BOTTONI:
1. Salva
2. Annulla
3. Fotocamera
```

## 🔄 **Flusso Dati nel Sistema**

```
JSON da xml_to_json.py
    ↓
prompt_generator.py
    ↓ (carica cronologia)
action_history.json
    ↓ (genera prompt)
Prompt Strutturato
    ↓ (invia a LLM)
llm_api.py
    ↓ (riceve decisione)
Comando Azione
    ↓ (salva in cronologia)
action_history.json (aggiornato)
```

## 🎯 **Integrazione con Altri Moduli**

### **Input da:**
- `xml_to_json.py` → JSON elementi UI
- `action_history.json` → Cronologia azioni
- `complete_instructions.txt` → Istruzioni LLM

### **Output per:**
- `llm_api.py` → Prompt completo per analisi
- LLM (Ollama) → Decisione azione da eseguire

### **Dati Chiave:**
- **Elementi UI**: Lista campi e bottoni disponibili
- **Stati campi**: VUOTO/COMPILATO per logica decisionale
- **Cronologia**: Azioni da evitare per diversificare esplorazione

## 📚 **Dipendenze**

```python
import json    # Parsing dati JSON e cronologia
import sys     # Argomenti command line
import os      # Gestione file e path
```

## ⚙️ **Configurazioni**

### **File Paths**
```python
history_file = "test/prompts/action_history.json"  # Cronologia azioni
instructions_file = "complete_instructions.txt"    # Istruzioni LLM
```

### **Limiti Elementi**
```python
text_fields[:5]   # Massimo 5 campi di testo
buttons[:8]       # Massimo 8 bottoni
history[-10:]     # Ultime 10 azioni cronologia
```

Questo generatore è il **ponte intelligente** tra l'analisi UI e le decisioni LLM! 🎯
