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
        if srvId == self._service_instance.service_id:
            return
        print("El srv "+srvId+" ha renombrado el id"+mediaId+" con el nombre "+name)
        for pelicula in self._service_instance.MediaDBList:
            if pelicula.mediaId == mediaId:
                pelicula.name = name
                self._service_instance.generateJson2DB()


    def addTags(self, mediaId, tags, user, srvId, current=None): 
        if srvId == self._service_instance.service_id:
            return
        print("El srv "+srvId+" ha añadido los tags para el usuario "+user)
        for pelicula in self._service_instance.MediaDBList:
            if pelicula.mediaId == mediaId:
                pelicula.tagsPerUser[user] = tags
                self._service_instance.generateJson2DB()
        
    def removeTags(self, mediaId, tags,  user, srvId, current=None):
        if srvId == self._service_instance.service_id:
            return
        print("El srv "+srvId+" ha eliminado los tags para el usuario "+user)
        if srvId == self._service_instance.service_id:
            return
        for pelicula in self._service_instance.MediaDBList:
            if pelicula.mediaId == mediaId:
                pelicula.tagsPerUser[user] = tags
                self._service_instance.generateJson2DB()


    
