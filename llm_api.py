#!/usr/bin/env python3
"""
LogiDroid LLM con Google Gemini 2.0 Flash + Random Injection
Sistema intelligente di automazione UI Android con AI gratuita e azioni casuali
"""

import requests
import json
import sys
import subprocess
import os
import re
import time
from datetime import datetime
from random_injector import RandomActionInjector

def load_config():
    """Carica configurazione da config.json"""
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print(f"❌ File {config_file} non trovato!")
        print("📝 Crea il file config.json copiando da config_example.json")
        print("🔑 Inserisci la tua API key Gemini nel file config.json")
        sys.exit(1)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ Errore nel caricare config.json: {e}")
        sys.exit(1)

# Carica configurazione
CONFIG = load_config()
GEMINI_API_KEY = CONFIG.get("gemini_api_key")
GEMINI_URL = CONFIG.get("api_url")

# Verifica API key
if not GEMINI_API_KEY or GEMINI_API_KEY == "your-google-gemini-api-key-here":
    print("❌ API Key Gemini non configurata!")
    print("🔑 Modifica config.json e inserisci la tua API key")
    print("📖 Ottieni la chiave da: https://makersuite.google.com/app/apikey")
    sys.exit(1)

# File per memorizzare l'azione precedente (fallback di sicurezza)
PREVIOUS_ACTION_FILE = "test/prompts/last_action.txt"

# Rate limiting - 15 richieste/minuto = 1 richiesta ogni 4 secondi
RATE_LIMIT_FILE = "test/prompts/last_api_call.txt"
RATE_LIMIT_DELAY = 4  # secondi tra chiamate

def enforce_rate_limit():
    """Applica rate limiting per rispettare i limiti di Gemini API (15 req/min)"""
    try:
        if os.path.exists(RATE_LIMIT_FILE):
            with open(RATE_LIMIT_FILE, 'r') as f:
                last_call_time = float(f.read().strip())
            
            time_since_last = time.time() - last_call_time
            if time_since_last < RATE_LIMIT_DELAY:
                sleep_time = RATE_LIMIT_DELAY - time_since_last
                print(f"⏳ Rate limiting: aspetto {sleep_time:.1f}s per rispettare i limiti API...")
                time.sleep(sleep_time)
    except:
        pass  # Se c'è un errore, procedi senza delay
    
    # Salva timestamp chiamata corrente
    try:
        os.makedirs(os.path.dirname(RATE_LIMIT_FILE), exist_ok=True)
        with open(RATE_LIMIT_FILE, 'w') as f:
            f.write(str(time.time()))
    except:
        pass

def call_gemini_api(prompt):
    """Chiama Gemini 1.5 Flash via API REST con rate limiting"""
    
    # Applica rate limiting prima della chiamata
    enforce_rate_limit()
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": CONFIG.get("max_output_tokens", 50),
            "temperature": CONFIG.get("temperature", 0.7),
            "topP": CONFIG.get("top_p", 0.9)
        }
    }
    
    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']['parts'][0]['text']
            return content.strip()
        else:
            print("❌ Nessuna risposta valida da Gemini")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore chiamata Gemini API: {e}")
        return None
    except Exception as e:
        print(f"❌ Errore parsing risposta Gemini: {e}")
        return None

def is_obvious_loop(action, history):
    """Rileva loop evidenti e azioni già fallite"""
    if not history:
        return False
    
    # 1. Loop tradizionale: stessa azione 3+ volte consecutive
    if len(history) >= 3:
        last_3_actions = [h.get('action', '') for h in history[-3:]]
        if all(a == action for a in last_3_actions):
            return True
    
    # 2. NUOVO: Evita azioni che sono già fallite recentemente
    recent_history = history[-5:]  # Ultimi 5 tentativi
    for entry in recent_history:
        if entry.get('action', '') == action and not entry.get('success', True):
            print(f"🚫 Azione già fallita recentemente: {action}")
            return True
    
    return False

