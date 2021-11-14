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
            usuario = user
            dictTokens ={
                0:{"user": "blas", "token":"hola"}
            }
            token = ""
            data = json.loads(open('credenciales.json').read())
            for user in data['users']:
                userJSON = user['user']
                if userJSON == usuario:
                    token = uuid.uuid4().hex
                    dictTokens[0]["token"] = token
                    print(dictTokens[0]["user"])
            print(dictTokens[0]["token"])        
            return token

            
        except IceFlix.Unauthorized as error:
            print("Usuario no autorizado")
            sys.exit(1)

class ClientAuthentication(Ice.Application):
    def run(self,argv):
        aux = AuthenticatorI()
        token = aux.refreshAuthorization("blas", "1224365terwae")

sys.exit(ClientAuthentication().main(sys.argv))
