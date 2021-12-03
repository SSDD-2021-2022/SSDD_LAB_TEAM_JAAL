#!/usr/bin/env python3

from os import remove
import sys
import uuid
import json

import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

dictTokens = { 0:{"user": "", "token":""}}
i = 0
#communicator = None

class AuthenticatorI(IceFlix.Authenticator):

    def __init__(self, main_c):
        self.main_c = main_c

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
        
        except IceFlix.Unauthorized as error:
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
        
        except IceFlix.Unauthorized as error:
            print("Usuario no autorizado")
            #sys.exit(1)

class ClientAuthentication(Ice.Application):

    def actualizarDictTokens(self,token, user):
        global i
        if(token != None):
            print(i)
            dictTokens[i] = {"user":str(user), "token":str(token)}
            i = i+1


    def run(self,argv):
        #obtencion del proxy, que se introduce por argumentos
        proxy = self.communicator().stringToProxy(argv[1])
        main_c = IceFlix.MainPrx.checkedCast(proxy)
        aux = AuthenticatorI(main_c)
        user = "antonio"
        user1= "ejemplo"
        token = aux.refreshAuthorization(user, "passssss")
        print("token "+str(token))

        self.actualizarDictTokens(token, user)

        print(dictTokens)

        token = aux.refreshAuthorization(user1, "ssdd")
        print("token "+str(token))

        self.actualizarDictTokens(token, user1)
        
        print(dictTokens)

        estaAutorizado = aux.isAuthorized(token)
        print(estaAutorizado)

        usuarioToken = aux.whois(token)
        print("El token pertenece a "+str(usuarioToken))
        aux.addUser("antonio","new password","blassss")
        aux.removeUser("aneg","blassss")


if __name__ == "__main__":
    ClientAuthentication().main(sys.argv)