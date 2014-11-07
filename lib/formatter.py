#!/usr/bin/env python
"""
Formatter

Places markdown in HTML with the specified CSS and JS etc.

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
import cgi
import sys
import codecs
import traceback
import re
import tempfile
from os.path import exists, isfile, join, abspath, relpath, dirname, normpath
from .resources import load_text_resource, splitenc, get_user_path, is_absolute
from .logger import Logger
try:
    from pygments.formatters import get_formatter_by_name
    pygments = True
except:
    pygments = False
    pass


PY3 = sys.version_info >= (3, 0)

if PY3:
    unicode_string = str
else:
    unicode_string = unicode  # flake8: noqa

RE_URL_START = re.compile(r"https?://")
RE_TEMPLATE_FILE = re.compile(r"\{%\s*filepath\s*\((.*?)\)\s*%\}")
RE_TEMPLATE_VARS = re.compile(r"\{\{\s*(title|css|js|meta)\s*\}\}")


class PyMdownFormatterException(Exception):
    pass


def get_js(js, link=False, encoding='utf-8'):
    """ Get the specified JS code """
    if link:
        return '<script type="text/javascript" charset="%s" src="%s"></script>\n' % (encoding, js)
    else:
        return '<script type="text/javascript">\n%s\n</script>\n' % js if js is not None else ""


def get_style(style, link=False, encoding=None):
    """ Get the specified CSS code """
    if link:
        return '<link href="%s" rel="stylesheet" type="text/css">\n' % style
    else:
        return '<style>\n%s\n</style>\n' % style if style is not None else ""


def get_pygment_style(style, css_class='codehilite'):
    """ Get the specified pygments sytle CSS """
    try:
        # Try and request pygments to generate it
        text = get_formatter_by_name('html', style=style).get_style_defs('.' + css_class)
    except:
        # Try and request pygments to generate default
        text = get_formatter_by_name('html', style="default").get_style_defs('.' + css_class)
    return '<style>\n%s\n</style>\n' % text if text is not None else ""


class Terminal(object):
    """ Have console output mimic the file output calls """
    name = None

    def write(self, text):
        """ Dump texst to screen """
        if PY3:
            sys.stdout.buffer.write(text)
        else:
            sys.stdout.write(text)

    def close(self):
        """ There is nothing to close """
        pass


class Html(object):
    def __init__(
        self, output, preview=False, title=None, encoding='utf-8',
        basepath=None, plain=False, aliases=[], settings={}
    ):
        self.settings = settings
        self.encode_file = True
        self.body_end = None
        self.no_body = False
        self.plain = plain
        self.template = None
        self.encoding = encoding
        self.basepath = basepath
        self.preview = preview
        self.aliases = aliases
        self.template_file = self.settings.get("template", None)
        self.title = "Untitled"
        self.user_path = get_user_path()
        self.set_output(output, preview)
        self.added_res = set()
        self.load_header(
            self.settings.get("style", None)
        )
        self.started = False

    def set_meta(self, meta):
        """ Create meta data tags """
        if "title" in meta:
            value = meta["title"]
            if isinstance(value, list):
                if len(value) == 0:
                    value = ""
                else:
                    value = value[0]
            self.title = unicode_string(value)
            del meta["title"]

        for k, v in meta.items():
            if isinstance(v, list):
                v = ','.join(v)
            if v is not None:
                self.meta.append(
                    '<meta name="%s" content="%s">' % (
                        cgi.escape(unicode_string(k), True),
                        cgi.escape(unicode_string(v), True)
                    )
                )

    def repl_vars(self, m):
        meta = '\n'.join(self.meta) + '\n'
        var = m.group(1)
        if var == "meta":
            var = '\n'.join(self.meta) + '\n'
        elif var == "css":
            var = ''.join(self.css)
        elif var == "js":
            var = ''.join(self.scripts)
        elif var == "title":
            var = cgi.escape(self.title)
        return var

    def repl_file(self, m):
        file_name = m.group(1).strip()
        relative_path = file_name.startswith('&')
        absolute_path = file_name.startswith('*')

        # Remove relative path marker
        if relative_path:
            file_name = file_name.replace('&', '', 1)

        # Remove absolute path markder
        elif absolute_path:
            file_name = file_name.replace('*', '', 1)

        user_path = join(get_user_path(), file_name)

        is_abs = is_absolute(file_name)

        # Find path relative to basepath or global user path
        # If basepath is defined set paths relative to the basepath if possible
        # or just keep the absolute
        if not is_abs:
            # Is relative path
            base_temp = normpath(join(self.basepath, file_name)) if self.basepath is not None else None
            user_temp = normpath(join(user_path, file_name)) if user_path is not None else None
            if exists(base_temp) and isfile(base_temp):
                file_path = base_temp
            elif exists(user_temp) and isfile(user_temp):
                file_path = user_temp
        elif is_abs and exists(file_name) and isfile(file_name):
            # Is absolute path
            file_path = file_name
        else:
            # Is an unknown path
            file_path = None

        # If using preview mode, adjust paths to be relative or absolute if not including content
        if self.preview and not relative_path and not absolute_path:
            mode = self.settings.get('preview_path_conversion', 'absolute')
            if mode == 'relative':
                relative_path = True
            else:
                absolute_path = True

        # Determine the output directory if possible
        output = dirname(abspath(self.file.name)) if self.file.name else None


        if file_path is not None:
            # Calculate the absolute path
            if is_abs or not self.basepath:
                abs_path = file_path
            else:
                abs_path = abspath(join(self.basepath, file_path))

            # Adjust path depending on whehter we are desiring
            # absolute output or relative output
            if relative_path and output:
                file_path = relpath(file_path, output)
            elif absolute_path:
                file_path = abs_path

            file_name = file_path.replace('\\', '/')

        return file_name

    def write_html_start(self):
        """ Output the HTML head and body up to the {{ content }} specifier """
        if (self.template_file is not None):
            template_path, encoding = splitenc(self.template_file)
            if (
                self.user_path is not None and
                (not exists(template_path) or not isfile(template_path))
            ):
                template_path = join(self.user_path, template_path)

            try:
                with codecs.open(template_path, "r", encoding=encoding) as f:
                    self.template = f.read()
            except:
                Logger.error(str(traceback.format_exc()))

        # If template isn't found, we will still output markdown html
        if self.template is not None:
            self.no_body = True

            # We have a template.  Look for {{ content }}
            # so we know where to insert the markdown.
            # If we can't find an insertion point, the html
            # will have no markdown content.
            self.template = RE_TEMPLATE_FILE.sub(self.repl_file, self.template)
            self.template = RE_TEMPLATE_VARS.sub(self.repl_vars, self.template)
            m = re.search(r"\{\{\s*content\s*\}\}", self.template)
            if m:
                self.no_body = False
                self.write(self.template[0:m.start(0)])
                self.body_end = m.end(0)

    def set_output(self, output, preview):
        """ Set and create the output target and target related flags """
        if output is None:
            self.file = Terminal()
        try:
            if not preview and output is not None:
                self.file = codecs.open(output, "w", encoding=self.encoding, errors="xmlcharrefreplace")
                self.encode_file = False
            elif preview:
                self.file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        except:
            Logger.error(str(traceback.format_exc()))
            raise PyMdownFormatterException("Could not open output file!")

    def close(self):
        """ Close the output file """
        if self.body_end is not None:
            self.write(self.template[self.body_end:])
        self.file.close()

    def write(self, text):
        """ Write the given text to the output file """
        if not self.plain and not self.started:
            # If we haven't already, print the file head
            self.started = True
            self.write_html_start()
        if not self.no_body:
            self.file.write(
                text.encode(self.encoding, errors="xmlcharrefreplace") if self.encode_file else text
            )

    def load_highlight(self, highlight_style):
        """ Load Syntax highlighter CSS """
        style = None
        if pygments and highlight_style is not None and bool(self.settings.get("use_pygments_css", True)):
            # Ensure pygments is enabled in the highlighter
            style = get_pygment_style(highlight_style, self.settings.get("pygments_class", "codehilite"))

        css = []
        if style is not None:
            css.append(style)

        return css

    def load_resources(self, template_resources, res_get, resources):
        if isinstance(template_resources, list) and len(template_resources):
            for pth in template_resources:
                resource = unicode_string(pth)
                is_url = RE_URL_START.match(resource)

                # Check for markers
                direct_include = True
                relative_path = resource.startswith('&')
                direct_include = not resource.startswith('!')
                absolute_path = resource.startswith('*')

                # Remove relative path marker
                if relative_path:
                    resource = resource.replace('&', '', 1)
                    direct_include = False

                # Remove absolute path markder
                elif absolute_path:
                    resource = resource.replace('*', '', 1)
                    direct_include = False

                # Remove inclusion reject marker
                elif not direct_include:
                    resource = resource.replace('!', '', 1)


                # Find path relative to basepath or global user path
                # If basepath is defined set paths relative to the basepath if possible
                # or just keep the absolute
                resource, encoding = splitenc(resource)
                is_abs = is_absolute(resource)
                if not is_abs and not is_url:
                    # Is relative path
                    base_temp = normpath(join(self.basepath, resource)) if self.basepath is not None else None
                    user_temp = normpath(join(self.user_path, resource)) if self.user_path is not None else None
                    if exists(base_temp) and isfile(base_temp):
                        res_path = resource
                    elif exists(user_temp) and isfile(user_temp):
                        res_path = relpath(user_temp, self.basepath) if self.basepath else user_temp
                elif is_abs and exists(resource) and isfile(resource):
                    # Is absolute path
                    res_path = relpath(resource, self.basepath) if self.basepath else resource
                else:
                    # Is a url or an unknown path
                    res_path = None

                # If using preview mode, adjust paths to be relative or absolute if not including content
                if not direct_include and self.preview and not relative_path and not absolute_path:
                    mode = self.settings.get('preview_path_conversion', 'absolute')
                    if mode == 'relative':
                        relative_path = True
                    else:
                        absolute_path = True

                # Determine the output directory if possible
                output = dirname(abspath(self.file.name)) if self.file.name else None

                # This is a URL, don't include content
                if is_url:
                    if resource not in self.added_res:
                        resources.append(res_get(resource, link=True, encoding=encoding))
                        self.added_res.add(resource)

                # Is an existing path.  Make path absolute, relative to output, or leave as is
                # If direct include is not desired, add resource as link.
                elif res_path is not None:
                    # Calculate the absolute path
                    if is_abs or not self.basepath:
                        abs_path = res_path
                    else:
                        abs_path = abspath(join(self.basepath, res_path))

                    # Adjust path depending on whehter we are desiring
                    # absolute output or relative output
                    if relative_path and output:
                        res_path = relpath(res_path, output)
                    elif absolute_path:
                        res_path = abs_path

                    # We check the absolute path against the current list and add the respath if not present
                    if abs_path not in self.added_res:
                        if not direct_include:
                            res_path = res_path.replace('\\', '/')
                            link = True
                        else:
                            res_path = load_text_resource(abs_path, encoding=encoding)
                            link = False
                        resources.append(res_get(res_path, link=link, encoding=encoding))
                        self.added_res.add(abs_path)

                # Not a known path and not a url, just add as is
                elif resource not in self.added_res:
                    resources.append(res_get(resource.replace('\\', '/'), link=True, encoding=encoding))
                    self.added_res.add(resource)

    def load_css(self, style):
        """ Load specified CSS sources """
        self.load_resources(self.settings.get("css", []), get_style, self.css)
        for alias in self.aliases:
            key = '@' + alias
            if key in self.settings:
                self.load_resources(self.settings.get(key).get("css"), get_style, self.css)
        self.css += self.load_highlight(style)

    def load_js(self):
        """ Load specified JS sources """
        self.load_resources(self.settings.get("js", []), get_js, self.scripts)
        for alias in self.aliases:
            key = '@' + alias
            if key in self.settings:
                self.load_resources(self.settings.get(key).get("js"), get_js, self.scripts)

    def load_header(self, style):
        """ Load up header related info """
        self.css = []
        self.scripts = []
        self.meta = ['<meta charset="%s">' % self.encoding]
        self.load_css(style)
        self.load_js()


class Text(object):
    def __init__(self, output, encoding):
        """ Initialize Text object """
        self.encode_file = True
        self.encoding = encoding

        # Set the correct output target and create the file if necessary
        if output is None:
            self.file = Terminal()
        else:
            try:
                self.file = codecs.open(output, "w", encoding=self.encoding)
                self.encode_file = False
            except:
                Logger.error(str(traceback.format_exc()))
                raise PyMdownFormatterException("Could not open output file!")

    def write(self, text):
        """ Write the content """
        self.file.write(
            text.encode(self.encoding, errors="xmlcharrefreplace") if self.encode_file else text
        )

    def close(self):
        """ Close the file """
        self.file.close()
