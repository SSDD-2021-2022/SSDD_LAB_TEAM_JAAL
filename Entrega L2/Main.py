#!/usr/bin/env python3

from multiprocessing.connection import wait
from sqlite3 import adapt
import sys
from time import process_time_ns, sleep
import uuid
import signal
import os
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
#import Authenticator
import random
import threading
import topics
from ServiceAnnounce import ServiceAnnouncements

class MainI(IceFlix.Main):

    def __init__(self, service_announcements_subscriber, prx_service, srv_announce_pub):
        self._id_ = str(uuid.uuid4())
        # self._comunicator = comunicator
        self._token_admin = sys.argv[1]
        self._service_announcements_subscriber = service_announcements_subscriber
        self._prx_service = prx_service
        self._srv_announce_pub = srv_announce_pub
        self._updated = False
        self.announcements = None
        # self.token = sys.argv[1]
        
        authenticatorList = []
        mediaCatalogsList = []
        
        self.VolatileServices = IceFlix.VolatileServices()
        self.VolatileServices.authenticators = authenticatorList
        self.VolatileServices.mediaCatalogs = mediaCatalogsList
        
        
        # self.authenticators = {}
        # self.catalogs = {}
        # self.mains = {} 
        
    @property
    def service_id(self):
        """Get instance ID."""
        return self._id_

    def isAdmin(self, adminToken, current = None):
        admin = False

        if adminToken == sys.argv[1]:
            admin = True
        
        return admin

    def register(self, service, srvId):
        # try:
        if(service.ice_isA("::IceFlix::Authenticator")):
            self.VolatileServices.authenticators.append(IceFlix.AuthenticatorPrx.uncheckedCast(service))
        elif(service.ice_isA("::IceFlix::MediaCatalog")):
            self.VolatileServices.mediaCatalogs.apeend(IceFlix.MediaCatalogPrx.uncheckedCast(service))
            print(self.VolatileServices.mediaCatalogs)
        else:
            raise IceFlix.UnknownService
                
        # except IceFlix.UnknownService:
        #     print("Servicio desconocido")

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
    
    def initService(self):
        print("Inicio de servicios")
        self._srv_announce_pub.newService(self._prx_service,self.service_id)

        self.announcements = threading.Timer(3.0, self.serviceAnnouncing)
        self.announcements.start()

    def serviceAnnouncing(self):
        self._srv_announce_pub.announce(self._prx_service,self.service_id)
        time = 10 + random.uniform(-2,2)
        self.announcements = threading.Timer(time,self.serviceAnnouncing)
        self.announcements.start()
    
    def getDB(self):
        return self.VolatileServices
    
    def getToken(self):
        return self.token
    
    def sendDB(self, srv_proxy):
        is_valid_token = srv_proxy.isAdmin(self._token_admin)
        if not is_valid_token:
            currentDB = self.getDB()
            srvId = str(False)
            srv_proxy.updateDB(currentDB, srvId)
        else:
            currentDB = self.getDB()
            srvId = self.service_id
            print("Enviando BD...")
            srv_proxy.updateDB(currentDB, srvId)
        
    def updateDB(self, currentDB, srvId, current = None):
        if srvId == "False":
            print("Token de administración erróneo")
            os.kill(os.getpid(), signal.SIGINT)
            # matar al proceso, no se puede con sys.exit
        if self._updated == True:
            return
        self.VolatileServices = currentDB
        print
        ("Base de datos actualizada desde: " + str(srvId))
        self._updated = True
        
    def check_volatile_services(self, volatile_services):
        wrong_proxies = []
        for vlt_srv in volatile_services:
            try:
                vlt_srv.ice_ping()
            except Exception as error:
                print(f'Proxy "{vlt_srv}" seems offline: {error}')
                wrong_proxies.append(vlt_srv)
    
        for srv_prx in wrong_proxies:
            volatile_services.remove(srv_prx)
    
        print("VOLATILE SERVICES AUTH " + str(volatile_services))

class ServerMain(Ice.Application):
    
    def run(self, args):
        adapter = self.communicator().createObjectAdapterWithEndpoints('MainService', 'tcp')
        adapter.activate()
        
        service_announce_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        service_announce_subscriber = ServiceAnnouncements("","","")
        service_announce_subscriber_proxy = adapter.addWithUUID(service_announce_subscriber)
        service_announce_publisher = IceFlix.ServiceAnnouncementsPrx.uncheckedCast(service_announce_topic.getPublisher())
        
        service_implementation = MainI(service_announce_subscriber, "", service_announce_publisher)
        service_proxy = adapter.addWithUUID(service_implementation)
        print(service_proxy, flush=True)
        print(service_implementation.service_id)
        
        service_announce_subscriber._service_type = service_proxy.ice_id()
        service_announce_subscriber._service_instance = service_implementation
        service_announce_subscriber._service_proxy = service_proxy
        service_implementation._prx_service = service_proxy
        
        service_announce_topic.subscribeAndGetPublisher({}, service_announce_subscriber_proxy)
                
        service_implementation.initService()
        #service_announce_publisher.newService(service_proxy, service_implementation.service_id)
        #service_announce_publisher.announce(service_proxy, service_implementation.service_id)
    
        
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        
        service_implementation.announcements.cancel()
        service_announce_subscriber.poll_timer.cancel()
        
        service_announce_topic.unsubscribe(service_announce_subscriber_proxy)
        
        return 0
        
        
        
        
        
        # def lanzarNuevoAnnounce():
        #     service_announcements_publisher.announce(service_proxy,service_implementation.service_id)
        #     announce = threading.Timer(12.0,lanzarNuevoAnnounce)
        #     announce.start()
            
            
        # """Initialize the servants and put them to work."""
        # adapter = self.communicator().createObjectAdapterWithEndpoints('Main', 'tcp')
        # adapter.activate()
        # qos = {}
        # service_announcements_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        # service_announcements_subscriber = ServiceAnnouncements()
        # service_announcements_subscriber_proxy = adapter.addWithUUID(service_announcements_subscriber)
        # service_announcements_topic.subscribeAndGetPublisher({}, service_announcements_subscriber_proxy)
        # service_announcements_subscriber.start()
        
        # print("Waiting events...")

        # service_implementation = MainI(service_announcements_subscriber)
        # service_proxy = adapter.addWithUUID(service_implementation)
        # print(service_proxy, flush=True)

        # service_announcements_publisher = IceFlix.ServiceAnnouncementsPrx.uncheckedCast(service_announcements_topic.getPublisher())
        
        # service_announcements_publisher.newService(service_proxy,service_implementation.service_id)

        # #announce=threading.Timer(3.0,service_announcements_subscriber.lanzarAnnounce,(service_announcements_subscriber,service_proxy,service_implementation.service_id,))
        # announce = threading.Timer(3.0,lanzarNuevoAnnounce)
        # announce.start()

        # #service_announcements_publisher.announce(service_proxy, service_implementation.service_id)
        
        # #announce = threading.Timer(12.0,lanzarNuevoAnnounce(service_proxy,service_implementation.service_id))
        # #announce.start()

        # #announce = threading.Timer(12.0,service_announcements_subscriber.lanzarAnnounce,(service_announcements_subscriber,service_proxy,service_implementation.service_id,))
        # #announce.start()

        # self.shutdownOnInterrupt()
        # self.communicator().waitForShutdown()
        

        # service_announcements_topic.unsubscribe(service_announcements_subscriber_proxy)
        # service_announcements_subscriber.stop()

        # return 0



if __name__ == '__main__':
    app=ServerMain()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)

