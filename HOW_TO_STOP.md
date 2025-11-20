# Come Fermare il Server

## Metodo 1: Dal Terminale di Start
Se hai ancora aperto il terminale dove hai eseguito `./start_all.sh`:
1. Vai su quella finestra
2. Premi semplicemente **Enter**
3. Tutti i servizi si fermeranno automaticamente

## Metodo 2: Da Qualsiasi Terminale
Apri un nuovo terminale e esegui:
```bash
killall python3
```

Questo fermerà tutti i processi Python in esecuzione.

## Riavviare Dopo le Modifiche
Dopo aver fermato i servizi:
```bash
cd /home/francesco/Scrivania/SED_PROJECT
./start_all.sh
```
