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

from basicflavor import BasicFlavor
from lookandfeel import history, btxInput
from cept import CHARS

from cepthtml import ceptHTML

class HTTPFlavor( BasicFlavor ):
	"""
	This specific server-flavor requests "BtxML"-encoded Webpages according to
	the user's input from a webserver. It does some error handling for
	connection- and HTTP-errors.
	"""
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
		
		self.currentPage=ceptHTML()		# this holds the currently parsed page
		self.ignoreInput=False			# locks the interpretation of input
		self.retryOnError=True			# retry getting error-pages only once
	
	def getHTTP(self, wait, pagename, arguments):
		"""
		This has to be implemented in a class inherited from this one. So this
		class can stay free of twisted-specific stuff.
		"""
		raise NotImplementedError
	
	def processHTTP(self, pagename, arguments, status, html):
		"""
		This is called when getHTTP was finished loading the website. Status is
		the standard HTTP response code or 0 for a connection error. This also
		is the place where the error handling happens, this is done in two
		stages: either the error-page returned by the server is a valid "BtxML"
		document, then we display it. Or it's not, then we try to get the
		error-specific page (eg. 404.btx), if this isn't successfull either we
		display a standard error-message.
		"""
		
		#print "processing",pagename,"status",status
		
		if not self.retryOnError:
			# this is a error-page, set the correct name, so it's not 404
			# so we can make sure the original pagename is inserted into the
			# history and the correct page is reloaded
			pagename=self.currentPage.name
		
		if status==0:
			# connection error
			self.currentPage.parseHTML(self.connectionError)
			self.retryOnError=True
			self.sendPage()
		elif status==200:
			self.currentPage.parseHTML(html, pagename)
			self.retryOnError=True
			self.sendPage()
		else:
			# test if webserver returned a "BtxML" document
			self.currentPage.parseHTML(html, pagename)
			if self.currentPage.parseError:
				if self.retryOnError:
					# it didn't, so we try to get the error-specific page
					self.getHTTP(0, str(status), [])
					self.retryOnError=False
				else:
					# wasn't successfull either, abort and show a simple page
					self.currentPage.parseHTML(self.otherError1+str(status)+self.otherError2)
					self.retryOnError=True
					self.sendPage()
			else:
				self.retryOnError=True
				self.sendPage()
	
	def sendPage(self):
		"""
		This is called by processHTTP. It sends the currently loaded page to
		the terminal.
		"""
		
		self.inputParser.reset()
		
		# the protocol handler calls dataSent when the data is sent, we don't want to process
		# user input while we are sending
		self.ignoreInput=True
		
		self.sendCb(chr(CHARS['cof']))	# curser off
		
		self.sendCb(self.currentPage.body)
		self.sendCb(chr(CHARS['dct']))
		
		
		if self.currentPage.loadpageTimeout>=0 and self.currentPage.loadpage!='':
			# the current page requests a page forward, we put it into the inputparser to be handled when the current page is sent
			self.inputParser.addPriorityAction( (btxInput.DELAYEDPAGE, (self.currentPage.loadpageTimeout, self.currentPage.loadpage)) )
			
		elif self.currentPage.disconnect>=0:
			# current page is a disconnect-page, disconnect in X seconds
			self.closeCb(self.currentPage.disconnect)
		
		elif self.currentPage.relayHost!='' and self.currentPage.relayPort>0:
			# relay the connection to a remote host, we just do this immediately
			self.relayCb(
				self.currentPage.relayHost,
				self.currentPage.relayPort,
				self.currentPage.relayAfter,
				self.currentPage.relayHeader)
			self.inputParser.reset()
			self.ignoreInput=False
		
		else:
			# cursor on
			self.sendCb(chr(CHARS['con']))
		
		
	
	def dataSent(self):
		# remove the lock from the inputparser, input still was passed to it, 
		# but we didn't interpret it
		self.ignoreInput=False
		
		# poke the input handler to interpret input, that was arrived while
		# we were sending
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
					# do nothing when there's no previous site
					self.inputParser.reset()
					self.getHTTP(0, previoussite, [])
				
			elif instruction == btxInput.NEXT:
				if self.currentPage.nextPage != '':
					self.inputParser.reset()
					if not self.currentPage.nohistory:
						self.history.add(self.currentPage.name)
					self.getHTTP(0, self.currentPage.nextPage, [])
				
			elif instruction == btxInput.PAGE:
				self.inputParser.reset()
				if not self.currentPage.nohistory:
					self.history.add(self.currentPage.name)
				self.getHTTP(0, content, [])
			
			elif instruction == btxInput.LINK:
				linkto=self.currentPage.getLink(content)
				if linkto is not None:
					if not self.currentPage.nohistory:
						self.history.add(self.currentPage.name)
					self.inputParser.reset()
					self.getHTTP(0, linkto, [])
			
			elif instruction == btxInput.DELAYEDPAGE:
				# this was the special instruction we added in sendPage()
				self.inputParser.reset()
				if not self.currentPage.nohistory:
					self.history.add(self.currentPage.name)
				self.getHTTP(content[0], content[1], [])



from twisted.web.client import getPage
from twisted.internet.reactor import callLater

class twistedHTTPFlavor( HTTPFlavor ):
	"""
	This just implements the getHTTP-part using twisted.
	"""
	
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
		try:
			if self.gethttpschedule.active():
				self.gethttpschedule.cancel()
		except(AttributeError):
			pass
		
		HTTPFlavor.connectionLost(self, reason)


