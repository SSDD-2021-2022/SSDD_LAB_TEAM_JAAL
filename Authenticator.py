#!/usr/bin/env python3

import sys
import uuid
import json

import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

class AuthenticatorI(IceFlix.Authenticator):

    def refreshAuthorization(self,user, passwordHash, current=None): #Metodo para crear un nuevo token (recibe user y hash de la password)
        try: 
            #usuario = user
            #passw = passwordHash

            token = ""
            data = json.loads(open('credenciales.json').read())

            for usuario in data['users']:
                userJSON = usuario['user']
                passHashJSON = usuario["passwordHash"]
                print (userJSON+" " +passHashJSON)
                print(userJSON==user)
                print(passHashJSON == passwordHash)

                if  (userJSON == user and passHashJSON == passwordHash):
                    print("usuario y password existentes")
                    token = uuid.uuid4().hex

            return token

            
        except IceFlix.Unauthorized as error:
            print("Usuario no autorizado")
            sys.exit(1)

class ClientAuthentication(Ice.Application):
    def run(self,argv):
        i = 0
        dictTokens = { 0:{"user": "", "token":""}}

        aux = AuthenticatorI()
        user = "antonio"
        token = aux.refreshAuthorization(user, "4ee3679892e6ac5a5b513eba7fd529d363d7a96508421c5dbd44b01b349cf514")

        if(token != ""):
            dictTokens[i]["user"] = user
            dictTokens[i]["token"] = token
            i = i+1

        print(dictTokens)

       

sys.exit(ClientAuthentication().main(sys.argv))
