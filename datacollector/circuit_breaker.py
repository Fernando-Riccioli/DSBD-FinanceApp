import time
import threading

class CircuitBreaker:
    """
    Implementazione di un Circuit Breaker personalizzato.
    """
    def __init__(self, fail_max, reset_timeout):
        self.fail_max = fail_max  # Numero massimo di errori consecutivi permessi
        self.reset_timeout = reset_timeout  # Tempo di ripristino (in secondi)
        self.failure_count = 0  # Conteggio degli errori
        self.state = "CLOSED"  # Stati: "CLOSED", "OPEN", "HALF-OPEN"
        self.lock = threading.Lock()  # Per gestire il multithreading
        self.last_failure_time = 0  # Timestamp dell'ultimo errore

    def call(self, func, *args, **kwargs):
        """
        Esegue una funzione protetta dal Circuit Breaker.
        """
        with self.lock:
            if self.state == "OPEN":
                # Verifica se il timeout è trascorso
                if time.time() - self.last_failure_time >= self.reset_timeout:
                    self.state = "HALF-OPEN"
                else:
                    raise Exception("CircuitBreaker: Stato OPEN, chiamata bloccata.")

        # Esegui la funzione e aggiorna lo stato
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            self.record_failure()
            raise Exception(f"CircuitBreaker: Errore durante l'esecuzione - {e}")
        else:
            self.record_success()
            return result

    def record_failure(self):
        """
        Registra un errore e aggiorna lo stato del Circuit Breaker.
        """
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.fail_max:
                self.state = "OPEN"
                print("CircuitBreaker: Stato cambiato a OPEN.")

    def record_success(self):
        """
        Registra un successo e ripristina lo stato del Circuit Breaker.
        """
        with self.lock:
            self.failure_count = 0
            if self.state == "HALF-OPEN":
                self.state = "CLOSED"
                print("CircuitBreaker: Stato cambiato a CLOSED.")

    def get_state(self):
        """
        Restituisce lo stato attuale del Circuit Breaker.
        """
        with self.lock:
            return self.state
