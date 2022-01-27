import uuid
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import threading

class UserUpdates (IceFlix.UserUpdates):

    def __init__(self, service_instance, service_proxy, current=None):
        """Initialize the Discover object with empty services."""
        self._service_instance = service_instance
        self._service_proxy = service_proxy

    def newUser(self, user, passwordHash, srvId, current=None):
        #actualizamos json
        if srvId == self._service_instance.service_id:
            return
        else:
            self._service_instance.UsersDB.userPasswords[user] = passwordHash
            print("Usuario "+ user +" añadido.")
            self._service_instance.newBD()

    def newToken(self, user, userToken, srvId, current=None):
        #actualizamos json
        if srvId == self._service_instance.service_id:
            return

        self._service_instance.UsersDB.usersToken[user] = userToken 
        self._service_instance.usersTok.append(user)

    
class Revocations (IceFlix.Revocations):

    def __init__(self, service_instance, service_proxy, current=None):
        """Initialize the Discover object with empty services."""
        self._service_instance = service_instance
        self._service_proxy = service_proxy

    def revokeToken(self, userToken, srvId, current=None):

        if srvId == self._service_instance.service_id or self._service_proxy.ice_isA("::IceFlix::MediaCatalog"):
            return
        
        token_encontrado = False
        user = ""
        for key, value in self._service_instance.UsersDB.usersToken.items():
            if value == userToken:
                token_encontrado = True
                user = key
                
        if token_encontrado:
            self._service_instance.usersTok.pop(0)
            self._service_instance.UsersDB.usersToken.pop(user)
            print("Token "+str(userToken)+" de "+str(user)+" ha expirado")
    
    def revokeUser(self, user, srvId, current=None):
        
        #actualizamos json
        if srvId == self._service_instance.service_id:
            return

        if self._service_proxy.ice_isA("::IceFlix::MediaCatalog"):
            continuar = False 
            for pelicula in self._service_instance.MediaDBList:
                if pelicula.tagsPerUser is not None and user in pelicula.tagsPerUser.keys():
                    continuar = True
                    pelicula.tagsPerUser.pop(user)
            if continuar:
                print("Tags del usuario "+ user +" eliminado.")
                self._service_instance.generateJson2DB(self._service_instance.ruta)
                             
        else: 
            user_encontrado = False
        
            for key, value in self._service_instance.UsersDB.userPasswords.items():
                if key == user:
                    user_encontrado = True
                    
            if user_encontrado:
                self._service_instance.UsersDB.userPasswords.pop(user)
                #se pone aqui actualizar el json propio de cada service --> lo hacen todos los service menos el emisor del evento
                self._service_instance.newBD()
            print("Usuario "+ user +" eliminado.")
        
    
