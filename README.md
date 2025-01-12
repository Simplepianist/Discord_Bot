# Simple-Bot
[![CodeFactor](https://www.codefactor.io/repository/github/simplepianist/discord_bot/badge)](https://www.codefactor.io/repository/github/simplepianist/discord_bot)

## Übersicht

Dieses Projekt ist ein Python-basiertes System, das einen Streamer-Bot für Twitch und Discord bereitstellt. Es verwendet Python 3.12 und verschiedene Python-Bibliotheken, die in der `requirements.txt` Datei aufgeführt sind.

## Voraussetzungen

- Python 3.12
- pip (Python Paket-Manager)

## Installation

1. Klonen Sie das Repository:
    ```bash
    git clone https://github.com/Simplepianist/Discord_Bot.git
    cd Discord_Bot
    ```

2. Erstellen Sie eine virtuelle Umgebung und aktivieren Sie sie:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Auf Windows: venv\Scripts\activate
    ```

3. Installieren Sie die Abhängigkeiten:
    ```bash
    pip install -r requirements.txt
    ```

## Konfiguration

Bearbeiten Sie die `jsons/config.json` Datei, um die Konfigurationsparameter anzupassen:
- `streamURL`: Die URL des Twitch-Streams.
- `inviteLink`: Der Einladungslink für den Discord-Server.
- `botrole`: Der Name der Rolle zum verwalten des Bots.
- `ownerId`: Die ID des Bot-Besitzers.
- `waifuit`: Anime-Quote API-Key.
- `test`: Ein boolescher Wert für Testzwecke.
- `embed`: Einstellungen für eingebettete Nachrichten.

## Verwendung

Starten Sie den Bot mit dem folgenden Befehl:
```bash
python streamer.py
