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
from twisted.internet.reactor import callLater

from httpshape import twistedHTTPShape
from basicshape import DummyShape


class URPServerProtocol(LineReceiver):
	def __init__(self, shape, verbosity, client):
		self.shape = shape
		self.shape.sendCb = self.send
		self.shape.closeCb = self.close
		
		self.version = None
		self.txspeed = None
		self.rxspeed = None
		self.userid = ""
		
		self.state = 0
		self.headerTimeout = callLater(10, self.close)
		self.idTimeout = None
		self.verbosity=verbosity
		self.client=client
		
		self.notifyDataSent = callLater(0, self.shape.dataSent)
	
	def connectionLost(self, reason):
		if self.verbosity>=2: print "Lost connection. ", self.client
		self.shape.connectionLost( reason )
	
	def lineReceived(self,line):
		if self.verbosity>=100: print "->", line
		
		if line == "":
			if self.verbosity>=3: print "\tHeader done. ", self.client
			if self.verbosity>=4:
				print "\t\tVersion:",self.version
				print "\t\tTX speed:",self.txspeed
				print "\t\tRX speed:",self.rxspeed
			
			self.headerTimeout.cancel()
			del(self.headerTimeout)
			
			self.setRawMode()
			
			if self.userid == "":
				self.state = 1	# header done, check for userid next
				if self.verbosity>=5: print "\t\tWaiting for User ID..."
				self.idTimeout = callLater(2, self.useridDone)
			else:
				self.useridDone()
			
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
			self.shape.write(data)
	
	def useridDone(self):
		if self.verbosity>=3: print "\t\tUser ID:", self.userid
		self.state = 2
		self.shape.hello()
	
	def send(self,data):
		if self.verbosity>=101: print "<-", data
		self.transport.write(data)
		
		
		if self.notifyDataSent.active():
			self.notifyDataSent.delay( float(len(data))/self.txspeed )
		else:
			self.notifyDataSent=callLater( float(len(data))/self.txspeed, self.shape.dataSent )
		
	
	def close(self, time=0):
		if self.verbosity>=2: print "Closing connection in %i seconds. "%time, self.client
		if time>0:
			callLater(time, self.transport.loseConnection())
		else:
			self.transport.loseConnection()
			
class URPServerFactory(ServerFactory):
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
		
		p = URPServerProtocol( shape, self.verbosity, addr )
		p.factory = self
		return p