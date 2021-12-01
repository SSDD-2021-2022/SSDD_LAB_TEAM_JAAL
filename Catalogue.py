#!/usr/bin/env python3

import sys
import uuid
import json
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
#import metodos

EXIT_ERROR=1



MediaInfo = IceFlix.MediaInfo
Media = IceFlix.Media


class MediaCatalogI(IceFlix.MediaCatalog):

    def getTile(self, id):
        data = json.loads(open('infoPeliculas.json').read())
        for ids in data:
            if(ids == id):
                tile = data[ids]
        Media.id = tile
        return Media
        

    def getTilesByName(self, name, exact):
        id = []
        data = json.loads(open('infoPeliculas.json').read())

        if(exact == True):
            for ids, pelis in data.items():
                if(pelis == name):
                    id.append(ids)
            
        else:
            for ids, pelis in data.items():
                if(name in pelis):
                    id.append(ids)
        return id

    def getTilesByTags(self, tags, allTags, userToken):
        id = []
        data = json.loads(open('usuariosPeliculas.json').read())

        user = "blas"
        for usuario in data["users"]:
            if (usuario["user"] == user):
#                print("el usuario existe ---> ", user)
                
                todosTags = usuario["tags"]
                for peliculas, tagsPelicula in todosTags.items():
                    print(peliculas)
                    for oneTag in tagsPelicula:
                        print(oneTag)
                        for meTag in tags:








                            if(meTag == oneTag):
                                id.append(peliculas)



#                if(allTags == True):
    

#                else:

                

#            else:
#                print("el usuario no existe ---> ", user)

        return id

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

class ClientAuthentication(Ice.Application):

    
    id = "id3"
    nombre = "thor"
    exact = False
    tags = ["terror", "aventura"]
    userToken = 0


    aux = MediaCatalogI()
    Media = aux.getTile(id)
    print(Media.id)
    print(aux.getTilesByTags(tags, exact, userToken))