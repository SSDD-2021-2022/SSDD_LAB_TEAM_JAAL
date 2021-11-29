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
def getTilesByName(self, name, exact):
    data = json.loads(open('infoPeliculas.json').read())
    for nombres in data["nombre"]:
        if(nombres["nombre"]==name):
            exact == True
            tile = data.get("nombre")
        else:
            exact==False
    return tile



#def añadirTags(self, id, tag):
    # data = json.loads(open('catalogueMedia.json').read())
     #for ids in data["idP"]:
      
def borrarTags(id, nameTag):
    data = json.loads(open('catalogueMedia.json').read())
    for ids in data["idP"]:
        if(ids["idP"]==id):
            for tag in data["tags"]:
                if(tag["tags"]==nameTag):
                    data["tags"].remove(tag)
                    print("Tag eliminado correctamente")
            
    with open('catalogueMedia.json', 'w') as data_file:
        data = json.dump(data, data_file)

