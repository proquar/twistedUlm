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

from basicshape import BasicShape
from lookandfeel import history, btxInput
from cept import CHARS

from cepthtml import ceptHTML

class HTTPShape( BasicShape ):
	sendCb = None
	closeCb = None
	userid = None
	
	connectionError="<cept><body><cs><aph><apr><apr>Ulm<sp>ist<sp>nicht<sp>erreichbar.</body></cept>"
	otherError1="<cept><body><cs><aph><apr><apr>Fehler<sp>"
	otherError2="<sp>ist<sp>aufgetreten.</body></cept>"
	
	def __init__(self, verbosity, httpServer, httpSuffix, httpDelimiter):
		self.verbosity=verbosity
		
		self.httpServer=httpServer
		self.httpSuffix=httpSuffix
		self.httpDelimiter=httpDelimiter
		
		self.history=history(size=100)
		self.inputParser=btxInput(maxSize=23)
		
		self.currentPage=ceptHTML()
		self.ignoreInput=False
		self.retryHTTP=True
	
	def getHTTP(self, wait, pagename, arguments):
		raise NotImplementedError
	
	def processHTTP(self, pagename, arguments, status, html):
		#print "processing",pagename,"status",status
		if status==0:
			# connection error
			self.currentPage.parseHTML(self.connectionError)
			self.sendPage()
		elif status==200:
			self.currentPage.parseHTML(html, pagename)
			self.sendPage()
		else:
			#print "error",status
			self.currentPage.parseHTML(html, pagename)
			if self.currentPage.parseError:
				#print "error page doesn't look like cept"
				if self.retryHTTP:
					#print "will try to get error-specific page"
					self.getHTTP(0, str(status), [])
					self.retryHTTP=False
				else:
					#print "last try. sending standard page."
					self.currentPage.parseHTML(self.otherError1+str(status)+self.otherError2)
					self.retryHTTP=True
					self.sendPage()
			else:
				self.sendPage()
	
	def sendPage(self):
		self.inputParser.reset()
		
		self.sendCb(chr(CHARS['cof']))
		
		self.sendCb(self.currentPage.body)
		self.sendCb(chr(CHARS['dct']))
		
		if self.currentPage.loadpageTimeout>=0 and self.currentPage.loadpage!='':
			self.inputParser.addPriorityAction( (btxInput.DELAYEDPAGE, (self.currentPage.loadpageTimeout, self.currentPage.loadpage)) )
			
		elif self.currentPage.disconnect>=0:
			self.closeCb(self.currentPage.disconnect)
		
		elif self.currentPage.relayTimeout>=0 and self.currentPage.relayHost!='' \
			and self.currentPage.relayPort>0:
			print "Relaying request. Not implemented yet" # TODO
		
		else:
			# cursor on
			self.sendCb(chr(CHARS['con']))
		
		# the protocol handler calls dataSent when the data is sent, we don't want to process
		# user input while we are sending
		self.ignoreInput=True
	
	def dataSent(self):
		self.ignoreInput=False
		self.write('')
	
	def hello(self):
		self.getHTTP(0, "index", [])
	
	def write(self, data):
		answer=self.inputParser.putChars(data)
		
		if not self.ignoreInput:
			if len(answer)>0:
				self.sendCb(answer)
			
			(instruction, content) = self.inputParser.getInstruction()
			
			if instruction == btxInput.RELOAD:
				self.inputParser.reset()
				self.getHTTP(0, self.currentPage.name, [])
				
			elif instruction == btxInput.PREVIOUS:
				previoussite=self.history.get()
				if previoussite is not None:
					self.inputParser.reset()
					self.getHTTP(0, previoussite, [])
				
			elif instruction == btxInput.NEXT:
				self.inputParser.reset()
				self.history.add(self.currentPage.name)
				self.getHTTP(0, self.currentPage.nextPage, [])
				
			elif instruction == btxInput.PAGE:
				self.inputParser.reset()
				self.history.add(self.currentPage.name)
				self.getHTTP(0, content, [])
			
			elif instruction == btxInput.LINK:
				linkto=self.currentPage.getLink(content)
				if linkto is not None:
					self.history.add(self.currentPage.name)
					self.inputParser.reset()
					self.getHTTP(0, linkto, [])
			
			elif instruction == btxInput.DELAYEDPAGE:
				self.inputParser.reset()
				self.history.add(self.currentPage.name)
				self.getHTTP(content[0], content[1], [])



from twisted.web.client import getPage
from twisted.internet.reactor import callLater

class twistedHTTPShape( HTTPShape ):
	def getHTTP(self, wait, pagename, arguments):
		if wait>0:
			self.gethttpschedule = callLater(wait, self.getHTTP, 0, pagename, arguments)
		else:
			url=self.httpServer+pagename+self.httpSuffix
			
			def succes(value):
				self.processHTTP( pagename, arguments, 200, value)
			
			def error(error):
				self.processHTTP( pagename, arguments, int(error.value.status), error.value.response)
				#print error.value.__dict__
			
			getPage(url).addCallbacks(callback=succes, errback=error )
	
	def connectionLost(self, reason):
		if self.gethttpschedule.active():
			self.gethttpschedule.cancel()
		
		HTTPShape.connectionLost(self, reason)


