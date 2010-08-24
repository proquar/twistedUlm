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

from twisted.internet.reactor import callLater
from cept import CHARS

class BasicFlavor():
	"""
	Inherit from this class to create new server flavors. You have several
	callback methods to the CeptServer:
	sendCb(str): used to send data to the user
	closeCb(): close the connection
	relayCb(host, port, commandAfter, sendHeader): relay a connection
	"""
	
	sendCb = None
	closeCb = None
	relayCb =None
	userid = None
	
	def hello(self):
		"""
		Called when the connection is established and header and user id is
		parsed. May be used to send a welcome message.
		"""
		pass
	
	def write(self, data):
		"""
		Data received from the user is passed to this function.
		"""
		pass
	
	def dataSent(self):
		"""
		Called when all data passed to self.sendCb() has been sent. (According
		the estimated speed of the user's connection)
		"""
		pass
	
	def connectionLost(self, reason):
		"""
		Connection was lost, either because self.closeCb() was called or the
		user hang up.
		"""
		pass

class RelayTest ( BasicFlavor ):
	"""
	Simple server-flavor to try to relay a connection.
	"""
	def hello(self):
		self.sendCb("Trying to connect you to Ringworld...")
		self.relayCb("rw1.m63.co.uk", 23, "*done#")
		
	def write(self, data):
		if data=="*done#":
			self.sendCb("Goodbye.")
			self.closeCb()

class DummyFlavor( BasicFlavor ):
	"""
	I used this to see what kind of user id I could expect. It sends a
	greeting to the user, several alphabets and then closes the connection.
	"""
	def __init__(self):
		self.elist=[]
		self.olist=[]
		self.nlist=[]
		self.flist=[]
	
	def hello(self):
		self.sendCb(chr(CHARS['dct']))
		print "start: no dct"
		self.wc=callLater(10, self.welcome)
		self.al=callLater(15, self.alphabet)
		self.cl=callLater(40, self.dummy_goodbye)
	
	def welcome(self):
		e=""
		o=""
		n=""
		f=""
		
		for c in self.elist:
			if c==0xff: e+="  "
			else: e+="%x"%c
		for c in self.olist:
			if c==0xff: o+="  "
			else: o+="%x"%c
		for c in self.nlist: n+="%x"%c
		for c in self.flist: f+="%x"%c
		print "even",e
		print "odd ",o
		print "7bit",n
		print "8bit",f
		self.sendCb("Welcome to Bildschirmtext.\r\n\r\n\r\n")
	
	def alphabet(self):
		#self.sendCb(chr(CHARS['dct']))
		self.sendCb("abcdefghijklmnopqrstuvwxyz\r\nABCDEFGHIJKLMNOPQRSTUVWXYZ\r\n\r\n")
		self.al=callLater(3, self.alphabet)
	
	def dummy_goodbye(self):
		if self.al.active(): self.al.cancel()
		self.sendCb("Goodbye Miss Erika Mustermann.\r\n")
		self.closeCb()
	
	def connectionLost(self, reason):
		if self.wc.active(): self.wc.cancel()
		if self.al.active(): self.al.cancel()
		if self.cl.active(): self.cl.cancel()
	
	def write(self,data):
		for c in data:
			original=ord(c)
			shorter=original>>1
			
			o_str="..."
			s_str="..."
			
			for (k,v) in CHARS.iteritems():
				if v==original:
					o_str=k
				if v==shorter:
					s_str=k
			
			pr=""
			if shorter>=32 and shorter<=126:
				pr=chr(shorter)
			
			par=0
			for i in range(8):
				if (original&(1<<i))>0:
					par+=1
			
			if par%2==0: 
				self.elist.append(shorter)
				self.olist.append(0xff)
			else:
				self.olist.append(shorter)
				self.elist.append(0xff)
			self.nlist.append(shorter)
			self.flist.append(original)
			
			print "0x%x %s\t0x%x %s <%s>\t%i"%(original,o_str,shorter,s_str,pr,par)
			
