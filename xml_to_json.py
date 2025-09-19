#!/usr/bin/env python3
"""
LogiDroid Simple - Convertitore XML UIAutomator → JSON pulito
Estrae solo pulsanti e campi di testo con etichette automatiche
"""

import xml.etree.ElementTree as ET
import json
import sys
import os
from datetime import datetime

# Funzione per analizzare le coordinate
def parse_bounds(bounds_str):
    """
    Riceve in ingresso una stringa di coordinate come '[x1,y1][x2,y2]'
    e restituisce un dizionario con le coordinate centrali e dimensioni.
    Se la stringa è vuota o non valida, restituisce None.
    """
    if not bounds_str:
        return None
    try:
        coords = bounds_str.replace('[', '').replace(']', ',').split(',')
        x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
        return {
            'x': (x1 + x2) // 2,  # centro bottone coordinate x
            'y': (y1 + y2) // 2,  # centro bottone coordinate y
            'width': x2 - x1,
            'height': y2 - y1
        }
    except:
        return None

def has_nearby_edittext(elements, target_bounds, min_distance=100):
    """Controlla se c'è un altro EditText nelle vicinanze di target_bounds"""
    if not target_bounds:
        return False
    
    target_center_y = target_bounds['y'] + target_bounds['height'] // 2
    
    for elem in elements:
        if elem.get('editable') and elem.get('bounds'):
            elem_bounds = elem['bounds']
            elem_center_y = elem_bounds['y'] + elem_bounds['height'] // 2
            
            # Se c'è un EditText più grande nella stessa area verticale
            if (abs(target_center_y - elem_center_y) < min_distance and 
                elem_bounds['width'] > target_bounds['width'] * 5):  # Almeno 5 volte più grande
                return True
    return False

def extract_elements(node, elements, text_nodes):
    """Estrae elementi utili dal nodo XML"""
    attrs = node.attrib
    bounds = parse_bounds(attrs.get('bounds', ''))
    
    if not bounds:  # Ignora nodi senza posizione
        for child in node:
            extract_elements(child, elements, text_nodes)
        return
    
    text = attrs.get('text', '').strip() #testo del nodo
    resource_id = attrs.get('resource-id', '').strip() #identificatore univoco del nodo
    hint = attrs.get('hint', '').strip() # suggerimento per il campo di testo
    content_desc = attrs.get('content-desc', '').strip() # descrizione del contenuto per accessibilità
    clickable = attrs.get('clickable', 'false') == 'true' # è cliccabile?

    # Normalizziamo il class_name per classificare il nodo in:
    # - pulsante (button)
    # - campo di testo (edittext/autocomplete/textinput)
    # - etichetta (textview)
    class_name = attrs.get('class', '').lower()
    is_button = ('button' in class_name or clickable) and not any(field_type in class_name for field_type in ['edittext', 'autocomplete', 'textinput'])
    is_edittext = any(field_type in class_name for field_type in ['edittext', 'autocomplete', 'textinput'])
    is_textview = 'textview' in class_name and text and not clickable and not is_edittext
    
    # Se è un pulsante clickable senza testo, cerca testo nei figli
    if is_button and clickable and not text:
        child_text = find_text_in_children(node)
        if child_text:
            text = child_text
    
    # Raccogli elementi utili
    if is_button or is_edittext:
        # ✨ FILTRO INTELLIGENTE MIGLIORATO: Distingui tab navigation da menu dropdown
        should_filter = False
        
        # ✨ FILTRO MIGLIORATO: Non filtrare se ha content_desc valido
        if is_button and not resource_id and (not text or len(text.strip()) < 2) and (not content_desc or len(content_desc.strip()) < 2):
            should_filter = True
            filter_reason = "senza ID, senza testo e senza content_desc"
        elif is_button and not resource_id and text and content_desc == text:
            # Tab navigation: content-desc uguale al testo (es. content-desc="Playlist", text="Playlist")
            should_filter = True  
            filter_reason = f"tab navigation '{text}'"
        
        if should_filter:
            print(f"🚫 FILTRATO elemento decorativo {filter_reason}: {text or 'NO_TEXT'}", file=sys.stderr)
        else:
            # Elementi validi: con resource_id, campi di testo, menu dropdown, o pulsanti con testo significativo
            elements.append({
                'type': 'button' if is_button else 'edit_text',
                'text': text,
                'hint': hint,
                'content_desc': content_desc,
                'resource_id': resource_id,
                'bounds': bounds,
                'clickable': clickable,
                'editable': is_edittext
            })
    
    if is_textview and bounds:
        text_nodes.append({'text': text, 'bounds': bounds})
    
    # Processa figli
    for child in node:
        extract_elements(child, elements, text_nodes)

