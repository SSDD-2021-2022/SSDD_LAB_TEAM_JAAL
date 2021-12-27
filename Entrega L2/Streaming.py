#!/usr/bin/env python3

import sys
import uuid
import json
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

class StreamProviderI(IceFlix.StreamProvider):
    
    def __init__(self, media_c,main_c):
        self.media_c = media_c
        self.main_c = main_c
        
    def getStream(self, mediaId, userToken, current=None):
        return
    
    def isAvailable(self, mediaId, current=None):
        return
    
    def uploadMedia(self, filename, uploader, adminToken, current=None):
        return
    
    def deleteMedia(self, mediaId, adminToken, current=None):
        return
    
        