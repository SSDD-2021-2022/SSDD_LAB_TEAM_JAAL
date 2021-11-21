#!/usr/bin/env python3

import sys
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

class MainI(IceFlix.Main):
    def isAdmin(self, adminToken, current = None):
        admin = False

        if adminToken == sys.argv[1]:
            admin = True
        
        return admin

class ServerMain(Ice.Application):
    def run(self, args):
        broker = self.communicator()
        servant = MainI()
        #print(aux.isAdmin("blasss"))
        adapter = broker.createObjectAdapter("MainAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("main1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

if __name__ == '__main__':
    app=ServerMain()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)

#sys.exit(ServerMain().main(sys.argv))