def extract_command_from_letter(response, ui_prompt):
    """Estrae comando dalla risposta dell'LLM (lettera o lettera:testo)"""
    response_clean = response.strip()
    
    # Rimuovi spiegazioni comuni
    response_clean = re.sub(r'^(scelgo|risposta|comando):\s*', '', response_clean, flags=re.IGNORECASE)
    response_clean = re.sub(r'^["\']?([A-Z]:?.*?)["\']?$', r'\1', response_clean)
    
    # Formato personalizzato: F:Mario Rossi
    if ':' in response_clean and len(response_clean.split(':')) == 2:
        letter, custom_text = response_clean.split(':', 1)
        letter = letter.strip().upper()
        custom_text = custom_text.strip()
        
        # Trova il comando FILL_CUSTOM corrispondente nel prompt
        fill_custom_pattern = rf'{letter}\.\s*FILL_CUSTOM:([^(]+)'
        match = re.search(fill_custom_pattern, ui_prompt)
        if match:
            field_name = match.group(1).strip()
            return f"FILL:{field_name}:{custom_text}"
    
    # Formato semplice: solo lettera
    letter = response_clean.upper()
    if len(letter) == 1 and letter.isalpha():
        # Estrai il comando dal prompt usando la lettera
        # Pattern più ampio per includere BACK e altri comandi
        pattern = rf'{letter}\.\s*(BACK|CLICK:[^(\n]+|FILL:[^(\n]+|FILL_CUSTOM:[^(\n]+)'
        match = re.search(pattern, ui_prompt)
        if match:
            command = match.group(1).strip()
            # Se è FILL_CUSTOM, restituisci il formato corretto
            if command.startswith('FILL_CUSTOM:'):
                return command.replace('FILL_CUSTOM:', 'FILL:')
            return command
    
    return None

def save_last_action(action, success=True, error_message=""):
    """Salva l'ultima azione per anti-ripetizione con stato di successo/errore"""
    try:
        # Sistema unificato action_history.json
        history_file = "test/prompts/action_history.json"
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        # Carica cronologia esistente
        history = []
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        # Aggiungi la nuova azione con status
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "success": success,
            "screen": "Azione completata" if success else f"ERRORE: {error_message}"
        }
        
        history.append(entry)
        
        # Mantieni solo le ultime 10 azioni
        if len(history) > 10:
            history = history[-10:]
        
        # Salva cronologia aggiornata
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            
        # Fallback di sicurezza
        status_text = "SUCCESS" if success else f"ERROR: {error_message}"
        with open(PREVIOUS_ACTION_FILE, 'w') as f:
            f.write(f"{action} | {status_text}")
            
    except Exception as e:
        print(f"Errore nel salvare azione: {e}")

