#!/usr/bin/env python3
"""
LogiDroid UI Analyzer
Converte file XML di UIAutomator in JSON strutturati con informazioni dettagliate sui nodi
"""

import xml.etree.ElementTree as ET
import json
import sys
import os
import argparse
from pathlib import Path

class UIAutomatorAnalyzer:
    def __init__(self):
        self.node_counter = 0
        self.interactive_elements = []
        self.all_nodes = []  # NUOVO: mantiene tutti i nodi per analisi contesto
        self.ui_stats = {
            'total_nodes': 0,
            'clickable_nodes': 0,
            'focusable_nodes': 0,
            'scrollable_nodes': 0,
            'text_nodes': 0,
            'buttons': 0,
            'text_views': 0,
            'edit_texts': 0,
            'images': 0,
            'containers': 0
        }
    
    def parse_bounds(self, bounds_str):
        """Converte stringa bounds '[x1,y1][x2,y2]' in coordinate"""
        if not bounds_str:
            return None
        
        try:
            # Rimuovi parentesi e split
            coords = bounds_str.replace('[', '').replace(']', ',').split(',')
            return {
                'x1': int(coords[0]),
                'y1': int(coords[1]),
                'x2': int(coords[2]),
                'y2': int(coords[3]),
                'width': int(coords[2]) - int(coords[0]),
                'height': int(coords[3]) - int(coords[1]),
                'center_x': (int(coords[0]) + int(coords[2])) // 2,
                'center_y': (int(coords[1]) + int(coords[3])) // 2
            }
        except (ValueError, IndexError):
            return None
    
    def classify_node_type(self, class_name):
        """Classifica il tipo di nodo basandosi sulla classe"""
        class_name = class_name.lower()
        
        if 'button' in class_name:
            return 'button'
        elif 'textview' in class_name:
            return 'text_view'
        elif 'edittext' in class_name:
            return 'edit_text'
        elif 'imageview' in class_name:
            return 'image_view'
        elif 'checkbox' in class_name:
            return 'checkbox'
        elif 'radiobutton' in class_name:
            return 'radio_button'
        elif 'switch' in class_name:
            return 'switch'
        elif 'seekbar' in class_name:
            return 'seek_bar'
        elif 'progressbar' in class_name:
            return 'progress_bar'
        elif 'spinner' in class_name:
            return 'spinner'
        elif 'listview' in class_name or 'recyclerview' in class_name:
            return 'list'
        elif 'scrollview' in class_name:
            return 'scroll_view'
        elif 'layout' in class_name or 'frame' in class_name or 'linear' in class_name:
            return 'container'
        else:
            return 'other'
    
    def extract_node_info(self, node, parent_id=None, depth=0):
        """Estrae informazioni complete da un nodo XML"""
        self.node_counter += 1
        node_id = f"node_{self.node_counter}"
        
        # Attributi base
        attributes = node.attrib
        
        # Informazioni posizione
        bounds_info = self.parse_bounds(attributes.get('bounds', ''))
        
        # Classificazione nodo
        class_name = attributes.get('class', '')
        node_type = self.classify_node_type(class_name)
        
        # TUTTE le informazioni di interattività
        is_clickable = attributes.get('clickable', 'false').lower() == 'true'
        is_focusable = attributes.get('focusable', 'false').lower() == 'true'
        is_scrollable = attributes.get('scrollable', 'false').lower() == 'true'
        is_long_clickable = attributes.get('long-clickable', 'false').lower() == 'true'
        is_enabled = attributes.get('enabled', 'false').lower() == 'true'
        is_checkable = attributes.get('checkable', 'false').lower() == 'true'
        
        # TUTTE le informazioni di testo e contenuto
        text = attributes.get('text', '').strip()
        content_desc = attributes.get('content-desc', '').strip()
        resource_id = attributes.get('resource-id', '').strip()
        
        # INFORMAZIONI AGGIUNTIVE per EditText (hint, placeholder, etc.)
        hint = attributes.get('hint', '').strip()  # Testo di suggerimento
        
        # TUTTE le informazioni di stato
        is_checked = attributes.get('checked', 'false').lower() == 'true'
        is_selected = attributes.get('selected', 'false').lower() == 'true'
        is_focused = attributes.get('focused', 'false').lower() == 'true'
        is_password = attributes.get('password', 'false').lower() == 'true'
        
        # TUTTE le informazioni aggiuntive che potrebbero essere utili
        index = int(attributes.get('index', 0))
        package = attributes.get('package', '')
        
        # NAF (Not Accessibility Friendly) - importante per automazione
        naf = attributes.get('NAF', 'false').lower() == 'true'
        
        # Crea oggetto nodo completo con TUTTE le informazioni
        node_info = {
            'id': node_id,
            'parent_id': parent_id,
            'depth': depth,
            'index': index,
            
            # Classificazione completa
            'class': class_name,
            'node_type': node_type,
            'package': package,
            
            # Posizione e dimensioni complete
            'bounds': bounds_info,
            
            # TUTTO il contenuto testuale
            'text': text,
            'content_desc': content_desc,
            'resource_id': resource_id,
            'hint': hint,  # NUOVO: testo di hint per EditText
            
            # TUTTE le proprietà di interattività
            'interactive': {
                'clickable': is_clickable,
                'focusable': is_focusable,
                'scrollable': is_scrollable,
                'long_clickable': is_long_clickable,
                'enabled': is_enabled,
                'checkable': is_checkable
            },
            
            # TUTTI gli stati
            'state': {
                'checked': is_checked,
                'selected': is_selected,
                'focused': is_focused,
                'password': is_password
            },
            
            # Metadati utili
            'has_text': bool(text),
            'has_description': bool(content_desc),
            'has_resource_id': bool(resource_id),
            'has_hint': bool(hint),  # NUOVO
            'is_interactive': is_clickable or is_focusable or is_scrollable or is_long_clickable,
            'naf': naf,  # NUOVO: Not Accessibility Friendly
            
            # Informazioni identificative complete
            'identifiers': {
                'text': text if text else None,
                'content_desc': content_desc if content_desc else None,
                'resource_id': resource_id if resource_id else None,
                'hint': hint if hint else None,  # NUOVO
                'class_name': class_name,
                'package': package
            },
            
            # Figli (sarà popolato dopo)
            'children': []
        }
        
        # Aggiorna statistiche
        self.update_stats(node_info)
        
        # NUOVO: Aggiungi il nodo all'array globale per l'analisi del contesto
        self.all_nodes.append({
            'node_info': node_info,
            'xml_element': node
        })
        
        # Se è un elemento interattivo, aggiungilo alla lista speciale con TUTTE le info
        if node_info['is_interactive']:
            # Per EditText, cerca informazioni aggiuntive dal contesto (nodi fratelli/genitori)
            context_info = self.extract_edittext_context(node, parent_id) if node_type == 'edit_text' else {}
            
            interactive_element = {
                'id': node_id,
                'node_type': node_type,
                'class': class_name,
                'package': package,
                
                # TUTTE le informazioni testuali (anche se vuote)
                'text': text,
                'content_desc': content_desc,
                'resource_id': resource_id,
                'hint': hint,  # NUOVO
                
                # NUOVO: Informazioni di contesto per EditText
                'context': context_info,
                
                # Posizione completa
                'bounds': bounds_info,
                
                # TUTTE le capacità interattive
                'capabilities': {
                    'clickable': is_clickable,
                    'long_clickable': is_long_clickable,
                    'focusable': is_focusable,
                    'scrollable': is_scrollable,
                    'checkable': is_checkable,
                    'enabled': is_enabled
                },
                
                # TUTTI gli stati attuali
                'current_state': {
                    'checked': is_checked,
                    'selected': is_selected,
                    'focused': is_focused,
                    'password': is_password
                },
                
                # Azioni possibili complete
                'possible_actions': self.get_possible_actions(node_info),
                
                # Informazioni per identificazione (aggiornate con hint)
                'identification': {
                    'primary_text': text if text else hint if hint else content_desc if content_desc else resource_id,
                    'all_identifiers': [x for x in [text, hint, content_desc, resource_id] if x],
                    'best_selector': self.get_best_selector(text, content_desc, resource_id, hint),
                    'field_label': None  # Sarà aggiornato in analyze_edittext_contexts per EditText
                }
            }
            
            self.interactive_elements.append(interactive_element)
        
        # Processa i figli
        for child in node:
            child_info = self.extract_node_info(child, node_id, depth + 1)
            node_info['children'].append(child_info)
        
        return node_info
    
    def update_stats(self, node_info):
        """Aggiorna le statistiche dell'UI"""
        self.ui_stats['total_nodes'] += 1
        
        if node_info['interactive']['clickable']:
            self.ui_stats['clickable_nodes'] += 1
        
        if node_info['interactive']['focusable']:
            self.ui_stats['focusable_nodes'] += 1
        
        if node_info['interactive']['scrollable']:
            self.ui_stats['scrollable_nodes'] += 1
        
        if node_info['has_text']:
            self.ui_stats['text_nodes'] += 1
        
        # Contatori per tipo
        node_type = node_info['node_type']
        if node_type == 'button':
            self.ui_stats['buttons'] += 1
        elif node_type == 'text_view':
            self.ui_stats['text_views'] += 1
        elif node_type == 'edit_text':
            self.ui_stats['edit_texts'] += 1
        elif node_type == 'image_view':
            self.ui_stats['images'] += 1
        elif node_type == 'container':
            self.ui_stats['containers'] += 1
    
    def get_possible_actions(self, node_info):
        """Determina le azioni possibili su un nodo"""
        actions = []
        
        interactive = node_info['interactive']
        
        if interactive['clickable']:
            actions.append('click')
        
        if interactive['long_clickable']:
            actions.append('long_click')
        
        if interactive['scrollable']:
            actions.extend(['scroll_up', 'scroll_down', 'scroll_left', 'scroll_right'])
        
        if node_info['node_type'] == 'edit_text':
            actions.extend(['type_text', 'clear_text'])
        
        if interactive['checkable']:
            actions.append('toggle')
        
        if interactive['focusable']:
            actions.append('focus')
        
        return actions
    
    def get_best_selector(self, text, content_desc, resource_id, hint=None):
        """Determina il miglior selettore per identificare l'elemento"""
        if resource_id:
            return f"resource_id:{resource_id}"
        elif text:
            return f"text:{text}"
        elif hint:  # NUOVO: considera anche hint
            return f"hint:{hint}"
        elif content_desc:
            return f"description:{content_desc}"
        else:
            return "no_selector"
    
    def extract_edittext_context(self, node, parent_id):
        """Estrae informazioni di contesto per un EditText (cerca label nei nodi vicini)"""
        context = {
            'labels': [],
            'related_text': [],
            'section_title': None
        }
        
        # Invece di usare getparent(), passiamo le informazioni necessarie
        # durante il parsing dell'albero. Per ora raccogliamo solo le informazioni 
        # disponibili direttamente
        
        # Cerca nei nodi figli per eventuali label (alcune app mettono label come figli)
        for child in node:
            child_class = child.get('class', '').lower()
            child_text = child.get('text', '').strip()
            
            if child_text and 'textview' in child_class:
                context['labels'].append(child_text)
        
        return context
    
    def analyze_file(self, xml_file_path):
        """Analizza un file XML e restituisce solo pulsanti e campi di testo"""
        try:
            # Parse XML
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # Reset contatori
            self.node_counter = 0
            self.interactive_elements = []
            self.all_nodes = []
            
            # Analizza tutti i nodi
            for child in root:
                self.extract_node_info(child)
                break  # Dovrebbe esserci solo un nodo root
            
            # Analizza il contesto per EditText
            self.analyze_edittext_contexts()
            
            # Raccogli anche TextView con testo utile (etichette di pulsanti)
            button_labels = []
            self.find_button_labels(self.all_nodes, button_labels)
            
            # Crea mappa pulsante->etichetta
            button_text_map = {}
            for label in button_labels:
                matching_button = self.find_matching_button(label, self.interactive_elements)
                if matching_button:
                    button_text_map[matching_button['id']] = label['text']
            
            # Filtra solo pulsanti e campi di testo
            buttons_and_inputs = []
            
            for element in self.interactive_elements:
                # Solo pulsanti, campi di testo e TextView cliccabili con testo
                if (element['node_type'] in ['button', 'edit_text'] or 
                    (element['capabilities']['clickable'] and element['text']) or
                    (element['node_type'] == 'text_view' and element['capabilities']['clickable'])):
                    
                    # Determina il tipo finale
                    final_type = element['node_type']
                    if element['node_type'] == 'text_view' and element['capabilities']['clickable']:
                        final_type = 'button'  # TextView cliccabile = pulsante
                    
                    # Per i pulsanti senza testo, usa la mappa delle etichette
                    button_text = element['text']
                    if element['node_type'] == 'button' and not button_text:
                        button_text = button_text_map.get(element['id'], '')
                    
                    # Crea elemento pulito con solo info essenziali
                    clean_element = {
                        'id': element['id'],
                        'type': final_type,
                        'text': button_text or '',
                        'label': element['identification']['field_label'] if element['node_type'] == 'edit_text' else button_text,
                        'hint': element.get('hint', ''),
                        'resource_id': element['resource_id'] or '',
                        'clickable': element['capabilities']['clickable'],
                        'editable': element['node_type'] == 'edit_text',
                        'position': {
                            'x': element['bounds']['center_x'] if element['bounds'] else 0,
                            'y': element['bounds']['center_y'] if element['bounds'] else 0,
                            'width': element['bounds']['width'] if element['bounds'] else 0,
                            'height': element['bounds']['height'] if element['bounds'] else 0
                        }
                    }
                    
                    buttons_and_inputs.append(clean_element)
            
            # Risultato finale pulito
            result = {
                'source_file': os.path.basename(xml_file_path),
                'timestamp': self.get_timestamp(),
                'total_buttons': len([e for e in buttons_and_inputs if not e['editable']]),
                'total_inputs': len([e for e in buttons_and_inputs if e['editable']]),
                'elements': buttons_and_inputs
            }
            
            return result
            
        except ET.ParseError as e:
            raise Exception(f"Errore parsing XML: {e}")
        except Exception as e:
            raise Exception(f"Errore analisi: {e}")
    
    def analyze_edittext_contexts(self):
        """Analizza il contesto per tutti gli EditText dopo aver raccolto tutti i nodi"""
        # Raccogli tutti i TextView con testo da all_nodes
        text_nodes = []
        
        for node_data in self.all_nodes:
            node_info = node_data['node_info']
            # Raccogli tutti i TextView con testo (anche se non interattivi)
            if node_info['node_type'] == 'text_view' and node_info['text']:
                text_nodes.append(node_info)
        
        # Aggiorna il contesto per ogni EditText
        for element in self.interactive_elements:
            if element['node_type'] == 'edit_text':
                context = self.find_context_for_edittext(element, text_nodes)
                element['context'] = context
                element['identification']['field_label'] = self.determine_field_label(
                    element['text'], 
                    element['hint'], 
                    element['content_desc'], 
                    context
                )
    
    def find_context_for_edittext(self, edittext_element, text_nodes):
        """Trova il contesto per un EditText specifico"""
        context = {
            'labels': [],
            'related_text': [],
            'section_title': None
        }
        
        if not edittext_element['bounds']:
            return context
        
        edit_bounds = edittext_element['bounds']
        
        # Cerca TextView che potrebbero essere label
        for text_node in text_nodes:
            if not text_node['bounds']:
                continue
                
            text_bounds = text_node['bounds']
            
            # Calcola distanza verticale e orizzontale
            vertical_distance = abs(text_bounds['center_y'] - edit_bounds['center_y'])
            horizontal_distance = abs(text_bounds['center_x'] - edit_bounds['center_x'])
            
            # Label: TextView vicino verticalmente (sopra o alla stessa altezza)
            if vertical_distance <= 200 and horizontal_distance <= 400:
                if text_bounds['y2'] <= edit_bounds['y1'] + 100:  # Sopra con tolleranza
                    context['labels'].append(text_node['text'])
                elif vertical_distance <= 50:  # Alla stessa altezza
                    context['related_text'].append(text_node['text'])
            
            # Titolo sezione: TextView più lontano sopra
            elif (text_bounds['y2'] < edit_bounds['y1'] - 50 and 
                  vertical_distance < 500 and horizontal_distance < 600):
                if not context['section_title']:  # Prendi solo il primo
                    context['section_title'] = text_node['text']
        
        return context
    
    def determine_field_label(self, text, hint, content_desc, context):
        """Determina l'etichetta del campo EditText"""
        # Priorità: hint > etichette del contesto > content_desc > testo
        if hint and hint.strip():
            return hint.strip()
        
        if context['labels']:
            # Prendi la label più vicina
            return context['labels'][0]
        
        if content_desc and content_desc.strip():
            return content_desc.strip()
        
        if text and text.strip():
            return text.strip()
        
        if context['related_text']:
            return context['related_text'][0]
        
        return "Campo senza etichetta"
    
    def find_button_labels(self, all_nodes, button_labels):
        """Trova TextView che potrebbero essere etichette di pulsanti"""
        for node_data in all_nodes:
            node_info = node_data['node_info']
            if (node_info['node_type'] == 'text_view' and 
                node_info['text'] and 
                not node_info['is_interactive']):
                
                # TextView con testo utile che potrebbero essere etichette
                text = node_info['text'].strip()
                if text and len(text) < 50:  # Etichette ragionevoli
                    button_labels.append(node_info)
    
    def find_matching_button(self, text_element, interactive_elements):
        """Trova il pulsante interattivo che corrisponde a un TextView"""
        if not text_element['bounds']:
            return None
            
        text_bounds = text_element['bounds']
        
        # Cerca pulsanti con bounds simili (stesso centro o contenenti)
        for element in interactive_elements:
            if element['node_type'] == 'button' and element['bounds']:
                btn_bounds = element['bounds']
                
                # Stessa posizione centro (±20 pixel di tolleranza)
                center_distance = abs(text_bounds['center_x'] - btn_bounds['center_x']) + abs(text_bounds['center_y'] - btn_bounds['center_y'])
                
                if center_distance <= 40:  # Molto vicini
                    return element
                    
                # O se il testo è contenuto nel pulsante
                if (btn_bounds['x1'] <= text_bounds['x1'] and 
                    btn_bounds['y1'] <= text_bounds['y1'] and
                    btn_bounds['x2'] >= text_bounds['x2'] and 
                    btn_bounds['y2'] >= text_bounds['y2']):
                    return element
        
        return None
    
    def create_element_summary(self):
        """Crea un riassunto dettagliato degli elementi interattivi organizzato per tipo"""
        summary = {
            'buttons_and_clickable': [],
            'text_inputs': [],
            'interactive_text': [],
            'images_and_icons': [],
            'scroll_containers': [],
            'checkable_elements': [],
            'all_interactive_summary': []
        }
        
        for element in self.interactive_elements:
            element_type = element['node_type']
            
            # Crea un riassunto compatto per ogni elemento
            compact_info = {
                'id': element['id'],
                'type': element_type,
                'text': element['text'] or 'NO_TEXT',
                'description': element['content_desc'] or 'NO_DESC',
                'resource_id': element['resource_id'] or 'NO_ID',
                'selector': element['identification']['best_selector'],
                'actions': element['possible_actions'],
                'coordinates': f"({element['bounds']['center_x']},{element['bounds']['center_y']})" if element['bounds'] else 'NO_COORDS'
            }
            
            summary['all_interactive_summary'].append(compact_info)
            
            # Categorizza per tipo
            if element['capabilities']['clickable'] and element_type == 'button':
                summary['buttons_and_clickable'].append(element)
            elif element['capabilities']['clickable'] and element_type != 'button':
                summary['buttons_and_clickable'].append(element)
            
            if element_type == 'edit_text':
                summary['text_inputs'].append(element)
            
            if element_type == 'text_view' and element['capabilities']['clickable']:
                summary['interactive_text'].append(element)
            
            if element_type == 'image_view' and element['capabilities']['clickable']:
                summary['images_and_icons'].append(element)
            
            if element['capabilities']['scrollable']:
                summary['scroll_containers'].append(element)
            
            if element['capabilities']['checkable']:
                summary['checkable_elements'].append(element)
        
        return summary
    
    def get_timestamp(self):
        """Restituisce timestamp corrente"""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    parser = argparse.ArgumentParser(description='Converte file XML UIAutomator in JSON dettagliato')
    parser.add_argument('xml_file', help='File XML da analizzare')
    parser.add_argument('-o', '--output', help='File JSON output (default: stesso nome con .json)')
    parser.add_argument('-p', '--pretty', action='store_true', help='Formatta JSON con indentazione')
    parser.add_argument('-s', '--stats', action='store_true', help='Mostra solo statistiche')
    
    args = parser.parse_args()
    
    # Verifica file input
    if not os.path.exists(args.xml_file):
        print(f"Errore: File {args.xml_file} non trovato")
        sys.exit(1)
    
    # Determina file output
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(args.xml_file)[0]
        output_file = f"{base_name}.json"
    
    try:
        # Analizza il file
        print(f"Analizzando {args.xml_file}...")
        analyzer = UIAutomatorAnalyzer()
        result = analyzer.analyze_file(args.xml_file)
        
        # Mostra statistiche se richiesto
        if args.stats:
            print("\n=== Statistiche UI ===")
            print(f"Pulsanti: {result['total_buttons']}")
            print(f"Campi di testo: {result['total_inputs']}")
            print(f"Totale elementi: {len(result['elements'])}")
            print("=" * 20)
        
        # Salva JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            if args.pretty:
                json.dump(result, f, indent=2, ensure_ascii=False)
            else:
                json.dump(result, f, ensure_ascii=False)
        
        print(f"✓ Analisi completata: {output_file}")
        print(f"  - {result['total_buttons']} pulsanti")
        print(f"  - {result['total_inputs']} campi di testo")
        print(f"  - {len(result['elements'])} elementi totali")
        
    except Exception as e:
        print(f"Errore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
