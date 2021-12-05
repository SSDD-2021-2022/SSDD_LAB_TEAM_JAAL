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

    def getTile(self, mediaId):
        data = json.loads(open('infoPeliculas.json').read())
        for ids in data:
            if(ids == mediaId):
                tile = data[ids]
        Media.mediaId = tile
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
        idAT = []
        id = []
        todasTags = 0
        data = json.loads(open('usuariosPeliculas.json').read())

        user = "blas"
        #comprobacion de que el usuario esta en el json
        for usuario in data["users"]:
            if (usuario["user"] == user):
#                print("el usuario existe ---> ", user)
                
                #sacamos las tags del usuario
                tagsUsuario = usuario["tags"]
                #se itera el json, peliculas --> id, tagsPelicula--> los tags de ese id de pelicula
                for peliculas, tagsPelicula in tagsUsuario.items():
                    print(peliculas)
                    print(tagsPelicula)
                    
                    for meTag in tags: #meTag--> cada una de las tag que se meten al metodo
                        if(meTag in tagsPelicula):
                            todasTags = todasTags+1
                            if(allTags == False):
                                idAT.append(peliculas)
                    print("variable todasTags "+str(todasTags))
                    if(todasTags == len(tags) and allTags):
                        id.append(peliculas)
                        print("El id "+peliculas+" coincide con los 3 tags")
                    todasTags = 0

        if(allTags == False):
            for i in idAT:
                if i not in id:
                    id.append(i)

        return id

    def addTags(self, mediaId, tag, userToken):
        user="blas"
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
    def removeTags(self, mediaId, tags, adminToken, current=None):
        try:
            user = "antonio"
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

        user = "blas"
        data = json.loads(open('infoPeliculas.json').read())

        for ids in data:
            if ids == mediaId:
                data[ids] = name
    
        with open('infoPeliculas.json', 'w') as data_file:
            data = json.dump(data, data_file)

    #def updateMedia(id, initialName, proveedor)

class ClientAuthentication(Ice.Application):

    
    id = "id3"
    nombre = "thor"

    exact = False
    tags = ["tag1"]

    exact = True
    tags = ["terror", "aventuta"]

    userToken = 0


    aux = MediaCatalogI()
    Media = aux.getTile(id)
    print(Media.id)

    aux.removeTags("id3", tags, "hola")
    print()