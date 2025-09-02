#!/usr/bin/env python3
"""
LogiDroid Prompt Generator
Genera prompt semplici per LLM basati su dati JSON dell'interfaccia Android
Con sistema di memoria delle azioni precedenti per mantenere il filo conduttore
"""

import json
import sys
import os
import subprocess
import re

def load_action_history(history_file: str = "test/prompts/action_history.json") -> list:
    """Carica la cronologia delle azioni precedenti dal file history_file"""
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def get_current_activity():
    """Rileva l'Activity corrente tramite ADB con metodi multipli"""
    try:
        # Metodo 1: Focus corrente
        result = subprocess.run(
            ["adb", "shell", "dumpsys", "activity", "activities"],
            capture_output=True, text=True, timeout=10
        )
        
        # Cerca il pattern dell'Activity corrente
        for line in result.stdout.split('\n'):
            if 'mCurrentFocus' in line or 'mFocusedActivity' in line:
                # Estrae il nome dell'Activity dal pattern
                # Esempio: mCurrentFocus=Window{abc123 u0 com.example.app/com.example.MainActivity}
                match = re.search(r'([a-zA-Z0-9_.]+)/([a-zA-Z0-9_.]+Activity)', line)
                if match:
                    return f"{match.group(1)}/{match.group(2)}"
        
        # Metodo 2: Lista attività correnti
        for line in result.stdout.split('\n'):
            if 'TaskRecord' in line and 'A=' in line:
                match = re.search(r'A=([a-zA-Z0-9_.]+/[a-zA-Z0-9_.]+Activity)', line)
                if match:
                    return match.group(1)
        
        # Metodo 3: Top Activity
        result2 = subprocess.run(
            ["adb", "shell", "dumpsys", "activity", "top"],
            capture_output=True, text=True, timeout=10
        )
        
        for line in result2.stdout.split('\n'):
            if 'ACTIVITY' in line and '/' in line:
                match = re.search(r'([a-zA-Z0-9_.]+)/([a-zA-Z0-9_.]+)', line)
                if match:
                    return f"{match.group(1)}/{match.group(2)}"
        
        # Metodo 4: Package name + Screen fingerprint
        package_result = subprocess.run(
            ["adb", "shell", "dumpsys", "window", "windows"],
            capture_output=True, text=True, timeout=10
        )
        
        current_package = "unknown"
        for line in package_result.stdout.split('\n'):
            if 'mCurrentFocus' in line:
                package_match = re.search(r'([a-zA-Z0-9_.]+)/', line)
                if package_match:
                    current_package = package_match.group(1)
                    break
        
        # Se il package è noto, genera un ID schermata basato sui contenuti
        return generate_screen_fingerprint(current_package)
                    
    except Exception as e:
        print(f"⚠️ Errore nel rilevamento Activity: {e}", file=sys.stderr)
    
    return generate_screen_fingerprint("unknown")

