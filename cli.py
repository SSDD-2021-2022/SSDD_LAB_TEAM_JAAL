"""Submodule containing the CLI command handlers."""

import sys
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import Authenticator
import getpass
import hashlib


def main_service():
    """Handles the `mainservice` CLI command."""
    print("Main service")
    sys.exit(0)


def catalog_service():
    """Handles the `catalogservice` CLI command."""
    print("Catalog service")
    sys.exit(0)


def streaming_service():
    """Handles the `streamingservice` CLI command."""
    print("Streaming service")
    sys.exit(0)


def authentication_service():
    """Handles the `authenticationservice` CLI command."""
    print("Authentication service")
    sys.exit(0)

class Client(Ice.Application):
    def run(self, args):

        conectado = False
        auth = ""
        salir = 0

        while(salir == 0):
            print("Menú del programa\n1. Conectar\n2. Autenticar\n3. Opciones de administración")
            conectar_opcion = input()
        
            if conectar_opcion == "1":
                archivoProxy=open("salida").read()
                proxy = self.communicator().stringToProxy(archivoProxy)
                main = IceFlix.MainPrx.checkedCast(proxy)
                print(proxy, flush=False)
                print("Se ha conectado")
                conectado = True

            elif(conectado and conectar_opcion == "2"):
                user = input("Introduce usuario:\n")
                password = getpass.getpass("Introduzca contraseña:\n")
                passSha = hashlib.sha256(password.encode()).hexdigest()
                
                print(main.getAuthenticator().refreshAuthorization(user, passSha))

            elif(conectar_opcion == "3"):
                tokenAdmin = input("Introduce el token de administracion:\n")
                opcionAdmin = input("Elige qué quieres hacer:\n1. Añadir usuario\n2. Eliminar usuario\n")
                if(opcionAdmin == "1"):
                    user = input("Introduce usuario:\n")
                    password = getpass.getpass("Introduzca contraseña:\n")
                    passSha = hashlib.sha256(password.encode()).hexdigest()
                    main.getAuthenticator().addUser(user, passSha, tokenAdmin)
                if(opcionAdmin == "2"):
                    user = input("Introduce usuario:\n")
                    main.getAuthenticator().removeUser(user, tokenAdmin)
                
                    

            else:
                print("Saliendo...")
                salir = 1
            

if _name_ == '_main_':
    app=Client()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)