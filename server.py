import hashlib
import grpc
import finance_app_pb2
import finance_app_pb2_grpc
import mysql.connector
import re
from cachetools import TTLCache
from concurrent import futures

def connessione_db():
    try:
        connection = mysql.connector.connect(
            host = 'mysqldb',   #TODO: mysqldb quando siamo su docker, localhost in locale
            user = 'server',
            password = '1234',
            database = 'finance_app'
        )
        return connection
    except mysql.connector.Error:
        print("Errore nella connessione al database.")
        return None

def formato_corretto(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None   #.match() ritorna Match o None

def genera_id(request, nome):
    hash = hashlib.sha256()
    hash.update(f"{nome}{request.email}{request.ticker}".encode('utf-8'))
    return hash.hexdigest()

cache = TTLCache(maxsize = 100, ttl = 30)

class ServizioUtente(finance_app_pb2_grpc.ServizioUtenteServicer):

    def RegistraUtente(request, context):

        if not formato_corretto(request.email):
            return finance_app_pb2.Conferma(conferma = False, messaggio = "Email non valida.")
        
        id = genera_id(request, "registrazione")
        if id in cache:
            return finance_app_pb2.Conferma(conferma = True, messaggio = "Operazione già effettuata.")
        
        #Conversione a NULL se 0.0       
        if not request.high_value:
            high_value = None
        else:
            high_value = request.high_value

        if not request.low_value:
            low_value = None
        else:
            low_value = request.low_value

        # Se entrambe le soglie sono impostate e la soglia massima è minore allora errore
        if high_value and low_value and high_value <= low_value:
            return finance_app_pb2.Conferma(conferma = False, messaggio = "Errore: La soglia massima deve essere maggiore della soglia minima.")

        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "INSERT INTO utenti (email, ticker, high_value, low_value) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (request.email, request.ticker, high_value, low_value))
            cache[id] = True
            connection.commit()
            return finance_app_pb2.Conferma(conferma = True, messaggio = "Registrazione effettuata.")
        except mysql.connector.Error as errore:
            print(f"Errore durante la registrazione: {errore}")
            return finance_app_pb2.Conferma(conferma = False, messaggio = f"Errore durante la registrazione: {errore}")
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

    def AggiornaUtente(request, context):

        id = genera_id(request, "aggiornamento")
        if id in cache:
            return finance_app_pb2.Conferma(conferma = True, messaggio = "Operazione già effettuata.")
        
        #Conversione a NULL se 0.0       
        if not request.high_value:
            high_value = None
        else:
            high_value = request.high_value

        if not request.low_value:
            low_value = None
        else:
            low_value = request.low_value

        # Se entrambe le soglie sono impostate e la soglia massima è minore allora errore
        if high_value and low_value and high_value <= low_value:
            return finance_app_pb2.Conferma(conferma = False, messaggio = "Errore: La soglia massima deve essere maggiore della soglia minima.")

        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "UPDATE utenti SET ticker = %s, high_value = %s, low_value = %s WHERE email = %s"
            cursor.execute(query, (request.ticker, high_value, low_value, request.email))
            cache[id] = True
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
    
    def CancellaUtente(request, context):
        try:
            connection = connessione_db()
            cursor = connection.cursor()

            query = "DELETE FROM data WHERE email = %s"
            cursor.execute(query, (request.email,))       
            query = "DELETE FROM utenti WHERE email = %s"
            cursor.execute(query, (request.email,)) #execute vuole la tupla
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

    def RecuperaValore(request, context):
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "SELECT valore FROM data WHERE email = %s ORDER BY timestamp DESC LIMIT 1"
            cursor.execute(query, (request.email,))
            risultato = cursor.fetchone()
            print(f"Valore ottenuto: {risultato[0]}")
            return finance_app_pb2.Valore(valore = risultato[0])
        except mysql.connector.Error as errore:
            print(f"Errore durante la richiesta: {errore}")
            return finance_app_pb2.Valore(valore = 0.0)
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

    def CalcolaMediaValori(request, context):
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = """SELECT AVG(valore) FROM data WHERE email = %s AND ticker = 
                     (SELECT ticker FROM data WHERE email = %s ORDER BY timestamp DESC LIMIT 1) 
                     ORDER BY timestamp DESC LIMIT %s"""    #La seconda riga della query è usata per selezionare solo le entrate dell'utente con l'ultimo ticker 
            #TODO: Se elimino le entrate in data quando aggiorno il ticker, non ho bisogno della query interna
            cursor.execute(query, (request.email, request.email, request.numeroDati))
            risultato = cursor.fetchone()
            print(f"Valore ottenuto: {round(risultato[0], 2)}")
            return finance_app_pb2.Valore(valore = risultato[0])
        except mysql.connector.Error as errore:
            print(f"Errore durante la richiesta: {errore}")
            return finance_app_pb2.Valore(valore = 0.0)
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    finance_app_pb2_grpc.add_ServizioUtenteServicer_to_server(ServizioUtente, server)
    finance_app_pb2_grpc.add_ServizioStockServicer_to_server(ServizioStock, server)
    print("Servizio Utente avviato.")
    print("Servizio Stock avviato.")
    print(f"Server in ascolto sulla porta {port}...")
    server.add_insecure_port('[::]:' + port)
    server.start()
    server.wait_for_termination()
    
if __name__ == '__main__':
    serve()