def generate_screen_fingerprint(package_name):
    """Genera un identificativo unico per la schermata corrente basato sui contenuti UI"""
    try:
        # Usa l'ultimo file JSON generato per creare un fingerprint
        json_files = []
        json_dir = "test/json"
        
        if os.path.exists(json_dir):
            for file in os.listdir(json_dir):
                if file.startswith("result_current_") and file.endswith(".json"):
                    json_files.append(os.path.join(json_dir, file))
        
        if json_files:
            # Prendi il file più recente
            latest_json = max(json_files, key=os.path.getctime)
            
            with open(latest_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Crea fingerprint basato sui primi 3 elementi visibili
                elements = data.get('elements', [])
                visible_elements = []
                
                for elem in elements[:5]:  # Prime 5 per essere sicuri
                    text = elem.get('text', '').strip()
                    content_desc = elem.get('content_desc', '').strip()
                    resource_id = elem.get('resource_id', '').strip()
                    
                    if text:
                        visible_elements.append(text)
                    elif content_desc:
                        visible_elements.append(content_desc)
                    elif resource_id:
                        visible_elements.append(resource_id.split(':')[-1])
                
                if visible_elements:
                    # Crea ID unico basato sui contenuti
                    content_hash = hash(tuple(visible_elements[:3]))  # Usa primi 3 elementi
                    return f"{package_name}/Screen_{abs(content_hash) % 10000}"
        
        # Fallback: usa timestamp
        import time
        return f"{package_name}/Screen_{int(time.time()) % 10000}"
        
    except Exception as e:
        print(f"⚠️ Errore nel fingerprinting: {e}", file=sys.stderr)
        return f"{package_name}/UnknownScreen"

def get_all_activities_from_apk(apk_path: str = "test/coverage/app.apk"):
    """Estrae tutte le Activity dall'APK usando aapt o mantiene lista manuale"""
    try:
        if not os.path.exists(apk_path):
            print(f"⚠️ APK non trovato: {apk_path}", file=sys.stderr)
            # Fallback: usa lista manuale se esistente
            return load_manual_activities_list()
            
        # Prova prima con aapt
        try:
            result = subprocess.run(
                ["aapt", "dump", "badging", apk_path],
                capture_output=True, text=True, timeout=30
            )
            
            activities = []
            for line in result.stdout.split('\n'):
                if 'activity' in line.lower():
                    # Estrae nomi Activity dal dump aapt
                    match = re.search(r"name='([^']+)'", line)
                    if match:
                        activities.append(match.group(1))
                        
            if activities:
                return list(set(activities))  # Rimuove duplicati
                
        except FileNotFoundError:
            print("⚠️ aapt non installato, usando rilevamento dinamico...", file=sys.stderr)
            
        # Fallback: usa lista manuale o rilevamento dinamico
        return load_manual_activities_list()
        
    except Exception as e:
        print(f"⚠️ Errore nell'analisi APK: {e}", file=sys.stderr)
        return load_manual_activities_list()

def load_manual_activities_list(file_path: str = "test/coverage/all_activities.txt"):
    """Carica lista Activity da file manuale o crea lista dinamica"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                activities = [line.strip() for line in f.readlines() if line.strip()]
                if activities:
                    return activities
    except Exception:
        pass
    
    # Se non esiste lista manuale, restituisce activity base rilevate dinamicamente
    visited = load_visited_activities()
    if visited:
        return visited  # Usa quelle già visitate come riferimento base
    
    # Ultima risorsa: lista vuota (coverage sarà 100% quando si inizia ad esplorare)
    return []

def load_visited_activities(file_path: str = "test/coverage/explored_activities.txt"):
    """Carica la lista delle Activity già visitate"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
    except Exception:
        pass
    return []

def save_current_activity(activity: str, file_path: str = "test/coverage/explored_activities.txt"):
    """Salva l'Activity corrente nella lista delle visitate (se non già presente)"""
    try:
        # ✨ FILTRO PACKAGE: Carica il package target
        package_name = ""
        try:
            with open("test/coverage/current_package.txt", 'r') as f:
                package_name = f.read().strip()
        except Exception:
            pass
        
        # ✨ FILTRO 1: Non salvare se non appartiene al package target
        if package_name and not activity.startswith(package_name):
            return False
            
        # ✨ FILTRO 2: Non salvare activity del launcher
        if "launcher" in activity.lower():
            return False
        
        visited = load_visited_activities(file_path)
        
        # ✨ MIGLIORAMENTO: Non salvare Unknown/UnknownActivity duplicati
        if activity == "Unknown/UnknownActivity":
            # Se esiste già una entry Unknown, non aggiungerne altre
            if any("Unknown" in v for v in visited):
                return False
        
        # Non salvare se già presente o se è veramente unknown
        if activity not in visited and not activity.endswith("/UnknownScreen"):
            # Crea directory se non esiste
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"{activity}\n")
            return True
    except Exception as e:
        print(f"⚠️ Errore nel salvataggio Activity: {e}", file=sys.stderr)
    return False

def calculate_activity_coverage():
    """Calcola la percentuale di coverage delle Activity"""
    try:
        all_activities = get_all_activities_from_apk()
        visited_activities = load_visited_activities()
        
        # ✨ DEBUG: Mostra cosa stiamo contando
        print(f"🔍 Debug Coverage:", file=sys.stderr)
        print(f"   Total activities trovate: {len(all_activities)}", file=sys.stderr)
        print(f"   Visited activities: {len(visited_activities)}", file=sys.stderr)
        
        if len(visited_activities) > 0:
            print(f"   Lista visited:", file=sys.stderr)
            for i, activity in enumerate(visited_activities):
                print(f"     {i+1}. {activity}", file=sys.stderr)
        
        if not all_activities:
            return 0, 0, 0, "APK non disponibile"
        
        # Salva la lista completa delle Activity per riferimento
        save_all_activities_reference(all_activities)
        
        # ✨ MIGLIORAMENTO: Rimuovi duplicati e conta correttamente
        unique_visited = list(set(visited_activities))  # Rimuove duplicati
        
        # Se ci sono Unknown, conta come 1 sola schermata
        unknown_count = sum(1 for activity in unique_visited if "Unknown" in activity)
        real_activities = [activity for activity in unique_visited if "Unknown" not in activity]
        
        # Conta: Unknown (max 1) + Activity reali
        effective_visited = len(real_activities) + min(unknown_count, 1)
        
        total = len(all_activities)
        percentage = (effective_visited / total) * 100 if total > 0 else 0
        
        print(f"   Effective visited (deduplicated): {effective_visited}", file=sys.stderr)
        print(f"   Coverage calcolata: {percentage:.1f}%", file=sys.stderr)
        
        return percentage, effective_visited, total, "OK"
        
    except Exception as e:
        return 0, 0, 0, f"Errore: {e}"

