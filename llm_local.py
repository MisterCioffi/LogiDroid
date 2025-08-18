#!/usr/bin/env python3

import requests
import json
import sys
import subprocess
import os

# Variabile globale per memorizzare l'azione precedente
PREVIOUS_ACTION_FILE = "test/prompts/last_action.txt"

def save_last_action(action):
    """Salva l'ultima azione eseguita"""
    try:
        os.makedirs(os.path.dirname(PREVIOUS_ACTION_FILE), exist_ok=True)
        with open(PREVIOUS_ACTION_FILE, 'w') as f:
            f.write(action)
    except Exception:
        pass

def get_last_action():
    """Recupera l'ultima azione eseguita"""
    try:
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
    
    # Recupera l'azione precedente
    previous_action = get_last_action()
    
    # Chiama prompt_generator con l'azione precedente se disponibile
    cmd = ["python3", "prompt_generator.py", json_file]
    if previous_action:
        cmd.append(previous_action)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Errore: {result.stderr}")
        return
    
    ui_prompt = result.stdout
    
    # Crea prompt per LLM più intelligente
    import random
    
    # Estrai bottoni disponibili dal prompt
    import re
    buttons_section = re.search(r'BOTTONI:\n(.*?)\n\n', ui_prompt, re.DOTALL)
    available_buttons = []
    if buttons_section:
        button_lines = buttons_section.group(1).split('\n')
        for line in button_lines:
            if line.strip() and '. ' in line:
                button_name = line.split('. ', 1)[1]
                available_buttons.append(button_name)
    
    # Scegli un'azione intelligente
    if available_buttons:
        suggested_button = random.choice(available_buttons)
        forced_action = f"CLICK:{suggested_button}"
    else:
        forced_action = "FILL:Nome:Test"
    
    full_prompt = f"""Interfaccia Android:

{ui_prompt}

⚠️ ESEGUI QUESTA AZIONE: {forced_action}

Scegli SOLO tra i bottoni disponibili sopra.
La tua risposta deve essere ESATTAMENTE: {forced_action}"""

    print("=" * 60)
    print("🤖 DOMANDA ALL'LLM:")
    print("=" * 60)
    print(full_prompt)
    print("=" * 60)
    
    # Chiama Ollama
    print("🤖 LLM sta analizzando...")
    
    payload = {
        'model': 'llama3.2:3b',
        'prompt': full_prompt,
        'stream': False,
        'options': {
            'temperature': 0.7,  # Aumentata per più creatività
            'num_predict': 50,
            'top_p': 0.9,       # Aggiunta diversità
            'repeat_penalty': 1.2  # Penalità per ripetizioni
        }
    }
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json=payload, timeout=30)
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
            
        # Parsing semplificato - cerca formato specifico
        if llm_response.startswith("CLICK:"):
            target = llm_response[6:].strip()
            # Rimuovi punteggiatura finale che l'LLM potrebbe aggiungere
            target = target.rstrip('.,!?;')
            action_type = "click"
            
        elif llm_response.startswith("FILL:"):
            parts = llm_response[5:].split(":", 2)
            if len(parts) >= 2:
                target = parts[0].strip()
                value = parts[1].strip()
                action_type = "type"
            elif len(parts) == 1:
                # Solo il nome del campo, usiamo un valore di default
                target = parts[0].strip()
                value = "Mario Rossi"  # Default per campi nome
                if "lavoro" in target.lower() or "work" in target.lower():
                    value = "Sviluppatore Software"
                elif "telefono" in target.lower() or "phone" in target.lower():
                    value = "3331234567"
                elif "email" in target.lower():
                    value = "mario.rossi@email.com"
                action_type = "type"
                print(f"🤖 Campo '{target}' senza valore specificato, uso default: '{value}'")
            else:
                print("❌ Formato FILL non valido")
                return
        else:
            # Fallback: cerca nel testo pattern più flessibili
            import re
            
            # Cerca pattern CLICK: nel testo
            click_match = re.search(r'CLICK:([^(\n]+)', llm_response)
            if click_match:
                target = click_match.group(1).strip()
                # Rimuovi punteggiatura finale
                target = target.rstrip('.,!?;')
                action_type = "click"
                print(f"🔍 Estratto: CLICK:'{target}'")
            else:
                # Cerca pattern FILL: nel testo
                fill_match = re.search(r'FILL:(\w+):([^(\n]+)', llm_response)
                if fill_match:
                    target = fill_match.group(1).strip()
                    value = fill_match.group(2).strip().rstrip('.,!?;')
                    action_type = "type"
                    print(f"🔍 Estratto: FILL:'{target}' con '{value}'")
                else:
                    # Ultimo tentativo: cerca menziones di bottoni specifici
                    buttons_mentioned = []
                    for btn in available_buttons:
                        if btn.lower() in llm_response.lower():
                            buttons_mentioned.append(btn)
                    
                    if buttons_mentioned:
                        target = buttons_mentioned[0]
                        action_type = "click"
                        print(f"🎯 Rilevato bottone menzionato: '{target}'")
                    else:
                        print(f"\n💭 L'LLM ha risposto: {llm_response}")
                        print("❓ Formato non riconosciuto. Atteso CLICK:nome o FILL:campo:valore")
                        return
        
        if target and action_type == "type" and value:
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
