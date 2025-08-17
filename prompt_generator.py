#!/usr/bin/env python3
"""
LogiDroid Prompt Generator
Genera prompt semplici per LLM basati su dati JSON dell'interfaccia Android
"""

import json
import sys

def generate_simple_prompt(json_file: str) -> str:
    """Genera un prompt semplice che mostra gli elementi disponibili"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        raise Exception(f"Errore nel caricamento JSON: {e}")
    
    # Separa bottoni e campi di testo
    buttons = []
    text_fields = []
    
    for elem in data['elements']:
        if elem['editable']:  # Campo di testo
            label = elem.get('label', elem.get('text', 'Campo senza nome'))
            text_fields.append(label)
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
    
    # Genera prompt semplice
    prompt = "Elementi disponibili in questa schermata:\n\n"
    
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
    
    prompt += "Che azione vuoi eseguire? Specifica se vuoi:\n"
    prompt += "- Compilare un campo (es. 'compila Nome con Mario Rossi')\n"
    prompt += "- Premere un bottone (es. 'premi Salva')\n"
    
    return prompt

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 prompt_generator.py <json_file>")
        print("\nGenera un prompt semplice che mostra gli elementi disponibili nella schermata")
        return
    
    json_file = sys.argv[1]
    
    try:
        prompt = generate_simple_prompt(json_file)
        print(prompt)
        
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
