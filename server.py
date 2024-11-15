import grpc
import finance_app_pb2
import finance_app_pb2_grpc
#import mysql.connector

class ServizioUtente(finance_app_pb2_grpc.ServizioUtenteServicer):  #estensione

    def RegistraUtente(self, request, context): #request è il messaggio ricevuto
        #request.email
        #request.ticker
        return finance_app_pb2.Conferma(conferma = True, messaggio = "Registrazione effettuata.")
        
    def AggiornaTicker(self, request, context):
        #logica
        return finance_app_pb2.Conferma(conferma = True, messaggio = "Ticker aggiornato.")
    
    def CancellaUtente(self, request, context):
        #logica
        return finance_app_pb2.Conferma(conferma = True, messaggio = "Utente cancellato.")
    

class ServizioStock(finance_app_pb2_grpc.ServizioStockServicer):

    def RecuperaValore(self, request, context):
        #logica
        return finance_app_pb2.Valore(valore = 1)

    def CalcolaMediaValori(self, request, context):
        #logica
        return finance_app_pb2.Valore(valore = 1)