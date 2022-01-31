#!/usr/bin/env python3
#pylint:disable=W0613
#pylint:disable=C0413
#pylint:disable=E0401
#pylint:disable=C0103
#pylint:disable=C0116
#pylint:disable=C0115

"""Main service."""

import sys
import getpass
import time
import hashlib
import Ice
import topics
Ice.loadSlice('iceflix.ice')
import IceFlix
from AuthenticatorChannel import Revocations

EXIT_OK = 0
EXIT_ERROR = 1

class Client(Ice.Application):

    def __init__(self, current=None):
        """Method"""
        self.auth = ""
        self.catalog = ""
        self.conectado = False
        self.check = 3
        self.salir = 0

    def checkPrxMain(self, current=None):
        """Method"""
        if self.check != 0:
            self.check = self.check - 1
            try:
                proxyMain = input("Introduzca el proxy del Main para realizar la conexión\n")
                proxy = self.communicator().stringToProxy(proxyMain)
                if proxy.ice_isA('::IceFlix::Main'):

                    main = IceFlix.MainPrx.checkedCast(proxy)
                    print("proxy correcto")
                    print("Se ha conectado")
                    self.conectado = True
                    return main
            except Ice.Exception as error:
                print("proxy erroneo")
                print(error)
                time.sleep(5)
        else:
            print("Demasiados intentos de conexión")
            self.salir = 1

    def run(self, args):
        """Method"""
        adapter = self.communicator().createObjectAdapterWithEndpoints('ClientService', 'tcp')
        adapter.activate()
        revoc_top = topics.getTopic(topics.getTopicManager(self.communicator()), 'Revocations')
        revocations_topic = revoc_top
        revocations_subscriber = Revocations("client", "")
        revocations_subscriber_proxy = adapter.addWithUUID(revocations_subscriber)
        revocations_topic.subscribeAndGetPublisher({}, revocations_subscriber_proxy)

        while self.salir == 0:
            print("Menú del programa\n1. Conectar\n2. Autenticar")
            print("3. Opciones de administración\n4. Opciones de catálogo sin autenticación\n")
            conectar_opcion = input()

            if conectar_opcion == "1":

                main = self.checkPrxMain()

            elif(self.conectado and conectar_opcion == "2"):
                userToken = ""
                user = input("Introduce usuario:\n")
                password = getpass.getpass("Introduzca contraseña:\n")
                passSha = hashlib.sha256(password.encode()).hexdigest()

                try:
                    self.auth = main.getAuthenticator()
                except IceFlix.TemporaryUnavailable:
                    print("AuthenticatorServices no disponibles")
                    return
                try:
                    userToken = self.auth.refreshAuthorization(user, passSha)
                    self.tokenAsignado = True
                except IceFlix.Unauthorized:
                    print("Usuario " + user + " no autorizado")

                self.auth = main.getAuthenticator()
                revocations_subscriber._service_proxy = self.auth
                print(userToken)
                if userToken != "":
                    revocations_subscriber.password = passSha
                    revocations_subscriber.userRevoked = user
                    revocations_subscriber.dictUsers[user] = passSha
                    revocations_subscriber.newTokenUser = userToken
                mostrarMenuC = True
                while mostrarMenuC:

                    opcion_catalogo = input("Elija si quiere hacer alguna gestión de catálogo o prefiere salir.\n1. Obtener título por id\n2. Obtener título por tags\n3. Añadir tags a un determinado medio\n4. Borrar tags\n5. Volver al menú\n")
                    if opcion_catalogo == "1":
                        idPelicula = input("Introduce id de la película\n")
                        try:
                            media = main.getCatalog()
                        except IceFlix.TemporaryUnavailable:
                            print("MediaCatalogServices no disponibles")
                        try:
                            userToken = revocations_subscriber.newTokenUser
                            print(media.getTile(idPelicula, userToken).info.name)
                        except IceFlix.WrongMediaId:
                            print("Id " + idPelicula + " erróneo")
                        except IceFlix.TemporaryUnavailable:
                            print("Microservicio no disponibles")
                        except IceFlix.Unauthorized:
                            print("Usuario no autorizado")

                    elif opcion_catalogo == "2":
                        tags = input("Introduzca las tags que quiera buscar separandolas por el caracter ','\n")
                        listaTags = tags.split(",")
                        todosTags = False
                        incTags = input("¿Desea mostrar todos los ids con algun tag de los que intriduce por teclado (1) o por el contrario el medio con esos tags específicos(2)\n")
                        if incTags == "2":
                            todosTags = True
                        try:
                            userToken = revocations_subscriber.newTokenUser
                            print(main.getCatalog().getTilesByTags(listaTags, todosTags, userToken))
                        except IceFlix.TemporaryUnavailable:
                            print("MediaCatalogServices no disponibles")
                        except IceFlix.Unauthorized:
                            print("Usuario no autorizado")

                    elif opcion_catalogo == "3":
                        id = input("Introduzca id del medio al que quiera añadir las tags\n")
                        tags = input("Introduzca las tags que quiera añadir separandolas por el caracter ','\n")
                        listaTags = tags.split(",")
                        try:
                            userToken = revocations_subscriber.newTokenUser
                            main.getCatalog().addTags(id, listaTags, userToken)
                        except IceFlix.TemporaryUnavailable:
                            print("MediaCatalogServices no disponibles")
                        except IceFlix.Unauthorized:
                            print("Usuario no autorizado")
                        except IceFlix.WrongMediaId:
                            print("Id " + id + " erróneo")

                    elif opcion_catalogo == "4":
                        id = input("Introduzca id del medio al que quiera borrar las tags\n")
                        tags = input("Introduzca las tags que quiera borrar separandolas por el caracter ','\n")
                        listaTags = tags.split(",")
                        try:
                            userToken = revocations_subscriber.newTokenUser
                            main.getCatalog().removeTags(id, listaTags, userToken)
                        except IceFlix.TemporaryUnavailable:
                            print("MediaCatalogServices no disponibles")
                        except IceFlix.Unauthorized:
                            print("Usuario no autorizado")
                        except IceFlix.WrongMediaId:
                            print("Id " + id + " erróneo")

                    else:
                        mostrarMenuC = False

            elif conectar_opcion == "3":
                tokenAdmin = input("Introduce el token de administracion:\n")
                opcionAdmin = input("Elige qué quieres hacer:\n1. Añadir usuario\n2. Eliminar usuario\n3. Catálogo: Renombrar un título\n")
                if opcionAdmin == "1":
                    user = input("Introduce usuario:\n")
                    password = getpass.getpass("Introduzca contraseña:\n")
                    passSha = hashlib.sha256(password.encode()).hexdigest()
                    try:
                        main.getAuthenticator().addUser(user, passSha, tokenAdmin)
                    except IceFlix.TemporaryUnavailable:
                        print("AuthenticatorServices no disponibles")
                    except IceFlix.Unauthorized:
                        print("Usuario inexistente")
                        sys.exit(1)

                elif opcionAdmin == "2":
                    user = input("Introduce usuario:\n")
                    try:
                        main.getAuthenticator().removeUser(user, tokenAdmin)
                    except IceFlix.TemporaryUnavailable:
                        print("AuthenticatorServices no disponibles")
                    except IceFlix.Unauthorized:
                        print("Usuario inexistente")
                elif opcionAdmin == "3":
                    id = input("Introduzca id del medio\n")
                    name = input("Introduzca el nuevo nombre que le quiera dar al título del medio\n")
                    try:
                        main.getCatalog().renameTile(id, name, tokenAdmin)
                    except IceFlix.TemporaryUnavailable:
                        print("MediaCatalogServices no disponibles")
                    except IceFlix.Unauthorized:
                        print("Usuario no autorizado")
                    except IceFlix.WrongMediaId:
                        print("Id " + id + " erróneo")

            elif conectar_opcion == "4":
                opcion_catalogo = input("¿Qué búsqueda quiere hacer?\n1. Búsqueda por nombre\n")
                if opcion_catalogo == "1":
                    nombrePel = input("Introduce nombre de la película\n")
                    nombrePelicula = nombrePel.lower()
                    todosIDUser = input("Desea sacar los id que contengan esa cadena (1) o sacar sólo los que específicamente tienen esa cadena (2)\n")
                    todosId = False
                    if todosIDUser == "2":
                        todosId = True
                    try:
                        print(str(main.getCatalog().getTilesByName(nombrePelicula, todosId)))
                    except IceFlix.TemporaryUnavailable:
                        print("MediaCatalogServices no disponibles")
            else:
                print("Saliendo...")
                self.salir = 1


if __name__ == '__main__':
    app = Client()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)
