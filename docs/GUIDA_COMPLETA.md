# Guida Utente - SmartHome IoT Simulator

Questa guida spiega come installare, configurare ed eseguire il sistema SmartHome IoT Simulator.

**Metodo Raccomandato**: Docker (Più semplice, nessuna dipendenza da installare).

---

## 🐳 Metodo 1: Esecuzione con Docker (Consigliato)

Il modo più pulito e veloce per avviare il progetto è utilizzare Docker. Questo isola l'ambiente e garantisce che tutto funzioni senza conflitti.

### Prerequisiti

- **Docker Desktop** (o Docker Engine + Docker Compose) installato.

### 1. Configurazione Automatica (Nuova Installazione)

Se stai installando il progetto su una nuova macchina, esegui questo script per configurare tutto automaticamente (creazione database e file .env):

```bash
./setup_docker.sh
```

### 2. Configurazione Manuale (Opzionale)

Se preferisci fare a mano o devi modificare le chiavi:

1. Copia il file di esempio:

   ```bash
   cp .env.example .env
   ```

2. Modifica il file `.env` (opzionale per test, necessario per funzionalità complete):
   - `SECRET_KEY`: Una stringa casuale per la sicurezza.
   - `OWM_API_KEY`: La tua chiave API di OpenWeatherMap (per meteo reale).
   - `TELEGRAM_TOKEN`: Il token del tuo Bot Telegram (per notifiche).

### 2. Avvio

Dalla cartella principale del progetto, esegui:

```bash
docker compose up --build -d
```

Attendi qualche istante. Docker scaricherà le immagini necessarie e avvierà tutti i 7 microservizi.

### 3. Accesso

Apri il browser e vai su:
👉 **<http://localhost:5008>**

### 4. Arresto

Per fermare il sistema, premi `Ctrl+C` nel terminale, oppure esegui in un altro terminale:

```bash
docker compose down
```

### 5. Persistenza dei Dati

Il sistema utilizza **MongoDB** come database.
I dati non vengono salvati in un file locale (come `users.db`), ma in un **Docker Volume** gestito internamente da Docker.

- **Nome del Volume**: `mongo_data`
- **Comportamento**:
  - Se spegni il sistema (`docker compose down`): **I dati rimangono salvi.**
  - Se riavvii il computer: **I dati rimangono salvi.**
  - I dati vengono cancellati **SOLO** se esegui esplicitamente: `docker compose down -v` (con il flag `-v` che sta per volumes).

---

## 🐍 Metodo 2: Esecuzione Locale (Python)

Se non puoi usare Docker, puoi eseguire i servizi direttamente sulla tua macchina.

### Prerequisiti

- Python 3.8 o superiore.
- `pip` (Python Package Manager).

### 1. Installazione Dipendenze

Esegui lo script di installazione o installa manualmente:

```bash
pip install -r requirements.txt
```

### 2. Avvio

Usa lo script di avvio fornito:

```bash
./start_all.sh
```

Questo script avvierà tutti i servizi in background e salverà i log nella cartella `logs/`.

### 3. Arresto

Per fermare tutti i servizi, premi **Invio** nel terminale dove hai lanciato lo script.

---

## 📱 Guida all'Uso

### Registrazione e Login

1. Al primo accesso, clicca su **Login**.
2. Seleziona la tab **Register**.
3. Crea un nuovo utente (es. `admin`, password `password123`).
4. Effettua il login.

### Dashboard

- **Indoor Temp**: Temperatura simulata dal sensore interno.
- **Outdoor Weather**: Meteo attuale (da OpenWeatherMap o Mock).
- **Energy Advice**: Consigli intelligenti basati sul confronto tra interno ed esterno (es. "Chiudi le finestre se fuori fa troppo caldo").
- **Device Control**: Accendi/spegni luci, riscaldamento e apri/chiudi finestre.

### Notifiche Telegram

Se configurato, riceverai notifiche quando:

- La temperatura interna supera i 28°C.
- Viene rilevata un'anomalia critica.

---

## 🛠 Risoluzione Problemi

**Errore: "Port already in use"**

- Assicurati di non avere altri servizi in esecuzione sulle porte 5000-5010.
- Se usavi Docker, assicurati di aver fatto `docker compose down`.

**Errore: "Connection Refused"**

- Attendi qualche secondo dopo l'avvio; i servizi potrebbero star ancora caricando.
- Controlla i log con `docker compose logs` (se usi Docker) o nella cartella `logs/` (se locale).
