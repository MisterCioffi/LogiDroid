#!/usr/bin/env python3

import requests
import json
import sys
import subprocess
import os

# Variabile globale per memorizzare l'azione precedente
PREVIOUS_ACTION_FILE = "test/prompts/last_action.txt"

def save_last_action(action):
    """Salva l'ultima azione eseguita usando lo stesso sistema del prompt_generator"""
    try:
        import json
        from datetime import datetime
        
        # Usa lo stesso file di action_history.json
        history_file = "test/prompts/action_history.json"
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        # Carica cronologia esistente
        history = []
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        # Aggiungi la nuova azione (senza screen context per ora)
        history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "screen": "Azione completata"
        })
        
        # Mantieni solo le ultime 10 azioni
        if len(history) > 10:
            history = history[-10:]
        
        # Salva cronologia aggiornata
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            
        # Mantieni anche il sistema legacy per compatibilità
        with open(PREVIOUS_ACTION_FILE, 'w') as f:
            f.write(action)
    except Exception as e:
        print(f"Errore nel salvare azione: {e}")

def get_last_action():
    """Recupera l'ultima azione dalla cronologia unificata"""
    try:
        import json
        
        # Prima prova dal sistema unificato
        history_file = "test/prompts/action_history.json"
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            if history:
                return history[-1].get('action', '')
        
        # Fallback al sistema legacy
        if os.path.exists(PREVIOUS_ACTION_FILE):
            with open(PREVIOUS_ACTION_FILE, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 llm_local.py <json_file>")
        return
    
    json_file = sys.argv[1]
    print(f"📁 Analizzando: {json_file}")
    
    # Genera prompt UI con cronologia
    print("📱 Generando prompt interfaccia...")
    
    # Verifica se è la prima iterazione (nessuna cronologia valida)
    history_file = "test/prompts/action_history.json"
    is_first_iteration = True
    
    if os.path.exists(history_file) and os.path.getsize(history_file) > 0:
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                is_first_iteration = len(history) == 0
        except:
            is_first_iteration = True
    
    # Chiama prompt_generator con l'informazione se è la prima iterazione
    cmd = ["python3", "prompt_generator.py", json_file, str(is_first_iteration).lower()]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Errore: {result.stderr}")
        return
    
    ui_prompt = result.stdout
    
    # Usa direttamente il prompt dal generator (già contiene tutto)
    prompt = ui_prompt
    # Crea prompt per LLM più intelligente
    import random
    import re
    
    # Estrai bottoni disponibili dal prompt per suggerire esempio intelligente
    buttons_section = re.search(r'BOTTONI:\n(.*?)\n\n', ui_prompt, re.DOTALL)
    available_buttons = []
    if buttons_section:
        button_lines = buttons_section.group(1).split('\n')
        for line in button_lines:
            if line.strip() and '. ' in line:
                button_name = line.split('. ', 1)[1]
                available_buttons.append(button_name)
    
    # Scegli un'azione intelligente per l'esempio
    if available_buttons:
        suggested_button = random.choice(available_buttons)
        forced_action = f"CLICK:{suggested_button}"
    else:
        forced_action = "FILL:Nome:Test"
    
    # Aggiungi esempio al prompt
    full_prompt = f"""{prompt}

💡 ESEMPIO: {forced_action}"""

    print("=" * 60)
    print("🤖 DOMANDA ALL'LLM:")
    print("=" * 60)
    print(full_prompt)
    print("=" * 60)
    
    # Chiama Ollama
    print("🤖 LLM sta analizzando...")
    
    payload = {
        'model': 'llama3.1:8b',
        'prompt': full_prompt,
        'stream': False,
        'options': {
            'temperature': 0.3,  # Ridotta per risposte più deterministiche e veloci
            'num_predict': 30,   # Ridotto da 50 a 30 per risposte più brevi
            'top_p': 0.8,        # Ridotto per maggiore focus
            'repeat_penalty': 1.1  # Ridotto per evitare rallentamenti
        }
    }
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json=payload, timeout=90)  # Aumentato a 90 secondi
        response.raise_for_status()
        
        result = response.json()
        llm_response = result.get('response', '').strip()
        
        print("=" * 60)
        print("💭 DECISIONE LLM:")
        print("=" * 60)
        print(llm_response)
        print("=" * 60)
        
        if not llm_response:
            print("❌ Nessuna risposta dal LLM")
            return
            
        # Inizializza variabili
        target = None
        action_type = None
        value = None
            
        # Parsing migliorato - estrae SOLO il primo comando valido
        import re
        
        # Pulisci la risposta e prendi solo la prima riga con comando
        lines = [line.strip() for line in llm_response.split('\n') if line.strip()]
        command_line = None
        
        # Trova la prima riga che contiene un comando valido
        for line in lines:
            if line.startswith("CLICK:") or line.startswith("FILL:"):
                command_line = line
                break
        
        if not command_line:
            # Cerca pattern nei testi
            click_match = re.search(r'CLICK:([^\n\(]+)', llm_response)
            fill_match = re.search(r'FILL:([^:\n]+):([^\n\(]+)', llm_response)
            
            if click_match:
                command_line = f"CLICK:{click_match.group(1).strip()}"
            elif fill_match:
                command_line = f"FILL:{fill_match.group(1).strip()}:{fill_match.group(2).strip()}"
        
        if not command_line:
            print(f"\n💭 L'LLM ha risposto: {llm_response}")
            print("❓ Formato non riconosciuto. Atteso CLICK:nome o FILL:campo:valore")
            return
        
        print(f"🎯 Comando estratto: {command_line}")
        
        # Processa il comando estratto
        if command_line.startswith("CLICK:"):
            target = command_line[6:].strip()
            # Rimuovi descrizioni tra parentesi e pulisci
            target = re.sub(r'\s*\([^)]*\)', '', target)
            target = target.rstrip('.,!?;').strip()
            action_type = "click"
            
        elif command_line.startswith("FILL:"):
            parts = command_line[5:].split(":", 1)
            if len(parts) >= 2:
                target = parts[0].strip()
                value = parts[1].strip()
                # Pulisci target e value
                target = re.sub(r'\s*\([^)]*\)', '', target).strip()
                value = value.rstrip('.,!?;').strip()
                action_type = "type"
            else:
                print("❌ Formato FILL non valido")
                return
        
        if target and action_type == "type" and value:
            # Prima controlla se il target è effettivamente un campo editabile
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cerca campi editabili che matchano il target
            editable_fields = []
            for elem in data['elements']:
                if elem['editable']:
                    label = elem.get('label', elem.get('text', elem.get('content_desc', '')))
                    if label and target.lower() in label.lower():
                        editable_fields.append(label)
            
            if not editable_fields:
                print(f"⚠️ '{target}' non è un campo editabile. Provo a cliccare invece.")
                # Converti in click se non è editabile
                action_type = "click"
                command = f"./adb_automator.sh {json_file} click_button '{target}'"
                action_performed = f"CLICK:{target}"
            else:
                # Usa il primo campo trovato
                target = editable_fields[0]
                command = f"./adb_automator.sh {json_file} fill_field '{target}' '{value}'"
                action_performed = f"FILL:{target}:{value}"
            
            print(f"\n✏️ Azione suggerita: Compilare '{target}' con '{value}'")
            print(f"🔧 Comando: {command}")
            
            print("⚡ Eseguendo...")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f"⚠️  {result.stderr}")
            
            # Salva l'azione per la prossima iterazione
            save_last_action(action_performed)
                
        elif target and action_type == "click":
            command = f"./adb_automator.sh {json_file} click_button '{target}'"
            action_performed = f"CLICK:{target}"
            
            print(f"\n👆 Azione suggerita: Premere '{target}'")
            print(f"🔧 Comando: {command}")
            
            print("⚡ Eseguendo...")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f"⚠️  {result.stderr}")
            
            # Salva l'azione per la prossima iterazione
            save_last_action(action_performed)
        else:
            print(f"\n💭 L'LLM suggerisce: {llm_response}")
            print("❓ Non è stato riconosciuto un comando specifico.")
            print("💡 Prova a eseguire manualmente uno di questi:")
            print("   ./adb_automator.sh", json_file, "list_elements")
    
    except Exception as e:
        print(f"❌ Errore LLM: {e}")

if __name__ == "__main__":
    main()
