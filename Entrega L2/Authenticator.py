#!/usr/bin/env python3

from os import remove
import sys
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
    
    
    UsersToken = {}

    def __init__(self):
        self._id_ = str(uuid.uuid4())
        
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
                self.UsersToken[user] = token

            print("diccionario "+str(self.UsersToken))

            return token

        except IceFlix.Unauthorized:
            print("Usuario no autorizado")
            
            
            
    def isAuthorized(self, userToken, current = None):
        isAuth = False
        
        for element in self.dictTokens:
            if userToken == self.dictTokens[element]["token"]:
                isAuth = True


        return isAuth

    def whois(self, userToken, current = None):
        user = ""
        try:
            for element in self.dictTokens:
                if userToken == self.dictTokens[element]["token"]:
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


    def sendUsersDB(currentDB, srvId):
        
        print("")
class UserUpdatesI(IceFlix.UserUpdates):
    def __init__(self):
        self.authenticators = {}
    def newUser(self, user,passwordHash, srvId):
        print("hola")
    def newToken(self, user, userToken, srvId):
        print("blas")
class ClientAuthentication(Ice.Application):

    def run(self,argv):
        aux = AuthenticatorI()
        aux.refreshAuthorization("blas", "b94f9822bfc56656418c1e554f8edf1091444231c538d4d751b6339d87addc05")

        adapter = self.communicator().createObjectAdapterWithEndpoints('Main', 'tcp')
        adapter.activate()
    
        user_updates_topic = topics.getTopic(topics.getTopicManager(self.communicator()), 'UserUpdates')
        user_updates_subscriber = UserUpdatesI()
        user_updates_subscriber_proxy = adapter.addWithUUID(user_updates_subscriber)
        user_updates_topic.subscribeAndGetPublisher({}, user_updates_subscriber_proxy)



if __name__ == "__main__":
    ClientAuthentication().main(sys.argv)