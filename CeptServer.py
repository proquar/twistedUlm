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

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.reactor import callLater, connectTCP

from httpflavor import twistedHTTPFlavor
from basicflavor import DummyFlavor, RelayTest
from Relay import RelayFactory


class CeptServerProtocol(LineReceiver):
	"""
	A instance of this class is created for every new connection. If choosen it
	can parse a header and stores the bytes received in the first few seconds
	as userid (useful for the German Btx-system).
	It handles the communication between the specific server-flavor and the
	network. It can be ordered to relay a connection to another host or to
	close a connection, it also tells the flavor that the connection was lost
	(when the user hangs up).
	"""
	
	def __init__(self, flavor, verbosity, client, getHeader=False, getUserid=False):
		self.flavor = flavor
		self.flavor.sendCb = self.send
		self.flavor.closeCb = self.close
		self.flavor.relayCb = self.relayConnection
		
		self.version = "0"
		self.txspeed = 120.0
		self.rxspeed = 7.5
		
		self.relay=None
		self.relayConnector=None
		self.relayData=False
		self.commandAfterRelay="*0#"
		
		self.idTimeout = None
		self.verbosity=verbosity
		self.client=client
		
		self.notifyDataSent = None
		
		if getUserid:
			self.userid = None	# means we still want to parse it
		else:
			self.userid = "" # we already have an (empty) id
			
		if getHeader:
			self.headerTimeout = callLater(10, self.close)
			self.state=0
		else:
			self.headerTimeout = None
			self.state=1
			self.headerDone() # just switch to raw-mode (and get user id)
	
	
	def relayConnection(self, host, port, commandAfter, sendHeader=False):
		"""
		Should be called by the server-flavor to request a relay of the connection.
		While the relay is active no data will be passed to the server-flavor and
		vice versa.
		"""
		header  = "Version: %s\r\n" % self.version
		header += "TXspeed: %.1f\r\n" % self.txspeed
		header += "RXspeed: %.1f\r\n" % self.rxspeed
		header += "UserID: %s\r\n" % self.userid
		
		self.commandAfterRelay=commandAfter
		self.relay=RelayFactory( self.relayClosed, self.send, sendHeader, header )
		self.relayData=True		# relay data instead of passing it to the flavor
		self.relayConnector=connectTCP(host, int(port), self.relay)
	
	
	def relayClosed(self):
		"""
		This is called by the Relay handler when it's connection was closed. All
		data is again passed to the flavor, beginning with the command passed to
		relayConnection() before.
		"""
		if self.relayConnector!=None:
			self.relayConnector.disconnect()
		self.relayData=False
		self.relay=None
		self.flavor.write(self.commandAfterRelay)
	
	
	def connectionLost(self, reason):
		"""
		Connection with the user was lost, either by choice or by accident.
		If we are relaying data, we close this connection, then we give the
		flavor the opportunity to clean some stuff up before it is destroyed.
		"""
		if self.verbosity>=2: print "Lost connection. ", self.client
		if self.relay!=None:
			self.relay=None
		if self.relayConnector!=None:
			self.relayConnector.disconnect()
			self.relayConnector=None
		self.flavor.connectionLost( reason )
	
	
	def lineReceived(self,line):
		"""
		This exclusively handles the header that may be received in the
		beginning. It parses known header-values and then switches to raw-mode.
		"""
		if self.verbosity>=100: print "->", line
		
		if line == "":
			self.headerDone()
			
		else:
			self.headerTimeout.reset(10)
			
			line = line.split(":")
			
			if line[0] == "Version":
				self.version = line[1].strip()
			
			elif line[0] == "TXspeed":
				try:
					self.txspeed = float(line[1].strip())
				except(ValueError):
					pass
			
			elif line[0] == "RXspeed":
				try:
					self.rxspeed = float(line[1].strip())
				except(ValueError):
					pass
			
			elif line[0] == "UserID":
				self.userid = line[1].strip()
	
	
	def rawDataReceived(self, data):
		"""
		Here we handle data coming from the user. In the first few seconds this
		may be the user id sent by the terminal, after that it's user-input.
		This is either passed to the flavor or relayed to a remote host.
		"""
		if self.verbosity>=100:
			print "->",
			for c in data:
				print "0x%x (%s)"%(ord(c),c),
			print
		
		if self.state == 1:
			# we only wait for 1 second between characters of the user id
			self.idTimeout.reset(1)
			self.userid += data
		else:
			if self.relayData:
				self.relay.send(data)
			else:
				self.flavor.write(data)
	
	
	def headerDone(self):
		"""
		Called by lineReceived() when a double newline was received. Switch to
		raw mode (from line mode) and (maybe) try to receive the user-id.
		"""
		if self.verbosity>=3: print "\tHeader done. ", self.client
		if self.verbosity>=4:
			print "\t\tVersion:",self.version
			print "\t\tTX speed:",self.txspeed
			print "\t\tRX speed:",self.rxspeed
		
		# header complete, so we don't need the timeout anymore
		if self.headerTimeout != None:
			self.headerTimeout.cancel()
			del(self.headerTimeout)
		
		self.setRawMode()
		
		if self.userid == None:
			# we still need to get the user id, so we wait 3 seconds for data
			# from the terminal
			self.state = 1	# header done, check for userid next
			self.userid=""
			if self.verbosity>=5: print "\t\tWaiting for User ID..."
			self.idTimeout = callLater(3, self.useridDone)
		else:
			# either we already received the user id through the header or we
			# don't want/need to parse it
			self.useridDone()
	
	def useridDone(self):
		"""
		Called after a timeout either from headerDone() or rawDataReceived().
		We store the userid as a nice hexadecimal string and pass it to the
		flavor.
		"""
		newid=""
		for c in self.userid:
			newid+="%x"%ord(c)	# make a string from those raw bytes
		self.userid=newid
		if self.verbosity>=4: print "\t\tUser ID:", self.userid
		self.state = 2	# everything else is just passed to the flavor
		self.flavor.userid=self.userid
		self.flavor.hello()
	
	
	def send(self,data):
		"""
		Data passed to this function is just passed onto the socket. We know
		(or assume) the speed of the connection, so we notify the flavor when
		all data is sent (so it may choose not to send too much data at once.)
		"""
		if self.verbosity>=101: print "<-", data
		self.transport.write(data)
		
		if not self.relayData:
			if self.notifyDataSent!=None and self.notifyDataSent.active():
				self.notifyDataSent.delay( float(len(data))/self.txspeed )
			else:
				self.notifyDataSent=callLater( float(len(data))/self.txspeed, self.flavor.dataSent )
	
	
	def close(self, time=0):
		"""
		This is either called by the flavor (on user's request) or after the
		header timed out.
		"""
		if self.verbosity>=2: print "Closing connection in %i seconds. "%time, self.client
		if time>0:
			callLater(time, self.transport.loseConnection)
		else:
			self.transport.loseConnection()


class CeptServerFactory(ServerFactory):
	"""
	Creates CeptServer instances based on the choosen server-flavor.
	"""
	
	def __init__(self, serverType, verbosity, *flavorArgs):
		self.serverType = serverType
		self.flavorArgs = flavorArgs
		self.verbosity = verbosity
		
	def buildProtocol(self, addr):
		if self.verbosity>=2:
			print "New connection from", addr
		if self.serverType == "http":
			flavor=twistedHTTPFlavor( self.verbosity, *self.flavorArgs )
		else:
			flavor=DummyFlavor()
		
		p = CeptServerProtocol( flavor, self.verbosity, addr, getHeader=True, getUserid=True )
		p.factory = self
		return p