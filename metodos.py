#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import uuid
import json


def getTile(id):
    data = json.loads(open('infoPeliculas.json').read())
    for ids in data:
        if(ids == id):
            tile = data[ids]
    print("El titulo de la pelicula es: ", tile)
    return tile


def getTilesByName(name, exact):
    id = []
    data = json.loads(open('infoPeliculas.json').read())

    if(exact == True):
        for ids, pelis in data.items():
            #print(ids, "---", pelis)
            if(pelis == name):
                id.append(ids)

        print("El titulo de la pelicula es: ", id)
        return id
    else:
        for ids, pelis in data.items():
            #print(ids, "---", pelis)
            if(name in pelis):
                id.append(ids)

        print("El titulo de la pelicula es: ", id)
        return id

def getTilesByTag(tags, allTtags)


# def añadirTags(self, id, tag):
    # data = json.loads(open('catalogueMedia.json').read())
    # for ids in data["idP"]:

def borrarTags(id, nameTag):
    data = json.loads(open('catalogueMedia.json').read())
    for ids in data["idP"]:
        if(ids["idP"] == id):
            for tag in data["tags"]:
                if(tag["tags"] == nameTag):
                    data["tags"].remove(tag)
                    print("Tag eliminado correctamente")

    with open('catalogueMedia.json', 'w') as data_file:
        data = json.dump(data, data_file)


name = "thor"
exact = False
getTilesByName(name, exact)
