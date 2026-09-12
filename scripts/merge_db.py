#!/usr/bin/env python3
"""
Merge intelligente dei nuovi dati dagli articoli nel DB SCU Graph.
Filtra, normalizza e valida i dati prima di aggiungerli.
"""

import json
import re
from typing import List, Dict, Set
from collections import defaultdict

# File dati attuali
CLAN_FILE = "/root/projects/scu-graph/data/clan_puglia.json"
CONN_FILE = "/root/projects/scu-graph/data/connessioni_nazionali.json"
GEO_FILE = "/root/projects/scu-graph/data/geografia.json"
ATTORI_FILE = "/root/projects/scu-graph/data/attori.json"

# File articoli in scope
ARTICLES_FILE = "/root/projects/scu-graph/sources/articoli/brindisireport_scu_in_scope.json"

# File output
OUTPUT_DIR = "/root/projects/scu-graph/data"

def load_json(filepath: str) -> Dict:
    """Carica un file JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(data: Dict, filepath: str):
    """Salva un file JSON."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def normalize_place(place: str) -> str:
    """Normalizza un luogo (title case, no duplicati)."""
    return place.strip().title()

def is_relevant_name(name: str, article: Dict) -> bool:
    """Determina se un nome è rilevante per SCU/mafia."""
    # Escludi nomi comuni/falsi positivi
    false_positives = {
        'Al Bano', 'Alberto Tomba', 'Adriano Celentano', 'Marco Polo',
        'Giuseppe Verdi', 'Leonardo Da Vinci', 'Michelangelo Buonarroti'
    }
    
    if name in false_positives:
        return False
    
    # Includi solo nomi associati a operazioni SCU
    text = f"{article['title']} {article['summary']}".lower()
    scu_keywords = ['scu', 'sacra corona unita', 'mafia', 'clan', 'boss', 'pentito']
    
    return any(keyword in text for keyword in scu_keywords)

def extract_relevant_names(articles: List[Dict]) -> Dict[str, List[Dict]]:
    """Estrae nomi rilevanti dagli articoli, raggruppati per nome."""
    names_map = defaultdict(list)
    
    for article in articles:
        if 'entities' not in article:
            continue
        
        for name in article['entities']['nomi']:
            if is_relevant_name(name, article):
                names_map[name].append({
                    'title': article['title'],
                    'url': article['url'],
                    'date': article['date'],
                    'operations': article['entities']['operazioni'],
                    'places': article['entities']['luoghi']
                })
    
    return dict(names_map)

def extract_relevant_places(articles: List[Dict]) -> Dict[str, List[Dict]]:
    """Estrae luoghi rilevanti dagli articoli, raggruppati per luogo."""
    places_map = defaultdict(list)
    
    for article in articles:
        if 'entities' not in article:
            continue
        
        for place in article['entities']['luoghi']:
            normalized = normalize_place(place)
            places_map[normalized].append({
                'title': article['title'],
                'url': article['url'],
                'date': article['date'],
                'operations': article['entities']['operazioni'],
                'names': article['entities']['nomi']
            })
    
    return dict(places_map)

def merge_attori(current_attori: List[Dict], new_names: Dict[str, List[Dict]]) -> List[Dict]:
    """Merge dei nuovi attori con quelli esistenti."""
    # Crea set di nomi esistenti (case insensitive)
    existing_names = {attore['nome'].lower() for attore in current_attori}
    
    # Aggiungi nuovi attori
    new_attori = []
    for name, articles in new_names.items():
        if name.lower() not in existing_names:
            # Estrai operazioni uniche
            operations = set()
            for article in articles:
                operations.update(article['operations'])
            
            # Estrai luoghi unici
            places = set()
            for article in articles:
                places.update(article['places'])
            
            new_attore = {
                'nome': name,
                'ruolo': 'Da definire',
                'clan': 'Da definire',
                'citta': list(places)[0] if places else 'Da definire',
                'operazioni': list(operations),
                'fonti': [article['url'] for article in articles[:3]],  # Max 3 fonti
                'note': f"Aggiunto automaticamente da {len(articles)} articoli"
            }
            
            new_attori.append(new_attore)
    
    return current_attori + new_attori

