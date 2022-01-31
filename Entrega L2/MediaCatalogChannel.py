# pylint:disable=W0613
# pylint:disable=C0413
#pylint:disable=W0212
# pylint:disable=E0401
# pylint:disable=C0103
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

class CatalogUpdates(IceFlix.CatalogUpdates):
    """Clase CatalogUpdates"""
    def __init__(self, service_instance, service_proxy, current=None):
        """Initialize the Discover object with empty services."""
        self._service_instance = service_instance
        self._service_proxy = service_proxy

    def renameTile(self, mediaId, name, srvId, current=None):
        """Method"""
        if srvId == self._service_instance.service_id:
            return
        print("El srv "+srvId+" ha renombrado el id"+mediaId+" con el nombre "+name)
        for pelicula in self._service_instance.MediaDBList:
            if pelicula.mediaId == mediaId:
                pelicula.name = name
                self._service_instance.generateJson2DB(self._service_instance.ruta)

    def addTags(self, mediaId, tags, user, srvId, current=None):
        """Method"""
        if srvId == self._service_instance.service_id:
            return
        print("El srv "+srvId+" ha añadido los tags para el usuario "+user)
        print(tags)
        dic = {}
        for pelicula in self._service_instance.MediaDBList:
            if pelicula.mediaId == mediaId:
                if pelicula.tagsPerUser is not None and user in pelicula.tagsPerUser.keys():
                    pelicula.tagsPerUser[user] = tags
                else:
                    dic[user] = tags
                    pelicula.tagsPerUser = dic

                self._service_instance.generateJson2DB(self._service_instance.ruta)

    def removeTags(self, mediaId, tags, user, srvId, current=None):
        """Method"""
        if srvId == self._service_instance.service_id:
            return
        print("El srv "+srvId+" ha eliminado los tags para el usuario "+user)
        if srvId == self._service_instance.service_id:
            return
        for pelicula in self._service_instance.MediaDBList:
            if pelicula.mediaId == mediaId:
                pelicula.tagsPerUser[user] = tags
                self._service_instance.generateJson2DB(self._service_instance.ruta)
