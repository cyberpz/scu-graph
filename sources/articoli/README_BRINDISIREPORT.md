# BrindisiReport SCU Articles Archive

Questo archivio contiene tutti gli articoli relativi alla Sacra Corona Unita (SCU) trovati su BrindisiReport.

## Struttura

- `brindisireport_scu_index.json` - Indice completo di tutte le pagine scaricate
- `brindisireport_scu_articles.json` - Articoli dettagliati (pagine 1-2)
- `operazione_fuori_gioco_richieste_condanne_2025-11-25.json` - Articolo specifico richiesto

## Statistiche

- **Pagine totali**: 88
- **Articoli stimati**: ~880
- **Articoli scaricati**: 29 (pagine 1-2) + 1 articolo specifico = 30
- **Data download**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Come usare

Per scaricare articoli da una pagina specifica:

```python
import requests
from bs4 import BeautifulSoup

url = f"https://www.brindisireport.it/search/query/SCU/pag/{{page_number}}"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Estrai articoli
articles = soup.find_all('article')
for article in articles:
    title = article.find('h2').text.strip()
    link = article.find('a')['href']
    print(f"{title}: {link}")
```

## Note

- Gli articoli sono ordinati dal più recente al più vecchio
- La pagina 88 è l'ultima disponibile
- Alcuni articoli potrebbero essere duplicati o non più disponibili
