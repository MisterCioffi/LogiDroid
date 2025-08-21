#!/usr/bin/env python3
"""
Esempio di come implementare streaming in llm_api.py
SOLO PER DIMOSTRAZIONE - non sostituisce il codice attuale
"""

import requests
import json

def call_llm_with_streaming(prompt):
    """Esempio di chiamata LLM con streaming"""
    
    payload = {
        'model': 'llama3.1:8b',
        'prompt': prompt,
        'stream': True,  # 🔄 STREAMING ATTIVO
        'options': {
            'temperature': 0.3,
            'num_predict': 30,
            'top_p': 0.8,
            'repeat_penalty': 1.1
        }
    }
    
    print("🤖 LLM sta analizzando...")
    print("💭 Risposta in tempo reale: ", end="", flush=True)
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate', 
            json=payload, 
            timeout=90,
            stream=True  # 🚨 IMPORTANTE: stream=True per requests
        )
        response.raise_for_status()
        
        full_response = ""
        
        # 🔄 Elabora ogni chunk in streaming
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    
                    # Estrai il pezzo di risposta
                    if 'response' in chunk:
                        token = chunk['response']
                        full_response += token
                        print(token, end='', flush=True)  # 📺 Mostra in tempo reale
                    
                    # Controlla se è finito
                    if chunk.get('done', False):
                        print()  # Nuova riga alla fine
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        print("=" * 60)
        print(f"✅ Risposta completa: {full_response}")
        print("=" * 60)
        
        return full_response.strip()
        
    except Exception as e:
        print(f"❌ Errore streaming: {e}")
        return None

# Test della funzione
if __name__ == "__main__":
    test_prompt = """
🤖 SISTEMA DI TEST AUTOMATICO ANDROID

INTERFACCIA CORRENTE:
BOTTONI:
1. Salva
2. Annulla

Scegli un'azione: CLICK:nome_bottone o FILL:campo:valore
    """
    
    result = call_llm_with_streaming(test_prompt)
    print(f"Risultato finale: {result}")
