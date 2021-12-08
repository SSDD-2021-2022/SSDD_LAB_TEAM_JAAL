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

    def _init_(self, auth_c,main_c):
        self.auth_c = auth_c
        self.main_c = main_c

    def getTile(self, mediaId):
        media = IceFlix.Media
        mediaInfo = IceFlix.MediaInfo
        data = json.loads(open('infoPeliculas.json').read())
        for ids in data:
            if(ids == mediaId):
                tile = data[ids]

        mediaInfo.name = tile
        media.mediaId = mediaId
        media.info = mediaInfo
        return media
        

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
        user = self.auth_c.whois(userToken)
        idAT = []
        id = []
        todasTags = 0
        data = json.loads(open('usuariosPeliculas.json').read())

        print(user)
        #comprobacion de que el usuario esta en el json
        for usuario in data["users"]:
            if (usuario["user"] == user):
            #print("el usuario existe ---> ", user)
                
                #sacamos las tags del usuario
                tagsUsuario = usuario["tags"]
                #se itera el json, peliculas --> id, tagsPelicula--> los tags de ese id de pelicula
                for peliculas, tagsPelicula in tagsUsuario.items():
                   
                    for meTag in tags: #meTag--> cada una de las tag que se meten al metodo
                        if(meTag in tagsPelicula):
                            todasTags = todasTags+1
                            if(allTags == False):
                                idAT.append(peliculas)

                    if(todasTags == len(tags) and allTags):
                        id.append(peliculas)

                    todasTags = 0

        if(allTags == False):
            for i in idAT:
                if i not in id:
                    id.append(i)

        return id

    def addTags(self, mediaId, tag, userToken):
        user = self.auth_c.whois(userToken)
        data=json.loads(open('usuariosPeliculas.json').read())

        for usuario in data["users"]:
            if usuario["user"] == user:
                listaTagsUsuario = usuario["tags"]
                for id_pel, tagsUser in listaTagsUsuario.items():
                    print(str(id_pel)+" "+str(tagsUser))
                    if id_pel == mediaId:  
                        for j in tag:
                            if(j in tagsUser):
                                tag.remove(j)
                            else:
                                tagsUser.append(j)
                                print(j)
                                print(tagsUser)
        
        with open('usuariosPeliculas.json', 'w') as data_file:
            data = json.dump(data, data_file)

        

        #preguntar lo de poner idmedia y lo de autorized
    def removeTags(self, mediaId, tags, userToken, current=None):
        try:
            user = self.auth_c.whois(userToken)
            data = json.loads(open('usuariosPeliculas.json').read())

            for usuario in data["users"]:
                if usuario["user"] == user:
                    listaTagsUsuario = usuario["tags"]
                    for id_pel, tagsUser in listaTagsUsuario.items():
                        print(str(id_pel)+" "+str(tagsUser))
                        if id_pel == mediaId:
                            for tagParametro in tags:
                                if tagParametro in tagsUser:
                                    tagsUser.remove(tagParametro)
                                    print(str(tagParametro)+" eliminado")
                                    print(tagsUser)
                                    
            with open('usuariosPeliculas.json', 'w') as data_file:
                data = json.dump(data, data_file)
        except IceFlix.Unauthorized as error:
            print("usuario no autorizado")
            sys.exit(1)

    def renameTile(self, mediaId, name, adminToken):

        if self.main_c.isAdmin(adminToken):
            data = json.loads(open('infoPeliculas.json').read())

            for ids in data:
                if ids == mediaId:
                    data[ids] = name
    
            with open('infoPeliculas.json', 'w') as data_file:
                data = json.dump(data, data_file)

    

class ClientCatalog(Ice.Application):

    def run(self, argv):
        print(type(argv[1]))
        proxyMain = open("salida").read()
        proxy = self.communicator().stringToProxy(proxyMain)
        main_c = IceFlix.MainPrx.checkedCast(proxy)
        print(proxy)
        #proxyAuth = self.communicator().stringToProxy(argv[2])
        print(main_c.getAuthenticator())
        auth_c = main_c.getAuthenticator()
        
        aux = MediaCatalogI(auth_c, main_c)

        
        id = "id3"
        nombre = "thor"

        exact = True

        tags = ["terror", "aventuta"]

        userToken = 0

        Media = aux.getTile(id)
        print(Media.info.name)

        #dict = aux.getTilesByTags(tags, exact, "59cdd2c9b1c04021a9e50cdefc7ab4ac")
        #aux.removeTags("id3", tags, "hola")
        #print("resultado metodo "+str(dict))

if _name_ == "_main_":
    ClientCatalog().main(sys.argv)