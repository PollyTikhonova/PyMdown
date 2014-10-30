"""
pymdown.math
Extension that preserves the following for MathJax use:
$$
  Display Equations
$$

and $Inline MathJax Equations$

Inline equations are converted to the following form:

\(Inline MathJax Equations\)

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import Pattern

RE_MATHJAX = r'(?<!\\)([$]{1,2})(?![$])((?:\\.|[^$])+?)(\2)'


class MathJaxPattern(Pattern):
    def __init__(self, pattern, md):
        Pattern.__init__(self, pattern)
        self.markdown = md

    def handleMatch(self, m):
        if m.group(2) == '$':
            # Use the more reliable inline pattern
            start = '\\('
            end = '\\)'
        else:
            start = m.group(2)
            end = m.group(4)

        return self.markdown.htmlStash.store(
            self.escape(start + m.group(3) + end),
            safe=True
        )

    def escape(self, txt):
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


class MathExtension(Extension):
    """Adds delete extension to Markdown class."""

    def extendMarkdown(self, md, md_globals):
        if "$" not in md.ESCAPED_CHARS:
            md.ESCAPED_CHARS.append('$')
        md.inlinePatterns.add("mathjax-dollar", MathJaxPattern(RE_MATHJAX, md), ">backtick")


def makeExtension(*args, **kwargs):
    return MathExtension(*args, **kwargs)
