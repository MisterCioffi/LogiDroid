#!/bin/bash

echo "=== LogiDroid: Batch XML to JSON Converter ==="

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni per output colorato
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Cartelle
UI_CAPTURES_DIR="ui_captures"
JSON_OUTPUT_DIR="json_analysis"

# Crea cartella output se non esiste
if [ ! -d "$JSON_OUTPUT_DIR" ]; then
    mkdir -p "$JSON_OUTPUT_DIR"
    print_success "Creata cartella: $JSON_OUTPUT_DIR"
fi

# Verifica presenza script Python
if [ ! -f "xml_to_json.py" ]; then
    print_error "Script xml_to_json.py non trovato"
    exit 1
fi

# Conta file XML
XML_COUNT=$(find "$UI_CAPTURES_DIR" -name "*.xml" 2>/dev/null | wc -l | tr -d ' ')

if [ "$XML_COUNT" -eq 0 ]; then
    print_warning "Nessun file XML trovato in $UI_CAPTURES_DIR"
    exit 0
fi

print_info "Trovati $XML_COUNT file XML da convertire"
echo ""

# Processa ogni file XML
success_count=0
error_count=0

for xml_file in "$UI_CAPTURES_DIR"/*.xml; do
    if [ -f "$xml_file" ]; then
        filename=$(basename "$xml_file" .xml)
        json_file="$JSON_OUTPUT_DIR/${filename}.json"
        
        print_info "Processando: $filename.xml"
        
        if python3 xml_to_json.py "$xml_file" -o "$json_file" -p; then
            print_success "Convertito: $json_file"
            
            # Mostra statistiche rapide
            stats=$(python3 -c "
import json
try:
    with open('$json_file', 'r') as f:
        data = json.load(f)
    stats = data['metadata']['statistics']
    interactive = len(data['interactive_elements'])
    print(f'  Nodi: {stats[\"total_nodes\"]}, Interattivi: {interactive}, Bottoni: {stats[\"buttons\"]}')
except:
    print('  Errore lettura statistiche')
")
            echo "  $stats"
            success_count=$((success_count + 1))
        else
            print_error "Errore convertendo $filename.xml"
            error_count=$((error_count + 1))
        fi
        echo ""
    fi
done

# Riassunto finale
echo "================================="
print_success "$success_count file convertiti con successo"
if [ "$error_count" -gt 0 ]; then
    print_error "$error_count errori"
fi

# Crea indice JSON di tutti i file
print_info "Creando indice generale..."

python3 -c "
import json
import os
from pathlib import Path

json_dir = '$JSON_OUTPUT_DIR'
index = {
    'captures': [],
    'total_files': 0,
    'summary': {
        'total_nodes': 0,
        'total_interactive_elements': 0,
        'total_buttons': 0
    }
}

for json_file in sorted(Path(json_dir).glob('*.json')):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        file_info = {
            'file': json_file.name,
            'source_xml': data['metadata']['source_file'],
            'timestamp': data['metadata']['analysis_timestamp'],
            'statistics': data['metadata']['statistics'],
            'interactive_count': len(data['interactive_elements'])
        }
        
        index['captures'].append(file_info)
        index['total_files'] += 1
        index['summary']['total_nodes'] += data['metadata']['statistics']['total_nodes']
        index['summary']['total_interactive_elements'] += len(data['interactive_elements'])
        index['summary']['total_buttons'] += data['metadata']['statistics']['buttons']
        
    except Exception as e:
        print(f'Errore processando {json_file}: {e}')

# Salva indice
with open(f'{json_dir}/index.json', 'w') as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print(f'Indice creato con {index[\"total_files\"]} file')
"

print_success "Conversione batch completata!"
print_info "File JSON salvati in: $JSON_OUTPUT_DIR"
print_info "Indice generale: $JSON_OUTPUT_DIR/index.json"

echo "=== Conversione completata ==="
