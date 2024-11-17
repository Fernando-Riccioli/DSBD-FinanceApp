import grpc
from concurrent import futures
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

    def registra_utente(self, request, context): #request è il messaggio ricevuto
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
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()  #viene eseguito anche dopo un return preso
        
    def aggiorna_ticker(self, request, context):
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
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
    
    def cancella_utente(self, request, context):
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
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

class ServizioStock(finance_app_pb2_grpc.ServizioStockServicer):

    def recupera_valore(self, request, context):
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "SELECT valore FROM data WHERE email = %s ORDER BY timestamp DESC LIMIT 1"
            cursor.execute(query, (request.email,))
            risultato = cursor.fetchone()
            return finance_app_pb2.Valore(valore = risultato)
        except mysql.connector.Error as errore:
            print(f"Errore durante la richiesta: {errore}")
            return finance_app_pb2.Valore(valore = risultato)
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
        

    def calcola_media_valori(self, request, context):
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = """SELECT AVG(valore) FROM data WHERE email = %s 
                     AND ticker = (SELECT ticker FROM data WHERE email = %s ORDER BY timestamp DESC LIMIT 1) 
                     ORDER BY timestamp DESC LIMIT %s"""    #query interna per selezionare solo entrate con lo stesso ticker
            cursor.execute(query, (request.email, request.email, request.numeroDati))
            risultato = cursor.fetchone()
            return finance_app_pb2.Valore(valore = risultato[0])
        except mysql.connector.Error as errore:
            print(f"Errore durante la richiesta: {errore}")
            return finance_app_pb2.Valore(valore = risultato)
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    finance_app_pb2_grpc.add_ServizioUtenteServicer_to_server(ServizioUtente, server)   #servizio richiesto dall'interfaccia
    finance_app_pb2_grpc.add_ServizioStockServicer_to_server(ServizioStock, server)
    print("Servizio Utente e Servizio Stock iniziati.")
    server.add_insecure_port('[::]:' + port)    #qualsiasi indirizzo di rete sulla porta
    server.start()  #asincrono (non blocca l'esecuzione del programma )
    server.wait_for_termination()   #necessario per condizione sopra
    
if __name__ == '__main__':
    serve()