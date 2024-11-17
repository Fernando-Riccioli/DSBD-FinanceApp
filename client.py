import logging
import grpc
import finance_app_pb2
import finance_app_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = finance_app_pb2_grpc.ServizioUtenteStub(channel)
        risposta = stub.RegistraUtente(finance_app_pb2.DatiUtente(email = "prova@gmail.com", ticker = "AAPL")) #secondo la struttura di .proto
        print("Conferma registrazione: " + risposta.conferma + ". " + risposta.messaggio)
        risposta = stub.AggiornaTicker(finance_app_pb2.DatiUtente(email = "prova@gmail.com", ticker = "GOOGL"))
        print("Conferma aggiornamento: " + risposta.conferma + ". " + risposta.messaggio)
        risposta = stub.CancellaUtente(finance_app_pb2.Email(email = "prova@gmail.com"))
        print("Conferma eliminazione: " + risposta.conferma + ". " + risposta.messaggio)

        stub = finance_app_pb2_grpc.ServizioStockStub(channel)
        risposta = stub.RecuperaValore(finance_app_pb2.Email(email = "pippo@gmail.com"))
        print("Valore ottenuto: " + risposta.valore + ".")
        risposta = stub.CalcolaMediaValori(finance_app_pb2.DatiMediaValori(email = "pippo@gmail.com", numeroDati = 10))
        print("Media valori ottenuta: " + risposta.valore + ".")

if __name__ == '__main__':
    logging.basicConfig()
    run()
