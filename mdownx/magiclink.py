"""
mdownx.magiclink
An extension for Python Markdown.
Find http|ftp links and turn them to actual links

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import LinkPattern
from markdown import util

RE_LINK = r'''((ht|f)tp(s?)://(([a-zA-Z0-9\-._]+(\.[a-zA-Z0-9\-._]+)+)|localhost)(/?)([a-zA-Z0-9\-.?,'/+&%$#_]*)([\d\w./%+-=&?:"',|~;]*)[A-Za-z\d\-_~:/?#@!$*+=])'''


class MagiclinkPattern(LinkPattern):
    def handleMatch(self, m):
        el = util.etree.Element("a")
        el.text = m.group(2)
        el.set("href", self.sanitize_url(self.unescape(m.group(2).strip())))

        return el


class MagiclinkExtension(Extension):
    """Adds Easylink extension to Markdown class"""

    def extendMarkdown(self, md, md_globals):
        """Adds support for turning html links to link tags"""

        md.inlinePatterns.add("magiclink", MagiclinkPattern(RE_LINK, md), "<not_strong")


def makeExtension(configs={}):
    return MagiclinkExtension(configs=dict(configs))