def find_text_in_children(node, max_depth=3):
    """Cerca ricorsivamente il primo testo significativo nei nodi figli"""
    if max_depth <= 0:
        return None
        
    for child in node:
        child_text = child.attrib.get('text', '').strip()
        if child_text and len(child_text) >= 2:
            return child_text
        
        # Ricerca ricorsiva nei nipoti
        grandchild_text = find_text_in_children(child, max_depth - 1)
        if grandchild_text:
            return grandchild_text
    
    return None

def find_label_for_edittext(edittext, text_nodes):
    """Trova l'etichetta più vicina per un campo EditText"""
    if not edittext['bounds']:
        return "Campo senza etichetta"
    
    edit_pos = edittext['bounds']
    best_label = None
    min_distance = float('inf')
    
    for text_node in text_nodes:
        text_pos = text_node['bounds']
        
        # Calcola distanza (priorità a quelli sopra)
        v_dist = abs(text_pos['y'] - edit_pos['y'])
        h_dist = abs(text_pos['x'] - edit_pos['x'])
        
        # Deve essere vicino e preferibilmente sopra
        if v_dist < 150 and h_dist < 300:
            distance = v_dist + (h_dist * 0.5)  # Peso maggiore alla distanza verticale
            if text_pos['y'] <= edit_pos['y']:  # Sopra
                distance *= 0.7  # Bonus per elementi sopra
            
            if distance < min_distance:
                min_distance = distance
                best_label = text_node['text']
    
    return best_label or edittext['hint'] or edittext['text'] or "Campo senza etichetta"

def find_label_for_button(button, text_nodes):
    """Trova l'etichetta per un pulsante senza testo"""
    if button['text']:
        return button['text']
    
    if not button['bounds']:
        return ""
    
    btn_pos = button['bounds']
    
    # Cerca TextView molto vicino al pulsante
    for text_node in text_nodes:
        text_pos = text_node['bounds']
        
        # Distanza molto piccola (stesso elemento)
        distance = abs(text_pos['x'] - btn_pos['x']) + abs(text_pos['y'] - btn_pos['y'])
        if distance <= 50:
            return text_node['text']
    
    return ""

