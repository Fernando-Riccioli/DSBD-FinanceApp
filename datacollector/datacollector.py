import time
import mysql.connector
import yfinance as yf
import finance_app_pb2

from circuit_breaker import CircuitBreaker
                
breaker = CircuitBreaker(fail_max=3, reset_timeout=10)

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
    
def RecuperaUtenti():
    try:
        connection = connessione_db()
        cursor = connection.cursor()
        query = "SELECT email, ticker FROM utenti;"
        cursor.execute(query)
        utenti = cursor.fetchall()
        cursor.close()
        return utenti
    except mysql.connector.Error as errore:
        print(f"Errore durante il recupero utenti dal database: {errore}")
        return None
    finally:
        if connection.is_connected():
                connection.close()
                
def RecuperaStockData(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")  # Recupera i dati finanziari di oggi
        if not data.empty:
            last_close = data['Close'].iloc[-1]
            return last_close
        else:
            return None
    except Exception as e:
        print(f"Errore durante il recupero del ticker {ticker}: {e}")
        return None
    
def SalvaStockData(email, ticker, value):
    try:
        connection = connessione_db()
        cursor = connection.cursor()
        query = """
        INSERT INTO data (email, ticker, value, timestamp)
        VALUES (%s, %s, %s, NOW());
        """
        cursor.execute(query, (email, ticker, value))
        connection.commit()
        return finance_app_pb2.Conferma(conferma = True, messaggio = "Dati salvati correttamente.")
    except mysql.connector.Error as errore:
        print(f"Errore durante il salvataggio dei dati: {errore}")
        return finance_app_pb2.Conferma(conferma = False, messaggio = f"Errore durante il salvataggio dei dat: {errore}")
    finally:
        if connection.is_connected():
                connection.close()
                
def AvviaDataCollector():
    while True:
        try:
            print("Recupero utenti...")
            utenti = RecuperaUtenti()
            for email, ticker in utenti:
                print("Recupero dati per {ticker} associato a {email}")
                try:
                    valore = breaker.call(RecuperaStockData, ticker)  # Chiamata protetta dal Circuit Breaker
                    SalvaStockData(email, ticker, valore)
                except Exception as e:
                    print(f"Errore per {ticker} (utente: {email}): {e}")

            print("Attendo 10 minuti prima del prossimo ciclo...")
            time.sleep(600)  # Attendi 10 minuti
        except:
            print("Errore durante il recupero utenti")        
        
if __name__ == "__main__":
    AvviaDataCollector()