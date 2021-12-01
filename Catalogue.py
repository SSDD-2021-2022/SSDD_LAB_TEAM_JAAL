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

class MediaInfo:
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags

class Media:


    def __init__(self, id, provider, MediaInfo):
        self.id = id
        self.provider = provider
        self.MediaInfo = MediaInfo

class Catalogue(Ice.Aplication, IceFlix.Authenticator):

    def getTile(self, id):
        data = json.loads(open('infoPeliculas.json').read())
        for ids in data:
            if(ids == id):
                tile = data[ids]
        print("El titulo de la pelicula es: ", tile)
        return Media(tile)
        

    def getTilesByName(self, name, exact):
        id = []
        data = json.loads(open('infoPeliculas.json').read())

        if(exact == True):
            for ids, pelis in data.items():
                if(pelis == name):
                    id.append(ids)
            print("El titulo de la pelicula es: ", id)
            return id
        else:
            for ids, pelis in data.items():
                if(name in pelis):
                    id.append(ids)
            print("El titulo de la pelicula es: ", id)
            return id

    def getTilesByTags(self, tags, allTags, userToken):
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


name = "id3"
exact = False
Catalogue.getTile(name)