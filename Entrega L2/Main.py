#!/usr/bin/env python3
# pylint:disable=W0613
# pylint:disable=C0413
#pylint:disable=W0212
# pylint:disable=E0401
# pylint:disable=C0103
#excepcion
#pylint:disable=E1101

import sys
import uuid
import threading
import random
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import topics
from ServiceAnnounce import ServiceAnnouncements

class MainI(IceFlix.Main):
    """Class Main"""
    def __init__(self, service_announcements_subscriber, prx_service, srv_announce_pub):
        """Method"""
        self._id_ = str(uuid.uuid4())
        self._token_admin = sys.argv[1]
        self._service_announcements_subscriber = service_announcements_subscriber
        self._prx_service = prx_service
        self._srv_announce_pub = srv_announce_pub
        self._updated = False
        self.announcements = None

        authenticatorList = []
        mediaCatalogsList = []

        self.VolatileServices = IceFlix.VolatileServices()
        self.VolatileServices.authenticators = authenticatorList
        self.VolatileServices.mediaCatalogs = mediaCatalogsList

    @property
    def service_id(self):
        """Get instance ID."""
        return self._id_

    def isAdmin(self, adminToken, current=None):
        """Method"""
        admin = False

        if adminToken == sys.argv[1]:
            admin = True

        return admin

    def register(self, service, srvId):
        """Method"""
        if service.ice_isA("::IceFlix::Authenticator"):
            self.VolatileServices.authenticators.append(IceFlix.AuthenticatorPrx.uncheckedCast(service))
        elif service.ice_isA("::IceFlix::MediaCatalog"):
            self.VolatileServices.mediaCatalogs.append(IceFlix.MediaCatalogPrx.uncheckedCast(service))
        else:
            raise IceFlix.UnknownService

    def getAuthenticator(self, current=None):
        """Method"""
        if not self.VolatileServices.authenticators:
            raise IceFlix.TemporaryUnavailable

        proxyAuth = random.choice(self.VolatileServices.authenticators)
        print(proxyAuth)
        try:
            proxyAuth.ice_ping()

        except Ice.ConnectionRefusedException:
            print("proxy inexistente")
            self.VolatileServices.authenticators.remove(proxyAuth)
            raise IceFlix.TemporaryUnavailable

        return IceFlix.AuthenticatorPrx.uncheckedCast(proxyAuth)

    def getCatalog(self, current=None):
        """Method"""
        if not self.VolatileServices.mediaCatalogs:
            raise IceFlix.TemporaryUnavailable

        proxyCtg = random.choice(self.VolatileServices.mediaCatalogs)
        print(proxyCtg)
        try:
            proxyCtg.ice_ping()

        except Ice.ConnectionRefusedException:
            print("proxy inexistente")
            self.VolatileServices.mediaCatalogs.remove(proxyCtg)
            raise IceFlix.TemporaryUnavailable

        return IceFlix.MediaCatalogPrx.uncheckedCast(proxyCtg)

    def initService(self):
        """Method"""
        print("Inicio de servicios")
        self._srv_announce_pub.newService(self._prx_service, self.service_id)

        self.announcements = threading.Timer(3.0, self.serviceAnnouncing)
        self.announcements.start()

    def serviceAnnouncing(self):
        """Method"""
        self._srv_announce_pub.announce(self._prx_service, self.service_id)
        time = 10 + random.uniform(-2, 2)
        self.announcements = threading.Timer(time, self.serviceAnnouncing)
        self.announcements.start()

    def getDB(self):
        """Method"""
        return self.VolatileServices

    def getToken(self):
        """Method"""
        return self.token

    def sendDB(self, srv_proxy):
        """Method"""
        try:
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
        except Exception as error:
            print(f'Proxy "{srv_proxy}" seems offline: {error}')
            return

    def updateDB(self, currentDB, srvId, current=None):
        """Method"""
        if self._updated is True:
            return

        if srvId == "False":
            print("Token de administración erróneo")
            current.adapter.getCommunicator().shutdown()
            return

        self.VolatileServices = currentDB
        print("Base de datos actualizada desde: " + str(srvId))
        self._updated = True

    def check_volatile_services(self, volatile_services):
        """Method"""
        wrong_proxies = []
        for vlt_srv in volatile_services:
            try:
                vlt_srv.ice_ping()
            except Exception as error:
                print(f'Proxy "{vlt_srv}" seems offline: {error}')
                wrong_proxies.append(vlt_srv)

        for srv_prx in wrong_proxies:
            volatile_services.remove(srv_prx)

class ServerMain(Ice.Application):
    """Application Main"""
    def run(self, args):
        """Method"""
        adapter = self.communicator().createObjectAdapterWithEndpoints('MainService', 'tcp')
        adapter.activate()

        service_announce_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        service_announce_subscriber = ServiceAnnouncements("", "", "")
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

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        service_implementation.announcements.cancel()
        service_announce_subscriber.poll_timer.cancel()

        service_announce_topic.unsubscribe(service_announce_subscriber_proxy)

        return 0

if __name__ == '__main__':
    app = ServerMain()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)
