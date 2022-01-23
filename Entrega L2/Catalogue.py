#!/usr/bin/env python3
from curses import use_default_colors
from os import mkdir, remove, rmdir
from shutil import rmtree
import sys
import uuid
import json
import Ice
import topics
import random
import threading
Ice.loadSlice('iceflix.ice')
import IceFlix
from ServiceAnnounce import ServiceAnnouncements
from MediaCatalogChannel import CatalogUpdates
EXIT_ERROR=1

UB_JSON_CATALOG = "./catalogBD/"

class MediaCatalogI(IceFlix.MediaCatalog):
    
    def __init__(self, service_announcements_subscriber, prx_service, srv_announce_pub, catalogUpdates_subscriber, catalogUpdates_publisher):
        self._id_ = str(uuid.uuid4())
        self._service_announcements_subscriber = service_announcements_subscriber
        self._prx_service = prx_service
        self._srv_announce_pub = srv_announce_pub
        self._updated = False
        self.announcements = None

        self.catalogUpdates_subscriber = catalogUpdates_subscriber
        self.catalogUpdates_publisher = catalogUpdates_publisher

        MediaId = ""
        Name = ""
        TagsPerUser = {}
        MediaDBList = []

        self.MediaDB = IceFlix.MediaDB()
        self.MediaDB.mediaId = MediaId
        self.MediaDB.name = Name
        self.MediaDB.tagsPerUser = TagsPerUser
        self.MediaDBList = MediaDBList

        self.newDirectory()
        #self.updateDBjson()

    @property
    def service_id(self):
        """Get instance ID."""
        return self._id_

    def newDirectory(self):
        global UB_JSON_CATALOG
        ruta_dir = UB_JSON_CATALOG+"bdCatalog_"+self.service_id
        mkdir(ruta_dir)
        #self.newBD(self)

    def newBD(self):
        global UB_JSON_CATALOG
        ruta_dir = UB_JSON_CATALOG+"bdCatalog_"+self.service_id
        # with open(ruta_dir+'/usuariosPeliculas.json','w') as file:
        #     json.dump(self.UsersDB.userPasswords, file) 

        infoPeliculas = {}
        for pelicula in self.MediaDBList:
            infoPeliculas[pelicula.mediaId] = pelicula.name
            
        with open(ruta_dir+'/infoPeliculas.json','w') as file:
            json.dump(infoPeliculas, file) 
    
    def updateLastServiceDB(self, usuariosPeliculas):
        with open('credenciales.json','w') as file:
            json.dump(usuariosPeliculas, file) 
    
    def checkLastInstance(self):
        dictAuth = self._service_announcements_subscriber.authenticators
        if(len(dictAuth) == 1 and dictAuth[self._id_]):
            print("Ultimo servicio en ejecucion, actualizando base de datos de credenciales.json...")
            self.updateLastServiceDB()

    def updateDBjson(self):
        infoPeliculas = json.loads(open('infoPeliculas.json').read())
        usuariosPeliculas = json.loads(open('usuariosPeliculas.json').read())

        for key,value in infoPeliculas.items():
            dic = {}
            pelicula = IceFlix.MediaDB()
            pelicula.mediaId = key
            pelicula.name = value

            for usuario in usuariosPeliculas["users"]:
                user = usuario["user"]
                listaTagsUsuario = usuario["tags"]
                for id_pel, tagsUser in listaTagsUsuario.items():
                    if id_pel == key:
                        dic[user] = tagsUser
                        pelicula.tagsPerUser = dic
            self.MediaDBList.append(pelicula)

        ruta_dir = UB_JSON_CATALOG+"bdCatalog_"+self.service_id
        with open(ruta_dir+'/infoPeliculas.json','w') as file:
            json.dump(infoPeliculas, file) 
        with open(ruta_dir+'/usuariosPeliculas.json','w') as file:
            json.dump(usuariosPeliculas, file) 

                            
    def getTile(self, mediaId, current=None):
        # try:
        continuar = False
        tile=""
        media = IceFlix.Media()
        mediaInfo = IceFlix.MediaInfo()
        data = json.loads(open('infoPeliculas.json').read())
        for ids in data:
            if(ids == mediaId):
                tile = data[ids]
                continuar=True
        if(continuar==False):
            raise IceFlix.WrongMediaId
        mediaInfo.name = tile
        media.mediaId = mediaId
        media.info = mediaInfo
        # except IceFlix.WrongMediaId:
        #     print("Id de la pelicula incorrecto\n")
        # except IceFlix.TemporaryUnavailable:
        #     print("Error TemporaryAvaible")
        return media
        

    def getTilesByName(self, name, exact, current=None):
        id = []
        data = json.loads(open('infoPeliculas.json').read())

        if(exact == True):
            for ids, pelis in data.items():
                if(pelis == name):
                    id.append(ids)
            
        else:
            for ids, pelis in data.items():
                if(name in pelis):
                    id.append(ids)
        return id

    def getTilesByTags(self, tags, allTags, userToken, current=None):
        # try: 
        idAT = []
        id = []
        todasTags = 0
        data = json.loads(open('usuariosPeliculas.json').read())
        
        user = self.auth_c.whois(userToken)
        print(user)
        if(user == ""):
            raise IceFlix.Unauthorized

        print(user)
        for usuario in data["users"]:
            if (usuario["user"] == user):
                tagsUsuario = usuario["tags"]
                for peliculas, tagsPelicula in tagsUsuario.items():
                    for meTag in tags:
                        if(meTag in tagsPelicula):
                            todasTags = todasTags+1
                            if(allTags == False):
                                idAT.append(peliculas)
                        
                    if(todasTags == len(tags) and allTags):
                        id.append(peliculas)

                    todasTags = 0

        if(allTags == False):
            for i in idAT:
                if i not in id:
                    id.append(i)
        # except IceFlix.Unauthorized:
        #     print("Usuario no autorizado.")
        return id

    def addTags(self, mediaId, tag, userToken, current=None):
        # try:
        user = self.auth_c.whois(userToken)
        if(user == ""):
            raise IceFlix.Unauthorized
        
        data=json.loads(open('usuariosPeliculas.json').read())
        continuar=False
        for usuario in data["users"]:
            if usuario["user"] == user:
                listaTagsUsuario = usuario["tags"]
                for id_pel, tagsUser in listaTagsUsuario.items():
                    print(str(id_pel)+" "+str(tagsUser))
                    if id_pel == mediaId:
                        continuar=True  
                        for j in tag:
                            if(j in tagsUser):
                                tagsUser.remove(j)

                            tagsUser.append(j)
                            print(j)
                            print(tagsUser)
        with open('usuariosPeliculas.json', 'w') as data_file:
            data = json.dump(data, data_file)

        if(continuar==False):
            raise IceFlix.WrongMediaId
  
        # except IceFlix.WrongMediaId:
        #     print("Id no valido\n")
        # except IceFlix.Unauthorized:
        #     print("Usuario no autorizado")
        
        
    def removeTags(self, mediaId, tags, userToken, current=None):
        # try:
        user = self.auth_c.whois(userToken)
        if(user == ""):
            raise IceFlix.Unauthorized
        
        data = json.loads(open('usuariosPeliculas.json').read())
        continuar=False

        for usuario in data["users"]:
            if usuario["user"] == user:
                listaTagsUsuario = usuario["tags"]
                for id_pel, tagsUser in listaTagsUsuario.items():
                    print(str(id_pel)+" "+str(tagsUser))
                    if id_pel == mediaId:
                        continuar=True
                        for tagParametro in tags:
                            if tagParametro in tagsUser:
                                tagsUser.remove(tagParametro)
                                print(str(tagParametro)+" eliminado")
                                print(tagsUser)
                                
        with open('usuariosPeliculas.json', 'w') as data_file:
            data = json.dump(data, data_file)
        if(continuar==False):
            raise IceFlix.WrongMediaId
        # except IceFlix.Unauthorized:
        #     print("Usuario no autorizado")
        # except IceFlix.WrongMediaId:
        #     print("Id de la pelicula incorrecto")

    def renameTile(self, mediaId, name, adminToken, current=None):
        # try:
        if self.main_c.isAdmin(adminToken):
            data = json.loads(open('infoPeliculas.json').read())
            continuar=False

            for ids in data:
                if ids == mediaId:
                    continuar=True
                    data[ids] = name
    
            with open('infoPeliculas.json', 'w') as data_file:
                data = json.dump(data, data_file)
        else:
            raise IceFlix.Unauthorized 
        if(continuar==False):
            raise IceFlix.WrongMediaId
        # except IceFlix.Unauthorized:
        #     print("usuario no autorizado")
        # except IceFlix.WrongMediaId:
        #     print("Id de la pelicula incorrecto")

    def initService(self):
        print("Inicio de servicios")
        self._srv_announce_pub.newService(self._prx_service,self.service_id)
        self.announcements = threading.Timer(3.0, self.serviceAnnouncing)
        self.announcements.start()

    def serviceAnnouncing(self):
        if not self._updated:
            print("Base de Datos actualizada del json")
            self.updateDBjson()
            self._updated = True

        self._srv_announce_pub.announce(self._prx_service,self.service_id)
        time = 10 + random.uniform(-2,2)
        self.announcements = threading.Timer(time,self.serviceAnnouncing)
        self.announcements.start()
    
    def getDB(self):
        return self.MediaDBList

    def sendDB(self, srv_proxy):
        catalogDB = self.getDB()
        srvId = self.service_id
        print("Enviando BD...")
        srv_proxy.updateDB(catalogDB, srvId)
    
    def updateDB(self, catalogDB, srvId, current = None):
        if self._updated == True:
            return
        self.MediaDBList = catalogDB        
        print("Base de datos actualizada desde: " + str(srvId))
        self.newBD()
        self._updated = True
        self._srv_announce_pub.announce(self._prx_service,self.service_id)

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

