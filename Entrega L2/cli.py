#!/usr/bin/env python3

"""Main service."""

import sys
import random
import threading
import Ice
import getpass
import hashlib
import topics
Ice.loadSlice('iceflix.ice')
import IceFlix

EXIT_OK = 0
EXIT_ERROR = 1



class Client(Ice.Application):

    def run(self, args):

        conectado = False
        auth = ""
        salir = 0



        while(salir == 0):
            print("Menú del programa\n1. Conectar\n2. Autenticar\n3. Opciones de administración\n4. Opciones de catálogo sin autenticación\n")
            conectar_opcion = input()
        
            if conectar_opcion == "1":
                archivoProxy = args[1]
                proxy = self.communicator().stringToProxy(args[1])
                main = IceFlix.MainPrx.checkedCast(proxy)
                print(proxy, flush = False)
                print("Se ha conectado")
                conectado = True

				

            elif(conectado and conectar_opcion == "2"):
                user = input("Introduce usuario:\n")
                password = getpass.getpass("Introduzca contraseña:\n")
                passSha = hashlib.sha256(password.encode()).hexdigest()
                userToken = ""
                
                userToken = main.getAuthenticator().refreshAuthorization(user, passSha)
                print(userToken)
            
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

                        main.getCatalog().addTags(id, listaTags, userToken)
                        
                    elif(opcion_catalogo == "3"):
                        id = input("Introduzca id del medio al que quiera borrar las tags\n")
                        tags = input("Introduzca las tags que quiera borrar separandolas por el caracter ','\n")
                        listaTags = tags.split(",")
                        main.getCatalog().removeTags(id, listaTags, userToken)

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
                    print(media.getTile(idPelicula, userToken).info.name)
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
    
