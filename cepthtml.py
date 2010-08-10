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


import cept
import re, string

class webPage():
	def __init__(self,name=''):
		self.name=name
		self.requestedName=''
		
		self.links={}
		
		self.loadpage=''
		self.loadpageTimeout=-1
		
		self.relayHost=''
		self.relayPort=-1
		self.relayTimeout=-1
		
		self.inputSize=-1
		self.inputTarget=''
		self.inputMethod='GET'
		
		self.nextPage=''
		
		self.disconnect=-1
		
		self.body=''
	
	def addLink(self,name,link):
		self.links[name]=link
	
	def getLink(self,name):
		try:
			return self.links[name]
		except:
			return None

def translateTag(tag):
	tag=tag.group(1)
	try:
		if tag[0:2]=='0x' or tag[0:2]=='0X':
			#print "tag %s interpreted as %i" %(tag, int(tag[2:], 16))
			return chr(int(tag[2:], 16))
	except:
		pass
	
	try:
		return chr(cept.CHARS[tag])
	except:
		print "unknown tag: "+tag
		return "<"+tag+">"
		
def interpretSitename(name):
		try:
			name=string.strip(str(name),string.whitespace+"\"'")
		except:
			name=''
		name=string.lstrip(name,'*')
		name=string.rstrip(name,'#')
		return name

parseerror="<cept><body>Seite<sp>fehlerhaft.</body></cept>"

def parse(content,pagename=''):
	page=webPage(pagename)
	
	#naive and extremely expensive parsing using regular expressions for now ;)
	pagecontent=re.search('<cept>(.*)</cept>',content,re.I|re.S)
	if pagecontent == None:
		print("ParseError: missing <cept>-tags")
		
		return parse(parseerror)
	
	print("<cept>-tags found")
	
	head=re.search('<head>(.*)</head>',pagecontent.group(1),re.I|re.S)
	if head is not None:
		print("<head>-tags found")
			
		metatags=re.findall('<meta\s+?(.*?)>',head.group(1),re.I|re.S)
		
		if metatags is not None:
			for tag in metatags:
				metaname=re.search('name\s*?=\s*?[\'\"]?(\S*?)[\'\"\s]',tag,re.I|re.S)
				metacontent=re.search('content=\s*?[\'\"]?(\S*?)[\'\"\s]',tag,re.I|re.S)
				
				if metaname != None and metacontent != None:
					if metaname.group(1)=="load_page":
						page.loadpage=interpretSitename(metacontent.group(1))
						print("setting loadpage to "+page.loadpage)
						
					elif metaname.group(1)=="load_timeout":
						try:
							page.loadpageTimeout=int(metacontent.group(1))
							print("setting loadpage timeout to %i" %page.loadpageTimeout)
						except:
							pass
						
					elif metaname.group(1)=="next_page":
						page.nextPage=interpretSitename(metacontent.group(1))
						print("setting next page to "+page.nextPage)
						
					elif metaname.group(1)=="disconnect":
						try:
							page.disconnect=int(metacontent.group(1))
							print("will disconnect in %i seconds" %page.disconnect)
						except:
							pass
						
					elif metaname.group(1)=="relay":
						try:
							(host,port)=metacontent.group(1).split(":")
							print("setting relay to %s:%i"%(host,int(port)))
							page.relayHost=host
							page.relayPort=int(port)
						except:
							pass
					
					elif metaname.group(1)=="relay_timeout":
						try:
							page.relayTimeout=int(metacontent.group(1))
							print("setting relay timeout to %i seconds" %page.relayTimeout)
						except:
							pass
					
					elif metaname.group(1)=="input_size":
						try:
							page.inputSize=int(metacontent.group(1))
							print("page wants input with up to %i chars" %page.inputSize)
						except:
							pass
					elif metaname.group(1)=="input_target":
						try:
							page.inputTarget=interpretSitename(metacontent.group(1))
							print("input should be send to %s" %page.inputTarget)
						except:
							pass
					elif metaname.group(1)=="input_method":
						try:
							if metacontent.group(1)=="POST":
								page.inputMethod="POST"
							else:
								page.inputMethod="GET"
							print("input is send using %s" %page.inputMethod)
						except:
							pass
							
					elif metaname.group(1)=="hyperlinks":
						for link in metacontent.group(1).split(","):
							parsedLink=re.search("^(\d+)(\*[a-zA-Z0-9]+#)$",link)
							if parsedLink is not None:
								linkfrom=parsedLink.group(1)
								linkto=interpretSitename(parsedLink.group(2))
								print("adding link from %s to %s" %(linkfrom,linkto))
								page.addLink(linkfrom,linkto)
	
	body=re.search('<body>(.*)</body>',pagecontent.group(1),re.I|re.S)
	if body is not None:
		print("<body>-tags found")
		
		body=re.sub(re.compile("(<!--.*?-->)|\s",re.I|re.S), "", body.group(1))
		body=re.sub(re.compile("<([a-zA-Z0-9]+?)>",re.I|re.S), translateTag, body)
		#print body
		page.body=body
	
	return page