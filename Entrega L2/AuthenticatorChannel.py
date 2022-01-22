import uuid
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import threading

class UserUpdates (IceFlix.UserUpdates):

    def __init__(self, service_instance, service_proxy, current=None):
        """Initialize the Discover object with empty services."""
        # self.volatile_services = IceFlix.VolatileServices()
        #aututhenticators = self.volatile_services.AuthenticatorList()
        # self._id_ = str(uuid.uuid4())
        # self._service_type = service_type
        self._service_instance = service_instance
        self._service_proxy = service_proxy

    def newUser(self, user, passwordHash, srvId, current=None):
        self._service_instance.UserDB.userPasswords[user] = passwordHash
        print("hola")
        
    def newToken(self, user, userToken, srvId, current=None):
        self._service_instance.UserDB.usersToken[user] = userToken 
        print("blas")
    
class Revocations (IceFlix.Revocations):

    def __init__(self, service_instance, service_proxy, current=None):
        """Initialize the Discover object with empty services."""
        self._service_instance = service_instance
        self._service_proxy = service_proxy

    def revokeToken(self, userToken, srvId, current=None):
        print("Token "+str(userToken)+" de "+str(srvId)+"ha expirado")
        for userToken in self.UsersDB.usersToken.values():
            self.UsersDB.usersToken.pop(self.UsersDB.usersToken.pop())
        return
    
    def revokeUser(self, user, srvId, current=None):
        print("HOLA")
    
