import logging
import grpc
import finance_app_pb2
import finance_app_pb2_grpc

# TODO: Implementare il retry?
# https://grpc.io/docs/guides/retry/
# https://github.com/grpc/grpc/blob/master/examples/python/retry/retry_client.py

def registra_utente(stub):
    try:
        risposta = stub.RegistraUtente(finance_app_pb2.DatiUtente(email = "prova@gmail.com", ticker = "AAPL"), timeout = 3)
        print("Conferma registrazione: " + str(risposta.conferma) + ". " + risposta.messaggio)
    except grpc.RpcError:
        print(f"Chiamata fallita.")

def aggiorna_ticker(stub):
    try:
        risposta = stub.AggiornaTicker(finance_app_pb2.DatiUtente(email = "prova@gmail.com", ticker = "GOOGL"), timeout = 3)
        print("Conferma aggiornamento: " + str(risposta.conferma) + ". " + risposta.messaggio)
    except grpc.RpcError:
        print(f"Chiamata fallita.")

def cancella_utente(stub):
    try:
        risposta = stub.CancellaUtente(finance_app_pb2.Email(email = "prova@gmail.com"), timeout = 3)
        print("Conferma eliminazione: " + str(risposta.conferma) + ". " + risposta.messaggio)   
    except grpc.RpcError:
        print(f"Chiamata fallita.")

def recupera_valore(stub):
    try:
        risposta = stub.RecuperaValore(finance_app_pb2.Email(email = "pippo@gmail.com"), timeout = 3)
        print(f"Valore ottenuto: {round(risposta.valore, 2)}")
    except grpc.RpcError:
        print(f"Chiamata fallita.")

def calcola_media_valori(stub):
    try:
        risposta = stub.CalcolaMediaValori(finance_app_pb2.DatiMediaValori(email = "pippo@gmail.com", numeroDati = 10), timeout = 3)
        print(f"Media valori ottenuta: {round(risposta.valore, 2)}")
    except grpc.RpcError:
        print(f"Chiamata fallita.")

def visualizza_menu():
    print("\nScegli un'opzione:")
    print("1. Registra utente")
    print("2. Aggiorna ticker")
    print("3. Cancella utente")
    print("4. Recupera valore")
    print("5. Recupera media valori")
    print("0. Esci")

def run():
    with grpc.insecure_channel('localhost:50051') as channel:

        stub_utente = finance_app_pb2_grpc.ServizioUtenteStub(channel)
        stub_stock = finance_app_pb2_grpc.ServizioStockStub(channel)

        while True:
            visualizza_menu()
            scelta = input("Inserisci il numero della funzione: ")
            # Gestisci le scelte
            if scelta == '1':
                registra_utente(stub_utente)
            elif scelta == '2':
                aggiorna_ticker(stub_utente)
            elif scelta == '3':
                cancella_utente(stub_utente)
            elif scelta == '4':
                recupera_valore(stub_stock)
            elif scelta == '5':
                calcola_media_valori(stub_stock)
            elif scelta == '0':
                print("Uscita dal programma.")
                break
            else:
                print("Scelta non valida, riprova.")

if __name__ == '__main__':
    logging.basicConfig()
    run()
