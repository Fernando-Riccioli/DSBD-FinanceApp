import grpc
from command_service import ServizioComandoUtente
import finance_app_pb2_grpc
from concurrent import futures
from query_service import ServizioQueryStock

class ServizioUtente(finance_app_pb2_grpc.ServizioUtenteServicer):

    def __init__(self):
        self.command_service = ServizioComandoUtente()

    def RegistraUtente(self, request, context):
        return self.command_service.RegistraUtente(request)

    def AggiornaUtente(self, request, context):
        return self.command_service.AggiornaUtente(request)
    
    def CancellaUtente(self, request, context):
        return self.command_service.CancellaUtente(request)   

class ServizioStock(finance_app_pb2_grpc.ServizioStockServicer):

    def __init__(self):
        self.query_service = ServizioQueryStock()

    def RecuperaValore(self, request, context):
        return self.query_service.RecuperaValore(request.email)

    def CalcolaMediaValori(self, request, context):
        return self.query_service.CalcolaMediaValori(request.email)


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