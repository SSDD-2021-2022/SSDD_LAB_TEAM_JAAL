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


class AuthenticatorI(IceFlix.Authenticator):

    def __init__(self, service_announcements_subscriber, prx_service, srv_announce_pub):
        #self._user_updates_subscriber_ = user_updates_subscriber
        self._id_ = str(uuid.uuid4())
        self._service_announcements_subscriber = service_announcements_subscriber
        self._prx_service = prx_service
        self._srv_announce_pub = srv_announce_pub
        self._updated = False
        self.announcements = None
        
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

        print("diccionario "+str(self.UsersDB.usersToken))

        return token

        # except IceFlix.Unauthorized:
        #     print("Usuario no autorizado")
            
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

        if(self.main_c.isAdmin(adminToken) == False):
            raise IceFlix.Unauthorized
        
        if(self.main_c.isAdmin(adminToken)):
            #data = json.loads(open('credenciales.json').read())

            for key, value in self.UsersDB.userPasswords.items():
                if key == user:
                    usuarioExistente = True
                    value = passwordHash
            if  not usuarioExistente:
                self.UsersDB.userPasswords[user] = passwordHash
            else:
                print("Usuario "+user+" existente. Password cambiada con éxito")
            
            ruta_dir = UB_JSON_USERS+"bdUser_"+self.service_id
            with open(ruta_dir+'/credenciales.json','w') as file:
                json.dump(self.UsersDB.userPasswords, file) 

            # for usuario in data["users"]:
            #     print(usuario)
            #     if(usuario['user'] == user):
            #         usuarioExistente = True
            #         usuario['passwordHash'] = passwordHash
            
            # if(usuarioExistente==False):
            #     dict = {"user":str(user), "passwordHash":str(passwordHash)}
            #     data["users"].append(dict)
            # else:
            #     print("Usuario "+user+" existente. Password cambiada con éxito")
            
            # with open('credenciales.json', 'w') as data_file:
            #     data = json.dump(data, data_file)
        
        # except IceFlix.Unauthorized:
        #     print("Usuario no autorizado")

    def removeUser(self, user, adminToken, current = None):
        # try:
        if(self.main_c.isAdmin(adminToken) == False):
            raise IceFlix.Unauthorized
        
        if(self.main_c.isAdmin(adminToken)):
            for key, value in self.UsersDB.userPasswords.items():
                if key == user:
                    self.UsersDB.userPasswords.pop(user)

            ruta_dir = UB_JSON_USERS+"bdUser_"+self.service_id
            with open(ruta_dir+'/credenciales.json','w') as file:
                json.dump(self.UsersDB.userPasswords, file) 

    def initService(self):
        print("Inicio de servicios")
        self._srv_announce_pub.newService(self._prx_service,self.service_id)
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
        
class UserUpdates(IceFlix.UserUpdates):
    
    def __init__(self):
        self.authenticators = {}
        self.poll_timer = threading.Timer(5.0, self.remote_wrong_proxies) #no ponemos los parentesis a la funcion porque sino cogeria lo que retorna como valor
    
    def newUser(self, user,passwordHash, srvId):
        print("hola")
        
    def newToken(self, user, userToken, srvId):
        print("blas")
    
    def remote_wrong_proxies(self):
        check_availability(self.authenticators)
        
        self.poll_timer = threading.Timer(5.0, self.remote_wrong_proxies) #no ponemos los parentesis a la funcion porque sino cogeria lo que retorna como valor
        self.poll_timer.start()

    def start(self):
        '''Start current timer'''
        self.poll_timer.start() #podemos hacer una comprobacion de que ya esta arrancado o parado
    def stop(self):
        '''Cancel current timer'''
        self.poll_timer.cancel()

class ClientAuthentication(Ice.Application):

    def run(self,argv):

        adapter = self.communicator().createObjectAdapterWithEndpoints('MainService', 'tcp')
        adapter.activate()
        
        service_announce_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        service_announce_subscriber = ServiceAnnouncements("","","")
        service_announce_subscriber_proxy = adapter.addWithUUID(service_announce_subscriber)
        service_announce_publisher = IceFlix.ServiceAnnouncementsPrx.uncheckedCast(service_announce_topic.getPublisher())
        
        service_implementation = AuthenticatorI(service_announce_subscriber, "", service_announce_publisher)
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
        service_implementation.checkLastInstance()
        service_implementation.removeDirR()
        service_implementation.announcements.cancel()
        service_announce_subscriber.poll_timer.cancel()
        
        service_announce_topic.unsubscribe(service_announce_subscriber_proxy)
        
        return 0


        ##____________________CANAL USER_UPDATES______________##
        # adapter = self.communicator().createObjectAdapterWithEndpoints('Main', 'tcp')
        # adapter.activate()
    
        # user_updates_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'UserUpdates')
        # user_updates_subscriber = UserUpdates()
        # user_updates_subscriber_proxy = adapter.addWithUUID(user_updates_subscriber)
        # user_updates_topic.subscribeAndGetPublisher({}, user_updates_subscriber_proxy)
        # user_updates_subscriber.start()

        # service_implementation = AuthenticatorI(user_updates_subscriber)
        # service_proxy = adapter.addWithUUID(service_implementation)
        # print(service_proxy, flush=True)

        # user_updates_publisher = IceFlix.UserUpdatesPrx.uncheckedCast(user_updates_topic.getPublisher())

        # ##____________________CANAL SERVICE_ANNOUNCEMENTS______________##
        # adapter = self.communicator().createObjectAdapterWithEndpoints('Main', 'tcp')
        # adapter.activate()
        # qos = {}
        # service_announcements_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        # service_announcements_subscriber = ServiceAnnouncements()
        # service_announcements_subscriber_proxy = adapter.addWithUUID(service_announcements_subscriber)
        # service_announcements_topic.subscribeAndGetPublisher({}, service_announcements_subscriber_proxy)
        # service_announcements_subscriber.start()
        
        # print("Waiting events...")

        # service_implementation = AuthenticatorI(service_announcements_subscriber)
        # service_proxy = adapter.addWithUUID(service_implementation)
        # print(service_proxy, flush=True)

        # #parte publisher

        # def lanzarNuevoAnnounce():
        #     discover_publisher.announce(service_proxy,service_implementation.service_id)
        #     announce = threading.Timer(10.0,lanzarNuevoAnnounce)
        #     announce.start()
        #     print("Authenticator anunciandose")

        discover_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        discover_publisher = IceFlix.ServiceAnnouncementsPrx.uncheckedCast(discover_topic.getPublisher())
        discover_publisher.announce(service_proxy,service_implementation.service_id)

        # #discover_publisher.announce(service_proxy,service_implementation.service_id)

        # announce = threading.Timer(10.0,lanzarNuevoAnnounce)
        # announce.start()



        # ##____________________CANAL REVOCATIONS______________##


        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        

        user_updates_topic.unsubscribe(user_updates_subscriber_proxy)
        user_updates_subscriber.stop()

        return 0


if __name__ == "__main__":
    app = ClientAuthentication()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)
