#!/usr/bin/env python3

import sys
import uuid
import json
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
#import metodos

EXIT_ERROR=1

class MediaCatalogI(IceFlix.MediaCatalog):
    
    def __init__(self, auth_c,main_c):
        self.auth_c = auth_c
        self.main_c = main_c

    def getTile(self, mediaId, current=None):
        tile = "Ese id no corresponde a ninguna película"
        #MediaInfo = IceFlix.MediaInfo
        #Media = IceFlix.Media
        media = IceFlix.Media()
        mediaInfo = IceFlix.MediaInfo()
        data = json.loads(open('infoPeliculas.json').read())
        for ids in data:
            if(ids == mediaId):
                tile = data[ids]
        #print(tile)
        mediaInfo.name = tile
        media.mediaId = mediaId
        media.info = mediaInfo
        return media
        

    def getTilesByName(self, name, exact, current=None):
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

    def getTilesByTags(self, tags, allTags, userToken, current=None):
        user = self.auth_c.whois(userToken)
        idAT = []
        id = []
        todasTags = 0
        data = json.loads(open('usuariosPeliculas.json').read())

        print(user)
        #comprobacion de que el usuario esta en el json
        for usuario in data["users"]:
            if (usuario["user"] == user):
#                print("el usuario existe ---> ", user)
                
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

    def addTags(self, mediaId, tag, userToken, current=None):
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

    def renameTile(self, mediaId, name, adminToken, current=None):

        if self.main_c.isAdmin(adminToken):
            data = json.loads(open('infoPeliculas.json').read())

            for ids in data:
                if ids == mediaId:
                    data[ids] = name
    
            with open('infoPeliculas.json', 'w') as data_file:
                data = json.dump(data, data_file)

    

class ClientCatalog(Ice.Application):

    def run(self, argv):
        
        proxyMain = open("salida").read()
        proxy = self.communicator().stringToProxy(proxyMain)
        main_c = IceFlix.MainPrx.checkedCast(proxy)
        
        auth_c = main_c.getAuthenticator() #modificacion, se ha puesto prx

        #aux = MediaCatalogI(auth_c, main_c)
        #Crear proxy de authenticator para registrarlo llamando a register-->del main
        broker = self.communicator()
        servant = MediaCatalogI(auth_c,main_c)
        #print(servant.getTile("id1").info)
        adapter = broker.createObjectAdapter("MediaCatalogAdapter")
        #time = datetime.datetime.now()
        proxyCtg = adapter.add(servant, broker.stringToIdentity("mediacatalog1"))
        print(proxyCtg, flush=False)
        
        adapter.activate()
        self.shutdownOnInterrupt()
        pCtg= IceFlix.MediaCatalogPrx.checkedCast(proxyCtg)
        main_c.register(pCtg)
        broker.waitForShutdown()
        return 0


if __name__ == "__main__":
    ClientCatalog().main(sys.argv)