def xml_to_json(xml_file):
    """Converte XML UIAutomator in JSON pulito"""
    try:
        tree = ET.parse(xml_file) #dato un xml fornise un albero formato da nodi
        root = tree.getroot()  #ottiene il nodo radice dell'albero
        
        # Estrai tutti gli elementi
        elements = [] #lista di bottoni o campi di testo
        text_nodes = [] #lista di nodi di testo (TextView)
        
        for child in root:
            extract_elements(child, elements, text_nodes)
        
        # ✨ FILTRO POST-PROCESSING: Gestione intelligente e universale dei duplicati
        # Fase 1: Analisi preliminare - identifica i pattern
        large_edittexts = {}  # label -> lista di EditText grandi
        small_edittexts = {}  # label -> lista di EditText piccoli  
        clickable_buttons = {}  # label -> lista di bottoni clickable
        
        for i, element in enumerate(elements):
            if element.get('bounds'):
                width = element['bounds']['width']
                height = element['bounds']['height']
                
                if element.get('editable'):
                    # Calcola label temporaneo
                    temp_label = find_label_for_edittext(element, text_nodes)
                    
                    if width > 100 and height > 50:  # EditText "grandi" (veri campi)
                        if temp_label not in large_edittexts:
                            large_edittexts[temp_label] = []
                        large_edittexts[temp_label].append((i, element))
                    elif width <= 10 and height <= 10:  # EditText "piccoli" (helper o campi dinamici)
                        if temp_label not in small_edittexts:
                            small_edittexts[temp_label] = []
                        small_edittexts[temp_label].append((i, element))
                
                elif element.get('clickable') and element.get('text'):
                    # Bottoni clickable
                    button_label = element['text']
                    if button_label not in clickable_buttons:
                        clickable_buttons[button_label] = []
                    clickable_buttons[button_label].append((i, element))
        
        # Fase 2: Identifica campi che sono bottoni di selezione (non input di testo)
        selection_field_keywords = ['gruppo', 'gruppi', 'categoria', 'categorie', 'tipo', 'selezione', 
                                   'scelta', 'opzione', 'lista', 'menu', 'preferenze', 'impostazioni',
                                   'annulla', 'salva', 'ok', 'conferma', 'chiudi', 'indietro']
        
        # Fase 3: Applica logica di filtro universale
        indices_to_remove = set()
        
        # Regola 1: Se esiste EditText grande + EditText piccolo con stesso label → rimuovi piccolo (è helper)
        for label in large_edittexts:
            if label in small_edittexts:
                print(f"🔍 Trovato EditText grande + piccolo per '{label}' - rimuovo helper piccolo", file=sys.stderr)
                for idx, elem in small_edittexts[label]:
                    bounds = elem['bounds']
                    indices_to_remove.add(idx)
                    print(f"🚫 FILTRATO EditText helper '{label}' ({bounds['width']}x{bounds['height']}px) - {elem.get('resource_id', 'NO_ID')}", file=sys.stderr)
        
        # Regola 2: Per campi di selezione, mantieni solo il bottone clickable
        for label in small_edittexts:
            label_lower = label.lower()
            is_selection_field = any(keyword in label_lower for keyword in selection_field_keywords)
            
            if is_selection_field and label in clickable_buttons:
                print(f"🔍 '{label}' è un campo di selezione - rimuovo EditText, mantengo bottone", file=sys.stderr)
                for idx, elem in small_edittexts[label]:
                    bounds = elem['bounds']
                    indices_to_remove.add(idx)
                    print(f"🚫 FILTRATO EditText di selezione '{label}' ({bounds['width']}x{bounds['height']}px) - {elem.get('resource_id', 'NO_ID')}", file=sys.stderr)
        
        # Regola 3: Per campi di input normali, rimuovi bottoni duplicati se c'è EditText piccolo
        for label in small_edittexts:
            label_lower = label.lower()
            is_selection_field = any(keyword in label_lower for keyword in selection_field_keywords)
            
            if not is_selection_field and label in clickable_buttons and label not in large_edittexts:
                print(f"🔍 '{label}' è un campo di input - rimuovo bottoni duplicati, mantengo EditText", file=sys.stderr)
                for idx, elem in clickable_buttons[label]:
                    bounds = elem['bounds']
                    indices_to_remove.add(idx)
                    print(f"🚫 FILTRATO Button duplicato '{label}' ({bounds['width']}x{bounds['height']}px) - {elem.get('resource_id', 'NO_ID')}", file=sys.stderr)
        
        # Rimuovi gli elementi identificati come duplicati
        filtered_elements = [elem for i, elem in enumerate(elements) if i not in indices_to_remove]
        elements = filtered_elements
        
        # Aggiungi etichette automatiche
        for element in elements:
            if element['editable']:
                # ✨ MIGLIORAMENTO: Se l'EditText ha un testo significativo che non è un placeholder, usalo come label
                element_text = element.get('text', '').strip()
                calculated_label = find_label_for_edittext(element, text_nodes)
                
                # Se il testo è significativo e diverso dal label calcolato, preferisci il testo
                if (element_text and len(element_text) > 1 and 
                    element_text != calculated_label and
                    not any(placeholder in element_text for placeholder in ['hint', 'placeholder', 'enter'])):
                    element['label'] = element_text
                else:
                    element['label'] = calculated_label
            else:
                element['text'] = find_label_for_button(element, text_nodes)
                element['label'] = element['text']
        
        # Risultato finale
        result = {
            'source_file': os.path.basename(xml_file),
            'timestamp': datetime.now().isoformat(),
            'total_buttons': len([e for e in elements if not e['editable']]),
            'total_inputs': len([e for e in elements if e['editable']]),
            'elements': elements
        }
        
        return result
        
    except Exception as e:
        raise Exception(f"Errore: {e}")

def main():
    """
    sys.argv[0] = nome dello script (xml_to_json_simple.py)
    sys.argv[1] = primo argomento dopo lo script (il file .xml)
    sys.argv[2] = eventuale secondo argomento (il file .json)
    """
    if len(sys.argv) < 2:
        print("Utilizza un comando del tipo: python3 xml_to_json_simple.py file.xml [output.json]")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else xml_file.replace('.xml', '.json')
    
    if not os.path.exists(xml_file):
        print(f"Errore: File {xml_file} non trovato")
        sys.exit(1)
    
    try:
        print(f"Convertendo {xml_file}...")
        result = xml_to_json(xml_file)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Completato: {output_file}")
        print(f"  - {result['total_buttons']} pulsanti")
        print(f"  - {result['total_inputs']} campi di testo")
        
    except Exception as e:
        print(f"Errore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
