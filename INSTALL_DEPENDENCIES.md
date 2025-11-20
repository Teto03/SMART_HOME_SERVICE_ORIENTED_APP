# Installazione Dipendenze Mancanti

## Problema
I servizi non partono perché Flask non è installato.

## Soluzione

Esegui questo comando nel terminale:

```bash
sudo apt install -y python3-flask python3-requests
```

Inserisci la password quando richiesto.

## Dopo l'Installazione

Lancia i servizi:

```bash
cd /home/francesco/Scrivania/SED_PROJECT
./start_all.sh
```

Il server dovrebbe ora partire correttamente su `http://localhost:5000`
