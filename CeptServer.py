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

from httpshape import twistedHTTPShape
from basicshape import DummyShape, RelayTest
from Relay import RelayFactory


class CeptServerProtocol(LineReceiver):
	def __init__(self, shape, verbosity, client, getHeader=False, getUserid=False):
		self.shape = shape
		self.shape.sendCb = self.send
		self.shape.closeCb = self.close
		self.shape.relayCb = self.relayConnection
		
		self.version = 0
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
			self.userid = None
		else:
			self.userid = ""
			
		if getHeader:
			self.headerTimeout = callLater(10, self.close)
			self.state=0
		else:
			self.headerTimeout = None
			self.state=1
			self.headerDone()
	
	def relayConnection(self, time, host, port, commandAfter, sendHeader=False):
		if time>0:
			callLater(time, self.relayConnection, 0, host, port, commandAfter, sendHeader)
		else:
			self.commandAfterRelay=commandAfter
			self.relay=RelayFactory( self.relayClosed, self.send )
			self.relayData=True
			self.relayConnector=connectTCP(host, int(port), self.relay)
	
	def relayClosed(self):
		if self.relayConnector!=None:
			self.relayConnector.disconnect()
		self.relayData=False
		self.relay=None
		self.shape.write(self.commandAfterRelay)
	
	def connectionLost(self, reason):
		if self.verbosity>=2: print "Lost connection. ", self.client
		if self.relay!=None:
			self.relay=None
		if self.relayConnector!=None:
			self.relayConnector.disconnect()
			self.relayConnector=None
		self.shape.connectionLost( reason )
	
	def lineReceived(self,line):
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
		if self.verbosity>=100:
			print "->",
			for c in data:
				print "0x%x (%s)"%(ord(c),c),
			print
		
		if self.state == 1:
			self.idTimeout.reset(1)
			self.userid += data
		else:
			if self.relayData:
				self.relay.send(data)
			else:
				self.shape.write(data)
	
	def headerDone(self):
		if self.verbosity>=3: print "\tHeader done. ", self.client
		if self.verbosity>=4:
			print "\t\tVersion:",self.version
			print "\t\tTX speed:",self.txspeed
			print "\t\tRX speed:",self.rxspeed
		
		if self.headerTimeout != None:
			self.headerTimeout.cancel()
			del(self.headerTimeout)
		
		self.setRawMode()
		
		if self.userid == None:
			self.state = 1	# header done, check for userid next
			self.userid=""
			if self.verbosity>=5: print "\t\tWaiting for User ID..."
			self.idTimeout = callLater(3, self.useridDone)
		else:
			self.useridDone()
	
	def useridDone(self):
		newid=""
		for c in self.userid:
			newid+="%x"%ord(c)
		self.userid=newid
		if self.verbosity>=4: print "\t\tUser ID:", self.userid
		self.state = 2
		self.shape.userid=self.userid
		self.shape.hello()
	
	def send(self,data):
		if self.verbosity>=101: print "<-", data
		self.transport.write(data)
		
		if not self.relayData:
			if self.notifyDataSent!=None and self.notifyDataSent.active():
				self.notifyDataSent.delay( float(len(data))/self.txspeed )
			else:
				self.notifyDataSent=callLater( float(len(data))/self.txspeed, self.shape.dataSent )
		
	
	def close(self, time=0):
		if self.verbosity>=2: print "Closing connection in %i seconds. "%time, self.client
		if time>0:
			callLater(time, self.transport.loseConnection)
		else:
			self.transport.loseConnection()
			
class CeptServerFactory(ServerFactory):
	def __init__(self, serverType, verbosity, *shapeArgs):
		self.serverType = serverType
		self.shapeArgs = shapeArgs
		self.verbosity = verbosity
		
	def buildProtocol(self, addr):
		if self.verbosity>=2:
			print "New connection from", addr
		if self.serverType == "http":
			shape=twistedHTTPShape( self.verbosity, *self.shapeArgs )
		else:
			shape=DummyShape()
		
		p = CeptServerProtocol( shape, self.verbosity, addr, getHeader=True, getUserid=True )
		p.factory = self
		return p