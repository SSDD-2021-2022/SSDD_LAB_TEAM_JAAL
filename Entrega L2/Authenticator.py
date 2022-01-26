#!/usr/bin/env python3

#from _typeshed import Self
from os import mkdir, remove, rmdir
from shutil import rmtree
import sys
import threading
import time
import uuid
import json
import random
import datetime
import topics
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

UB_JSON_USERS = "./usersBD/"

from ServiceAnnounce import ServiceAnnouncements
from AuthenticatorChannel import Revocations
from AuthenticatorChannel import UserUpdates

class AuthenticatorI(IceFlix.Authenticator):

    def __init__(self, service_announcements_subscriber, prx_service, srv_announce_pub, userUpdates_subscriber, userUpdates_publisher, revocations_subscriber, revocations_publisher):
        #self._user_updates_subscriber_ = user_updates_subscriber
        self._id_ = str(uuid.uuid4())
        self._service_announcements_subscriber = service_announcements_subscriber
        self._prx_service = prx_service
        self._srv_announce_pub = srv_announce_pub
        self._updated = False
        self.announcements = None

        self.userUpdates_subscriber = userUpdates_subscriber
        self.userUpdates_publisher = userUpdates_publisher
        self.revocations_subscriber = revocations_subscriber
        self.revocations_publisher = revocations_publisher
        
        UsersPasswords = {}
        UsersToken = {}

        self.UsersDB = IceFlix.UsersDB()
        self.UsersDB.userPasswords = UsersPasswords
        self.UsersDB.usersToken = UsersToken
        self.newDirectory()
        #self.newBD()
    
    @property
    def service_id(self):
        """Get instance ID."""
        return self._id_
    
    def newDirectory(self):
        global UB_JSON_USERS
        ruta_dir = UB_JSON_USERS+"bdUser_"+self.service_id
        mkdir(ruta_dir)
        #self.newBD(self)

    def newBD(self):
        global UB_JSON_USERS
        ruta_dir = UB_JSON_USERS+"bdUser_"+self.service_id
        with open(ruta_dir+'/credenciales.json','w') as file:
            json.dump(self.UsersDB.userPasswords, file) 
    
    def updateLastServiceDB(self):
        with open('credenciales.json','w') as file:
            json.dump(self.UsersDB.userPasswords, file) 
    
    def checkLastInstance(self):
        dictAuth = self._service_announcements_subscriber.authenticators
        if(len(dictAuth) == 1 and dictAuth[self._id_]):
            print("Ultimo servicio en ejecucion, actualizando base de datos de credenciales.json...")
            self.updateLastServiceDB()



    def removeDirR(self):
        global UB_JSON_USERS
        ruta_dir = UB_JSON_USERS+"bdUser_"+self.service_id
        rmtree(ruta_dir)

    def refreshAuthorization(self,user, passwordHash, current=None):
        # try: 

        for key, value in self.UsersDB.userPasswords.items():
            userJSON = key
            passHashJSON = value
            
            if  (userJSON == user and passHashJSON == passwordHash):
                token = uuid.uuid4().hex

        if (token == ""):
            raise IceFlix.Unauthorized

        if(token != ""):
            self.UsersDB.usersToken[user] = token
            self.userUpdates_publisher.newToken(user, token, self.service_id)

        print("diccionario "+str(self.UsersDB.usersToken))

        #A los 2 min revocar token y dar otro
        revokeToken = threading.Timer(120.0, self.revokeTokenUser(user, token))
        revokeToken.start()
        #self.revokeTokenUser(token)

        return token

        # except IceFlix.Unauthorized:
        #     print("Usuario no autorizado")

    def revokeTokenUser(self,user, token):
        #eliminamos el token y mandamos notificacion al canal
        self.UsersDB.usersToken.pop(user)
        self.revocations_publisher.revokeToken(token, self.service_id)
            
    def isAuthorized(self, userToken, current = None):
        isAuth = False

        if userToken in self.UsersDB.usersToken.values():
            isAuth = True
  
        return isAuth

    def whois(self, userToken, current = None):
        user = ""
        # try:
        for key, value in self.UsersDB.usersToken.items():
            if userToken == value:
                user = key

        # for element in self.UsersDB.UsersToken:
        #     if userToken == self.UsersDB.UsersToken[element]["token"]:
        #         user = self.dictTokens[element]["user"]
        
        if (user == ""):
            raise IceFlix.Unauthorized

        return user
        
        # except IceFlix.Unauthorized:
        #     print("Usuario no autorizado")

    def addUser(self, user, passwordHash, adminToken, current = None):
        global UB_JSON_USERS
        # try: 
        usuarioExistente = False
        main_c = random.choice(list(self._service_announcements_subscriber.mains.values()))

        if(main_c.isAdmin(adminToken) == False):
            raise IceFlix.Unauthorized
        
        if(main_c.isAdmin(adminToken)):
            #data = json.loads(open('credenciales.json').read())
            self.UsersDB.userPasswords[user] = passwordHash
            #print("Usuario "+user+" existente. Password cambiada con éxito")
            
            ruta_dir = UB_JSON_USERS+"bdUser_"+self.service_id
            with open(ruta_dir+'/credenciales.json','w') as file:
                json.dump(self.UsersDB.userPasswords, file) 
        
        # except IceFlix.Unauthorized:
        #     print("Usuario no autorizado")

        self.userUpdates_publisher.newUser(user, passwordHash, self.service_id)


    def removeUser(self, user, adminToken, current = None):
        # try:
        userEncontrado = False
        print("lista de mains que se han publicado:\n"+str(self._service_announcements_subscriber.mains))
        main_c = random.choice(list(self._service_announcements_subscriber.mains.values()))
        if(main_c.isAdmin(adminToken) == False):
            raise IceFlix.Unauthorized
        
        if(main_c.isAdmin(adminToken)):
            for key, value in self.UsersDB.userPasswords.items():
                if key == user:
                    userEncontrado = True
                    #self.UsersDB.userPasswords.pop(user)
            if userEncontrado:
                self.UsersDB.userPasswords.pop(user)
            ruta_dir = UB_JSON_USERS+"bdUser_"+self.service_id
            with open(ruta_dir+'/credenciales.json','w') as file:
                json.dump(self.UsersDB.userPasswords, file) 
        print("Base de datos modificada\n"+str(self.UsersDB.userPasswords))

        self.revocations_publisher.revokeUser(user, self.service_id)



    def initService(self):
        print("Inicio de servicios")
        self._srv_announce_pub.newService(self._prx_service, self.service_id)
        self.announcements = threading.Timer(3.0, self.serviceAnnouncing)
        self.announcements.start()

    def updateDBjson(self):
        data = json.loads(open('credenciales.json').read())

        for key,value in data.items():
            self.UsersDB.userPasswords[key] = value
        self.newBD()

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
        return self.UsersDB
    
    def sendDB(self, srv_proxy):
        currentDB = self.getDB()
        srvId = self.service_id
        print("Enviando BD...")
        srv_proxy.updateDB(currentDB, srvId)

    def updateDB(self, currentDB, srvId, current = None):
        if self._updated == True:
            return
        self.UsersDB = currentDB
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
        

