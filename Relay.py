# -*- coding: utf-8 -*-

from twisted.internet.protocol import ClientFactory, Protocol

class Relay(Protocol):
	"""
	This one just relays data to and from a remote host. If requested it can
	send the header when the connection is established. When the remote host
	closes the connection it will make a call to it's closedCb function.
	"""
	def __init__(self, closedCb, putDataCb, sendHeader=False, header=""):
		self.sendHeader=sendHeader
		self.header=header
		
		self.closedCb=closedCb
		self.putDataCb=putDataCb
		
		self.relay=None
	
	def connectionMade(self):
		if self.sendHeader:
			# check for trailing double newline and append one if necessary
			if header[-4:]=="\r\n\r\n":
				self.send(header)
			elif header[-2:]=="\r\n":
				self.send(header+"\r\n")
			else:
				self.send(header+"\r\n\r\n")
	
	def dataReceived(self, data):
		self.putDataCb(data)
	
	def connectionLost(self, reason=None):
		self.closedCb()
	
	def send(self,data):
		self.transport.write(data)
	
	

class RelayFactory(ClientFactory):
	"""
	The factory for the relay "protocol". It won't create more than one
	instance of the protocol.
	"""
	def __init__(self, closedCb, putDataCb, sendHeader=False, header=""):
		self.sendHeader=sendHeader
		self.header=header
		
		self.closedCb=closedCb
		self.putDataCb=putDataCb
		
		self.relay=None
	
	def buildProtocol(self, addr):
		if self.relay == None:
			self.relay=Relay(self.closedCb, self.putDataCb, self.sendHeader, self.header)
		return self.relay
	
	def send(self,data):
		"""
		Since we only create one instance of the protocol this function can be
		used to send data to the remote host.
		"""
		self.relay.send(data)
		