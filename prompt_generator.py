#!/usr/bin/env python3
"""
LogiDroid Prompt Generator
Genera prompt semplici per LLM basati su dati JSON dell'interfaccia Android
Con sistema di memoria delle azioni precedenti per mantenere il filo conduttore
"""

import json
import sys
import os
from datetime import datetime

def load_action_history(history_file: str = "prompts/action_history.json") -> list:
    """Carica la cronologia delle azioni precedenti"""
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_action_to_history(action: str, screen_info: str, history_file: str = "prompts/action_history.json"):
    """Salva un'azione nella cronologia"""
    try:
        # Crea la directory se non esiste
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        history = load_action_history(history_file)
        
        # Aggiungi la nuova azione
        history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "screen": screen_info
        })
        
        # Mantieni solo le ultime 10 azioni per non appesantire
        if len(history) > 10:
            history = history[-10:]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Errore nel salvare cronologia: {e}", file=sys.stderr)

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

def generate_simple_prompt(json_file: str) -> str:
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
        if elem['editable']:  # Campo di testo
            label = elem.get('label', elem.get('text', 'Campo senza nome'))
            current_value = elem.get('text', '').strip()
            
            # Per campi duplicati, aggiungi un identificatore univoco
            field_id = f"{label}"
            if current_value:
                field_id += f" (COMPILATO: '{current_value}')"
            else:
                field_id += f" (VUOTO)"
            
            # Aggiungi anche coordinate per debugging
            bounds = elem.get('bounds', {})
            x, y = bounds.get('x', 0), bounds.get('y', 0)
            field_id += f" [pos:{x},{y}]"
            
            text_fields.append(field_id)
        elif elem['clickable']:  # Tutti i bottoni clickable
            # Usa il testo se presente, altrimenti usa la descrizione, altrimenti l'ID
            button_text = elem.get('text', '').strip()
            if not button_text:
                content_desc = elem.get('content_desc', '').strip()
                if content_desc:
                    button_text = f"{content_desc}"
                else:
                    resource_id = elem.get('resource_id', '')
                    if resource_id:
                        button_text = f"[{resource_id.split(':')[-1]}]"
                    else:
                        button_text = "[bottone senza nome]"
            buttons.append(button_text)
    
    # Genera prompt con contesto storico
    prompt = "🤖 ESPLORAZIONE AUTONOMA ANDROID - MANTIENI IL FILO CONDUTTORE\n\n"
    
    # Aggiungi cronologia se presente
    if history:
        prompt += "📱 AZIONI PRECEDENTI (mantieni la logica!):\n"
        for i, action_data in enumerate(history[-5:], 1):  # Mostra solo le ultime 5
            action = action_data.get('action', 'N/A')
            screen = action_data.get('screen', 'N/A')
            prompt += f"{i}. {action} → {screen}\n"
        prompt += "\n"
    
    prompt += f"📍 SCHERMATA ATTUALE: {screen_context}\n\n"
    
    if text_fields:
        prompt += "CAMPI DI TESTO:\n"
        for i, field in enumerate(text_fields, 1):
            prompt += f"{i}. {field}\n"
        prompt += "\n"
    
    if buttons:
        prompt += "BOTTONI:\n"
        for i, button in enumerate(buttons, 1):
            prompt += f"{i}. {button}\n"
        prompt += "\n"
    
    # Istruzioni specifiche per mantenere il filo conduttore
    prompt += "🎯 OBIETTIVO: Esplora l'app in modo logico e coerente\n"
    prompt += "• Ricorda le azioni precedenti e continua il percorso\n"
    prompt += "• Se hai appena compilato campi, considera di salvare\n"
    prompt += "• Se sei in una lista, prova a aprire elementi\n"
    prompt += "• Evita di ripetere sempre le stesse azioni\n"
    prompt += "• Esplora diverse sezioni dell'app\n\n"
    
    prompt += "Specifica l'azione da eseguire:\n"
    prompt += "- CLICK:nome_bottone (per premere un bottone)\n"
    prompt += "- FILL:nome_campo:valore (per compilare un campo)\n"
    
    return prompt

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 prompt_generator.py <json_file> [azione_precedente]")
        print("\nGenera un prompt che mostra gli elementi disponibili nella schermata")
        print("con memoria delle azioni precedenti per mantenere il filo conduttore")
        return
    
    json_file = sys.argv[1]
    previous_action = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Se c'è un'azione precedente, salvala nella cronologia
        if previous_action:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            screen_context = get_screen_context(data)
            save_action_to_history(previous_action, screen_context)
        
        prompt = generate_simple_prompt(json_file)
        print(prompt)
        
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
