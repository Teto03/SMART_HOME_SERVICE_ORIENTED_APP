# Documentazione di Compliance (SDE Project)

## 1. Introduzione

Questo documento attesta la conformità del progetto "SmartHome IoT Simulator" rispetto alle specifiche tecniche del corso di Software Design & Engineering (SDE). Il sistema implementa un'architettura a microservizi (SOA) completa per la gestione domotica intelligente.

## 2. Matrice di Compliance

Di seguito viene mappata l'implementazione attuale rispetto ai requisiti standard.

| Requisito | Stato | Implementazione nel Progetto |
| :--- | :--- | :--- |
| **Layered Architecture** | ✅ COMPLIANT | Il progetto è diviso rigorosamente in 4 livelli logici: Data, Adapter, Business Logic, Process Centric. Ogni livello ha responsabilità definite (vedi *architecture_and_logic.md*). |
| **Microservices / SOA** | ✅ COMPLIANT | Il sistema è composto da **7 microservizi indipendenti**, ognuno in esecuzione nel proprio container Docker e comunicante via REST/JSON. |
| **Orchestration** | ✅ COMPLIANT | Due processi di orchestrazione distinti: <br>1. **Dashboard Process**: Aggrega dati sincroni per la UI. <br>2. **Alert Process**: Loop asincrono che coordina Data, Anomaly e Telegram. |
| **External Adapters** | ✅ COMPLIANT | Pattern Adapter implementato per: <br>- **OpenWeatherMap** (Meteo Reale). <br>- **Telegram Bot API** (Notifiche Push). |
| **Containerization** | ✅ COMPLIANT | Ogni servizio ha il suo `Dockerfile`. Il sistema è avviato tramite `docker-compose.yml`, gestendo network e volumi. |
| **Business Logic Isolation** | ✅ COMPLIANT | Le regole di business (Anomaly Detection, Energy Optimization) sono incapsulate in servizi dedicati e non mischiate con la logica di UI o di accesso ai dati grezzi. |

---

## 3. Dettaglio Requisiti Funzionali

### Gestione Dati e Persistenza
- **Specifica**: "Tutti i dati devono essere gestiti da un servizio dedicato."
- **Implementazione**: `Device Data Service` (Porta 5001) è l'unico gateway per MongoDB. Nessun altro servizio scrive su DB direttamente.

### Gestione Utenti (Auth)
- **Specifica**: "Sistema di Login e Registrazione sicuro".
- **Implementazione**: `Auth Service` gestisce utenti, password hashate (SHA-256/Bcrypt) e rilascio token JWT per sessioni stateless.

### Logica "Smart" (IoT)
- **energy_optimizer.py**: Implementa algoritmi decisionali basati su input ambientali (Stagione, Meteo, Temp Interna). Non è un semplice "if-else" cablato, ma una logica dinamica.
- **anomaly_detector.py**: Valuta insiemi di dati eterogenei (Finestre + AC + Meteo) per dedurre stati complessi (Waste, Conflict).

### Interfaccia Utente
- **Specifica**: "Dashboard per visualizzazione e controllo".
- **Implementazione**: Web App Flask responsive che permette il controllo bidirezionale (Lettura sensori + Invio comandi).

---

## 4. Strumenti e Tecnologie

Il progetto rispetta lo stack tecnologico moderno suggerito:

- **Linguaggio**: Python 3.9+
- **Framework Web**: Flask (Micro-framework ideale per microservizi).
- **Database**: MongoDB (NoSQL per flessibilità schema IoT).
- **Deployment**: Docker & Docker Compose.
- **Documentation**: OpenAPI (Swagger) per le specifiche API.
