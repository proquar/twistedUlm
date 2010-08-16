# -*- coding: utf-8 -*-

from twisted.internet.protocol import ClientFactory, Protocol

class Relay(Protocol):
	def __init__(self, closedCb, putDataCb, sendHeader=False, header=""):
		self.sendHeader=sendHeader
		self.header=header
		
		self.closedCb=closedCb
		self.putDataCb=putDataCb
		
		self.relay=None
	
	def connectionMade(self):
		if self.header:
			self.send(header)
	
	def dataReceived(self, data):
		self.putDataCb(data)
	
	def connectionLost(self, reason=None):
		self.closedCb()
	
	def send(self,data):
		self.transport.write(data)
	
	

class RelayFactory(ClientFactory):
	def __init__(self, closedCb, putDataCb, sendHeader=False, header=""):
		self.sendHeader=sendHeader
		self.header=header
		
		self.closedCb=closedCb
		self.putDataCb=putDataCb
		
		self.relay=None
	
	def buildProtocol(self, addr):
		self.relay=Relay(self.closedCb, self.putDataCb, self.sendHeader, self.header)
		return self.relay
	
	def send(self,data):
		self.relay.send(data)
		