#!/usr/bin/env python3

import sys
import uuid
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
#import Authenticator
import random
import threading
import topics



id = 0

class MainI(IceFlix.Main):
    listaObjAuth = []
    listaObjCtg = []

    def __init__(self, service_announcements_subscriber):
        self._discover_subscriber_ = service_announcements_subscriber
        self._id_ = str(uuid.uuid4())
        self.authenticators = {}
        self.catalogs = {}
        self.mains = {} 
        
    @property
    def service_id(self):
        """Get instance ID."""
        return self._id_

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

    def __init__(self,current=None):
        """Initialize the Discover object with empty services."""
        self.jose = IceFlix.VolatileServices()
        #aututhenticators = self.jose.AuthenticatorList()
        self._id_ = str(uuid.uuid4())
        self.authenticators = {}
        self.catalogs = {}
        self.mains = {}
        self.poll_timer = threading.Timer(5.0, self.remote_wrong_proxies) #no ponemos los parentesis a la funcion porque sino cogeria lo que retorna como valor
        self.con = 0

    @property
    def known_services(self):
        """Get serviceIds for all services."""
        return list(self.authenticators.keys()) + list(self.catalogs.keys()) + list(self.mains.keys())

    def newService(self, service, srvId, current=None):  # pylint: disable=unused-argument
        if srvId != self._id_:
            print(self._id_)
            print(srvId+" Hay que actualizar la base de datos de "+srvId)
            if srvId in self.known_services:
                return
            print(">>>>>>>>>>>>>>Hello, new service type")
            if service.ice_isA('::IceFlix::Authenticator'):
                print(f'New Authenticator service: {srvId}')
                if not self.authenticators:
                    print("Soy el primer Authenticator")
                    print(self.jose.authenticators)
                    #self.jose.authenticators[0] = "tu madre"
                    #print(str(self.jose.authenticators[0]))
                    print(type(self.jose))


                else:
                    auth = IceFlix.AuthenticatorPrx.checkedCast(service)
                    misco = auth.isAuthorized("miTula")
                    print("----------------"+str(misco)+"------------")
                    
                self.authenticators[srvId] = IceFlix.AuthenticatorPrx.uncheckedCast(service)
            elif service.ice_isA('::IceFlix::MediaCatalog'):
                print(f'New MediaCatalog service: {srvId}')
                self.catalogs[srvId] = IceFlix.MediaCatalogPrx.uncheckedCast(service)
            elif service.ice_isA('::IceFlix::Main'):
                print(f'nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn--New Main service: {srvId}')
                self.mains[srvId] = IceFlix.MainPrx.uncheckedCast(service)
                self.con = self.con + 1
                print("--------------------------------"+str(self.con)+"---------------------------------")
                #mandar solicitud de actualizar base de datos
            print(self.mains.keys())

    def announce(self, service, srvId, current=None):  # pylint: disable=unused-argument
        """Check service type and add it."""
        if srvId in self.known_services:
            print(f'Servicio {srvId} anunciandose')
            print("Servicio ya conocido")
            print(self.known_services)
            return
        if service.ice_isA('::IceFlix::Authenticator'):
            print(f'New Authenticator service: {srvId}')
            self.authenticators[srvId] = IceFlix.AuthenticatorPrx.uncheckedCast(service)
            
        elif service.ice_isA('::IceFlix::MediaCatalog'):
            print(f'New MediaCatalog service: {srvId}')
            self.catalogs[srvId] = IceFlix.MediaCatalogPrx.uncheckedCast(service)

        elif service.ice_isA('::IceFlix::Main'):
             print(f'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa---New Main service: {srvId}')
             self.mains[srvId] = IceFlix.MainPrx.uncheckedCast(service)
             #actualiza base de datos
        print(self.known_services)
        
        

    def lanzarAnnounce(self,publisher,service,srvId,current=None):
        publisher.announce(service,srvId)
        announce = threading.Timer(12.0,self.lanzarAnnounce,(publisher,service,srvId,))
        announce.start()

            

    def remote_wrong_proxies(self):
        check_availability(self.authenticators)
        check_availability(self.catalogs)
        check_availability(self.mains)

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

        def lanzarNuevoAnnounce():
            print("tupac")
            service_announcements_publisher.announce(service_proxy,service_implementation.service_id)
            announce = threading.Timer(12.0,lanzarNuevoAnnounce)
            announce.start()
            print("misco")
            
            
        """Initialize the servants and put them to work."""
        adapter = self.communicator().createObjectAdapterWithEndpoints('Main', 'tcp')
        adapter.activate()
        qos = {}
        service_announcements_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        service_announcements_subscriber = ServiceAnnouncements()
        service_announcements_subscriber_proxy = adapter.addWithUUID(service_announcements_subscriber)
        service_announcements_topic.subscribeAndGetPublisher({}, service_announcements_subscriber_proxy)
        service_announcements_subscriber.start()
        
        print("Waiting events...")

        service_implementation = MainI(service_announcements_subscriber)
        service_proxy = adapter.addWithUUID(service_implementation)
        print(service_proxy, flush=True)

        service_announcements_publisher = IceFlix.ServiceAnnouncementsPrx.uncheckedCast(service_announcements_topic.getPublisher())
        
        service_announcements_publisher.newService(service_proxy,service_implementation.service_id)

        #announce=threading.Timer(3.0,service_announcements_subscriber.lanzarAnnounce,(service_announcements_subscriber,service_proxy,service_implementation.service_id,))
        announce = threading.Timer(3.0,lanzarNuevoAnnounce)
        announce.start()

        #service_announcements_publisher.announce(service_proxy, service_implementation.service_id)
        
        #announce = threading.Timer(12.0,lanzarNuevoAnnounce(service_proxy,service_implementation.service_id))
        #announce.start()

        #announce = threading.Timer(12.0,service_announcements_subscriber.lanzarAnnounce,(service_announcements_subscriber,service_proxy,service_implementation.service_id,))
        #announce.start()

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        

        service_announcements_topic.unsubscribe(service_announcements_subscriber_proxy)
        service_announcements_subscriber.stop()

        return 0





if __name__ == '__main__':
    app=ServerMain()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)

