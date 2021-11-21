#!/usr/bin/env python3

from os import remove
import sys
import uuid
import json

import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

EXIT_ERROR = 1

dictTokens = { 0:{"user": "", "token":""}}
i = 0
proxy_argv = ""

class AuthenticatorI(Ice.Application, IceFlix.Authenticator):

    def refreshAuthorization(self,user, passwordHash, current=None): #Metodo para crear un nuevo token (recibe user y hash de la password)
        try: 
            #usuario = user
            #passw = passwordHash

            token = None
            data = json.loads(open('credenciales.json').read())

            for usuario in data['users']:
                userJSON = usuario['user']
                passHashJSON = usuario["passwordHash"]
                
                if  (userJSON == user and passHashJSON == passwordHash):
                    token = uuid.uuid4().hex
            
            if token == None:
                raise IceFlix.Unauthorized()

            return token

        except IceFlix.Unauthorized as error:
            print("Usuario no autorizado")
            return None
            
            
    
    def isAuthorized(self, userToken, current = None):
        isAuth = False
        
        for element in dictTokens:
            if userToken == dictTokens[element]["token"]:
                isAuth = True


        return isAuth

    def whois(self, userToken, current = None):
        user = None
        try:
            for element in dictTokens:
                if userToken == dictTokens[element]["token"]:
                    user = dictTokens[element]["user"]
            
            if(user == None):
                raise IceFlix.Unauthorized()

            return user
        
        except IceFlix.Unauthorized as error:
            print("Usuario no autorizado")
            return None

    def addUser(self, user, passwordHash, adminToken, current = None):
        try: 
            proxy = self.communicator().stringToProxy(sys.argv[1])
            main_c = IceFlix.MainPrx.checkedCast(proxy)
            if(main_c.isAdmin(adminToken) == False):
                raise IceFlix.Unauthorized
            
            if(main_c.isAdmin(adminToken)):
                i = 0
                data = json.loads(open('credenciales.json').read())

                for usuario in data["users"]:
                    i = i+1
                dict = {"user":str(user), "passwordHash":str(passwordHash)}
                data["users"].append(dict)
                #data["users"][i]["passwordHash"] = passwordHash

                with open('credenciales.json', 'w') as data_file:
                    data = json.dump(data, data_file)
        
        except IceFlix.Unauthorized as error:
            print("Usuario no autorizado")

    def removeUser(self, user, adminToken, current = None):
        try:
            proxy = self.communicator().stringToProxy(sys.argv[1])
            main_c = IceFlix.MainPrx.checkedCast(proxy)
            if(main_c.isAdmin(adminToken) == False):
                raise IceFlix.Unauthorized
            
            if(main_c.isAdmin(adminToken)):
                data = json.loads(open('credenciales.json').read())
                for usuario in data["users"]:
                    if(usuario["user"] == user):
                        data["users"].remove(usuario)

                with open('credenciales.json', 'w') as data_file:
                    data = json.dump(data, data_file)
        
        except IceFlix.Unauthorized as error:
            print("Usuario no autorizado")
            #sys.exit(1)

class ClientAuthentication(Ice.Application):
    def run(self,argv):
        proxy_argv = argv[1] 
        
        i = 0
        aux = AuthenticatorI()
        user = "antoni"
        token = aux.refreshAuthorization(user, "4ee3679892e6ac5a5b513eba7fd529d363d7a96508421c5dbd44b01b349cf514")
        print("token "+str(token))

        if(token != None):
            dictTokens[i]["user"] = user
            dictTokens[i]["token"] = token
            i = i+1
        
        print(dictTokens)

        estaAutorizado = aux.isAuthorized(token)
        print(estaAutorizado)

        usuarioToken = aux.whois(token)
        print("El token pertenece a "+str(usuarioToken))
        aux.addUser("ssdd","ssdd","blassss")


sys.exit(ClientAuthentication().main(sys.argv))