def main():
    if len(sys.argv) < 2:
        print("Utilizza: python3 llm_api.py <json_file>")
        return
    
    json_file = sys.argv[1]
    print(f"📁 Analizzando: {json_file}")
    
    # 🎲 INIZIALIZZA RANDOM INJECTOR
    random_injector = RandomActionInjector(frequency=6)  # Ogni 6 iterazioni
    
    # Verifica se è la prima iterazione
    history_file = "test/prompts/action_history.json"
    is_first_iteration = True
    history = []
    
    if os.path.exists(history_file) and os.path.getsize(history_file) > 0:
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                is_first_iteration = len(history) == 0
        except Exception as e:
            print(f"⚠️ Error loading history: {e}")
            is_first_iteration = True
    
    # 🎲 CONTROLLO RANDOM INJECTION PRIMA DELL'LLM
    if not is_first_iteration and random_injector.should_inject_random():
        print("🎲 " + "="*60)
        print("🎲 RANDOM INJECTION TRIGGERED - SKIPPING LLM THIS ITERATION")
        print("🎲 " + "="*60)
        
        # Esegui ciclo random completo
        new_json_file = random_injector.full_random_cycle()
        
        if new_json_file:
            print(f"✅ Random injection successful!")
            print(f"📱 New screen captured: {new_json_file}")
            print("🔄 Next iteration will analyze the new screen with LLM")
            
            # IMPORTANTE: Richiama se stesso con la nuova schermata
            print("🔄 Restarting analysis with new screen...")
            subprocess.run(["python3", "llm_api.py", new_json_file])
            return
        else:
            print("❌ Random injection failed, continuing with normal flow...")
    
    # Continua con normale workflow LLM solo se non c'è stata random injection
    
    # Genera prompt UI
    print("📱 Generando prompt interfaccia...")
    cmd = ["python3", "prompt_generator.py", json_file, str(is_first_iteration).lower()]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Errore: {result.stderr}")
        return
    
    ui_prompt = result.stdout
    
    print("=" * 60)
    print("🧠 DOMANDA A GEMINI 2.0 FLASH:")
    print("=" * 60)
    print(ui_prompt)
    print("=" * 60)
    
    # Chiamata a Gemini 2.0 Flash
    print("🤖 Gemini sta analizzando...")
    llm_response = call_gemini_api(ui_prompt)
    
    if not llm_response:
        print("❌ Nessuna risposta da Gemini")
        return
    
    print("=" * 60)
    print("💭 DECISIONE GEMINI:")
    print("=" * 60)
    print(llm_response)
    print("=" * 60)
    
    # Estrai comando dalla risposta a lettera
    command_line = extract_command_from_letter(llm_response, ui_prompt)
    
    if not command_line:
        print(f"❓ Formato non riconosciuto: {llm_response}")
        print("ℹ️ Atteso: lettera (A) o lettera:testo (F:Mario)")
        return
    
    print(f"🎯 Comando estratto: {command_line}")
    
    # Controllo anti-loop
    if is_obvious_loop(command_line, history):
        print(f"🔄 Loop rilevato: {command_line}")
        print("⏭️ Saltando iterazione per evitare loop...")
        return
    
    # Processa ed esegui comando
    if command_line == "BACK":
        # Comando BACK - pressione tasto back Android
        command = "adb shell input keyevent KEYCODE_BACK"
        action_performed = "BACK"
        
        print(f"\n⬅️ Azione: Premere tasto BACK")
        print(f"🔧 Comando: {command}")
        
    elif command_line.startswith("CLICK:"):
        target = command_line[6:].strip()
        target = re.sub(r'\s*\([^)]*\)', '', target)
        target = target.rstrip('.,!?;').strip()
        
        command = f"./adb_automator.sh {json_file} click_button '{target}'"
        action_performed = f"CLICK:{target}"
        
        print(f"\n👆 Azione: Premere '{target}'")
        print(f"🔧 Comando: {command}")
        
    elif command_line.startswith("FILL:"):
        parts = command_line[5:].split(":", 1)
        if len(parts) >= 2:
            target = parts[0].strip()
            value = parts[1].strip()
            target = re.sub(r'\s*\([^)]*\)', '', target).strip()
            value = value.rstrip('.,!?;').strip()
            
            command = f"./adb_automator.sh {json_file} fill_field '{target}' '{value}'"
            action_performed = f"FILL:{target}:{value}"
            
            print(f"\n✏️ Azione: Compilare '{target}' con '{value}'")
            print(f"🔧 Comando: {command}")
        else:
            print("❌ Formato FILL non valido")
            return
    else:
        print(f"❓ Comando non riconosciuto: {command_line}")
        return
    
    # Esecuzione
    print("⚡ Eseguendo...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"⚠️ {result.stderr}")
    
    # Controllo del successo dell'operazione
    success = result.returncode == 0
    error_message = ""
    
    # Controlla se ci sono messaggi di errore specifici nell'output
    output_text = result.stdout + result.stderr
    if not success or "non trovato" in output_text.lower() or "errore" in output_text.lower():
        success = False
        error_message = "Comando fallito o elemento non trovato"
    
    # Salva azione per cronologia CON stato di successo/errore
    save_last_action(action_performed, success, error_message)
    
    if not success:
        print(f"❌ Azione fallita: {action_performed}")
        print(f"🚫 Motivo: {error_message}")
    else:
        print(f"✅ Azione completata: {action_performed}")

if __name__ == "__main__":
    main()
