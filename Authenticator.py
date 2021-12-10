#!/usr/bin/env python3

from os import remove
import sys
import time
import uuid
import json
import random
import datetime

import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix


class AuthenticatorI(IceFlix.Authenticator):
    dictTokens = { 0:{"user": "", "token":""}}
    i = 0

    def __init__(self, main_c):
        self.main_c = main_c

    def refreshAuthorization(self,user, passwordHash, current=None): #Metodo para crear un nuevo token (recibe user y hash de la password)
        try: 
            #usuario = user
            #passw = passwordHash

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
                #print(self.i)
                self.dictTokens[self.i] = {"user":str(user), "token":str(token)}
                self.i = self.i+1

            print("diccionario "+str(self.dictTokens))

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

class ClientAuthentication(Ice.Application):

    def run(self,argv):
        
        #obtencion del proxy, que se introduce por argumentos
        proxyMain = open("salida").read()
        proxy = self.communicator().stringToProxy(proxyMain)
        main_c = IceFlix.MainPrx.checkedCast(proxy)
        #aux = AuthenticatorI(main_c)

       
       #Crear proxy de authenticator para registrarlo llamando a register-->del main
        broker = self.communicator()
        servant = AuthenticatorI(main_c)
        adapter = broker.createObjectAdapter("AuthenticatorAdapter")
        #time = datetime.datetime.now()
        proxyAuth = adapter.add(servant, broker.stringToIdentity("authenticator1"))
        print(proxyAuth, flush=False)
        
        adapter.activate()
        self.shutdownOnInterrupt()
        pAuth= IceFlix.AuthenticatorPrx.checkedCast(proxyAuth)
        main_c.register(pAuth)
        broker.waitForShutdown()
        return 0

       

        """token = aux.refreshAuthorization(user1, "ssdd")
        print("token "+str(token))

        self.actualizarDictTokens(token, user1)
        
        print(dictTokens)

        estaAutorizado = aux.isAuthorized(token)
        print(estaAutorizado)

        usuarioToken = aux.whois(token)
        print("El token pertenece a "+str(usuarioToken))
        aux.addUser("antonio","new password","blassss")
        aux.removeUser("aneg","blassss")"""


if __name__ == "__main__":
    ClientAuthentication().main(sys.argv)