class ClientAuthentication(Ice.Application):

    def run(self,argv):
        adapter = self.communicator().createObjectAdapterWithEndpoints('AuthenticatorService', 'tcp')
        adapter.activate()
        
        #subscribe and publisher to ServiceAnnounce channel
        service_announce_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        service_announce_subscriber = ServiceAnnouncements("","","")
        service_announce_subscriber_proxy = adapter.addWithUUID(service_announce_subscriber)
        service_announce_publisher = IceFlix.ServiceAnnouncementsPrx.uncheckedCast(service_announce_topic.getPublisher())

        #subscribe and publisher to UsersUpdates Channel
        userUpdates_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'UserUpdates')
        userUpdates_subscriber = UserUpdates("", "")
        userUpdates_subscriber_proxy = adapter.addWithUUID(userUpdates_subscriber)
        userUpdates_publisher = IceFlix.UserUpdatesPrx.uncheckedCast(userUpdates_topic.getPublisher())

        #subscribe and publisher to Revocations Channel
        revocations_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'Revocations')
        revocations_subscriber = Revocations("", "")
        revocations_subscriber_proxy = adapter.addWithUUID(revocations_subscriber)
        revocations_publisher = IceFlix.RevocationsPrx.uncheckedCast(revocations_topic.getPublisher())

        service_implementation = AuthenticatorI(service_announce_subscriber, "", service_announce_publisher, userUpdates_subscriber, userUpdates_publisher, revocations_subscriber, revocations_publisher)
        service_proxy = adapter.addWithUUID(service_implementation)
        print(service_proxy, flush=True)
        print(service_implementation.service_id)
        
        #Asignacion al init de Service Announce
        service_announce_subscriber._service_type = service_proxy.ice_id()
        service_announce_subscriber._service_instance = service_implementation
        service_announce_subscriber._service_proxy = service_proxy
        service_implementation._prx_service = service_proxy

        service_announce_topic.subscribeAndGetPublisher({}, service_announce_subscriber_proxy)


        #Asignacion al init de UserUpdates
        userUpdates_subscriber._service_instance = service_implementation
        userUpdates_subscriber._service_proxy = service_proxy

        userUpdates_topic.subscribeAndGetPublisher({}, userUpdates_subscriber_proxy)


        #Asignacion al init de Revocations
        revocations_subscriber._service_instance = service_implementation
        revocations_subscriber._service_proxy = service_proxy

        revocations_topic.subscribeAndGetPublisher({}, revocations_subscriber_proxy)


        
                
        service_implementation.initService()


        # def llamarRemove():
        #     service_implementation.addUser("jose", "antonio", "token")
        # t=threading.Timer(16.0, llamarRemove)
        # t.start()


    
        
        self.shutdownOnInterrupt()
        
       
        self.communicator().waitForShutdown()
        service_implementation.checkLastInstance()
        service_implementation.removeDirR()
        service_implementation.announcements.cancel()
        service_announce_subscriber.poll_timer.cancel()
        
        service_announce_topic.unsubscribe(service_announce_subscriber_proxy)
        
        return 0


if __name__ == "__main__":
    app = ClientAuthentication()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)
