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
            print("Menú del programa\n1. Conectar\n2. Autenticar\n3. Opciones de administración\n4. Opciones de catálogo sin autenticación\n")
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
                userToken = ""
                
                userToken = main.getAuthenticator().refreshAuthorization(user, passSha)
                
                if userToken == "":
                    print("Usuario no existente o  contraseña errónea")
                    
                else:
                    mostrarMenuC = True
                    while(mostrarMenuC):
                        opcion_catalogo = input("Elija si quiere hacer alguna gestión de catálogo o prefiere salir.\n1. Obtener título por tags\n2. Añadir tags a un determinado medio\n3. Borrar tags\n4. Volver al menú\n")
                        if(opcion_catalogo == "1"):
                            tags = input("Introduzca las tags que quiera buscar separandolas por el caracter ','\n")
                            listaTags = tags.split(",")
                            todosTags = False
                            incTags=input("¿Desea mostrar todos los ids con algun tag de los que intriduce por teclado (1) o por el contrario el medio con esos tags específicos(2)\n")
                            if(incTags == "2"):
                                todosTags = True
                            print(main.getCatalog().getTilesByTags(listaTags, todosTags, userToken))

                        elif(opcion_catalogo == "2"):
                            id = input("Introduzca id del medio al que quiera añadir las tags\n")
                            tags = input("Introduzca las tags que quiera añadir separandolas por el caracter ','\n")
                            listaTags = tags.split(",")

                            print(main.getCatalog().addTags(id, listaTags, userToken))
                            print("tags "+str(listaTags)+" añadidas al medio "+str(id))
                            #else:
                                #print("No se han podido añadir los tags de forma correcta")
                        
                        elif(opcion_catalogo == "3"):
                            id = input("Introduzca id del medio al que quiera borrar las tags\n")
                            tags = input("Introduzca las tags que quiera borrar separandolas por el caracter ','\n")
                            listaTags = tags.split(",")

                            print(main.getCatalog().removeTags(id, listaTags, userToken))
                            print("tags "+str(listaTags)+" borradas del medio "+str(id))
                        else:
                            mostrarMenuC = False
                

            elif(conectar_opcion == "3"):
                tokenAdmin = input("Introduce el token de administracion:\n")
                opcionAdmin = input("Elige qué quieres hacer:\n1. Añadir usuario\n2. Eliminar usuario\n3. Catálogo: Renombrar un título\n")
                if(opcionAdmin == "1"):
                    user = input("Introduce usuario:\n")
                    password = getpass.getpass("Introduzca contraseña:\n")
                    passSha = hashlib.sha256(password.encode()).hexdigest()
                    try:
                        main.getAuthenticator().addUser(user, passSha, tokenAdmin)
                    except IceFlix.Unauthorized:
                        print("Usuario inexistente")
                        sys.exit(1)

                elif(opcionAdmin == "2"):
                    user = input("Introduce usuario:\n")
                    main.getAuthenticator().removeUser(user, tokenAdmin)
                elif(opcionAdmin == "3"):
                    id = input("Introduzca id del medio\n")
                    name = input("Introduzca el nuevo nombre que le quiera dar al título del medio\n")
                    main.getCatalog().renameTile(id,name,tokenAdmin)
            elif(conectar_opcion == "4"):
                opcion_catalogo = input("¿Qué búsqueda quiere hacer?\n1. Búsqueda por id\n2. Búsqueda por nombre\n")
                if(opcion_catalogo == "1"):
                    idPelicula = input("Introduce id de la película\n")
                    media = main.getCatalog()
                    print(media.getTile(idPelicula).info.name)
                if(opcion_catalogo == "2"):
                    nombrePelicula = input("Introduce nombre de la película\n")
                    todosIDUser = input("Desea sacar los id que contengan esa cadena (1) o sacar sólo los que específicamente tienen esa cadena (2)\n")
                    todosId = False
                    if todosIDUser == "2":
                        todosId = True
                    print(str(main.getCatalog().getTilesByName(nombrePelicula, todosId)))
            else:
                print("Saliendo...")
                salir = 1
            

if __name__ == '__main__':
    app=Client()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)

    
