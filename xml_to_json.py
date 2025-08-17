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

def parse_bounds(bounds_str):
    """Converte '[x1,y1][x2,y2]' in coordinate"""
    if not bounds_str:
        return None
    try:
        coords = bounds_str.replace('[', '').replace(']', ',').split(',')
        x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
        return {
            'x': (x1 + x2) // 2,  # centro x
            'y': (y1 + y2) // 2,  # centro y  
            'width': x2 - x1,
            'height': y2 - y1
        }
    except:
        return None

def extract_elements(node, elements=[], text_nodes=[]):
    """Estrae tutti gli elementi interessanti dall'XML"""
    attrs = node.attrib
    
    # Info base
    bounds = parse_bounds(attrs.get('bounds', ''))
    text = attrs.get('text', '').strip()
    resource_id = attrs.get('resource-id', '').strip()
    hint = attrs.get('hint', '').strip()
    clickable = attrs.get('clickable', 'false') == 'true'
    class_name = attrs.get('class', '').lower()
    
    # È un pulsante?
    is_button = ('button' in class_name or clickable) and 'edittext' not in class_name
    
    # È un campo di testo?
    is_edittext = 'edittext' in class_name
    
    # È un TextView con testo (possibile etichetta)?
    is_textview = 'textview' in class_name and text and not clickable
    
    # Raccogli elementi utili
    if is_button or is_edittext:
        elements.append({
            'type': 'button' if is_button else 'edit_text',
            'text': text,
            'hint': hint,
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
    
    return elements, text_nodes

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
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Estrai tutti gli elementi
        elements = []
        text_nodes = []
        
        for child in root:
            extract_elements(child, elements, text_nodes)
        
        # Aggiungi etichette automatiche
        for element in elements:
            if element['editable']:
                element['label'] = find_label_for_edittext(element, text_nodes)
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
    if len(sys.argv) < 2:
        print("Uso: python3 xml_to_json_simple.py file.xml [output.json]")
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
