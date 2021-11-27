import sys
import uuid
import json

def getTile(self, id):
    data = json.loads(open('infoPeliculas.json').read())
    for ids in data["idP"]:
        if(ids["idP"]==id):
             tile = data.get("nombre")
    print("El titulo de la pelicula es: %s", tile)
    return tile

#no es asi jj
def getTilesByName(self, name, exact ):
    data = json.loads(open('infoPeliculas.json').read())
    for nombres in data["nombre"]:
        if(nombres["nombre"]==name):
            tile = data.get("nombre")
    return tile



def addTags(self, id, tag, userToken):
     data = json.loads(open('catalogueMedia.json').read())
     for tag in data["tags"]:
         


def removeTags(id, nameTag, adminToken, current=None):
    data = json.loads(open('catalogueMedia.json').read())
    for tag in data["tags"]:
        if(tag["tags"]==nameTag):
            data["tags"].remove(tag)
            
    with open('catalogueMedia.json', 'w') as data_file:
        data = json.dump(data, data_file)

