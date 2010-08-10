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

class BasicShape():
	
	sendCb = None
	closeCb = None
	userid = None
	
	def hello(self):
		pass
	
	def write(self, data):
		pass
	
	def connectionLost(self, reason):
		pass
	
	def dataSent(self):
		pass

class DummyShape( BasicShape ):
	
	def hello(self):
		self.sendCb("Welcome to Bildschirmtext.\r\n\r\n\r\n")
		self.al=callLater(5, self.alphabet)
		self.cl=callLater(40, self.dummy_goodbye)
	
	def alphabet(self):
		self.sendCb("abcdefghijklmnopqrstuvwxyz\r\nABCDEFGHIJKLMNOPQRSTUVWXYZ\r\n\r\n")
		self.al=callLater(3, self.alphabet)
	
	def dummy_goodbye(self):
		if self.al.active(): self.al.cancel()
		self.sendCb("Goodbye Miss Erika Mustermann.\r\n")
		self.closeCb()
	
	def connectionLost(self, reason):
		if self.al.active(): self.al.cancel()
		if self.cl.active(): self.cl.cancel()
