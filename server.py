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
            host = 'localhost',
            user = 'server',
            password = '1234',
            database = 'finance_app'
        )
        return connection
    except mysql.connector.Error:
        print("Errore nella connessione al database.")
        return None

#Verifica che il formato sia valido
def verifica_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

#Hash per l'at-most-once
def genera_id_richiesta(request, nome):
    hash = hashlib.sha256()
    hash.update(f"{nome}{request.email}{request.ticker}".encode('utf-8'))
    return hash.hexdigest()

#At-most-once
cache = TTLCache(maxsize = 100, ttl = 30)   #time_to_live

class ServizioUtente(finance_app_pb2_grpc.ServizioUtenteServicer):

    def RegistraUtente(request, context):

        if not verifica_email(request.email):
            return finance_app_pb2.Conferma(conferma = False, messaggio = "Email non valida.")
        
        #Implementazione at-most-once
        id_richiesta = genera_id_richiesta(request, "registrazione")
        if id_richiesta in cache:   #salvare anche la risposta?
            return finance_app_pb2.Conferma(conferma = True, messaggio = "Registrazione già effettuata.")
        
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "INSERT INTO utenti (email, ticker) VALUES (%s, %s)"    #preveniamo SQL injection usando %s
            cursor.execute(query, (request.email, request.ticker))
            cache[id_richiesta] = True  # TODO: salvare anche la risposta?
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
        
    def AggiornaTicker(request, context):

        #Implementazione at-most-once
        id_richiesta = genera_id_richiesta(request, "aggiornamento")
        if id_richiesta in cache:
            return finance_app_pb2.Conferma(conferma = True, messaggio = "Aggiornamento già effettuato.")
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "UPDATE utenti SET ticker = %s WHERE email = %s"
            cursor.execute(query, (request.ticker, request.email))
            cache[id_richiesta] = True  # TODO: salvare anche la risposta?
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
            query = "DELETE FROM utenti WHERE email = %s"
            cursor.execute(query, (request.email,)) #execute vuole la tupla
            query = "DELETE FROM data WHERE email = %s"
            cursor.execute(query, (request.email,))
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
        print(f"Recupero l'ultimo valore del ticker associato all'utente {request.email}")
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "SELECT valore FROM data WHERE email = %s ORDER BY timestamp DESC LIMIT 1"
            cursor.execute(query, (request.email,))
            risultato = cursor.fetchone()   #torna una tupla
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
        print(f"Calcolo la media degli ultimi {request.numeroDati} valori del ticker associato all'utente {request.email}")
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = """SELECT AVG(valore) FROM data WHERE email = %s 
                     AND ticker = (SELECT ticker FROM data WHERE email = %s ORDER BY timestamp DESC LIMIT 1) 
                     ORDER BY timestamp DESC LIMIT %s"""    #query interna per selezionare solo entrate con lo stesso ticker
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
    server.add_insecure_port('[::]:' + port)    #qualsiasi indirizzo di rete sulla porta
    server.start()  #asincrono (non blocca l'esecuzione del programma )
    server.wait_for_termination()
    
if __name__ == '__main__':
    serve()