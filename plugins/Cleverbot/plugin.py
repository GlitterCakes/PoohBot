#!/usr/bin/env python
# CleverBot Supybot Plugin v1.0
# (C) Copyright 2012 Albert H. (alberthrocks)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import cleverbot
import re, random, time
from htmlentitydefs import name2codepoint

class Cleverbot(callbacks.Plugin):
	"""This plugin replies using the Cleverbot API upon intercepting an invalid command."""
	threaded = True
	callAfter = ['MoobotFactoids','Factoids','Infobot']
	def __init__(self,irc):
		self.__parent = super(Cleverbot,self)
		self.__parent.__init__(irc)
		self.nicks = {}
		self.hashes = {}
		self.sessions = {}
	@staticmethod
	def decode_htmlentities(s):
		def substitute_entity(match):
			ent = match.group(3)
			if match.group(1) == "#":	# number, decimal or hexadecimal
				return unichr(int(ent)) if match.group(2) == '' else unichr(int('0x'+ent,16))
			else:	# name
				cp = name2codepoint.get(ent)
				return unichr(cp) if cp else match.group()
		return re.compile(r'&(#?)(x?)(\w+);').subn(substitute_entity,s)[0]
	@staticmethod
	def _randHash():
		return '%016x'%random.getrandbits(64)
	@classmethod
	def _post(cls,bot,hash,line,sess):
		try:
			m = sess.Ask(line)
		except:
			return None
		if m:
			return m
		return None
	@classmethod
	def _identify(cls,bot,hash,name):
		return cleverbot.Session()
	def getHash(self,nick):
		nick = nick.lower()
		if nick not in self.nicks:
			self.nicks[nick] = self._randHash()
		return self.nicks[nick]
	def getResponse(self,irc,msg,line):
		hash = self.getHash(msg.nick)
		args = (self.registryValue('bot'),hash)
		if hash not in self.hashes or time.time()-self.hashes[hash] > 300:
			sess = self._identify(*(args+(msg.nick,)))
			self.sessions[hash] = sess
		else:
			sess = self.sessions[hash]
		self.hashes[hash] = time.time()
		line = re.compile(r'\b'+re.escape(irc.nick)+r'\b',re.I).sub('you',re.compile(r'^'+re.escape(irc.nick)+r'\S',re.I).sub('',line))
		reply = self._post(*(args+(line,sess,)))
		if reply is None:
			return """Let's talk about something else."""
		name = self.registryValue('name')
		return reply
	def invalidCommand(self,irc,msg,tokens):
		try:
			print "[Cleverbot] DEBUG: Channel is: "+str(irc.isChannel(msg.args[0]))
			print "[Cleverbot] DEBUG: Message is: "+str(msg.args)
		except:
			print "[Cleverbot] ERROR... message not retrievable."
		
		if irc.isChannel(msg.args[0]) and self.registryValue('react',msg.args[0]):
			channel = msg.args[0]
			print "[Cleverbot] Fetching response..."
			reply = self.getResponse(irc,msg,ircutils.stripFormatting(msg.args[1]).strip())
			print "[Cleverbot] Got response!"
			if reply is not None:
				print "[Cleverbot] DEBUG: Reply is: "+str(reply)
				irc.reply(reply, prefixNick=True)
			else:
				irc.reply("My AI is down, sorry! :( I couldn't process what you said... blame it on a brain fart. :P", prefixNick=True)
		elif (msg.args[0] == irc.nick) and self.registryValue('reactprivate',msg.args[0]):
			err = ""
			print "[Cleverbot] Fetching response..."
			reply = self.getResponse(irc,msg,ircutils.stripFormatting(msg.args[1]).strip())
			print "[Cleverbot] Got response!"
			if reply is not None:
				print "[Cleverbot] DEBUG: Reply is: "+str(reply)
				irc.reply(reply)
			else:
				irc.reply("My AI is down, sorry! :( I couldn't process what you said... blame it on a brain fart. :P", err, None, True, None, None)
			
	def cleverbot(self,irc,msg,args,line):
		"""<line>
		Fetches response from Cleverbot
		"""
		reply = self.getResponse(irc,msg,line)
		if reply is not None:
			irc.reply(reply, prefixNick=True)
		else:
			irc.reply('There was no response.', prefixNick=True)
	cleverbot = wrap(cleverbot,['text'])
	def doNick(self,irc,msg):
		try:
			del self.nicks[msg.nick.lower()]
		except KeyError:
			pass
		self.nicks[msg.args[0].lower()] = self._randHash()
		self._identify(self.registryValue('bot'),self.getHash(msg.args[0].lower()),msg.args[0])
#	def doKick(self,irc,msg):
#		del self.nicks[msg.args[1]]
#	def doPart(self,irc,msg):
#		del self.nicks[msg.nick.lower()]
	def doQuit(self,irc,msg):
		try:
			del self.nicks[msg.nick.lower()]
		except KeyError:
			pass
			
	def doPrivmsg(self, irc, msg):
#		if callbacks.addressed(irc.nick, msg):
#			return
#		if not irc.isChannel(msg.args[0]):
#			if callbacks.addressed(irc.nick, msg):
#				return
#			if re.search(r'ACTION(.+)?', msg.args[1], re.I):
#				return
#			reply = self.getResponse(irc,msg,ircutils.stripFormatting(msg.args[1]).strip())
#			if reply is not None:
#				irc.reply(reply)
		line = msg.args[1]
		if re.search(r'ACTION(.+)?', line, re.I):
			return
		if re.search(r'(.+)?%s(.+)?' % irc.nick, line, re.I):
			channel = msg.args[0]
			if callbacks.addressed(irc.nick, msg):
				return
			response = self.getResponse(irc,msg,ircutils.stripFormatting(msg.args[1]).strip())
			irc.reply(response, prefixNick=True)
		else:
			return None


Class = Cleverbot


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
