import sys
import uuid
import json

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

