#!/usr/bin/env python3
from asyncio import FastChildWatcher
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
from AuthenticatorChannel import Revocations
EXIT_ERROR=1

UB_JSON_CATALOG = "./catalogBD/"

class MediaCatalogI(IceFlix.MediaCatalog):
    
    def __init__(self, service_announcements_subscriber, prx_service, srv_announce_pub, catalogUpdates_subscriber, catalogUpdates_publisher, catalogRevocations_subscriber):
        self._id_ = str(uuid.uuid4())
        self._service_announcements_subscriber = service_announcements_subscriber
        self._prx_service = prx_service
        self._srv_announce_pub = srv_announce_pub
        self._updated = False
        self.announcements = None

        self.catalogUpdates_subscriber = catalogUpdates_subscriber
        self.catalogUpdates_publisher = catalogUpdates_publisher
        self.catalogRevocations_subscriber = catalogRevocations_subscriber

        MediaId = ""
        Name = ""
        TagsPerUser = {}
        MediaDBList = []

        self.MediaDB = IceFlix.MediaDB()
        self.MediaDB.mediaId = MediaId
        self.MediaDB.name = Name
        self.MediaDB.tagsPerUser = TagsPerUser
        self.MediaDBList = MediaDBList
        self.ruta = UB_JSON_CATALOG+"bdCatalog_"+self.service_id
        self.newDirectory()

    @property
    def service_id(self):
        """Get instance ID."""
        return self._id_

    def newDirectory(self):
        global UB_JSON_CATALOG
        ruta_dir = UB_JSON_CATALOG+"bdCatalog_"+self.service_id
        mkdir(ruta_dir)

    def newBD(self):
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
        
    def removeDirR(self):
        global UB_JSON_CATALOG
        ruta_dir = UB_JSON_CATALOG+"bdCatalog_"+self.service_id
        rmtree(ruta_dir)
    
    def checkLastInstance(self):
        dictCatalog = self._service_announcements_subscriber.catalogs
        if(len(dictCatalog) == 1 and dictCatalog[self._id_]):
            print("Ultimo servicio en ejecucion, actualizando base de datos del servicio de catálogo...")
            return True
        return False

    def updateDBjson(self):
        self.newBD()
        self.generateJson2DB(self.ruta)

    def generateJson2DB(self, ruta_dir):
        infoPeliculas = {}
        for pelicula in self.MediaDBList:
            infoPeliculas[pelicula.mediaId] = pelicula.name
        with open(ruta_dir+'/infoPeliculas.json','w') as file:
            json.dump(infoPeliculas, file)
    
        users = []
       
        for infoPel in self.MediaDBList:
            if  infoPel.tagsPerUser is not None:
                listaUsers = list(infoPel.tagsPerUser.items())
                
                for usuario, i in listaUsers:
                    users.append(usuario)

                users = set(users)
                users = list(users)

        listUsersDef = []         
        for i in users:
            dictUserId = {}
            dictIdTags = {}
            for infoPel in self.MediaDBList:
                if  infoPel.tagsPerUser is not None and i in infoPel.tagsPerUser:
                    dictIdTags[infoPel.mediaId] = infoPel.tagsPerUser.get(i)

            dictUserId["user"] = i
            dictUserId["tags"] = dictIdTags
            listUsersDef.append(dictUserId)

        dictDef = {}    
        dictDef["users"] = listUsersDef
        
        with open(ruta_dir+'/usuariosPeliculas.json','w') as file:
            json.dump(dictDef, file)
            
    def getTile(self, mediaId, userToken, current=None):
        continuar = False
        auth_c = random.choice(list(self._service_announcements_subscriber.authenticators.values()))

        user = auth_c.whois(userToken)

        if(user == ""):
            raise IceFlix.Unauthorized
            
        media = IceFlix.Media()
        mediaInfo = IceFlix.MediaInfo()
        
        for pelicula in self.MediaDBList:
            if pelicula.mediaId == mediaId:
                continuar = True
                mediaInfo.name = pelicula.name
                media.mediaId = mediaId
                media.info = mediaInfo
                
        if(continuar==False):
            raise IceFlix.WrongMediaId

        return media

    def getTilesByName(self, name, exact, current=None):
        id = []
     
        if(exact == True):
            for pelis in self.MediaDBList:
                if(pelis.name == name):
                    id.append(pelis.mediaId)
            
        else:
            for pelis in self.MediaDBList:
                if(name in pelis.name):
                    id.append(pelis.mediaId)
        return id

    def getTilesByTags(self, tags, allTags, userToken, current=None):
        idAT = []

        auth_c = random.choice(list(self._service_announcements_subscriber.authenticators.values()))
        user = auth_c.whois(userToken)

        if(user == ""):
            raise IceFlix.Unauthorized
        
        if allTags == True:
            for pelicula in self.MediaDBList:
                if pelicula.tagsPerUser is not None and pelicula.tagsPerUser.get(user):
                    todasTags = 0
                    for tag in tags:
                        if tag in pelicula.tagsPerUser.get(user):
                            todasTags = todasTags + 1
                    if todasTags == len(pelicula.tagsPerUser.get(user)):
                        idAT.append(pelicula.mediaId)
        else:
            for pelicula in self.MediaDBList:
                if pelicula.tagsPerUser is not None and pelicula.tagsPerUser.get(user):
                    continuar = True
                    for tag in tags:
                        if tag not in pelicula.tagsPerUser.get(user):
                            continuar = False
                    if continuar:
                        idAT.append(pelicula.mediaId)
            
        return idAT

    def addTags(self, mediaId, tag, userToken, current=None):
       
        continuar = False
        auth_c = random.choice(list(self._service_announcements_subscriber.authenticators.values()))
        user = auth_c.whois(userToken)
        dic = {}
        newTags = []
        if(user == ""):
            raise IceFlix.Unauthorized
        
        for pelicula in self.MediaDBList:
            if pelicula.mediaId == mediaId:
                continuar = True
                
                if pelicula.tagsPerUser is not None and user in pelicula.tagsPerUser.keys():
                    newTags = pelicula.tagsPerUser.get(user)
                else:
                    dic[user] = newTags
                    pelicula.tagsPerUser = dic
                for etiqueta in tag:
                    if etiqueta not in newTags:
                        newTags.append(etiqueta)

                pelicula.tagsPerUser[user] = newTags
                self.generateJson2DB(self.ruta)
                self.catalogUpdates_publisher.addTags(mediaId, newTags, user, self.service_id)

        if(continuar==False):
            raise IceFlix.WrongMediaId
        
    def removeTags(self, mediaId, tags, userToken, current=None):

        auth_c = random.choice(list(self._service_announcements_subscriber.authenticators.values()))
        continuar=False
        user = auth_c.whois(userToken)
        if(user == ""):
            raise IceFlix.Unauthorized
        for pelicula in self.MediaDBList:
            if pelicula.mediaId == mediaId:
                continuar = True
                newTags = pelicula.tagsPerUser.get(user)
                for etiqueta in tags:
                    if etiqueta in newTags:
                        newTags.remove(etiqueta)
        
                pelicula.tagsPerUser[user] = newTags

                self.generateJson2DB(self.ruta)
                self.catalogUpdates_publisher.removeTags(mediaId, newTags, user, self.service_id)
    
        if(continuar==False):
            raise IceFlix.WrongMediaId

    def renameTile(self, mediaId, name, adminToken, current=None):
        
        main_c = random.choice(list(self._service_announcements_subscriber.mains.values()))
        if main_c.isAdmin(adminToken):
            continuar=False

            for pelicula in self.MediaDBList:
                if pelicula.mediaId == mediaId:
                    continuar = True
                    pelicula.name = name
                    self.generateJson2DB(self.ruta)
                    self.catalogUpdates_publisher.renameTile(mediaId, name, self.service_id)
    
        else:
            raise IceFlix.Unauthorized 
        if(continuar==False):
            raise IceFlix.WrongMediaId

    def initService(self):
        print("Inicio de servicios")
        self._srv_announce_pub.newService(self._prx_service, self.service_id)
        self.announcements = threading.Timer(3.0, self.serviceAnnouncing)
        self.announcements.start()

    def serviceAnnouncing(self):
        if not self._updated:
            print("Base de Datos actualizada del json")
            self.updateDBjson()
            self._updated = True

        self._srv_announce_pub.announce(self._prx_service, self.service_id)
        time = 10 + random.uniform(-2,2)
        self.announcements = threading.Timer(time, self.serviceAnnouncing)
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
        self.generateJson2DB(self.ruta)
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

        #subscribe and publisher to Revocations Channel
        catalogRevocations_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'Revocations')
        catalogRevocations_subscriber = Revocations("", "")
        catalogRevocations_subscriber_proxy = adapter.addWithUUID(catalogRevocations_subscriber)
        #catalogURevocations_publisher = IceFlix.RevocationsPrx.uncheckedCast(catalogRevocations_topic.getPublisher())

        service_implementation = MediaCatalogI(service_announce_subscriber, "", service_announce_publisher, catalogUpdates_subscriber, catalogUpdates_publisher, catalogRevocations_subscriber)
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

        #Asignacion al init de Revocations
        catalogRevocations_subscriber._service_instance = service_implementation
        catalogRevocations_subscriber._service_proxy = service_proxy

        catalogRevocations_topic.subscribeAndGetPublisher({}, catalogRevocations_subscriber_proxy)

        
        service_implementation.initService()
     
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        
        if(service_implementation.checkLastInstance()):
            service_implementation.generateJson2DB("./")
        service_implementation.removeDirR()
        service_implementation.announcements.cancel()
        service_announce_subscriber.poll_timer.cancel()
        
        service_announce_topic.unsubscribe(service_announce_subscriber_proxy)
        
        return 0


if __name__ == "__main__":
    ClientCatalog().main(sys.argv)