#!/usr/bin/env python3

import sys
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import Authenticator
import random

dictObjAuth = {0:{"id":"", "proxy":""}}
dictObjCatg = {0:{"id":"", "proxy":""}}

id = 0


class MainI(IceFlix.Main):
    listaObjAuth = []
    listaObjCtg = []


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
                self.listaObjAuth.append(service)
            if(service.ice_isA("::IceFlix::MediaCatalog")):
                self.listaObjCtg.append(service)
            print(dictObjAuth)
        except IceFlix.UnknownService:
            print("Servicio desconocido")

    def getAuthenticator(self, current=None):
        
            
        #print(listaObjAuth[0].ice_ping())

        if(not self.listaObjAuth):
            raise IceFlix.TemporaryUnavailable
            
        proxyAuth = random.choice(self.listaObjAuth)
        print(proxyAuth)
        try:
            proxyAuth.ice_ping()

        except Ice.ConnectionRefusedException:
            print("proxy inexistente")
            self.listaObjAuth.remove(proxyAuth) 
            raise IceFlix.TemporaryUnavailable
            
            

        return IceFlix.AuthenticatorPrx.uncheckedCast(proxyAuth)
        
            
        
    
    def getCatalog(self, current=None):

        if(not self.listaObjCtg):
            raise IceFlix.TemporaryUnavailable
            
        proxyCtg = random.choice(self.listaObjCtg)
        print(proxyCtg)
        try:
            proxyCtg.ice_ping()

        except Ice.ConnectionRefusedException:
            print("proxy inexistente")
            self.listaObjCtg.remove(proxyCtg) 
            raise IceFlix.TemporaryUnavailable
            
        return IceFlix.MediaCatalogPrx.uncheckedCast(proxyCtg)
class ServerMain(Ice.Application):
    def run(self, args):
        broker = self.communicator()
        servant = MainI()
        #servant.getAuthenticator()
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
