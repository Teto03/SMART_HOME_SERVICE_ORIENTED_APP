# SmartHome IoT Simulator - Documentazione Architetturale e Logica di Business

## 1. Visione e Obiettivo

Il progetto **SmartHome IoT Simulator** nasce con l'obiettivo di ideare, progettare e sviluppare un sistema Service-Oriented (SOA) per la gestione intelligente e automatizzata di un ambiente domestico. Il sistema affronta due problematiche principali:
1.  **Efficienza Energetica**: Ottimizzazione dei consumi basata non solo sulle condizioni interne (temperatura rilevata), ma anche sulle condizioni meteorologiche reali esterne (ottenute tramite API di terze parti).
2.  **Sicurezza Domestica**: Monitoraggio continuo per il rilevamento di anomalie critiche (es. principi di incendio, temperature fuori norma) con notifica tempestiva all'utente.

L'applicazione simula un ecosistema IoT completo, dove sensori virtuali generano dati che vengono elaborati da una catena di microservizi orchestrati per fornire valore aggiunto all'utente finale tramite una Dashboard Web e notifiche istantanee su Telegram.

---

## 2. Architettura del Sistema

L'architettura adotta rigorosamente il **Layered Architectural Pattern** (Architettura a Strati), come richiesto dalle specifiche del corso SDE. Questo approccio garantisce:
*   **Separazione delle Responsabilità (SoC)**: Ogni livello ha un ruolo ben definito.
*   **Disaccoppiamento**: I livelli comunicano solo con quelli adiacenti.
*   **Manutenibilità e Scalabilità**: È possibile modificare o sostituire un componente senza impattare l'intero sistema.

Il sistema è composto da microservizi **RESTful** autonomi che comunicano scambiando payload **JSON**.

### Diagramma Logico dei Livelli

```mermaid
graph TD
    subgraph "User Interface Layer"
        UI[Web Dashboard]
        TG[Telegram Client]
    end

    subgraph "Process Centric Layer (Orchestration)"
        DO[Dashboard Orchestrator Service]
        SM[Security Monitor Service]
    end

    subgraph "Business Logic Layer (Intelligence)"
        EO[Energy Optimization Service]
        AD[Anomaly Detection Service]
    end

    subgraph "Adapter Services Layer (Integration)"
        WA[Weather Adapter Service]
        NA[Notification Adapter Service]
    end

    subgraph "Data Services Layer (Persistence)"
        DR[Device Registry & Data Service]
        US[User Service (Optional)]
    end

    subgraph "IoT Layer"
        SIM[IoT Simulators]
    end

    UI --> DO
    TG <--> NA
    DO --> DR
    DO --> WA
    DO --> EO
    SM --> DR
    SM --> AD
    SM --> NA
    EO --> WA
    AD --> DR
    SIM --> DR
```

---

## 3. Dettaglio dei Livelli e dei Servizi

### A. Data Services Layer (Persistenza)
Questo livello gestisce l'accesso ai dati e la persistenza. È l'unico punto di contatto con il database. Nessun servizio di business o di processo accede direttamente al DB.

#### 1. Device Registry & Data Service
*   **Responsabilità**:
    *   Gestione dell'anagrafica dei dispositivi (sensori di temperatura, rilevatori di fumo, luci).
    *   Storicizzazione delle letture (telemetria) inviate dai simulatori.
    *   Fornitura dello storico dati agli altri servizi.
*   **Tecnologia**: Python/Flask + SQLite.
*   **Endpoints Principali**:
    *   `POST /readings`: Ingestione dati dai simulatori.
    *   `GET /devices`: Lista dei dispositivi registrati.
    *   `GET /history`: Recupero serie temporali di letture.
*   **Logica**: CRUD (Create, Read, Update, Delete) pura, senza elaborazioni complesse.

#### 2. User Service
*   **Responsabilità**: Gestione dei profili utente, autenticazione e preferenze.
*   **Tecnologia**: Python/Flask + SQLite.

---

### B. Adapter Services Layer (Integrazione Esterna)
Questo livello funge da "ponte" (Adapter Pattern) verso servizi esterni, normalizzando interfacce e dati eterogenei in un formato JSON standard interno comprensibile dal sistema.

#### 3. Weather Adapter Service
*   **Responsabilità**: Fornire dati meteorologici correnti per la localizzazione della casa.
*   **Integrazione**: Interroga API esterne reali (es. OpenWeatherMap o WeatherAPI).
*   **Logica di Adattamento**:
    *   Effettua la chiamata HTTP all'API esterna.
    *   Estrae solo i campi rilevanti (Temperatura esterna, Umidità, Condizioni).
    *   Restituisce un JSON standardizzato al chiamante interno.

#### 4. Notification Adapter Service (Telegram)
*   **Responsabilità**: Inviare notifiche push agli utenti tramite Telegram.
*   **Integrazione**: Telegram Bot API.
*   **Logica di Adattamento**:
    *   Riceve un payload JSON generico dal sistema (es. `{ "message": "Allarme Fuoco!", "priority": "high" }`).
    *   Formatta il messaggio secondo le specifiche di Telegram.
    *   Esegue la chiamata alle API di Telegram per la consegna al Chat ID dell'utente.

---

### C. Business Logic Services Layer (Intelligenza)
Questo livello contiene il "cervello" dell'applicazione. Esegue calcoli, prende decisioni e applica regole di dominio. È **Stateless** e non accede direttamente al database (chiede i dati al Data Layer o li riceve in input).

