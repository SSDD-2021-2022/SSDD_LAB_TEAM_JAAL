#!/usr/bin/env python3

import sys
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

listaObjAuth = []
listaObjCatg = []

class MainI(IceFlix.Main):
    def isAdmin(self, adminToken, current = None):
        admin = False

        if adminToken == sys.argv[1]:
            admin = True
        
        return admin

    def register(self, service, current = None):
        try:
            #Se comprueba el tipo de objeto remoto que llega
            print(service.ice_id())
            if(service.ice_isA("::IceFlix::Authenticator")):
                listaObjAuth.append(service)
            if(service.ice_isA("::IceFlix::MediaCatalog")):
                listaObjCatg.append(service)
            print(listaObjAuth)
        except IceFlix.UnknownService:
            print("Servicio desconocido")

    def getAuthenticator(self, current=None):
        try:
            if(len(listaObjAuth) !=0 and listaObjAuth[0].ice_ping()):
                print("holaaaaaaaaaaa")
                return listaObjAuth[0]
            else:
                raise IceFlix.TemporaryUnavailable
        except IceFlix.TemporaryUnavailable:
            print("No hay ningun servicio de autenticacion abierto")
    
    def getCatalog(self, current=None):
        try:
            if(len(listaObjCatg) !=0 and listaObjCatg[0].ice_ping()):
                return listaObjCatg[0]
            else:
                raise IceFlix.TemporaryUnavailable
        except IceFlix.TemporaryUnavailable:
            print("No hay ningun servicio de catalogo abierto")

class ServerMain(Ice.Application):
    def run(self, args):
        broker = self.communicator()
        servant = MainI()
        servant.getAuthenticator()
        adapter = broker.createObjectAdapter("MainAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("main1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

if __name__ == '__main__':
    app=ServerMain()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)

#sys.exit(ServerMain().main(sys.argv))
