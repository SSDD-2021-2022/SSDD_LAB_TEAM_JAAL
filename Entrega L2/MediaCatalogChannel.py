import uuid
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import threading

class CatalogUpdates (IceFlix.CatalogUpdates):

    def __init__(self, service_instance, service_proxy, current=None):
        """Initialize the Discover object with empty services."""
        self._service_instance = service_instance
        self._service_proxy = service_proxy

    def renameTile(self, mediaId, name, srvId, current=None):
        print("hola")

    def addTags(self, mediaId, tags, user, srvId, current=None):
        print("hola")
        
    def removeTags(self, mediaId, tags,  user, srvId, current=None):
        print("hola")


    