def merge_geografia(current_geo: List[Dict], new_places: Dict[str, List[Dict]]) -> List[Dict]:
    """Merge dei nuovi luoghi con quelli esistenti."""
    # Crea set di città esistenti (case insensitive)
    existing_citta = {citta['citta'].lower() for citta in current_geo}
    
    # Aggiungi nuove città
    new_geo = []
    for place, articles in new_places.items():
        if place.lower() not in existing_citta:
            # Estrai operazioni uniche
            operations = set()
            for article in articles:
                operations.update(article['operations'])
            
            # Estrai nomi unici
            names = set()
            for article in articles:
                names.update(article['names'])
            
            new_citta = {
                'provincia': 'Da definire',
                'citta': place,
                'clan_dominante': 'Da definire',
                'periodo_attivita': 'Da definire',
                'operazioni_principali': [{'nome': op, 'anno': 'Da definire', 'esito': 'Da definire'} for op in list(operations)[:3]],
                'membri_chiave': list(names)[:5],  # Max 5 membri
                'note': f"Aggiunto automaticamente da {len(articles)} articoli"
            }
            
            new_geo.append(new_citta)
    
    return current_geo + new_geo

def validate_data(data: List[Dict], data_type: str) -> bool:
    """Valida la coerenza dei dati."""
    if data_type == 'attori':
        # Campi richiesti per nuovi attori
        required_fields = ['nome', 'ruolo', 'clan', 'citta']
        for item in data:
            # Se ha 'nome' e 'cognome', è un attore esistente (OK)
            if 'nome' in item and 'cognome' in item:
                continue
            # Se ha solo 'nome', deve avere anche gli altri campi
            if not all(field in item for field in required_fields):
                return False
    elif data_type == 'geografia':
        required_fields = ['provincia', 'citta', 'clan_dominante']
        for item in data:
            if not all(field in item for field in required_fields):
                return False
    
    return True

def main():
    print("=== MERGE INTELLIGENTE DB SCU GRAPH ===\n")
    
    # Carica dati attuali
    print("📂 Caricamento dati attuali...")
    clan_data = load_json(CLAN_FILE)
    conn_data = load_json(CONN_FILE)
    geo_data = load_json(GEO_FILE)
    attori_data = load_json(ATTORI_FILE)
    
    # Carica articoli
    print("📂 Caricamento articoli...")
    articles_data = load_json(ARTICLES_FILE)
    articles = articles_data if isinstance(articles_data, list) else articles_data.get('articles', [])
    
    # Estrai entità rilevanti
    print("🔍 Estrazione entità rilevanti...")
    new_names = extract_relevant_names(articles)
    new_places = extract_relevant_places(articles)
    
    print(f"  - Nomi rilevanti: {len(new_names)}")
    print(f"  - Luoghi rilevanti: {len(new_places)}")
    
    # Merge attori
    print("\n🔄 Merge attori...")
    updated_attori = merge_attori(attori_data['attori'], new_names)
    print(f"  - Attori prima: {len(attori_data['attori'])}")
    print(f"  - Attori dopo: {len(updated_attori)}")
    print(f"  - Nuovi attori: {len(updated_attori) - len(attori_data['attori'])}")
    
    # Merge geografia
    print("\n🔄 Merge geografia...")
    updated_geo = merge_geografia(geo_data['geografia'], new_places)
    print(f"  - Città prima: {len(geo_data['geografia'])}")
    print(f"  - Città dopo: {len(updated_geo)}")
    print(f"  - Nuove città: {len(updated_geo) - len(geo_data['geografia'])}")
    
    # Valida dati
    print("\n✅ Validazione dati...")
    if not validate_data(updated_attori, 'attori'):
        print("❌ Errore: dati attori non validi")
        return
    
    if not validate_data(updated_geo, 'geografia'):
        print("❌ Errore: dati geografia non validi")
        return
    
    print("✅ Dati validi")
    
    # Salva dati aggiornati
    print("\n💾 Salvataggio dati aggiornati...")
    
    attori_data['attori'] = updated_attori
    save_json(attori_data, ATTORI_FILE)
    print(f"  - Attori salvati: {ATTORI_FILE}")
    
    geo_data['geografia'] = updated_geo
    save_json(geo_data, GEO_FILE)
    print(f"  - Geografia salvata: {GEO_FILE}")
    
    # Statistiche finali
    print("\n=== STATISTICHE FINALI ===")
    print(f"Clan: {len(clan_data['clans'])}")
    print(f"Attori: {len(updated_attori)}")
    print(f"Città: {len(updated_geo)}")
    print(f"Connessioni: {len(conn_data['connessioni'])}")
    
    # Salva report
    report = {
        'timestamp': str(datetime.now()),
        'clan': len(clan_data['clans']),
        'attori': len(updated_attori),
        'citta': len(updated_geo),
        'connessioni': len(conn_data['connessioni']),
        'nuovi_attori': len(updated_attori) - len(attori_data['attori']),
        'nuove_citta': len(updated_geo) - len(geo_data['geografia'])
    }
    
    with open('/root/projects/scu-graph/merge_report.json', 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Report salvato: /root/projects/scu-graph/merge_report.json")
    print("\n🎉 Merge completato con successo!")

if __name__ == '__main__':
    from datetime import datetime
    main()
