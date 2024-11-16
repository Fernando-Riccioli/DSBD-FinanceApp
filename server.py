import grpc
import finance_app_pb2
import finance_app_pb2_grpc
import mysql.connector

def connessione_db():
    try:
        connection = mysql.connector.connect(
            host = 'localhost', #database sulla stessa macchina
            user = 'server',
            password = '1234',
            database = 'finance_app'
        )
        return connection
    except mysql.connector.Error:
        print("Errore nella connessione al database.")
        return None

class ServizioUtente(finance_app_pb2_grpc.ServizioUtenteServicer):  #estensione

    def RegistraUtente(self, request, context): #request è il messaggio ricevuto
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "INSERT INTO utenti (email, ticker) VALUES (%s, %s)"    #preveniamo SQL injection
            cursor.execute(query, (request.email, request.ticker))
            connection.commit()
            return finance_app_pb2.Conferma(conferma = True, messaggio = "Registrazione effettuata.")
        except mysql.connector.Error as errore:
            print(f"Errore durante la registrazione: {errore}")
            return finance_app_pb2.Conferma(conferma = False, messaggio = f"Errore durante la registrazione: {errore}")
        finally:
            if connection.is_connected():
                connection.close()  #viene eseguito anche dopo un return preso
        
    def AggiornaTicker(self, request, context):
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "UPDATE utenti SET ticker = %s WHERE email = %s"
            cursor.execute(query, (request.ticker, request.email))
            connection.commit()
            return finance_app_pb2.Conferma(conferma = True, messaggio = "Aggiornamento effettuato.")
        except mysql.connector.Error as errore:
            print(f"Errore durante l'aggiornamento: {errore}")
            return finance_app_pb2.Conferma(conferma = False, messaggio = f"Errore durante l'aggiornamento: {errore}")
        finally:
            if connection.is_connected():
                connection.close()
    
    def CancellaUtente(self, request, context):
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "DELETE FROM utenti WHERE email = %s"
            cursor.execute(query, (request.email,)) #execute vuola la tupla
            connection.commit()
            return finance_app_pb2.Conferma(conferma = True, messaggio = "Utente eliminato.")
        except mysql.connector.Error as errore:
            print(f"Errore durante l'eliminazione: {errore}")
            return finance_app_pb2.Conferma(conferma = False, messaggio = f"Errore durante l'eliminazione: {errore}")
        finally:
            if connection.is_connected():
                connection.close()
    
    #rpc RecuperaValore (Email) returns (Valore) {}
    #rpc CalcolaMediaValori (DatiMediaValori) returns (Valore) {}

class ServizioStock(finance_app_pb2_grpc.ServizioStockServicer):

    def RecuperaValore(self, request, context):
        return finance_app_pb2.Valore(valore = 1)

    def CalcolaMediaValori(self, request, context):
        #logica
        return finance_app_pb2.Valore(valore = 1)