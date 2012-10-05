###
# Copyright (c) 2010, quantumlemur
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###


import re
import string
import urllib
import StringIO
import lxml.html
from lxml import etree
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

# plugins.wikipedia.snippetStyle in ['sentence','paragraph','none']

def filter_non_printable(str):
  return ''.join([c for c in str if ord(c) > 31 or ord(c) == 9])

class Wikipedia(callbacks.Plugin):
    """Add the help for "@plugin help Wikipedia" here
    This should describe *how* to use this plugin."""
    threaded = True


    def wiki(self, irc, msg, args, search):
        """<search term>

        Returns the first paragraph of a Wikipedia article"""
# first, we get the page
        addr = 'http://en.wikipedia.org/wiki/Special:Search?search=%s' % urllib.quote_plus(search)
        try:
            article = utils.web.getUrl(addr)
        except:
            irc.reply('Hmm, something went wrong fetching the page.  I\'m highlighting PoohBear so he can take a look.', prefixNick=True)
            return
# parse the page
        tree = lxml.html.document_fromstring(article)
# check if it gives a "Did you mean..." redirect
        didyoumean = tree.xpath('//div[@class="searchdidyoumean"]/a[@title="Special:Search"]')
        if didyoumean:
            redirect = didyoumean[0].text_content().strip()
            redirect = redirect.encode('utf-8')
            irc.reply('I didn\'t find anything for "%s". Did you mean "%s"?' % (search, redirect), prefixNick=True)
            addr = 'http://en.wikipedia.org%s' % didyoumean[0].get('href')
            article = utils.web.getUrl(addr)
            tree = lxml.html.document_fromstring(article)
            search = filter_non_printable(redirect)
# check if it's a page of search results (rather than an article), and if so, retrieve the first result
        searchresults = tree.xpath('//div[@class="mw-search-result-heading"]/a[1]')
        if searchresults:
            redirect = searchresults[0].text_content().strip()
            redirect = redirect.encode('utf-8')
            irc.reply('I didn\'t find anything for "%s", but here\'s the result for "%s":' % (search, redirect), prefixNick=False)
            addr = 'http://en.wikipedia.org%s' % searchresults[0].get('href')
            article = utils.web.getUrl(addr)
            tree = lxml.html.document_fromstring(article)
            search = redirect
# otherwise, simply return the title and whether it redirected
        else:
            redirect = re.search('\(Redirected from <a href=[^>]*>([^<]*)</a>\)', article)
            if redirect:
                redirect = tree.xpath('//div[@id="contentSub"]/a')[0].text_content().strip()
                redirect = redirect.encode('utf-8')
                title = tree.xpath('//*[@class="firstHeading"]')
                title = title[0].text_content().strip()
                title = title.encode('utf-8')
                irc.reply('"%s" (Redirect from "%s"):' % (ircutils.bold(title), ircutils.bold(redirect)))
# extract the address we got it from
        addr = re.search('Retrieved from "<a href="([^"]*)">', article)
        addr = addr.group(1)
# check if it's a disambiguation page
        disambig = tree.xpath('//table[@id="disambigbox"]')
        if disambig:
            disambig = tree.xpath('//div[@class="mw-content-ltr"]/ul/li/a')
            disambig = disambig[:5]
            disambig = [item.text_content() for item in disambig]
            r = utils.str.commaAndify(disambig)
            irc.reply('%s is a disambiguation page.  Possible results are: %s' % (addr, ircutils.bold(r)), prefixNick=False)
# or just as bad, a page listing events in that year
        elif re.search('This article is about the year [\d]*\.  For the [a-zA-Z ]* [\d]*, see', article):
            irc.reply('"%s" is a page full of events that happened in that year.  If you were looking for information about the number itself, try searching for "%s_(number)", but don\'t expect anything useful...' % (ircutils.bold(search), ircutils.bold(search)), prefixNick=False)
        else:
##### etree!
#            irc.reply(tree.xpath(".//div[@class='mw-content-ltr']/p[1]")[0].text_content())
            p = tree.xpath("//div[@class='mw-content-ltr']/p[1]")[0]
            p = p.text_content()
            p = p.strip()
            p = re.sub('\[\d+\]', '', p)
            p = p.encode('utf-8')
            title = tree.xpath('//*[@class="firstHeading"]')
            title = title[0].text_content().strip()
            title = title.encode('utf-8')
            addr = re.sub('&amp;', '&', addr)
# and finally, return what we've got
            irc.reply(addr, prefixNick=False)
            irc.reply(ircutils.bold(title) + ': ' + p)
    wiki = wrap(wiki, ['text'])


Class = Wikipedia


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
