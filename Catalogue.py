#!/usr/bin/env python3

from os import name
import sys
import uuid
import json
import Ice
Ice.LoadSlice('iceflix.ice')
import IceFlix
import metodos

EXIT_ERROR=1

class Catalogue(Ice.Aplication, IceFlix.Authenticator):

    def getTile(self, id):
        return tile

    def getTilesByName(self, name, exact ):
        return tile

    def getTilesByTags(self, tag, includeAllTags, userToken):
        return tiles

    #def addTags(self, id, tag, userToken):
        

        #preguntar lo de poner idmedia y lo de autorized
    def removeTags(self, id, nameTag, adminToken, current=None):
        try:
            proxy = self.communicator().stringToProxy(sys.argv[1])
            main_c = IceFlix.MainPrx.checkedCast(proxy)

            if(main_c.isAdmin(adminToken)==False):
                raise IceFlix.Unauthorized
            
            if(main_c.isAdmin(adminToken)):
               metodos.borrarTags(id,nameTag) 
            
                #with open('catalogueMedia.json', 'w') as data_file:
                   #data = json.dump(data, data_file)
        except IceFlix.Unathorized as error:
            print("usuario no autorizado")
            sys.exit(1)

    #def renameTile(id, name, adminToken):

    #def updateMedia(id, initialName, proveedor)

