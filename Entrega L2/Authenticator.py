#!/usr/bin/env python3

from _typeshed import Self
from os import remove
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


class AuthenticatorI(IceFlix.Authenticator):
    
    
    def __init__(self, user_updates_subscriber):
        self._user_updates_subscriber_ = user_updates_subscriber
        self._id_ = str(uuid.uuid4())
        
        UsersPasswords = {}
        UsersToken = {}

        self.UsersDB = IceFlix.UsersDB()
        self.UsersDB.userPasswords = UsersPasswords
        self.UsersDB.usersToken = UsersToken

        
    @property
    def service_id(self):
        """Get instance ID."""
        return self._id_

    def refreshAuthorization(self,user, passwordHash, current=None):
        try: 
            token = ""
            data = json.loads(open('credenciales.json').read())

            for usuario in data['users']:
                userJSON = usuario['user']
                passHashJSON = usuario["passwordHash"]
                
                if  (userJSON == user and passHashJSON == passwordHash):
                    token = uuid.uuid4().hex
            
            if (token == ""):
                raise IceFlix.Unauthorized

            if(token != ""):
                self.UsersDB.UsersToken[user] = token

            print("diccionario "+str(self.UsersDB.UsersToken))

            return token

        except IceFlix.Unauthorized:
            print("Usuario no autorizado")
            
            
            
    def isAuthorized(self, userToken, current = None):
        isAuth = False
        
        for element in self.UsersDB.UsersToken:
            if userToken == self.UsersDB.UsersToken[element]:
                isAuth = True


        return isAuth

    def whois(self, userToken, current = None):
        user = ""
        try:
            for element in self.UsersDB.UsersToken:
                if userToken == self.UsersDB.UsersToken[element]["token"]:
                    user = self.dictTokens[element]["user"]
            
            if (user == ""):
                raise IceFlix.Unauthorized

            return user
        
        except IceFlix.Unauthorized:
            print("Usuario no autorizado")

    def addUser(self, user, passwordHash, adminToken, current = None):
        try: 
            usuarioExistente = False

            if(self.main_c.isAdmin(adminToken) == False):
                raise IceFlix.Unauthorized
            
            if(self.main_c.isAdmin(adminToken)):
                i = 0
                data = json.loads(open('credenciales.json').read())

                for usuario in data["users"]:
                    print(usuario)
                    if(usuario['user'] == user):
                        usuarioExistente = True
                        usuario['passwordHash'] = passwordHash
                
                if(usuarioExistente==False):
                    dict = {"user":str(user), "passwordHash":str(passwordHash)}
                    data["users"].append(dict)
                else:
                    print("Usuario "+user+" existente. Password cambiada con éxito")
                
                with open('credenciales.json', 'w') as data_file:
                    data = json.dump(data, data_file)
        
        except IceFlix.Unauthorized:
            print("Usuario no autorizado")

    def removeUser(self, user, adminToken, current = None):
        try:
            if(self.main_c.isAdmin(adminToken) == False):
                raise IceFlix.Unauthorized
            
            if(self.main_c.isAdmin(adminToken)):
                data = json.loads(open('credenciales.json').read())
                for usuario in data["users"]:
                    if(usuario["user"] == user):
                        data["users"].remove(usuario)

                with open('credenciales.json', 'w') as data_file:
                    data = json.dump(data, data_file)
            print("Usuario "+user+" eliminado")
        
        except IceFlix.Unauthorized:
            print("Usuario no autorizado")
            #sys.exit(1)

    def updateDB(self, currentDatabase, srvId):
        self.UsersDB = currentDatabase
        
        
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
        

        ##____________________CANAL USER_UPDATES______________##
        adapter = self.communicator().createObjectAdapterWithEndpoints('Main', 'tcp')
        adapter.activate()
    
        user_updates_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'UserUpdates')
        user_updates_subscriber = UserUpdates()
        user_updates_subscriber_proxy = adapter.addWithUUID(user_updates_subscriber)
        user_updates_topic.subscribeAndGetPublisher({}, user_updates_subscriber_proxy)
        user_updates_subscriber.start()



        service_implementation = AuthenticatorI(user_updates_subscriber)
        service_proxy = adapter.addWithUUID(service_implementation)
        print(service_proxy, flush=True)

        user_updates_publisher = IceFlix.UserUpdatesPrx.uncheckedCast(user_updates_topic.getPublisher())

        ##____________________CANAL SERVICE_ANNOUNCEMENTS______________##
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

        #parte publisher

        def lanzarNuevoAnnounce():
            discover_publisher.announce(service_proxy,service_implementation.service_id)
            announce = threading.Timer(10.0,lanzarNuevoAnnounce)
            announce.start()
            print("Authenticator anunciandose")

        discover_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'ServiceAnnouncements')
        discover_publisher = IceFlix.ServiceAnnouncementsPrx.uncheckedCast(discover_topic.getPublisher())
        discover_publisher.newService(service_proxy,service_implementation.service_id)

        #discover_publisher.announce(service_proxy,service_implementation.service_id)

        announce = threading.Timer(10.0,lanzarNuevoAnnounce)
        announce.start()



        ##____________________CANAL REVOCATIONS______________##


        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        

        user_updates_topic.unsubscribe(user_updates_subscriber_proxy)
        user_updates_subscriber.stop()

        return 0


if __name__ == "__main__":
    app=ClientAuthentication()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)
