import time
import mysql.connector
import yfinance as yf

from circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
                
circuit_breaker = CircuitBreaker()  #argomenti personalizzati

def connessione_db():
    try:
        connection = mysql.connector.connect(
            host = 'localhost', #TODO: mysqldb quando spostiamo su docker, localhost in locale
            user = 'server',
            password = '1234',
            database = 'finance_app'
        )
        return connection
    except mysql.connector.Error:
        print("Errore nella connessione al database.")
        return None
    
def recupera_righe_utenti():   #database utenti: | email | ticker |
    try:
        connection = connessione_db()
        cursor = connection.cursor()
        query = "SELECT email, ticker FROM utenti;"
        cursor.execute(query)
        righe = cursor.fetchall()
        return righe
    except mysql.connector.Error as errore:
        print(f"Errore durante il recupero dal database: {errore}")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
                
def recupera_ultimo_valore(ticker):
    try:
        azione = yf.Ticker(ticker)
        dati_giornalieri = azione.history(period="1d", interval="1m") # dataframe con ingressi distanziati di 1m
        if not dati_giornalieri.empty:
            ultimo_valore = dati_giornalieri['Close'].iloc[-1] # valore di chiusura
            return ultimo_valore
        else:
            print(f"Nessun dato trovato per {ticker}")
            return None
    except Exception as e:
        print(f"Errore durante il recupero del ticker {ticker}: {e}")
    
def salva_stock_data(email, ticker, valore):
    try:
        connection = connessione_db()
        cursor = connection.cursor()
        query = """
                INSERT INTO data (email, ticker, valore, timestamp)
                VALUES (%s, %s, %s, NOW());
                """
        cursor.execute(query, (email, ticker, valore))
        connection.commit()
        print("Dati salvati correttamente.")
    except mysql.connector.Error as errore:
        print(f"Errore durante il salvataggio dei dati: {errore}")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
                connection.close()
                
def avvia_data_collector():
    while True:
        try:
            righe = recupera_righe_utenti()
            for email, ticker in righe:
                print(f"Recupero dati per {ticker} associato a {email}")
                try:
                    ultimo_valore = circuit_breaker.call(recupera_ultimo_valore, ticker)  # Chiamata protetta dal CB
                    salva_stock_data(email, ticker, ultimo_valore)
                except CircuitBreakerOpenException:
                    print("Errore: il circuito è aperto.")
                except Exception as e:
                    print(f"Errore per {ticker} (utente: {email}): {e}")
        except:
            print("Errore durante il recupero degli utenti nel database.")

        print("Attendo un minuto prima del prossimo ciclo...")
        time.sleep(60)

#TODO: Data Collector diventa un producer ch pubblica sul topic 'to-alert-system'
        
if __name__ == "__main__":  #per avviare "data_collector.py"
    avvia_data_collector()