class ClientCatalog(Ice.Application):    

    def run(self, argv):
        adapter = self.communicator().createObjectAdapterWithEndpoints('MediaCatalogService', 'tcp')
        adapter.activate()

        #subscribe and publisher to ServiceAnnounce channel
        service_announce_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        service_announce_subscriber = ServiceAnnouncements("","","")
        service_announce_subscriber_proxy = adapter.addWithUUID(service_announce_subscriber)
        service_announce_publisher = IceFlix.ServiceAnnouncementsPrx.uncheckedCast(service_announce_topic.getPublisher())

        #subscribe and publisher to CatalogUpdates Channel
        catalogUpdates_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'CatalogUpdates')
        catalogUpdates_subscriber = CatalogUpdates("", "")
        catalogUpdates_subscriber_proxy = adapter.addWithUUID(catalogUpdates_subscriber)
        catalogUpdates_publisher = IceFlix.CatalogUpdatesPrx.uncheckedCast(catalogUpdates_topic.getPublisher())

        service_implementation = MediaCatalogI(service_announce_subscriber, "", service_announce_publisher, catalogUpdates_subscriber, catalogUpdates_publisher)
        service_proxy = adapter.addWithUUID(service_implementation)
        print(service_proxy, flush=True)
        print(service_implementation.service_id)

        
        #Asignacion al init de Service Announce
        service_announce_subscriber._service_type = service_proxy.ice_id()
        service_announce_subscriber._service_instance = service_implementation
        service_announce_subscriber._service_proxy = service_proxy
        service_implementation._prx_service = service_proxy

        service_announce_topic.subscribeAndGetPublisher({}, service_announce_subscriber_proxy)


        #Asignacion al init de catalogUpdates
        catalogUpdates_subscriber._service_instance = service_implementation
        catalogUpdates_subscriber._service_proxy = service_proxy

        catalogUpdates_topic.subscribeAndGetPublisher({}, catalogUpdates_subscriber_proxy)

        
        service_implementation.initService()

        
        self.shutdownOnInterrupt()
    
        self.communicator().waitForShutdown()

        service_announce_subscriber.poll_timer.cancel()
        
        service_announce_topic.unsubscribe(service_announce_subscriber_proxy)
        
        return 0


if __name__ == "__main__":
    ClientCatalog().main(sys.argv)