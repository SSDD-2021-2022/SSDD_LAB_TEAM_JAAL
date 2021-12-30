#!/usr/bin/env python3

import sys
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import Authenticator
import random
import threading
import topics


id = 0

class MainI(IceFlix.Main):
    listaObjAuth = []
    listaObjCtg = []

    def __init__(self, discover_subscriber):
        self._discover_subscriber_ = discover_subscriber
        

    def isAdmin(self, adminToken, current = None):
        admin = False

        if adminToken == sys.argv[1]:
            admin = True
        
        return admin

    def register(self, service, current = None):
        try:
            print(service.ice_id())
            if(service.ice_isA("::IceFlix::Authenticator")):
                self.listaObjAuth.append(service)
            elif(service.ice_isA("::IceFlix::MediaCatalog")):
                self.listaObjCtg.append(service)
                print(self.listaObjCtg)
            else:
                raise IceFlix.UnknownService
                
        except IceFlix.UnknownService:
            print("Servicio desconocido")

    def getAuthenticator(self, current=None):
        
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

    def prueba(self):
        print("mis pelotas")


# metodo de check proxy para ver que proxy hay que eliminar. Como este metodo no usa self lo sacamos fuera de la clase
def check_availability(proxies):
    '''Chech ping of all stored proxies'''
    wrong_proxies = []
    for proxyId in proxies:
        try:
            proxies[proxyId].ice_ping()
        except Exception as error:
            print(f'Proxy "{proxyId}" seems offline: {error}')
            wrong_proxies.append(proxyId)

    for proxyId in wrong_proxies:
        del proxies[proxyId]


class ServiceAnnouncements(IceFlix.ServiceAnnouncements):

    def __init__(self):
        """Initialize the Discover object with empty services."""
        self.authenticators = {}
        self.catalogs = {}

        self.poll_timer = threading.Timer(5.0, self.remote_wrong_proxies) #no ponemos los parentesis a la funcion porque sino cogeria lo que retorna como valor


    @property
    def known_services(self):
        """Get serviceIds for all services."""
        return list(self.authenticators.keys()) + list(self.catalogs.keys())


    def newService(self, service, srvId, current=None):  # pylint: disable=unused-argument
        if service.ice_isA('::IceFlix::Authenticator'):
            if not self.authenticators:
                return
            else:
                self.authenticators.items[0]
                return

        elif service.ice_isA('::IceFlix::MediaCatalog'):
            if not self.catalogs:
                return

    def announce(self, service, srvId, current=None):  # pylint: disable=unused-argument
        """Check service type and add it."""
        if srvId in self.known_services:
            return
        if service.ice_isA('::IceFlix::Authenticator'):
            print(f'New Authenticator service: {srvId}')
            self.authenticators[srvId] = IceFlix.AuthenticatorPrx.uncheckedCast(service)
        elif service.ice_isA('::IceFlix::MediaCatalog'):
            print(f'New MediaCatalog service: {srvId}')
            self.catalogs[srvId] = IceFlix.MediaCatalogPrx.uncheckedCast(service)

    def remote_wrong_proxies(self):
        check_availability(self.authenticators)
        check_availability(self.catalogs)

        self.poll_timer = threading.Timer(5.0, self.remote_wrong_proxies) #no ponemos los parentesis a la funcion porque sino cogeria lo que retorna como valor
        self.poll_timer.start()

    def start(self):
        '''Start current timer'''
        self.poll_timer.start() #podemos hacer una comprobacion de que ya esta arrancado o parado

    def stop(self):
        '''Cancel current timer'''
        self.poll_timer.cancel()


class ServerMain(Ice.Application):
    def run(self, args):
        """Initialize the servants and put them to work."""
        adapter = self.communicator().createObjectAdapterWithEndpoints('MainIceFlix', 'tcp')
        adapter.activate()

        discover_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        discover_subscriber = ServiceAnnouncements()
        discover_subscriber_proxy = adapter.addWithUUID(discover_subscriber)
        discover_topic.subscribeAndGetPublisher({}, discover_subscriber_proxy)
        #discover_subscriber.start()

        service_implementation = MainI(discover_subscriber)
        service_proxy = adapter.addWithUUID(service_implementation)
        print(service_proxy, flush=True)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()


        discover_topic.unsubscribe(discover_subscriber_proxy)
        discover_subscriber.stop()

        return 0





if __name__ == '__main__':
    app=ServerMain()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)