def save_all_activities_reference(activities: list, file_path: str = "test/coverage/all_activities.txt"):
    """Salva la lista completa delle Activity per riferimento"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            for activity in sorted(activities):
                f.write(f"{activity}\n")
    except Exception as e:
        print(f"⚠️ Errore nel salvataggio riferimento Activity: {e}", file=sys.stderr)

def generate_simple_prompt(json_file: str, is_first_iteration: bool = False) -> str:
    """Genera un prompt semplice che mostra gli elementi disponibili 
        suddividendo in bottoni e campi di testo"""
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        raise Exception(f"Errore nel caricamento JSON: {e}")
    
    # Carica la cronologia delle azioni precedenti
    history = load_action_history()
    
    # ✨ NUOVA FUNZIONALITÀ: Tracking Activity Coverage
    current_activity = get_current_activity()
    save_current_activity(current_activity)  # Salva se nuova
    
    # Calcola e mostra coverage delle Activity
    coverage_percentage, visited_count, total_count, status = calculate_activity_coverage()
    
    # Separa bottoni e campi di testo
    buttons = []
    text_fields = []
    
    for elem in data['elements']:
        if elem['editable']:  # Campo di testo editabile
            label = elem.get('label', elem.get('text', elem.get('content_desc', 'Campo')))
            current_value = elem.get('text', '').strip()
            resource_id = elem.get('resource_id', '').lower()
            
            # Determina il tipo di campo
            is_search = any(keyword in (label.lower() + resource_id) for keyword in ['search', 'ricerca', 'cerca', 'find'])
            
            if current_value:
                if is_search:
                    field_id = f"{label} (RICERCA COMPILATA: '{current_value[:20]}...' - USA ALTRO CAMPO)"
                else:
                    field_id = f"{label} (COMPILATO: '{current_value[:20]}...' - EVITA SE POSSIBILE)"
            else:
                if is_search:
                    field_id = f"{label} (RICERCA VUOTA - PREMI ENTER AUTOMATICO DOPO SCRITTURA)"
                else:
                    field_id = f"{label} (VUOTO)"
            
            text_fields.append(field_id)
        elif elem['clickable']:  # Bottoni clickable
            button_text = elem.get('text', '').strip()
            if not button_text:
                content_desc = elem.get('content_desc', '').strip()
                if content_desc:
                    button_text = content_desc
                    resource_id = elem.get('resource_id', '')
                    if resource_id:
                        button_text = f"[{resource_id.split(':')[-1]}]"
                    else:
                        button_text = "[bottone]"
            buttons.append(button_text)
    
    # SEMPRE carica le istruzioni complete 
    with open('complete_instructions.txt', 'r', encoding='utf-8') as f:
        prompt = f.read() + "\n\n"
    
    # ✨ AGGIUNGI INFORMAZIONI COVERAGE AL PROMPT
    prompt += "📊 STATO ESPLORAZIONE APP:\n"
    prompt += f"🎯 Activity corrente: {current_activity}\n"
    
    if status == "OK":
        prompt += f"📈 Coverage Activity: {coverage_percentage:.1f}% ({visited_count}/{total_count} esplorate)\n"
        
        # Indicatori visivi di progresso
        if coverage_percentage < 25:
            prompt += "🟥 COVERAGE BASSA - Esplora nuove sezioni!\n"
        elif coverage_percentage < 50:
            prompt += "🟨 COVERAGE MEDIA - Continua l'esplorazione!\n" 
        elif coverage_percentage < 75:
            prompt += "🟦 COVERAGE BUONA - Quasi completata!\n"
        else:
            prompt += "🟩 COVERAGE ALTA - Esplorazione quasi completa!\n"
    else:
        prompt += f"⚠️ Coverage Status: {status}\n"
    
    # ✨ AGGIUNGI LISTA ACTIVITY ESPLORATE
    visited_activities = load_visited_activities()
    if visited_activities:
        prompt += "\n🏃‍♂️ ACTIVITY GIÀ ESPLORATE:\n"
        for activity in visited_activities:
            # Mostra solo il nome della classe per brevità
            activity_name = activity.split('/')[-1] if '/' in activity else activity
            prompt += f"✅ {activity_name}\n"
        prompt += "🎯 OBIETTIVO: Esplora nuove sezioni non ancora visitate!\n"
    else:
        prompt += "\n🆕 PRIMA ESPLORAZIONE - Nessuna activity ancora visitata\n"
    
    prompt += "\n"
    
    # Aggiungi cronologia solo se NON è la prima iterazione
    if not is_first_iteration and history:
        prompt += "🚫 AZIONI RECENTI DA VARIARE:\n"
        recent_actions = history[-20:]  # Ultime 20 azioni per contesto molto ampio
        
        failed_actions = []
        successful_actions = []
        
        for action_data in recent_actions:
            action = action_data.get('action', 'N/A')
            success = action_data.get('success', True)  # Default True per retrocompatibilità
            
            if not success:
                failed_actions.append(action)
                prompt += f"❌ {action} (FALLITA - NON RIPETERE!)\n"
            else:
                successful_actions.append(action)
                prompt += f"• {action}\n"
        
        if failed_actions:
            prompt += f"\n🚨 ATTENZIONE: {len(failed_actions)} azioni fallite sopra - NON ripeterle!\n"
        
        prompt += "\n⚠️ Prova a scegliere qualcosa di diverso se possibile.\n\n"
    
    prompt += "📱 COMANDI DISPONIBILI - SCEGLI UNO:\n\n"

    command_options = [] # Lista dei comandi disponibili
    option_letter = 'A'
    
    # Aggiunta del tasto BACK tra le opzioni
    command_options.append("BACK")
    prompt += f"{option_letter}. BACK (torna alla schermata precedente)\n"
    option_letter = chr(ord(option_letter) + 1)
    
    # Aggiungi comandi CLICK per i bottoni con prioritizzazione intelligente
    if buttons:
        # Prioritizza bottoni importanti
        priority_keywords = ["salva", "save", "ok", "conferma", "annulla", "cancel", "indietro", "back", "fine", "done"]
        
        # Separa bottoni prioritari e normali
        priority_buttons = []
        normal_buttons = []
        
        for button in buttons:
            button_lower = button.lower()
            if any(keyword in button_lower for keyword in priority_keywords):
                priority_buttons.append(button)
            else:
                normal_buttons.append(button)
        
        # Combina prioritari + normali, senza limite (mostra tutti)
        selected_buttons = priority_buttons + normal_buttons
        
        for button in selected_buttons:  # Mostra tutti i bottoni
            command = f"CLICK:{button}"
            command_options.append(command)
            prompt += f"{option_letter}. {command}\n"
            option_letter = chr(ord(option_letter) + 1)
    
    # Aggiungi comandi FILL per i campi di testo
    if text_fields:
        for field in text_fields[:5]:  # Max 5 campi
            clean_field = field.split(' (')[0]  # Rimuovi (VUOTO)/(COMPILATO)
            
            # Aggiungi solo opzione per testo personalizzato 
            if option_letter <= 'Z':
                command = f"FILL_CUSTOM:{clean_field}"
                command_options.append(command)
                prompt += f"{option_letter}. FILL_CUSTOM:{clean_field} (scrivi {option_letter}:TuoTesto)\n"
                option_letter = chr(ord(option_letter) + 1)

    prompt += f"\n💡 RISPOSTA RICHIESTA: Scrivi solo UNA lettera (A-{chr(ord(option_letter)-1)})\n"
    
    prompt += "⚠️ NON aggiungere spiegazioni, scrivi solo la lettera scelta.\n\n"
     
    return prompt

def main():
    if len(sys.argv) < 2:
        print("Utilizza il comando: python3 prompt_generator.py <json_file> [is_first_iteration]")
        print("\nGenera un prompt che mostra gli elementi disponibili nella schermata")
        print("con memoria delle azioni precedenti per mantenere il filo conduttore")
        return
    
    json_file = sys.argv[1]
    # Se il secondo argomento è 'true', significa che è la prima iterazione e non abbiamo memoria
    is_first_iteration = len(sys.argv) > 2 and sys.argv[2].lower() == 'true'
    
    try:
        prompt = generate_simple_prompt(json_file, is_first_iteration)
        print(prompt)

    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
