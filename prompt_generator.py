#!/usr/bin/env python3
"""
LogiDroid Prompt Generator
Genera prompt semplici per LLM basati su dati JSON dell'interfaccia Android
Con sistema di memoria delle azioni precedenti per mantenere il filo conduttore
"""

import json
import sys
import os

def load_action_history(history_file: str = "test/prompts/action_history.json") -> list:
    """Carica la cronologia delle azioni precedenti dal file history_file"""
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []

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
    
    # Separa bottoni e campi di testo
    buttons = []
    text_fields = []
    
    for elem in data['elements']:
        if elem['editable']:  # Campo di testo editabile
            label = elem.get('label', elem.get('text', elem.get('content_desc', 'Campo')))
            current_value = elem.get('text', '').strip()
            
            if current_value:
                field_id = f"{label} (COMPILATO)"
            else:
                field_id = f"{label} (VUOTO)"
            
            text_fields.append(field_id)
        elif elem['clickable']:  # Bottoni clickable
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
            buttons.append(button_text)
    
    # SEMPRE carica le istruzioni complete 
    with open('complete_instructions.txt', 'r', encoding='utf-8') as f:
        prompt = f.read() + "\n\n"
    
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
