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

from cept import CHARS

import string

class history():
	def __init__(self,size=50):
		self.size=50
		self.history=[]
		
	def add(self,entry):
		if string.strip(str(entry)) != '':
			self.history.append(string.strip(str(entry)))
			return True
		return False
	
	def get(self):
		try:
			return self.history.pop()
		except:
			return None

class btxInput():
	
	PAGE=0
	LINK=1
	DELAYEDPAGE=2
	
	BACKSPACE=chr(CHARS['apb'])+chr(CHARS['sp'])+chr(CHARS['apb']) # back-space-back
	RELOAD='*09#'
	NEXT='#'
	PREVIOUS='*#'
	
	def __init__(self, maxSize=23, verbose=False):
		self.currentInstruction=""
		self.terminated=False
		self.startsWithAsterisk=False
		
		self.maxSize=maxSize
		self.verbose=verbose
		self.priorityAction=None
	
	def putChars(self,chars):
		ret=""
		for c in chars:
			ret+=self.putChar(ord(c))
		return ret
	
	def putChar(self,char):
		"""
		This functions inserts user input into the input buffer. Since we need to echo user-input
		we do some simple checks here and return one or more characters to be send to the user as
		soon as possible.
		"""
		
		if char == ord('*'):			#interpret normal asterisk and hash-sign as 
			char = CHARS['ini']	#init/term-sign for convenience-reasons
		elif char == ord('#'):
			char = CHARS['ter']
		
		# normal printable characters are simply added to the buffer
		# except that the input was already terminated or the buffer is full
		if char >= 0x20 and char <= 0x7e:
			if not self.terminated:
				if len(self.currentInstruction) < self.maxSize:
					self.currentInstruction += chr(char)
					if self.verbose: print "printable character added to buffer: "+chr(char)
					return chr(char)
				else:
					if self.verbose: print "cannot allow any more characters"
					return ''
			else:
				return ''
		
		# the opening asterisk is added to the input buffer
		# except when the user entered 2 asterisks, then he wants to clear the whole input
		elif char == CHARS['ini']:	#asterisk
			if not self.terminated:		#ignore input, once terminator was entered
				if len(self.currentInstruction) < self.maxSize:
					
					if len(self.currentInstruction)>0 and self.currentInstruction[-1] == '*':
						#cancel entry with double asterisk
						if self.verbose: print "double asterisk, cancel input and clear buffer"
						self.startsWithAsterisk=False
						self.terminated=False
						
						length=len(self.currentInstruction)
						self.currentInstruction=""
						return length * self.BACKSPACE
					
					else:
						if self.verbose: print "asterisk added to buffer"
						if len(self.currentInstruction) == 0:
							self.startsWithAsterisk = True
						self.currentInstruction += '*'
						return '*'
				else:
					if self.verbose: print "cannot allow any more characters"
					return ''
			else:
				return ''
		
		# the hash-sign is the closing character of an input
		# except when the user didn't enter an asterisk at the beginning, then it's
		# treated as a standard character probably belonging to the link
		elif char == CHARS['ter']:
			if not self.terminated:		#ignore input, once terminator was entered
				if len(self.currentInstruction) < self.maxSize:
					if self.startsWithAsterisk or len(self.currentInstruction) == 0:
						self.terminated=True
						if self.verbose: print "input terminated, no more characters allowed"
					self.currentInstruction += '#'
					return '#'
				else:
					return ''
			else:
				return ''
			
		# backspace or back-key
		elif char == CHARS['apb']:
			if len(self.currentInstruction)>0:
				if self.verbose: print "delete last character"
				
				if self.currentInstruction[-1] == '#':
					self.terminated = False
				
				self.currentInstruction = self.currentInstruction[:-1]
				
				if len(self.currentInstruction) == 0:
					self.startsWithAsterisk = False
				return self.BACKSPACE
			else:
				if self.verbose: print "cannot delete any more characters"
				return ''
			
		else:
			return ''
	
	def addPriorityAction(self,action):
		self.priorityAction=action
	
	def getInstruction(self):
		if self.priorityAction!=None:
			action=self.priorityAction
			self.priorityAction=None
			return action
		
		if self.currentInstruction==self.RELOAD:
			return (self.RELOAD, None)
		elif self.currentInstruction==self.PREVIOUS:
			return (self.PREVIOUS, None)
		elif self.currentInstruction==self.NEXT:
			return (self.NEXT, None)
		elif self.startsWithAsterisk and self.terminated:
			return (self.PAGE, self.currentInstruction[1:-1])
		else:
			return (self.LINK, self.currentInstruction)
	
	#def checkLink(self, links):
		#if self.startsWithAsterisk:
			#return None
		
		#if isinstance(links,list):
			#for link in links:
				#if link==self.currentInstruction[:len(link)]:
					#return link
		#elif isinstance(links,str) or isinstance(links,int):
			#links=str(links)
			#if links==self.currentInstruction[:len(links)]:
				#return links
		
		#return None
	
	def reset(self):
		self.currentInstruction=""
		self.terminated=False
		self.startsWithAsterisk=False
	
