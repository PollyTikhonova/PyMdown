from __future__ import unicode_literals
from markdown import Extension

extensions = [
    'extra',
    'mdownx.delete',
    'mdownx.githubemoji',
    'mdownx.magiclink',
    'mdownx.tasklist',
    'mdownx.headeranchor',
    'nl2br'
]


class GithubExtension(Extension):
    """Add various extensions to Markdown class"""

    def extendMarkdown(self, md, md_globals):
        """Register extension instances"""
        md.registerExtensions(extensions, self.config)


def makeExtension(configs={}):
    return GithubExtension(configs=dict(configs))
