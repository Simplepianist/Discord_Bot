# Simple-Bot

[![CodeFactor](https://www.codefactor.io/repository/github/simplepianist/discord_bot/badge)](https://www.codefactor.io/repository/github/simplepianist/discord_bot)

## Übersicht

Simple-Bot ist ein Python-basierter Discord- und Twitch-Bot für Streamer-Communities. Er bietet zahlreiche Funktionen rund um Community-Management, Spiele, Zitate, Anime-Features und mehr. Die Architektur ist modular (Cogs), die Konfiguration erfolgt über eine JSON-Datei.

## Features

- Discord- und Twitch-Integration
- Umfangreiche Admin- und Community-Kommandos
- Spiele (z.B. Blackjack, Roulette, Higher/Lower)
- Anime- und Zitate-APIs
- Datenbankanbindung (PostgreSQL, SQLAlchemy, Alembic)
- Dropdown-Menüs und interaktive Embeds
- Logging und Fehlerbehandlung

## Voraussetzungen

- Python 3.12
- pip

## Installation

1. Repository klonen:
    ```bash
    git clone https://github.com/Simplepianist/Discord_Bot.git
    cd Discord_Bot
    ```

2. Virtuelle Umgebung erstellen und aktivieren:
    ```bash
    python -m venv venv
    # Linux/Mac:
    source venv/bin/activate
    # Windows:
    venv\Scripts\activate
    ```

3. Abhängigkeiten installieren:
    ```bash
    pip install -r requirements.txt
    ```

## Konfiguration

Bearbeite die Datei `jsons/config.json` und trage dort deine Einstellungen ein:

- `streamURL`: Twitch-Stream-URL
- `inviteLink`: Discord-Server-Einladungslink
- `botrole`: Rolle für Bot-Management
- `ownerId`: Bot-Besitzer-ID
- `waifuit`: API-Key für Anime-Quotes
- `test`: Bool für Testzwecke
- `embed`: Einstellungen für Embeds

Außerdem muss der Discord-Bot-Token als Umgebungsvariable `token` gesetzt werden.

### Setzbare Umgebungsvariablen

| Variable         | Beschreibung                                 | Standardwert (falls vorhanden)         |
|------------------|----------------------------------------------|----------------------------------------|
| `token`          | Discord-Bot-Token                            | –                                      |
| `OWNER_ID`       | Discord User-ID des Bot-Besitzers            | 325779745436467201                     |
| `NTFY_URL`       | URL für ntfy-Benachrichtigungen (optional)   | –                                      |
| `DB_USER`        | Datenbank-Benutzername                       | –                                      |
| `DB_PASSWORD`    | Datenbank-Passwort                           | –                                      |
| `DB_HOST`        | Datenbank-Host                               | –                                      |
| `DB_PORT`        | Datenbank-Port                               | 5432                                   |
| `DB_NAME`        | Name der Datenbank                           | –                                      |
| `waifuit`        | API-Key für Anime-Quotes                     | –                                      |
| `APPLICATION_ID` | Discord Application ID (für Tests)           | 1234567890 (nur in Tests)              |

## Start

Starte den Bot mit:
```bash
python streamer.py
```

## Tests

Unit- und Integrationstests befinden sich im `tests/`-Verzeichnis und können mit pytest ausgeführt werden:
```bash
pytest
```

## Verzeichnisstruktur (Auszug)

- `simplebot.py` – Hauptbot-Klasse
- `streamer.py` – Einstiegspunkt
- `cogs/` – Erweiterungsmodule (Cogs)
- `Commands/` – Kommandos
- `Database/` – Datenbankzugriff
- `API/` – Schnittstellen zu externen APIs
- `Dropdowns/`, `View/`, `Util/` – weitere Features

## Lizenz

MIT
