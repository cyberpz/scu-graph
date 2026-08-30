# SCU Graph — Sacra Corona Unita

Applicazione web investigativa e documentale per esplorare la storia e la distribuzione della **Sacra Corona Unita**, dei clan pugliesi e delle connessioni con altre organizzazioni criminali.

> Periodo principale dei dati strutturati: **2006–2026**. Il corpus storico include anche fonti precedenti.

## Funzioni

L'interfaccia, ispirata al design system **Jarvis-Domus**, contiene tre sezioni:

- **Grafo** — persone, clan, città, province e organizzazioni esterne visualizzate con `vis-network`.
- **Mappa** — SVG interattiva della Puglia, zoomabile e navigabile, con distribuzione provinciale e punti comunali.
- **Tabelle** — statistiche aggregate, attori, operazioni giudiziarie e collegamenti inter-organizzazione.

L'applicazione è responsive e supporta mouse, touch, zoom e pan.

## Dataset strutturati

La directory `data/` contiene:

| File | Contenuto |
|---|---|
| `attori.json` | Dati anagrafici disponibili, condanne, stato e scarcerazione stimata |
| `clan_puglia.json` | Profili, ruoli, arresti, condanne e appartenenze |
| `connessioni_nazionali.json` | Collegamenti con Camorra, 'Ndrangheta, Cosa Nostra e reti criminali |
| `geografia.json` | Distribuzione per provincia e comune, clan e operazioni |

I dati richiedono verifica incrociata: omonimie, stato detentivo e date giudiziarie possono cambiare o risultare discordanti tra le fonti.

## Archivio documentale

Le fonti sono conservate localmente in `sources/`, così il progetto non dipende esclusivamente dalla disponibilità futura delle pagine web o da Wayback Machine.

### Stato del corpus

- **70 file** complessivi sotto `sources/`.
- **67 file** sotto `sources/articoli/`.
- **21 acquisizioni Markdown** di pagine complete, tra cui Wikipedia IT/EN e Treccani.
- **40 raccolte JSON** iniziali e tematiche.
- **400 risultati web** ottenuti da 20 ricerche Firecrawl approfondite (`limit=20`).
- **414 titoli ANSA pertinenti** estratti da un archivio SQLite di 135.325 record, periodo 2020–2026.
- **154 record BrindisiReport** dal database dello scraper locale.
- **182 risultati storici BrindisiReport** recuperati tramite ricerche mirate Firecrawl.
- Dimensione attuale dell'archivio `sources/`: circa **2,5 MB**.

I conteggi delle diverse raccolte possono sovrapporsi: non rappresentano necessariamente articoli unici globali.

### Fonti principali

- ANSA, archivio Telegram `@notizieansa`.
- BrindisiReport.
- Direzione Investigativa Antimafia e DDA.
- Corte di Cassazione e documentazione giudiziaria pubblica.
- Commissione Parlamentare Antimafia.
- Wikipedia, Treccani e pubblicazioni accademiche.
- Testate giornalistiche nazionali e locali.

### Organizzazione delle fonti

```text
sources/
├── articoli/      # Markdown completi, risultati Firecrawl e archivi ANSA/BrindisiReport
├── sentenze/      # Provvedimenti e documenti giudiziari pubblici
├── screenshot/    # Copie visive delle pagine rilevanti
└── README.md      # Convenzioni di archiviazione
```

Naming consigliato per nuovi documenti:

```text
YYYY-MM-DD_fonte_argomento.ext
```

## Struttura della repository

```text
.
├── src/
│   └── index.html                # SPA: Grafo, Mappa e Tabelle
├── data/
│   ├── attori.json
│   ├── clan_puglia.json
│   ├── connessioni_nazionali.json
│   └── geografia.json
├── assets/
│   └── puglia_provinces.svg
├── sources/
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```

## Avvio rapido

```bash
git clone https://github.com/cyberpz/scu-graph.git
cd scu-graph
docker compose up -d --build
```

Applicazione:

```text
http://localhost:8097
```

Health check:

```bash
curl http://localhost:8097/healthz
```

Arresto:

```bash
docker compose down
```

## Deploy

Il container usa `nginx:alpine`, espone la porta `80` internamente e viene pubblicato sulla porta `8097` dall'attuale `docker-compose.yml`.

Per cambiare porta:

```yaml
ports:
  - "NUOVA_PORTA:80"
```

## Avvertenza metodologica

Questo progetto ha finalità **documentali, giornalistiche e storiche**. Non costituisce un atto giudiziario né certifica responsabilità penali.

- Le informazioni devono essere attribuite alle rispettive fonti.
- Un arresto o un'indagine non equivalgono a una condanna definitiva.
- Lo stato di una persona può cambiare nel tempo.
- Le date di scarcerazione indicate come stime non tengono necessariamente conto di cumuli, benefici, cautelare, liberazione anticipata o successivi provvedimenti.
- Eventuali errori di identità o appartenenza devono essere corretti conservando traccia della fonte e della revisione.

## Licenze

- Codice del progetto: **MIT**.
- La mappa SVG della Puglia deriva da Wikimedia Commons ed è indicata come pubblico dominio nella relativa pagina sorgente.
- Articoli, documenti e contenuti archiviati conservano i diritti e le condizioni delle rispettive fonti; la loro presenza nella repository non ne modifica la titolarità.
