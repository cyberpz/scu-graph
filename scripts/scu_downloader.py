#!/usr/bin/env python3
"""
SCU Articles Downloader - Safe & Resumable
Scarica tutti gli articoli SCU da BrindisiReport con rate limiting e resume.
"""

import json
import os
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional

# Configurazione
BASE_URL = "https://www.brindisireport.it/search/query/SCU/pag/{}"
OUTPUT_DIR = "/root/projects/scu-graph/sources/articoli"
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "download_progress.json")
ARTICLES_FILE = os.path.join(OUTPUT_DIR, "brindisireport_all_articles.json")
LOG_FILE = os.path.join(OUTPUT_DIR, "download_log.txt")

# Rate limiting
MIN_DELAY = 3
MAX_DELAY = 5
MAX_RETRIES = 3

# User-Agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]

class SCUDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.progress = self.load_progress()
        self.articles = self.load_articles()
        
    def load_progress(self) -> Dict:
        """Carica il progresso del download."""
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        return {
            'last_page': 0,
            'total_articles': 0,
            'start_time': None,
            'end_time': None,
            'status': 'not_started'
        }
    
    def save_progress(self):
        """Salva il progresso del download."""
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def load_articles(self) -> List[Dict]:
        """Carica gli articoli già scaricati."""
        if os.path.exists(ARTICLES_FILE):
            with open(ARTICLES_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_articles(self):
        """Salva gli articoli scaricati."""
        with open(ARTICLES_FILE, 'w') as f:
            json.dump(self.articles, f, indent=2, ensure_ascii=False)
    
    def log(self, message: str):
        """Log con timestamp."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(LOG_FILE, 'a') as f:
            f.write(log_message + '\n')
    
    def get_random_user_agent(self) -> str:
        """Restituisce un User-Agent casuale."""
        return random.choice(USER_AGENTS)
    
    def download_page(self, page_num: int) -> Optional[str]:
        """Scarica una pagina con retry e backoff."""
        url = BASE_URL.format(page_num)
        
        for attempt in range(MAX_RETRIES):
            try:
                # Cambia User-Agent ad ogni tentativo
                self.session.headers['User-Agent'] = self.get_random_user_agent()
                
                self.log(f"Scaricamento pagina {page_num} (tentativo {attempt + 1}/{MAX_RETRIES})")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Delay casuale tra 3-5 secondi
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                self.log(f"Attesa {delay:.2f}s...")
                time.sleep(delay)
                
                return response.text
                
            except requests.exceptions.RequestException as e:
                self.log(f"Errore pagina {page_num}: {e}")
                if attempt < MAX_RETRIES - 1:
                    # Backoff esponenziale
                    backoff = (2 ** attempt) * random.uniform(1, 2)
                    self.log(f"Retry in {backoff:.2f}s...")
                    time.sleep(backoff)
                else:
                    self.log(f"Fallito download pagina {page_num} dopo {MAX_RETRIES} tentativi")
                    return None
        
        return None
    
    def parse_articles(self, html: str, page_num: int) -> List[Dict]:
        """Estrae gli articoli dalla pagina HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Trova tutti gli articoli
        for article in soup.find_all('article'):
            try:
                # Estrai titolo (h1, non h2)
                title_elem = article.find('h1')
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                
                # Estrai link (dentro header > a)
                header = article.find('header')
                if not header:
                    continue
                
                link_elem = header.find('a')
                if not link_elem:
                    continue
                
                link = link_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.brindisireport.it{link}"
                
                # Estrai immagine
                img_elem = article.find('img')
                image_url = img_elem.get('src', '') if img_elem else ''
                if image_url and not image_url.startswith('http'):
                    image_url = f"https:{image_url}"
                
                # Estrai data (se presente)
                date_elem = article.find('time')
                date = date_elem.get('datetime', '') if date_elem else ''
                
                # Estrai sommario
                summary_elem = article.find('p')
                summary = summary_elem.text.strip() if summary_elem else ''
                
                article_data = {
                    'page': page_num,
                    'title': title,
                    'url': link,
                    'image': image_url,
                    'date': date,
                    'summary': summary,
                    'downloaded_at': datetime.now().isoformat()
                }
                
                articles.append(article_data)
                
            except Exception as e:
                self.log(f"Errore parsing articolo: {e}")
                continue
        
        return articles
    
    def download_all(self, start_page: int = 1, end_page: int = 88):
        """Scarica tutte le pagine."""
        self.progress['start_time'] = datetime.now().isoformat()
        self.progress['status'] = 'in_progress'
        self.save_progress()
        
        self.log(f"Inizio download da pagina {start_page} a {end_page}")
        
        for page_num in range(start_page, end_page + 1):
            # Salta se già scaricata
            if page_num <= self.progress['last_page']:
                self.log(f"Pagina {page_num} già scaricata, salto")
                continue
            
            html = self.download_page(page_num)
            if html is None:
                self.log(f"Salto pagina {page_num} per errori")
                continue
            
            articles = self.parse_articles(html, page_num)
            self.articles.extend(articles)
            
            # Aggiorna progresso
            self.progress['last_page'] = page_num
            self.progress['total_articles'] = len(self.articles)
            self.save_progress()
            self.save_articles()
            
            self.log(f"Pagina {page_num}: {len(articles)} articoli (totale: {len(self.articles)})")
            
            # Log ogni 10 pagine
            if page_num % 10 == 0:
                self.log(f"=== PROGRESSO: {page_num}/{end_page} pagine, {len(self.articles)} articoli ===")
        
        self.progress['end_time'] = datetime.now().isoformat()
        self.progress['status'] = 'completed'
        self.save_progress()
        
        self.log(f"Download completato! Totale articoli: {len(self.articles)}")
    
    def get_stats(self) -> Dict:
        """Restituisce statistiche sul download."""
        return {
            'total_articles': len(self.articles),
            'last_page': self.progress['last_page'],
            'status': self.progress['status'],
            'start_time': self.progress['start_time'],
            'end_time': self.progress['end_time']
        }

def main():
    downloader = SCUDownloader()
    
    # Mostra statistiche attuali
    stats = downloader.get_stats()
    print(f"=== STATISTICHE DOWNLOAD ===")
    print(f"Articoli scaricati: {stats['total_articles']}")
    print(f"Ultima pagina: {stats['last_page']}")
    print(f"Stato: {stats['status']}")
    print()
    
    # Chiedi conferma per continuare
    if stats['status'] == 'completed':
        print("Download già completato!")
        return
    
    # Avvia download
    start_page = stats['last_page'] + 1
    downloader.download_all(start_page=start_page, end_page=88)
    
    # Mostra statistiche finali
    final_stats = downloader.get_stats()
    print(f"\n=== DOWNLOAD COMPLETATO ===")
    print(f"Articoli totali: {final_stats['total_articles']}")
    print(f"Pagine scaricate: {final_stats['last_page']}")
    print(f"Inizio: {final_stats['start_time']}")
    print(f"Fine: {final_stats['end_time']}")

if __name__ == '__main__':
    main()
