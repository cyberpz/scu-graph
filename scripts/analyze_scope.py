#!/usr/bin/env python3
"""
Analizza gli articoli scaricati e filtra quelli in scope per SCU/mafia.
"""

import json
import re
from typing import List, Dict

ARTICLES_FILE = "/root/projects/scu-graph/sources/articoli/brindisireport_all_articles.json"
SCOPE_FILE = "/root/projects/scu-graph/sources/articoli/brindisireport_scu_in_scope.json"
OUT_SCOPE_FILE = "/root/projects/scu-graph/sources/articoli/brindisireport_scu_out_scope.json"

# Keywords per identificare articoli in scope
SCOPE_KEYWORDS = [
    'sacra corona unita', 'scu', 'mafia', 'clan', 'boss', 'pentito',
    'operazione', 'arresti', 'estorsione', 'racket', 'usura',
    'droga', 'narcotraffico', 'riciclaggio', 'omicidio', 'agguato',
    'camorra', 'ndrangheta', 'cosa nostra', 'antimafia', 'dda',
    'rogoli', 'campana', 'buccarella', 'guadalupi', 'parisi',
    'mesagne', 'san donaci', 'san pietro vernotico', 'brindisi',
    'lecce', 'taranto', 'foggia', 'bari', 'bat', 'gargano'
]

# Keywords per identificare articoli out of scope
OUT_SCOPE_KEYWORDS = [
    'scuola', 'sport', 'calcio', 'piscina', 'nuoto', 'campionati',
    'meteo', 'tempo', 'previsioni', 'allerta', 'maltempo',
    'traffico', 'incidente', 'strada', 'lavori', 'cantieri',
    'politica', 'elezioni', 'comune', 'consiglio', 'giunta',
    'cultura', 'teatro', 'musica', 'festival', 'mostra',
    'economia', 'lavoro', 'disoccupazione', 'azienda', 'impresa'
]

def is_in_scope(article: Dict) -> bool:
    """Determina se un articolo è in scope per SCU/mafia."""
    text = f"{article['title']} {article['summary']}".lower()
    
    # Conta keywords in scope
    scope_score = sum(1 for keyword in SCOPE_KEYWORDS if keyword in text)
    
    # Conta keywords out of scope
    out_scope_score = sum(1 for keyword in OUT_SCOPE_KEYWORDS if keyword in text)
    
    # In scope se ha almeno 2 keywords in scope e meno di 3 out of scope
    return scope_score >= 2 and out_scope_score < 3

def extract_entities(article: Dict) -> Dict:
    """Estrae entità dall'articolo (nomi, luoghi, operazioni)."""
    text = f"{article['title']} {article['summary']}"
    
    # Estrai operazioni (es. "Operazione Fuori Gioco")
    operazioni = re.findall(r'operazione\s+["\']?([^"\']+)["\']?', text, re.IGNORECASE)
    
    # Estrai nomi propri (semplice euristica)
    nomi = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text)
    
    # Estrai luoghi
    luoghi = re.findall(r'\b(?:Mesagne|San Donaci|San Pietro Vernotico|Brindisi|Lecce|Taranto|Foggia|Bari|Bat|Gargano|Ceglie|Ostuni|Oria|Cellino|Torchiarolo|Tuturano)\b', text, re.IGNORECASE)
    
    return {
        'operazioni': list(set(operazioni)),
        'nomi': list(set(nomi)),
        'luoghi': list(set(luoghi))
    }

def main():
    # Carica articoli
    with open(ARTICLES_FILE, 'r') as f:
        articles = json.load(f)
    
    print(f"=== ANALISI SCOPE ===")
    print(f"Articoli totali: {len(articles)}")
    
    # Filtra articoli
    in_scope = []
    out_scope = []
    
    for article in articles:
        if is_in_scope(article):
            # Estrai entità
            article['entities'] = extract_entities(article)
            in_scope.append(article)
        else:
            out_scope.append(article)
    
    print(f"In scope: {len(in_scope)} ({len(in_scope)/len(articles)*100:.1f}%)")
    print(f"Out of scope: {len(out_scope)} ({len(out_scope)/len(articles)*100:.1f}%)")
    
    # Salva risultati
    with open(SCOPE_FILE, 'w') as f:
        json.dump(in_scope, f, indent=2, ensure_ascii=False)
    
    with open(OUT_SCOPE_FILE, 'w') as f:
        json.dump(out_scope, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ File salvati:")
    print(f"  - In scope: {SCOPE_FILE}")
    print(f"  - Out of scope: {OUT_SCOPE_FILE}")
    
    # Statistiche entità
    all_operazioni = []
    all_nomi = []
    all_luoghi = []
    
    for article in in_scope:
        all_operazioni.extend(article['entities']['operazioni'])
        all_nomi.extend(article['entities']['nomi'])
        all_luoghi.extend(article['entities']['luoghi'])
    
    print(f"\n=== ENTITÀ ESTRATTE ===")
    print(f"Operazioni uniche: {len(set(all_operazioni))}")
    print(f"Nomi unici: {len(set(all_nomi))}")
    print(f"Luoghi unici: {len(set(all_luoghi))}")
    
    # Top 10 operazioni
    from collections import Counter
    top_operazioni = Counter(all_operazioni).most_common(10)
    print(f"\n=== TOP 10 OPERAZIONI ===")
    for op, count in top_operazioni:
        print(f"  {op}: {count} articoli")
    
    # Top 10 luoghi
    top_luoghi = Counter(all_luoghi).most_common(10)
    print(f"\n=== TOP 10 LUOGHI ===")
    for luogo, count in top_luoghi:
        print(f"  {luogo}: {count} articoli")

if __name__ == '__main__':
    main()