#### 5. Energy Optimization Service
*   **Responsabilità**: Calcolare consigli per il risparmio energetico.
*   **Logica**:
    *   Confronta la temperatura interna (ricevuta dal Data Layer) con quella esterna (ricevuta dal Weather Adapter).
    *   **Regola Esempio**: `SE (Temp_Interna > 24°C) AND (Temp_Esterna < 20°C) ALLORA Consiglio = "Apri le finestre per raffrescare gratuitamente."`
    *   **Regola Esempio**: `SE (Temp_Interna < 18°C) AND (Temp_Esterna > 22°C) ALLORA Consiglio = "Apri le finestre per riscaldare gratuitamente."`

#### 6. Anomaly Detection Service
*   **Responsabilità**: Identificare situazioni di pericolo o malfunzionamenti.
*   **Logica**:
    *   Analizza un set di letture recenti.
    *   **Rilevamento Picchi**: Se la temperatura sale di X gradi in Y minuti -> Possibile incendio.
    *   **Soglie Critiche**: Se Fumo = Rilevato O Temp > 50°C -> Allarme Critico.
    *   Restituisce un oggetto di stato (es. `{ "status": "CRITICAL", "reason": "Fire detected" }`).

---

### D. Process Centric Services Layer (Orchestrazione)
Questo livello espone le API finali per l'interfaccia utente. Coordina (orchestra) chiamate multiple ai servizi sottostanti per soddisfare casi d'uso complessi.

#### 7. Processo 1: Dashboard Orchestrator Service
*   **Obiettivo**: Popolare la dashboard principale dell'utente con una singola chiamata.
*   **Flusso di Orchestrazione**:
    1.  Chiama **Device Data Service** -> Ottiene le ultime letture dei sensori.
    2.  Chiama **Weather Adapter** -> Ottiene il meteo attuale.
    3.  Chiama **Energy Optimization Service** (passando dati interni ed esterni) -> Ottiene consigli di ottimizzazione.
    4.  **Aggregazione**: Combina tutti i risultati in un unico JSON strutturato per il frontend.

#### 8. Processo 2: Security Monitor Service
*   **Obiettivo**: Monitoraggio attivo in background e gestione emergenze.
*   **Flusso di Orchestrazione**:
    1.  Recupera periodicamente le letture dal **Device Data Service**.
    2.  Invia i dati all'**Anomaly Detection Service**.
    3.  **Logica Condizionale**:
        *   **SE** l'Anomaly Detection restituisce uno stato di allarme:
            *   Chiama **Notification Adapter** -> Invia alert su Telegram "PERICOLO RILEVATO".
            *   Chiama **Device Data Service** -> Aggiorna lo stato del dispositivo a "WARNING".

---

## 4. Conformità alle Specifiche (Compliance Matrix)

| Requisito SDE | Implementazione nel Progetto |
| :--- | :--- |
| **Architettura Gerarchica** | Implementata con 4 livelli distinti (Data, Adapter, Business, Process). |
| **Servizi REST** | Tutti i componenti espongono interfacce HTTP RESTful. |
| **Formato Dati** | Utilizzo esclusivo di JSON per input/output. |
| **Servizi Interni ed Esterni** | Interni: Data, Business, Process. Esterni: Weather (OpenWeather), Notification (Telegram). |
| **Process Centric Services** | Implementati 2 servizi di processo (Dashboard, Security) che orchestrano 3+ servizi ciascuno. |
| **Database** | Utilizzo di SQLite gestito esclusivamente dal Data Layer. |
| **UI** | Interfaccia Web + Bot Telegram. |
| **Autenticazione** | Implementata (Token Header Authorization) come richiesto per i progetti da 2/3 studenti. |

---

## 5. Stack Tecnologico

*   **Linguaggio**: Python 3.x
*   **Framework Web**: Flask (leggero, ideale per microservizi).
*   **Database**: SQLite (file-based, portabile).
*   **Containerizzazione**: Docker & Docker Compose (per l'orchestrazione dei container).
*   **Version Control**: Git & GitHub.
*   **Documentazione API**: OpenAPI 3.0 (Swagger).
*   **Librerie Esterne**:
    *   `requests`: Per chiamate HTTP sincrone tra servizi.
    *   `python-telegram-bot`: Per interazione con Telegram.

## 6. Flussi di Dati (Data Flow)

### Flusso di Monitoraggio Sicurezza (Security Loop)
1.  **IoT Simulator**: Genera una lettura (es. Temp=60°C) e la invia via POST al *Device Data Service*.
2.  **Security Monitor**: (Job schedulato) Chiede le ultime letture al *Device Data Service*.
3.  **Security Monitor**: Invia le letture all'*Anomaly Detection Service*.
4.  **Anomaly Detection**: Rileva la soglia critica (>50°C) e restituisce `{"alert": true}`.
5.  **Security Monitor**: Riceve l'alert e invoca il *Notification Adapter*.
6.  **Notification Adapter**: Chiama le API di Telegram.
7.  **Utente**: Riceve la notifica sul telefono.

### Flusso Dashboard (User Request)
1.  **Utente**: Apre la Web App.
2.  **Web App**: Chiama `GET /dashboard-data` sul *Dashboard Orchestrator*.
3.  **Dashboard Orchestrator**:
    *   Parallelo: Chiama *Device Data Service* e *Weather Adapter*.
    *   Sequenziale: Chiama *Energy Optimization* con i dati ricevuti.
4.  **Dashboard Orchestrator**: Costruisce la risposta JSON aggregata.
5.  **Web App**: Renderizza grafici e consigli.
