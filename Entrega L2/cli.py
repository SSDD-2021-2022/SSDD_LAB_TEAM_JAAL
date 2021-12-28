#!/usr/bin/env python3

"""Main service."""

import sys
import random
import threading
import Ice

Ice.loadSlice('iceflix.ice')
import IceFlix

import topics


EXIT_OK = 0
EXIT_ERROR = 1



class Client(Ice.Application):
	def run(self, args):
		try:
			main_proxy = self.communicator().stringToProxy(args[1])
		except IndexError:
			print('Mandatory argument main_proxy not provided!')
			return EXIT_ERROR
		main_service = IceFlix.MainPrx.checkedCast(main_proxy)
		if not main_service:
			print('Provided main_proxy is not a ::Service::Main() instance')
			return EXIT_ERROR
		printer = main_service.prueba()
		print('Printer proxy: ' + printer)
		return EXIT_OK

if __name__ == '__main__':
	sys.exit(Client().main(sys.argv))