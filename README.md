# 🕐 Timesheet App



Eine moderne, benutzerfreundliche Multi-User Zeiterfassungs-Webapp mit Docker-Support und vollständiger Authentifizierung.



![License](https://img.shields.io/badge/license-MIT-blue.svg)

![Python](https://img.shields.io/badge/python-3.11-blue.svg)

![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)

![Docker](https://img.shields.io/badge/docker-ready-blue.svg)



## 📋 Inhaltsverzeichnis



- [Features](#-features)

- [Screenshots](#-screenshots)

- [Voraussetzungen](#-voraussetzungen)

- [Installation](#-installation)

- [Konfiguration](#-konfiguration)

- [Verwendung](#-verwendung)

- [Admin-Tools](#-admin-tools)

- [Deployment](#-deployment)

- [Projektstruktur](#-projektstruktur)

- [Technologie-Stack](#-technologie-stack)

- [Entwicklung](#-entwicklung)

- [Troubleshooting](#-troubleshooting)

- [Mitwirken](#-mitwirken)

- [Lizenz](#-lizenz)

- [Kontakt](#-kontakt)



## ✨ Features



### Zeiterfassung

- ⏱️ **Einfache Timer-Steuerung** - Start/Stop mit einem Klick

- 📊 **Ticket-basierte Zeiterfassung** - Organisiere Zeiten nach Projekten/Aufgaben

- 🎨 **Farbcodierte Tickets** - Visuelle Unterscheidung verschiedener Projekte

- 📝 **Bemerkungen** - Füge Notizen zu jedem Zeiteintrag hinzu

- 📅 **Datum-basierte Ansicht** - Übersichtliche Gruppierung nach Tagen

- ⏲️ **Live-Timer** - Echtzeit-Anzeige der laufenden Zeit

- ✏️ **Inline-Bearbeitung** - Start/End-Zeiten direkt anpassen



### Ticket-Management

- ➕ **Tickets erstellen/bearbeiten** - Mit Name, Farbe, Jira/Matrix-Nummer

- 🎨 **Farbauswahl** - Vordefinierte Farben + Custom-Farbwähler

- 🔄 **Drag & Drop Sortierung** - Tickets per Ziehen neu anordnen

- 🗑️ **Ticket-Verwaltung** - Einfaches Löschen nicht mehr benötigter Tickets



### Benutzer-System

- 🔐 **Sichere Authentifizierung** - Passwort-Hashing mit bcrypt

- 👥 **Multi-User Support** - Vollständige Datentrennung zwischen Usern

- 🔑 **Passwort-Management** - User können Passwörter selbst ändern

- 👤 **User-Profile** - Personalisierte Einstellungen pro Benutzer



### Reporting

- 📈 **Zeitübersicht** - Auswertungen nach Zeitraum

- 📊 **Ticket-Statistiken** - Stunden pro Ticket mit Prozentangaben

- 📅 **Flexible Zeiträume** - Beliebige Von/Bis-Datumswahl

- 💾 **Tages-Summen** - Automatische Berechnung der Tagesarbeitszeit



### Technical Features

- 🐳 **Docker-Ready** - Vollständige Containerisierung

- 🔒 **Traefik-Integration** - Automatisches HTTPS mit Let's Encrypt

- 💾 **SQLite-Datenbank** - Keine externe Datenbank nötig

- 📱 **Responsive Design** - Funktioniert auf Desktop, Tablet, Mobile

- 🎯 **GitHub-Style UI** - Modernes, aufgeräumtes Design

- 🔧 **Admin-Tools** - Scripts für User-Migration und Passwort-Reset



## 📸 Screenshots



### Hauptansicht

```

┌─────────────────────────────────────────────────────────┐

│  Zeiterfassung              👤 tom  [Passwort] [Logout] │

├─────────────────────────────────────────────────────────┤

│  [Stopp] [Projekt A] [Projekt B] [Support] [Admin] [+] │

│                                                          │

│  🟢 Timer läuft: 02:15:43                               │

│                                                          │

│  Erfasste Zeiten                                        │

│  ┌─────────────────────────────────────────────────────┐│

│  │ Heute (2025-10-06) - 7.5h                     ▼    ││

│  │ Ticket    Start      Ende      Dauer  Bemerkungen  ││

│  │ Projekt A 09:00     11:30     2.5h   Meeting       ││

│  │ Support   11:30     16:00     4.5h   Bug fixes     ││

│  │ Admin     16:00     ...       läuft  Doku          ││

│  └─────────────────────────────────────────────────────┘│

└─────────────────────────────────────────────────────────┘

```



### Zusammenfassung

```

┌─────────────────────────────────────────────────────────┐

│  Zusammenfassung                                         │

│  Von: 2025-10-01  Bis: 2025-10-06  [Aktualisieren]     │

│                                                          │

│  2025-10-01 bis 2025-10-06            Gesamt: 42.5h    │

│  ┌─────────────────────────────────────────────────────┐│

│  │ Ticket         Stunden      Anteil                  ││

│  │ Projekt A      18.5h        43.5%                   ││

│  │ Support        15.0h        35.3%                   ││

│  │ Admin           9.0h        21.2%                   ││

│  └─────────────────────────────────────────────────────┘│

└─────────────────────────────────────────────────────────┘

```



## 🔧 Voraussetzungen



### Produktiv (Docker)

- **Docker** >= 20.10

- **Docker Compose** >= 2.0

- **Git** (zum Klonen des Repositories)



### Entwicklung (Lokal)

- **Python** >= 3.11

- **pip** (Python Package Manager)

- **Git**



### Optional

- **Traefik** (für automatisches HTTPS in Production)

- **SSH-Zugang** zu einem Server (für Deployment)



## 📦 Installation



### Schnellstart mit Docker (Empfohlen)



```bash

# 1. Repository klonen

git clone https://github.com/yourusername/timesheet-app.git

cd timesheet-app



# 2. Environment-Variablen konfigurieren

cp .env.example .env

nano .env  # SECRET_KEY anpassen!



# 3. Container starten

docker-compose up -d



# 4. App öffnen

# Lokal: http://localhost:5000

# Production: https://your-domain.com



# 5. Mit Demo-User einloggen

# Username: demoUser

# Passwort: demo123

```



### Lokale Entwicklung (ohne Docker)



```bash

# 1. Repository klonen

git clone https://github.com/yourusername/timesheet-app.git

cd timesheet-app



# 2. Virtual Environment erstellen

python3 -m venv venv

source venv/bin/activate  # Linux/Mac

# oder: venv\Scripts\activate  # Windows



# 3. Dependencies installieren

pip install -r requirements.txt



# 4. Environment-Variablen setzen

export SECRET_KEY="your-secret-key-here"

export DATABASE_PATH="./timesheet.db"

export FLASK_ENV="development"



# 5. App starten

python volumes/app/timesheet_app.py



# 6. Browser öffnen

# http://localhost:5000

```



## ⚙️ Konfiguration



### Environment-Variablen (.env)



```bash

# Secret Key für Flask Sessions (WICHTIG: Ändern!)

SECRET_KEY=your-super-secret-key-change-this-1758709029



# Datenbank-Pfad (im Container)

DATABASE_PATH=/app/data/timesheet.db



# Flask Environment (production/development)

FLASK_ENV=production



# Timezone

TZ=Europe/Zurich

```



### Secret Key generieren



```bash

# Sicheren Random Key generieren

python -c 'import os; print(os.urandom(24).hex())'

```



### Docker Compose Konfiguration



Die `docker-compose.yml` kann angepasst werden:



```yaml

services:

  timesheet-app:

    build: .

    ports:

      - "5000:5000"  # Port ändern falls nötig

    volumes:

      - ./volumes/app:/app

    environment:

      - TZ=Europe/Zurich  # Timezone anpassen

    user: "1001:1001"  # UID/GID anpassen

    networks:

      - proxy  # Für Traefik

    labels:

      # Traefik-Labels für automatisches HTTPS

      - "traefik.enable=true"

      - "traefik.http.routers.timesheet.rule=Host(`your-domain.com`)"

      - "traefik.http.routers.timesheet.entrypoints=websecure"

      - "traefik.http.routers.timesheet.tls.certresolver=letsencrypt"

```



## 🚀 Verwendung



### Erster Login



1. Öffne die App in deinem Browser

2. Klicke auf **"Jetzt registrieren"**

3. Wähle Username und Passwort (min. 6 Zeichen)

4. Du wirst automatisch eingeloggt



Oder verwende den Demo-User:

- **Username:** `demoUser`

- **Passwort:** `demo123`



⚠️ **WICHTIG:** Ändere das Demo-Passwort sofort!



### Zeiterfassung



#### Ticket erstellen

1. Klicke auf **[+]** Button

2. Gib Namen ein (z.B. "Projekt Alpha")

3. Optional: Jira-Nummer, Matrix-Nummer

4. Wähle eine Farbe

5. Klicke **"Erstellen"**



#### Timer starten

1. Klicke auf ein **Ticket** (farbige Kachel)

2. Timer startet automatisch

3. Vorheriger Timer wird gestoppt



#### Timer stoppen

1. Klicke auf **[Stopp]** Button

2. Timer wird beendet und gespeichert



#### Zeiten bearbeiten

- **Start-Zeit:** Klicke auf das Datum/Zeit-Feld → ändere → automatisch gespeichert

- **End-Zeit:** Gleich wie Start-Zeit

- **Bemerkungen:** Textfeld editieren → automatisch gespeichert



#### Eintrag löschen

- Klicke auf **[×]** Button rechts



### Tickets verwalten



#### Sortieren (Drag & Drop)

1. Klicke und halte auf ein Ticket (gesamte Kachel ist ziehbar)

2. Ziehe zur gewünschten Position

3. Loslassen → Reihenfolge wird gespeichert



#### Bearbeiten

1. Hover über Ticket

2. Klicke auf **[✎]** Button

3. Ändere Details

4. Klicke **"Speichern"**



#### Löschen

1. Hover über Ticket

2. Klicke auf **[×]** Button

3. Bestätige Löschung



### Zusammenfassung anzeigen



1. Klicke auf **"Zusammenfassung"** oben rechts

2. Wähle Zeitraum (Von/Bis)

3. Klicke **"Aktualisieren"**

4. Siehe Aufschlüsselung nach Tickets



### Passwort ändern



1. Klicke auf **"Passwort ändern"** oben rechts

2. Gib aktuelles Passwort ein

3. Gib neues Passwort ein (min. 6 Zeichen)

4. Bestätige neues Passwort

5. Klicke **"Passwort ändern"**



### Logout



Klicke auf **"Abmelden"** oben rechts (roter Button)



## 🛠️ Admin-Tools



Das Projekt enthält Admin-Tools für User-Management:



### Passwort zurücksetzen



Wenn ein User sein Passwort vergessen hat:



```bash

# Interaktiver Modus

./reset_password.sh



# Oder direkt per Kommando

./reset_password.sh reset-user username neuesPasswort

```



Siehe [docs/PASSWORD_RESET.md](docs/PASSWORD_RESET.md) für Details.



### User-Daten migrieren



Daten von einem User zu einem anderen übertragen:



```bash

# Interaktiver Modus

./migrate_users.sh



# Oder direkt per Kommando

./migrate_users.sh migrate source_id target_id

```



Siehe [docs/USER_MIGRATION.md](docs/USER_MIGRATION.md) für Details.



### Backup erstellen



```bash

# Datenbank-Backup

docker cp timesheet-app:/app/data/timesheet.db ./backup_$(date +%Y%m%d).db



# Komplettes Volume-Backup

tar -czf backup_volumes_$(date +%Y%m%d).tar.gz volumes/

```



### Restore aus Backup



```bash

# Datenbank wiederherstellen

docker cp ./backup_20251006.db timesheet-app:/app/data/timesheet.db

docker-compose restart

```



## 🌐 Deployment



### Production-Deployment mit Traefik



```bash

# 1. Server vorbereiten

ssh user@your-server.com



# 2. Repository klonen

git clone https://github.com/yourusername/timesheet-app.git

cd timesheet-app



# 3. Environment konfigurieren

cp .env.example .env

nano .env  # SECRET_KEY setzen!



# 4. Docker-Compose anpassen

nano docker-compose.yml

# - Domain anpassen (traefik.http.routers.timesheet.rule)

# - UID/GID anpassen falls nötig



# 5. Traefik-Netzwerk erstellen (falls nicht vorhanden)

docker network create proxy



# 6. Container starten

docker-compose up -d



# 7. Logs prüfen

docker logs -f timesheet-app



# 8. App testen

curl -I https://your-domain.com

```



### Updates deployen



```bash

# 1. Code aktualisieren

git pull origin main



# 2. Container neu bauen und starten

docker-compose down

docker-compose up -d --build



# 3. Prüfen

docker logs -f timesheet-app

```



### Health Check



```bash

# Container-Status prüfen

docker ps | grep timesheet



# Logs anschauen

docker logs timesheet-app



# In Container einloggen

docker exec -it timesheet-app /bin/bash



# Datenbank prüfen

docker exec -it timesheet-app sqlite3 /app/data/timesheet.db "SELECT COUNT(*) FROM users;"

```



## 📁 Projektstruktur



```

timesheet-app/

├── volumes/

│   └── app/

│       ├── timesheet_app.py          # Haupt-Flask-App

│       ├── data/

│       │   └── timesheet.db          # SQLite-Datenbank

│       ├── templates/

│       │   ├── base.html             # Base-Template

│       │   ├── login.html            # Login-Seite

│       │   ├── register.html         # Registrierungs-Seite

│       │   ├── timesheet.html        # Haupt-Zeiterfassungs-Ansicht

│       │   ├── summary.html          # Zusammenfassungs-Ansicht

│       │   ├── change_password.html  # Passwort ändern

│       │   └── components/

│       │       ├── _header.html      # Header-Component

│       │       ├── _entry_table.html # Einträge-Tabelle

│       │       └── _ticket_modal.html# Ticket-Modal

│       ├── static/

│       │   ├── css/

│       │   │   ├── base.css          # Basis-Styles

│       │   │   ├── timesheet.css     # Zeiterfassungs-Styles

│       │   │   └── modal.css         # Modal-Styles

│       │   └── js/

│       │       ├── main.js           # Haupt-JavaScript

│       │       ├── timer.js          # Timer-Funktionalität

│       │       ├── modal.js          # Modal-Handling

│       │       └── drag-drop.js      # Drag & Drop

│       └── start.sh                  # Container-Startscript

├── docs/

│   ├── PASSWORD_RESET.md             # Passwort-Reset Doku

│   └── USER_MIGRATION.md             # User-Migration Doku

├── scripts/

│   ├── reset_password.py             # Passwort-Reset Tool

│   ├── reset_password.sh             # Shell-Wrapper

│   ├── migrate_users.py              # User-Migration Tool

│   └── migrate_users.sh              # Shell-Wrapper

├── Dockerfile                        # Docker-Image Definition

├── docker-compose.yml                # Docker-Compose Config

├── requirements.txt                  # Python-Dependencies

├── .env.example                      # Example Environment

├── .gitignore                        # Git-Ignore

├── stopAndKill.sh                    # Container stoppen/löschen

├── LICENSE                           # MIT Lizenz

└── README.md                         # Diese Datei

```



## 🔨 Technologie-Stack



### Backend

- **Flask 2.3.3** - Python Web Framework

- **Werkzeug 2.3.7** - WSGI Utilities (Password Hashing)

- **SQLite** - Embedded Database

- **Python 3.11** - Programming Language



### Frontend

- **HTML5 / CSS3** - Markup & Styling

- **Vanilla JavaScript** - No Framework Dependencies

- **GitHub-Style Design** - Clean, Professional UI



### Infrastructure

- **Docker** - Containerization

- **Docker Compose** - Multi-Container Orchestration

- **Traefik** - Reverse Proxy & Automatic HTTPS

- **Let's Encrypt** - Free SSL Certificates



### Development Tools

- **Git** - Version Control

- **Shell Scripts** - Automation

- **SQLite3** - Database Management



## 👨‍💻 Entwicklung



### Development Setup



```bash

# Repository klonen

git clone https://github.com/yourusername/timesheet-app.git

cd timesheet-app



# Virtual Environment

python3 -m venv venv

source venv/bin/activate



# Dependencies installieren

pip install -r requirements.txt



# Development Server

export FLASK_ENV=development

python volumes/app/timesheet_app.py

```



### Code-Struktur



Die App folgt dem **MVC-Pattern**:

- **Model:** `TimesheetManager` Klasse (Datenbank-Operationen)

- **View:** Jinja2 Templates in `templates/`

- **Controller:** Flask Routes in `timesheet_app.py`



### Neue Features entwickeln



1. **Branch erstellen**

   ```bash

   git checkout -b feature/my-new-feature

   ```



2. **Code schreiben**

   - Backend: `timesheet_app.py`

   - Frontend: Templates + CSS/JS



3. **Testen**

   ```bash

   python volumes/app/timesheet_app.py

   # Browser: http://localhost:5000

   ```



4. **Commit & Push**

   ```bash

   git add .

   git commit -m "Add: My new feature"

   git push origin feature/my-new-feature

   ```



5. **Pull Request erstellen**



### Database Schema



```sql

-- Users

CREATE TABLE users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE NOT NULL,

    password_hash TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



-- Tickets

CREATE TABLE tickets (

    id TEXT PRIMARY KEY,

    user_id INTEGER,

    name TEXT NOT NULL,

    color TEXT NOT NULL,

    jira_ticket TEXT DEFAULT '',

    matrix_ticket TEXT DEFAULT '',

    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users (id)

);



-- Time Entries

CREATE TABLE time_entries (

    id TEXT PRIMARY KEY,

    user_id INTEGER,

    ticket_name TEXT NOT NULL,

    start_time TIMESTAMP NOT NULL,

    end_time TIMESTAMP,

    memo TEXT DEFAULT '',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users (id)

);



-- Current Entries

CREATE TABLE current_entries (

    user_id INTEGER PRIMARY KEY,

    entry_id TEXT,

    FOREIGN KEY (user_id) REFERENCES users (id),

    FOREIGN KEY (entry_id) REFERENCES time_entries (id)

);



-- User Ticket Order

CREATE TABLE user_ticket_order (

    user_id INTEGER PRIMARY KEY,

    ticket_order TEXT,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users (id)

);

```



## 🐛 Troubleshooting



### Container startet nicht



```bash

# Logs anschauen

docker logs timesheet-app



# Container neu bauen

docker-compose down

docker-compose build --no-cache

docker-compose up -d

```



### Datenbank-Fehler



```bash

# Datenbank-Pfad prüfen

docker exec -it timesheet-app ls -la /app/data/



# Berechtigungen prüfen

docker exec -it timesheet-app ls -la /app/data/timesheet.db



# Datenbank reparieren

docker exec -it timesheet-app sqlite3 /app/data/timesheet.db "PRAGMA integrity_check;"

```



### Kein Logout-Button sichtbar



```bash

# Header-Fix ausführen

./fix_header.sh



# Oder manuell

docker cp volumes/app/templates/components/_header.html timesheet-app:/app/templates/components/_header.html

docker-compose restart



# Browser-Cache leeren (Strg+F5)

```



### Port bereits belegt



```bash

# Port in docker-compose.yml ändern

# Von: "5000:5000"

# Zu:  "5001:5000"



docker-compose down

docker-compose up -d

```



### Passwort vergessen



```bash

# Passwort zurücksetzen

./reset_password.sh reset-user username neuesPasswort



# Oder direkt per URL

# https://your-domain.com/logout

# Dann neuen Account registrieren

```



### Drag & Drop funktioniert nicht



1. Browser-Cache leeren (Strg+F5)

2. Prüfe ob `drag-drop.js` geladen wird (Browser DevTools → Network)

3. JavaScript-Konsole auf Fehler prüfen (F12)



```bash

# Script-Dateien aktualisieren

docker cp volumes/app/static/js/drag-drop.js timesheet-app:/app/static/js/drag-drop.js

docker-compose restart

```



## 🤝 Mitwirken



Beiträge sind willkommen! Hier ist wie du helfen kannst:



### Bug Reports



Öffne ein [Issue](https://github.com/yourusername/timesheet-app/issues) mit:

- **Beschreibung** des Problems

- **Schritte zur Reproduktion**

- **Erwartetes** vs **tatsächliches** Verhalten

- **Screenshots** (falls relevant)

- **Environment** (OS, Browser, Docker-Version)



### Feature Requests



Öffne ein [Issue](https://github.com/yourusername/timesheet-app/issues) mit:

- **Beschreibung** des Features

- **Use Case** - Warum ist es nützlich?

- **Mockups** (optional)



### Pull Requests



1. Fork das Repository

2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)

3. Commit deine Änderungen (`git commit -m 'Add: Amazing Feature'`)

4. Push zum Branch (`git push origin feature/AmazingFeature`)

5. Öffne einen Pull Request



### Coding Guidelines



- **Python:** PEP 8 Style Guide

- **JavaScript:** ESLint (Standard Config)

- **CSS:** BEM Naming Convention

- **Commits:** Conventional Commits Format

  - `feat:` Neue Features

  - `fix:` Bugfixes

  - `docs:` Dokumentation

  - `style:` Formatierung

  - `refactor:` Code-Refactoring

  - `test:` Tests

  - `chore:` Maintenance



## 📄 Lizenz



Dieses Projekt ist lizenziert unter der **MIT License** - siehe [LICENSE](LICENSE) Datei für Details.



```

MIT License



Copyright (c) 2025 [Dein Name]



Permission is hereby granted, free of charge, to any person obtaining a copy

of this software and associated documentation files (the "Software"), to deal

in the Software without restriction, including without limitation the rights

to use, copy, modify, merge, publish, distribute, sublicense, and/or sell

copies of the Software, and to permit persons to whom the Software is

furnished to do so, subject to the following conditions:



The above copyright notice and this permission notice shall be included in all

copies or substantial portions of the Software.



THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR

IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,

FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE

AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER

LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,

OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE

SOFTWARE.

```



## 📞 Kontakt



**Projekt Link:** [https://github.com/yourusername/timesheet-app](https://github.com/yourusername/timesheet-app)



**Issues:** [https://github.com/yourusername/timesheet-app/issues](https://github.com/yourusername/timesheet-app/issues)



**Author:** Dein Name - [@yourhandle](https://twitter.com/yourhandle)



**Website:** [https://your-domain.com](https://your-domain.com)



---



## 🙏 Acknowledgments



- [Flask](https://flask.palletsprojects.com/) - Das Web Framework

- [GitHub Primer](https://primer.style/) - Design-Inspiration

- [Docker](https://www.docker.com/) - Containerization

- [Traefik](https://traefik.io/) - Reverse Proxy



---



## 📊 Project Stats



![GitHub stars](https://img.shields.io/github/stars/yourusername/timesheet-app?style=social)

![GitHub forks](https://img.shields.io/github/forks/yourusername/timesheet-app?style=social)

![GitHub issues](https://img.shields.io/github/issues/yourusername/timesheet-app)

![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/timesheet-app)

![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/timesheet-app)



---



<p align="center">Made with ❤️ and ☕</p>

<p align="center">⭐ Star dieses Projekt wenn es dir gefällt!</p>
