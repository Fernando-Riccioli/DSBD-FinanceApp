# FinanceApp - Progetto Distributed Systems & Big Data 2024-2025
- Fernando Riccioli
- Daniele Lucifora

## Descrizione 

Un'applicazione moderna per la gestione di dati finanziari, sviluppata con un'**architettura a microservizi** che utilizza **gRPC** per la comunicazione tra componenti. L'applicazione permette la registrazione e gestione degli utenti, l'aggiornamento e monitoraggio dei ticker finanziari, la configurazione di soglie personalizzate per i ticker e l'invio automatico di notifiche via email. Il sistema implementa l'utilizzo della cache per garantire l'unicità delle operazioni (**at-most-once**).

## Componenti Principali
- **MySQL** come databse per la persistenza dei dati
- **Kafka** come broker dei messaggi per il sistema di notifica
- **Kubernetes** (Minikube) per il deployment
- **Prometheus** per il monitoraggio delle metriche e per l'osservabilità
- **gRPC** con serializzazione **Protobuf** come protocollo per le chiamate client-server
- Pattern **CQRS** per separare operazioni di lettura e scrittura
- **Docker** per la containerizzazione

## Build & Deploy

### Prerequisiti Windows
Per avviare il makefile su Windows è stato scelto di utilizzare `GnuWin32`. Per installarlo dal terminale:
- Digitare `winget install GnuWin32.Make`
- Digitare `winget install GnuWin32.GetText` <!-- Necessario per envsubst -->
- Aggiungere `C:\Program Files (x86)\GnuWin32\bin` come variabile di ambiente al PATH di sistema. 

### Passi introduttivi
1. Avviare Docker Desktop
2. Aprire il terminale e selezionare una directory per clonare la repository.
3. Digitare `git clone https://github.com/Fernando-Riccioli/FinanceApp`
4. Digitare `minikube start --driver=docker` per avviare Minikube.
5. Digitare `minikube docker-env` e il comando successivo fornito dal terminale.

### Makefile
6. Recuperare il proprio username su Docker Hub.
7. Spostarsi all'interno della cartella clonata e digitare.
    - Mac/Linux: `export IMAGE_REPO=usernameDockerHub` <!-- Definiamo una variabile d'ambiente IMAGE_REPO -->
    - Windows: `$env:IMAGE_REPO = "usernameDockerHub"`
8. Digitare `make build` <!-- per creare le immagini Docker, effettuare il tagging delle immagini ed il push alla repository remota. -->
9. Digitare `make prepare` <!-- per caricare le immagini Docker nel Minikube ed applicare i manifest. -->
10. Attendere che i pod siano in stato _running_, per controllare è possibile utilizzare il comando `kubectl get pods`. Questo passaggio può richiedere qualche minuto. 

### Port Forwarding
11. Tramite `kubectl get pods` ottenere il name del pod server e del pod prometheus
12. Digitare `kubectl port-forward pod/nome_server 50051:50051` sostituendo `nome_server` con il nome ottenuto.
13. Aprire un'altra finestra di terminale e digitare `kubectl port-forward pod/nome_prometheus 9090:9090` sostituendo `nome_prometheus` con il nome ottenuto.
14. Aprire un'altra finestra di terminale, spostarsi all'interno della directory gRPC e digitare `python client.py`
15. Eseguire le istruzioni visualizzate nel terminale

### Eliminazione 
Per eliminare Minikube e le immagini Docker eseguire i seguenti comandi in sequenza:
- `minikube delete`
- `eval $(minikube docker-env --unset)` 
- `docker rmi -f $(docker images -q)` 
