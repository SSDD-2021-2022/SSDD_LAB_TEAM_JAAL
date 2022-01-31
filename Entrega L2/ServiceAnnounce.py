# pylint:disable=W0613
# pylint:disable=C0413
# pylint:disable=E0401
#pylint:disable=W0212
# pylint:disable=C0103
import uuid
import threading
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix


class ServiceAnnouncements(IceFlix.ServiceAnnouncements):
    """Class ServiceAnnouncements"""
    def __init__(self, service_type, service_instance, service_proxy, current=None):
        """Initialize the Discover object with empty services."""
        self._id_ = str(uuid.uuid4())
        self._service_type = service_type
        self._service_instance = service_instance
        self._service_proxy = service_proxy
        self.authenticators = {}
        self.catalogs = {}
        self.mains = {}
        self.poll_timer = threading.Timer(5.0, self.remote_wrong_proxies) #no ponemos los parentesis a la funcion porque sino cogeria lo que retorna como valor
        self.poll_timer.start()
        self.announce_time = None

    @property
    def known_services(self):
        """Get serviceIds for all services."""
        return list(self.authenticators.keys()) + list(self.catalogs.keys()) + list(self.mains.keys())

    def newService(self, service, srvId, current=None):  # pylint: disable=unused-argument
        """Method"""
        if not service.ice_isA(self._service_type) or service == self._service_proxy:
            return

        if service.ice_isA('::IceFlix::Main'):
            print(f'New possible MainService: {srvId}')
            # Comprobar token administracion
            srv_prx = IceFlix.MainPrx.checkedCast(service)

        elif service.ice_isA('::IceFlix::Authenticator'):
            print(f'New possible AuthenticatorService: {srvId}')
            srv_prx = IceFlix.AuthenticatorPrx.checkedCast(service)

        elif service.ice_isA('::IceFlix::MediaCatalog'):
            print(f'New possible MediaCatalogService: {srvId}')
            srv_prx = IceFlix.MediaCatalogPrx.checkedCast(service)

        self._service_instance.sendDB(srv_prx)


    def announce(self, service, srvId, current=None):  # pylint: disable=unused-argument
        """Check service type and add it."""
        if srvId in self.known_services:
            return
        if service.ice_isA('::IceFlix::Authenticator'):
            print(f'New AuthenticatorService running: {srvId}')
            self.authenticators[srvId] = IceFlix.AuthenticatorPrx.uncheckedCast(service)
            if self._service_proxy.ice_isA('::IceFlix::Main'):
                self._service_instance.register(service, srvId)
        elif service.ice_isA('::IceFlix::MediaCatalog'):
            print(f'New MediaCatalogService running: {srvId}')
            self.catalogs[srvId] = IceFlix.MediaCatalogPrx.uncheckedCast(service)
            if self._service_proxy.ice_isA('::IceFlix::Main'):
                self._service_instance.register(service, srvId)

        elif service.ice_isA('::IceFlix::Main'):
            print(f'New MainService running: {srvId}')
            self.mains[srvId] = IceFlix.MainPrx.uncheckedCast(service)
        print(self.known_services)


    def remote_wrong_proxies(self):
        """Method"""
        check_availability(self.authenticators)
        check_availability(self.catalogs)
        check_availability(self.mains)
        if self._service_proxy.ice_isA('::IceFlix::Main'):
            self._service_instance.check_volatile_services(self._service_instance.VolatileServices.authenticators)
            self._service_instance.check_volatile_services(self._service_instance.VolatileServices.mediaCatalogs)


        self.poll_timer = threading.Timer(5.0, self.remote_wrong_proxies) #no ponemos los parentesis a la funcion porque sino cogeria lo que retorna como valor
        self.poll_timer.start()

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
        