# Guida Completa - SmartHome IoT Simulator

Questa guida contiene tutte le informazioni necessarie per installare, configurare e utilizzare il SmartHome IoT Simulator.

---

## 📦 Installazione Dipendenze

### Problema
I servizi non partono perché Flask non è installato.

### Soluzione

Esegui questo comando nel terminale:

```bash
sudo apt install -y python3-flask python3-requests
```

Inserisci la password quando richiesto.

### Dopo l'Installazione

Lancia i servizi:

```bash
cd /home/francesco/Scrivania/SED_PROJECT
./start_all.sh
```

Il server dovrebbe ora partire correttamente su `http://localhost:5000`

---

## 🚀 Avvio del Sistema

### ✅ Avvio Corretto

1. Apri un terminale
2. Vai nella directory del progetto:
   ```bash
   cd /home/francesco/Scrivania/SED_PROJECT
   ```
3. Lancia lo script:
   ```bash
   ./start_all.sh
   ```

4. **IMPORTANTE**: Vedrai questo messaggio:
   ```
   All services running. Press Enter to stop...
   ```
   
   **Questo è NORMALE!** Il terminale sembra "bloccato" ma i servizi stanno girando.

5. **NON chiudere il terminale!** Lascialo aperto.

6. Apri il browser e vai su: **http://localhost:5000**

### ✅ Come Verificare che Funziona

Dopo aver lanciato `start_all.sh`, apri un **NUOVO** terminale e esegui:
```bash
curl http://localhost:5000
```

Se vedi HTML, funziona! Vai su http://localhost:5000 nel browser.

### ❌ Problemi Comuni

**"Il terminale è bloccato"**
→ È normale! I servizi stanno girando. Apri un nuovo terminale per altri comandi.

**"localhost:5000 non risponde"**
→ Controlla i log:
```bash
tail -f logs_webapp.txt
```

**"Come faccio altri comandi?"**
→ Apri un nuovo terminale. Il primo deve rimanere aperto con `start_all.sh` in esecuzione.

---

## 🛑 Fermare il Sistema

### Metodo 1: Dal Terminale di Start (Raccomandato)
Se hai ancora aperto il terminale dove hai eseguito `./start_all.sh`:
1. Vai su quella finestra
2. Premi semplicemente **Enter**
3. Tutti i servizi si fermeranno automaticamente

### Metodo 2: Da Qualsiasi Terminale
Se hai chiuso il terminale, apri un nuovo terminale e esegui:
```bash
killall python3
```

Questo fermerà tutti i processi Python in esecuzione.

### 🔄 Riavvio Dopo Modifiche

1. Ferma i servizi (Metodo 1 o 2)
2. Rilancia:
   ```bash
   cd /home/francesco/Scrivania/SED_PROJECT
   ./start_all.sh
   ```

---

## 🐳 Esecuzione con Docker

Se preferisci non installare dipendenze Python locali, puoi usare Docker.

### Prerequisiti
- Docker installato
- Docker Compose installato

### Avvio
1. Apri un terminale nella cartella del progetto.
2. Esegui:
   ```bash
   docker compose up --build
   ```
3. Attendi che tutti i servizi siano avviati.
4. Vai su **http://localhost:5000** nel browser.

### Arresto
Premi `Ctrl+C` nel terminale dove sta girando Docker.

---

## 📱 Configurazione Telegram Bot

Per ricevere notifiche dal tuo SmartHome IoT Simulator, devi creare un Bot Telegram e ottenere il tuo Chat ID.

### 1. Creare un Bot
1. Apri Telegram e cerca **@BotFather**.
2. Avvia una chat e invia il comando `/newbot`.
3. Segui le istruzioni per scegliere un nome e username per il tuo bot.
4. **BotFather** ti darà un **API Token** (es. `123456789:ABCdefGhI...`).
   * Salva questo token. Lo userai come variabile d'ambiente `TELEGRAM_TOKEN`.

### 2. Ottenere il Chat ID
1. Avvia una chat con il tuo nuovo bot e invia un messaggio (es. "Hello").
2. Apri il browser e visita:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   *(Sostituisci `<YOUR_BOT_TOKEN>` con il token ottenuto al passo 1)*
3. Cerca l'oggetto `"chat"` nella risposta JSON:
   ```json
   "chat": {
       "id": 123456789,
       "first_name": "Francesco",
       ...
   }
   ```
4. Il numero accanto a `"id"` è il tuo **Chat ID**.
   * Salva questo ID. Lo userai come variabile d'ambiente `TELEGRAM_CHAT_ID`.

### 3. Configurare il Simulatore
1. Copia il file di esempio `.env.example` in un nuovo file chiamato `.env`:
   ```bash
   cp .env.example .env
   ```
2. Apri il file `.env` con un editor di testo.
3. Inserisci il tuo **Token** e **Chat ID** nelle variabili corrispondenti:
   ```ini
   TELEGRAM_TOKEN=123456789:ABCdefGhI...
   TELEGRAM_CHAT_ID=987654321
   ```
4. Salva il file.

Riavvia il sistema con `./start_all.sh` per applicare le modifiche.

Ora, quando il sistema rileva un'anomalia (come l'apertura di una finestra), riceverai un messaggio su Telegram!

---

## 🌤️ Configurazione Weather API

Per ottenere dati meteo in tempo reale per il tuo SmartHome IoT Simulator, puoi configurare una chiave API gratuita di OpenWeatherMap.

### 1. Ottenere una Chiave API Gratuita
1. Vai su [OpenWeatherMap](https://openweathermap.org/) e registrati per un account gratuito.
2. Naviga nella scheda **API Keys** nel tuo profilo.
3. Copia la chiave API generata (sembra una lunga stringa di caratteri casuali).

### 2. Configurare il Simulatore
1. Se non l'hai già fatto, crea il file `.env` copiando l'esempio:
   ```bash
   cp .env.example .env
   ```
2. Apri il file `.env`.
3. Inserisci la tua chiave API nella variabile `OWM_API_KEY`:
   ```ini
   OWM_API_KEY=e7c09dd6eaba4bd292958f2fbcff734b
   ```
4. Salva il file.

### 3. Riavviare
Esegui di nuovo `./start_all.sh`. La dashboard mostrerà ora dati meteo reali per qualsiasi città tu selezioni!

---

## 📝 Riepilogo Rapido

1. **Installare dipendenze**: `sudo apt install -y python3-flask python3-requests`
2. **Avviare**: `./start_all.sh`
3. **Accedere**: http://localhost:5000
4. **Fermare**: Premi Enter nel terminale di avvio
5. **Configurare Segreti**: Crea `.env` da `.env.example` e inserisci le chiavi.
6. **Configurare Meteo/Telegram**: Modifica `.env` con le tue chiavi.
