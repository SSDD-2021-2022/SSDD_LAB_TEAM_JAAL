#pylint:disable=W0613
#pylint:disable=C0413
#pylint:disable=W0212
#pylint:disable=E0401
#pylint:disable=C0103

import time
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

class UserUpdates(IceFlix.UserUpdates):
    """Class UserUpdates"""

    def __init__(self, service_instance, service_proxy, current=None):
        """Initialize the Discover object with empty services."""
        self._service_instance = service_instance
        self._service_proxy = service_proxy

    def newUser(self, user, passwordHash, srvId, current=None):
        """Method"""
        #actualizamos json
        if srvId == self._service_instance.service_id:
            return
        self._service_instance.UsersDB.userPasswords[user] = passwordHash
        print("Usuario "+ user +" añadido.")
        self._service_instance.newBD()

    def newToken(self, user, userToken, srvId, current=None):
        """Method"""
        #actualizamos json
        if srvId == self._service_instance.service_id:
            return

        self._service_instance.UsersDB.usersToken[user] = userToken
        self._service_instance.usersTok.append(user)
class Revocations(IceFlix.Revocations):
    """Class Revocations"""
    def __init__(self, service_instance, service_proxy, current=None):
        """Initialize the Discover object with empty services."""
        self._service_instance = service_instance
        self._service_proxy = service_proxy
        self.userRevoked = ""
        self.password = ""
        self.newTokenUser = ""
        self.dictUsers = {}

    def revokeToken(self, userToken, srvId, current=None):
        """Method"""

        if self._service_instance == "client":

            if self.userRevoked != "":
                time.sleep(0.05)
                #password = self._service_instance.UsersDB.userPasswords.get(self.userRevoked)
                #for user, password in self.dictUsers.items():
                newToken = self._service_proxy.refreshAuthorization(self.userRevoked, self.password)
                self.newTokenUser = newToken
        else:
            isCatalog = self._service_proxy.ice_isA("::IceFlix::MediaCatalog")
            if srvId == self._service_instance.service_id or isCatalog:
                return

            if self._service_proxy.ice_isA("::IceFlix::Authenticator"):
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
                    self.userRevoked = user

    def revokeUser(self, user, srvId, current=None):
        """Method"""
        if self._service_instance == "client":
            return
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

            for key in self._service_instance.UsersDB.userPasswords.keys():
                if key == user:
                    user_encontrado = True

            if user_encontrado:
                self._service_instance.UsersDB.userPasswords.pop(user)
                #se pone aqui actualizar el json propio de cada service
                self._service_instance.newBD()
                print("Usuario "+ user +" eliminado.")
