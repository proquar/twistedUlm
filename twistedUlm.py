#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#    This file is part of twistedUlm.
#
#    2010, Christian Groeger <code@proquari.at>
#
#    twistedUlm is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    twistedUlm is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with twistedUlm.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


import sys, getopt

from twisted.internet import reactor

from URPprotocol import URPServerFactory


def main(argv):
	
	homepage="index"
	host="localhost"
	port=8289
	verbosity=101
	httpServer="http://btx.runningserver.com/"
	httpSuffix=".btx"
	httpDelimiter="?"

	version="0.3"

	
	print "twistedUlm HTTP Server",version
	print
	
	try:
		opts, args = getopt.getopt(argv, "h:p:v:s:", ["host=", "port=", "verbose=", "server=", "help", "suffix=", "delimiter="])
	except getopt.GetoptError, err:
		print str(err)
		printhelp()
		sys.exit(1)
	
	for o,a in opts:
		if o=="--help":
			printhelp()
			sys.exit(0)
		
		if o in ("-h","--host"):
			host=a
		
		if o in ("-p","--port"):
			try:
				port=int(a)
			except:
				print "Port needs to be a number"
				printhelp()
				sys.exit(1)
				
			if port<1 or port>65535:
				print "Port must be a number between 1 and 65535"
				printhelp()
				sys.exit(1)
		
		if o in ("-v","--verbose"):
			try:
				verbosity=int(a)
			except:
				print "Verbosity needs to be a number >=0"
				printhelp()
				sys.exit(1)
				
			if verbosity<0:
				print "Verbosity needs to be a number >=0"
				printhelp()
				sys.exit(1)
		
		if o in ("-s","--server"):
			httpServer=a
		
		if o=="--delimiter":
			httpDelimiter=a
		if o=="--suffix":
			httpSuffix=a
	
	if verbosity>=1:
		print "Will bind to host: %s, port: %i."%(host,port)
		print "Will get pages in the form of %sfoo%s%sbar."\
			%(httpServer,httpSuffix,httpDelimiter)
	
	factory = URPServerFactory("http", verbosity, httpServer, httpSuffix, httpDelimiter)
	
	reactor.listenTCP(port, factory, interface=host)
	
	if verbosity>=1:
		print "Starting server..."
	
	reactor.run()

if __name__ == "__main__":
    main(sys.argv[1:])