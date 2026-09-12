#!/usr/bin/env python3
"""
Analizza i dati attuali e i nuovi articoli per identificare cosa aggiungere al DB.
"""

import json
from typing import List, Dict, Set

# File dati attuali
CLAN_FILE = "/root/projects/scu-graph/data/clan_puglia.json"
CONN_FILE = "/root/projects/scu-graph/data/connessioni_nazionali.json"
GEO_FILE = "/root/projects/scu-graph/data/geografia.json"
ATTORI_FILE = "/root/projects/scu-graph/data/attori.json"

# File articoli in scope
ARTICLES_FILE = "/root/projects/scu-graph/sources/articoli/brindisireport_scu_in_scope.json"

def load_json(filepath: str) -> Dict:
    """Carica un file JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_names_from_articles(articles: List[Dict]) -> Set[str]:
    """Estrae tutti i nomi propri dagli articoli."""
    names = set()
    for article in articles:
        if 'entities' in article:
            names.update(article['entities']['nomi'])
    return names

def extract_places_from_articles(articles: List[Dict]) -> Set[str]:
    """Estrae tutti i luoghi dagli articoli."""
    places = set()
    for article in articles:
        if 'entities' in article:
            places.update(article['entities']['luoghi'])
    return places

def extract_operations_from_articles(articles: List[Dict]) -> Set[str]:
    """Estrae tutte le operazioni dagli articoli."""
    operations = set()
    for article in articles:
        if 'entities' in article:
            operations.update(article['entities']['operazioni'])
    return operations

def main():
    print("=== ANALISI DATI ATTUALI VS NUOVI ===\n")
    
    # Carica dati attuali
    clan_data = load_json(CLAN_FILE)
    conn_data = load_json(CONN_FILE)
    geo_data = load_json(GEO_FILE)
    attori_data = load_json(ATTORI_FILE)
    
    # Carica articoli
    articles_data = load_json(ARTICLES_FILE)
    articles = articles_data if isinstance(articles_data, list) else articles_data.get('articles', [])
    
    # Estrai entità dai dati attuali
    current_clans = {clan['clan'] for clan in clan_data['clans']}
    current_attori = {attore['nome'] for attore in attori_data['attori']}
    current_citta = {citta['citta'] for citta in geo_data['geografia']}
    
    print(f"📊 Dati attuali:")
    print(f"  - Clan: {len(current_clans)}")
    print(f"  - Attori: {len(current_attori)}")
    print(f"  - Città: {len(current_citta)}")
    print(f"  - Connessioni: {len(conn_data['connessioni'])}")
    
    # Estrai entità dagli articoli
    article_names = extract_names_from_articles(articles)
    article_places = extract_places_from_articles(articles)
    article_operations = extract_operations_from_articles(articles)
    
    print(f"\n📊 Entità dagli articoli:")
    print(f"  - Nomi: {len(article_names)}")
    print(f"  - Luoghi: {len(article_places)}")
    print(f"  - Operazioni: {len(article_operations)}")
    
    # Identifica nuovi elementi
    new_names = article_names - current_attori
    new_places = article_places - current_citta
    
    print(f"\n🆕 Nuovi elementi da aggiungere:")
    print(f"  - Nuovi nomi: {len(new_names)}")
    print(f"  - Nuovi luoghi: {len(new_places)}")
    
    # Mostra esempi
    print(f"\n📝 Esempi nuovi nomi (primi 10):")
    for name in sorted(new_names)[:10]:
        print(f"  - {name}")
    
    print(f"\n📝 Esempi nuovi luoghi:")
    for place in sorted(new_places):
        print(f"  - {place}")
    
    # Salva analisi
    analysis = {
        'current': {
            'clans': len(current_clans),
            'attori': len(current_attori),
            'citta': len(current_citta),
            'connessioni': len(conn_data['connessioni'])
        },
        'articles': {
            'nomi': len(article_names),
            'luoghi': len(article_places),
            'operazioni': len(article_operations)
        },
        'new': {
            'nomi': len(new_names),
            'luoghi': len(new_places),
            'nomi_list': sorted(new_names),
            'luoghi_list': sorted(new_places)
        }
    }
    
    with open('/root/projects/scu-graph/analysis_db_update.json', 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analisi salvata in: /root/projects/scu-graph/analysis_db_update.json")

if __name__ == '__main__':
    main()
