# Sacra Corona Unita — Grafo Relazionale (2006-2026)

Mappatura interattiva della Sacra Corona Unita: membri, clan, connessioni con Camorra/'Ndrangheta/Cosa Nostra, distribuzione geografica in Puglia.

## Contenuto

- **Grafo relazionale** — nodi e connessioni tra persone, clan e organizzazioni criminali
- **Mappa vettoriale Puglia** — distribuzione per provincia/città con intensità cromatica
- **Dataset grezzi** — JSON strutturati in `data/` per analisi e verifiche
- **Fonti archiviate** — screenshot e articoli originali in `sources/` come prova documentale

## Quick Start

```bash
docker compose up -d --build
# → http://localhost:8097
```

## Struttura

```
├── src/              # HTML/CSS/JS del grafo e mappa
├── data/             # Dataset JSON (clan, connessioni, geografia)
├── assets/           # SVG mappa Puglia, immagini
├── sources/          # Archivi fonti (screenshot, PDF, articoli)
├── Dockerfile        # Container nginx:alpine
├── docker-compose.yml
└── nginx.conf
```

## Fonti

Tutti i dati sono raccolti da fonti pubbliche:
- Sentenze Cassazione, Corte d'Appello, Tribunali pugliesi
- Report DIA e Direzione Distrettuale Antimafia
- Inchieste giornalistiche (Repubblica, Corriere della Sera, Gazzetta del Mezzogiorno, Il Fatto Quotidiano)
- Audizioni Commissione Parlamentare Antimafia

⚠️ Questo progetto è una documentazione giornalistica/storica basata su fonti pubbliche. Non costituisce atto giudiziario.

## License

MIT
