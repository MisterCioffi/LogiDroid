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
    """Carica la cronologia delle azioni precedenti"""
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def get_screen_context(data: dict) -> str:
    """Determina il contesto della schermata corrente"""
    text_fields = []
    buttons = []
    
    for elem in data['elements']:
        if elem['editable']:
            label = elem.get('label', elem.get('text', 'Campo'))
            text_fields.append(label)
        elif elem['clickable']:
            button_text = elem.get('text', '').strip()
            if button_text:
                buttons.append(button_text)
    
    context = ""
    if "Nome" in text_fields or "Cognome" in text_fields:
        context = "Schermata di creazione contatto"
    elif "Cerca" in buttons or "cerca" in str(buttons).lower():
        context = "Schermata di ricerca"
    elif any("salva" in btn.lower() for btn in buttons):
        context = "Schermata di conferma/salvataggio"
    else:
        context = f"Schermata con {len(buttons)} bottoni disponibili"
    
    return context

def generate_simple_prompt(json_file: str, is_first_iteration: bool = False) -> str:
    """Genera un prompt semplice che mostra gli elementi disponibili"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        raise Exception(f"Errore nel caricamento JSON: {e}")
    
    # Carica la cronologia delle azioni precedenti
    history = load_action_history()
    screen_context = get_screen_context(data)
    
    # Separa bottoni e campi di testo
    buttons = []
    text_fields = []
    
    for elem in data['elements']:
        if elem['editable']:  # Campo di testo VERO
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
    
    # SEMPRE carica le istruzioni complete (essenziale per LLM stateless)
    with open('complete_instructions.txt', 'r', encoding='utf-8') as f:
        prompt = f.read() + "\n\n"
    
    # Aggiungi cronologia solo se NON è la prima iterazione
    if not is_first_iteration and history:
        prompt += "🚫 ULTIME 10 AZIONI (NON RIPETERE QUESTE):\n"
        for action_data in history[-10:]:
            action = action_data.get('action', 'N/A')
            prompt += f"• {action}\n"
        prompt += "\n"
    
    prompt += "📱 INTERFACCIA:\n\n"
    
    if text_fields:
        prompt += "CAMPI:\n"
        for i, field in enumerate(text_fields[:5], 1):  # Max 5 campi
            # Rimuovi coordinate e semplifica
            clean_field = field.split(' [pos:')[0]
            prompt += f"{i}. {clean_field}\n"
        prompt += "\n"
    
    if buttons:
        prompt += "BOTTONI:\n"
        for i, button in enumerate(buttons[:8], 1):  # Max 8 bottoni
            prompt += f"{i}. {button}\n"
        prompt += "\n"
     
    return prompt

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 prompt_generator.py <json_file> [is_first_iteration]")
        print("\nGenera un prompt che mostra gli elementi disponibili nella schermata")
        print("con memoria delle azioni precedenti per mantenere il filo conduttore")
        return
    
    json_file = sys.argv[1]
    is_first_iteration = len(sys.argv) > 2 and sys.argv[2].lower() == 'true'
    
    try:
        # Non salvare più qui - il salvataggio avviene solo in llm_local.py
        # per evitare duplicazioni
        
        prompt = generate_simple_prompt(json_file, is_first_iteration)
        print(prompt)
        
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
