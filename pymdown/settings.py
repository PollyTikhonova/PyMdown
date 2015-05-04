#!/usr/bin/env python
"""
PyMdown Settings

Manage Settings

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import absolute_import
import json
import codecs
import traceback
from copy import deepcopy
import os.path as path
from . import resources as res
from . import logger
from . import util
from . import file_strip as fstrip
from collections import OrderedDict
from .compat import unicode_string, string_type
try:
    from pygments.styles import get_style_by_name
    PYGMENTS_AVAILABLE = True
except:
    PYGMENTS_AVAILABLE = False

CRITIC_IGNORE = 0
CRITIC_ACCEPT = 1
CRITIC_REJECT = 2
CRITIC_VIEW = 4
CRITIC_DUMP = 8


class Settings(object):
    def __init__(
        self, settings_path=None, stream=False,
        batch=False, critic=CRITIC_IGNORE,
        plain=False, preview=False, encoding='utf-8', output_encoding='utf-8',
        force_stdout=False, force_no_template=False,
        clean=False
    ):
        """ Initialize """
        self.critic = critic
        self.plain = plain
        self.batch = batch
        self.encoding = encoding
        self.output_encoding = output_encoding
        self.preview = preview
        self.is_stream = stream
        self.pygments_noclasses = False
        self.force_stdout = force_stdout
        self.clean = clean
        self.force_no_template = force_no_template
        self.settings = {
            "page": {
                "destination": None,
                "basepath": None,
                "relpath": None,
                "references": [],
                "include": [],
                "meta": {}
            },
            "settings": {}
        }

        # Use default file if one was not provided
        self.settings_path = settings_path if settings_path is not None else 'pymdown.cfg'

    def read_settings(self):
        """
        Get the settings and add absolutepath
        extention if a preview is planned.
        Unpack the settings file if needed.
        """

        # Unpack user files if needed
        res.unpack_user_files()

        settings = None

        # Unpack default settings file if needed
        if not path.exists(self.settings_path):
            text = res.load_text_resource(res.DEFAULT_SETTINGS, internal=True)
            try:
                with codecs.open(self.settings_path, "w", encoding="utf-8") as f:
                    f.write(text)
            except:
                logger.Log.error(traceback.format_exc())

        # Try and read settings file
        try:
            with codecs.open(self.settings_path, "r", encoding='utf-8') as f:
                contents = f.read()
                try:
                    settings = json.loads(fstrip.json.sanitize_json(contents))
                except:
                    settings = util.yaml_load(contents)
        except:
            logger.Log.error(traceback.format_exc())

        if settings is None:
            settings = {}

        self.settings["settings"] = settings

    def get(self, file_name, output=None, basepath=None, relpath=None, frontmatter=None):
        """ Get the complete settings object for the given file """
        self.file_name = file_name
        settings = deepcopy(self.settings)
        settings["page"]["destination"] = self.resolve_output(output)
        settings["page"]["basepath"] = self.resolve_base_path(basepath)
        settings["page"]["relpath"] = self.resolve_rel_path(relpath)
        if frontmatter is not None:
            self.apply_frontmatter(frontmatter, settings)
        # Store destination as our output reference directory.
        # This is used for things like converting relative paths.
        # If there is no output location, try to come up with a rational
        # output reference directory by falling back to the source file.
        if settings['page']['destination'] is not None:
            self.out = path.dirname(path.abspath(settings['page']['destination']))
        elif file_name:
            self.out = path.dirname(path.abspath(self.file_name))
        # elif settings["page"]["basepath"] is not None:
        #     self.out = settings["page"]["basepath"]
        else:
            self.out = None
        # Try to come up with a sane relative path since one was not provided
        if settings['page']['relpath'] is None:
            if settings['page']['destination'] is not None:
                settings['page']['relpath'] = path.dirname(path.abspath(settings['page']['destination']))
            elif file_name:
                settings['page']['relpath'] = path.dirname(path.abspath(self.file_name))
        if self.force_stdout:
            settings["page"]["destination"] = None
        if self.force_no_template:
            settings['settings']['template'] = None
        self.post_process_settings(settings)
        return settings

    def resolve_output(self, out_name):
        """ Get the path to output the file. """

        critic_enabled = self.critic & (CRITIC_ACCEPT | CRITIC_REJECT | CRITIC_VIEW)
        output = None
        if out_name is not None:
            out_name = path.expanduser(out_name)
        if not self.batch:
            if out_name is not None:
                name = path.abspath(out_name)
                if path.isdir(out_name):
                    logger.Log.error("'%s' is a directory!" % name)
                elif path.exists(path.dirname(name)):
                    output = name
                else:
                    logger.Log.error("'%s' directory does not exist!" % name)
        else:
            name = path.abspath(self.file_name)
            if self.critic & CRITIC_DUMP and critic_enabled:
                if self.critic & CRITIC_REJECT:
                    label = ".rejected"
                elif self.critic & CRITIC_ACCEPT:
                    label = ".accepted"
                else:
                    label = '.view'
                base, ext = path.splitext(path.abspath(self.file_name))
                output = path.join(name, "%s%s%s" % (base, label, ext))
            else:
                output = path.join(name, "%s.html" % path.splitext(path.abspath(self.file_name))[0])

        return output

    def resolve_rel_path(self, relpath):
        """ Get the base path to use when resolving basepath paths if possible """
        if relpath is not None:
            relpath = path.expanduser(relpath)
        if relpath is not None and path.exists(relpath):
            # A valid path was fed in
            pth = relpath
            relpath = path.dirname(path.abspath(pth)) if path.isfile(pth) else path.abspath(pth)
        else:
            # Okay, there is no way to tell the orign.
            # We are probably a stream that has no specified
            # physical location.
            relpath = None

        return relpath

    def resolve_base_path(self, basepath):
        """ Get the relative path to use when resolving relative paths if possible """
        if basepath is not None:
            basepath = path.expanduser(basepath)
        if basepath is not None and path.exists(basepath):
            # A valid path was fed in
            pth = basepath
            basepath = path.dirname(path.abspath(pth)) if path.isfile(pth) else path.abspath(pth)
        elif not self.is_stream:
            # Use the current file path
            basepath = path.dirname(path.abspath(self.file_name))
        else:
            # Okay, there is no way to tell the orign.
            # We are probably a stream that has no specified
            # physical location.
            basepath = None

        return basepath

    def resolve_meta_path(self, target, basepath):
        """
        Resolve the path returned in the meta data.
        1. See if path is defined as absolute and if so see
           if it exists
        2. If relative, use the file's basepath (default its physical directory
           if available) if the file
           can be found
        """
        if target is not None:
            target = path.expanduser(target)
            if not res.is_absolute(target):
                new_target = None
                if basepath is not None:
                    temp = path.join(basepath, target)
                    if path.exists(temp):
                        new_target = temp
                target = new_target
            elif not path.exists(target):
                target = None
        return target

    def process_settings_path(self, pth, base):
        """ General method to process paths in settings file """
        target, encoding = res.splitenc(pth)

        file_path = self.resolve_meta_path(
            pth,
            base
        )
        if file_path is None or not path.isfile(file_path):
            file_path = None
        else:
            file_path = path.normpath(file_path)
        return file_path + ';' + encoding if file_path is not None else None

    def apply_frontmatter(self, frontmatter, settings):
        """
        Apply front matter to settings object etc.
        PAGE_KEYS: destination, basepath, references,
                   include.js', include.css', include
        SETTIGS_KEY: settings
        META_KEYS: all other keys that aren't handled above
        """
        css = []
        js = []

        # Handle basepath first
        if "basepath" in frontmatter:
            value = frontmatter["basepath"]
            settings["page"]["basepath"] = self.resolve_base_path(value)
            del frontmatter["basepath"]
        base = settings["page"]["basepath"]

        # Handle relative path
        if "relpath" in frontmatter:
            value = frontmatter["relpath"]
            settings["page"]["relpath"] = self.resolve_rel_path(value)
            del frontmatter["relpath"]

        # The destination/output location and name
        if "destination" in frontmatter:
            value = frontmatter['destination']
            file_name = self.resolve_meta_path(path.dirname(unicode_string(value)), base)
            if file_name is not None and path.isdir(file_name):
                value = path.normpath(path.join(file_name, path.basename(value)))
                if path.exists(value) and path.isdir(value):
                    value = None
            else:
                value = None
            if value is not None:
                settings["page"]["destination"] = value
            del frontmatter['destination']

        # Javascript and CSS includes quick load aliases
        if "include" in frontmatter:
            value = frontmatter['include']
            if not isinstance(value, list):
                value = []
            settings["page"]['include'] = [unicode_string(v) for v in value if isinstance(v, string_type)]
            del frontmatter['include']

        # Javascript and CSS include
        for i in ("css", "js"):
            key = 'include.%s' % i
            if key in frontmatter:
                value = frontmatter[key]
                items = []
                for j in value:
                    pth = unicode_string(j)
                    items.append(pth)
                if i == 'css':
                    css += items
                else:
                    js += items
                del frontmatter[key]

        if 'references' in frontmatter:
            value = frontmatter['references']
            if not isinstance(value, list):
                value = [value]
            refs = []
            for v in value:
                pth = unicode_string(v)
                refs.append(pth)
            settings["page"]['references'] = refs
            del frontmatter['references']

        # Handle PyMdown settings
        if 'settings' in frontmatter and isinstance(frontmatter['settings'], dict):
            value = frontmatter['settings']
            for subkey, subvalue in value.items():
                # Html template
                if subkey == "template":
                    org_pth = unicode_string(subvalue)
                    new_pth = self.process_settings_path(org_pth, base)
                    settings['settings'][subkey] = new_pth if new_pth is not None else org_pth

                # Handle optional extention assets
                elif subkey.startswith('@'):
                    for assetkey, assetvalue in subvalue.items():
                        if assetkey in ('cs', 'js'):
                            items = []
                            for i in assetvalue:
                                pth = unicode_string(i)
                                items.append(pth)
                            settings['settings'][subkey][assetkey] = items
                        else:
                            settings['settings'][subkey][assetkey] = assetvalue

                # Javascript and CSS files
                elif subkey in ("css", "js"):
                    items = []
                    for i in subvalue:
                        pth = unicode_string(i)
                        items.append(pth)
                    settings['settings'][subkey] = items

                # All other settings that require no other special handling
                else:
                    settings['settings'][subkey] = subvalue
            del frontmatter['settings']

        # Resolve all other frontmatter items
        for key, value in frontmatter.items():
            if isinstance(value, list):
                value = [unicode_string(v) for v in value]
            else:
                value = unicode_string(value)
            settings["page"]["meta"][unicode_string(key)] = value

        # Append CSS and JS from built-in keys if any
        if len(css):
            css = settings['settings'].get('css', []) + css
            settings['settings']['css'] = css
        if len(js):
            js = settings['settings'].get('js', []) + js
            settings['settings']['js'] = js

    def set_style(self, extensions, settings):
        """
        Search the extensions for the style to be used and return it.
        If it is not explicitly set, go ahead and insert the default
        style (github).
        """
        style = None

        if not PYGMENTS_AVAILABLE:
            settings["settings"]["use_pygments_css"] = False

        # Search for codehilite to see what style is being set.
        if "markdown.extensions.codehilite" in extensions:
            config = extensions["markdown.extensions.codehilite"]
            if config is None:
                config = {}

            if not PYGMENTS_AVAILABLE and bool(config.get('use_pygments', True)):
                config['use_pygments'] = False

            if bool(config.get('noclasses', False)) or not bool(config.get('use_pygments', True)):
                settings["settings"]["use_pygments_css"] = False

            css_class = config.get('css_class', None)
            if css_class is not None:
                settings["settings"]["pygments_class"] = css_class
            else:
                settings["settings"]["pygments_class"] = "codehilite"

            style = config.get('pygments_style', None)
            if style is None:
                # Explicitly define a pygment style and store the name
                # This is to ensure the "noclasses" option always works
                style = "default"
            else:
                try:
                    # Check if the desired style exists internally
                    get_style_by_name(style)
                except:
                    logger.Log.error("Cannot find style: %s! Falling back to 'default' style." % style)
                    style = "default"
            config['pygments_style'] = style

        settings["settings"]["style"] = style

    def post_process_settings(self, settings):
        """ Process the settings files making needed adjustements """

        extensions = settings["settings"].get("extensions", OrderedDict())

        # See if we need to handle the appropriate critic from CLI
        # Critic will be appended to end of extension list if CLI requested it.
        critic_mode = "ignore"
        if self.critic & CRITIC_ACCEPT:
            critic_mode = "accept"
        elif self.critic & CRITIC_REJECT:
            critic_mode = "reject"
        elif self.critic & CRITIC_VIEW:
            critic_mode = "view"

        # Remove critic extension if manually defined
        # and remove plainhtml if defined and --plain-html is specified on CLI
        if "pymdownx.critic" in extensions:
            del extensions["pymdownx.critic"]
        if "pymdownx.plainhtml" in extensions and self.plain:
            del extensions["pymdownx.plainhtml"]

        disable_path_conversion = settings["settings"].get("disable_path_conversion", False)
        path_conversion_absolute = settings["settings"].get("path_conversion_absolute", False)

        # Ensure previews are using absolute paths or relative paths
        if self.preview or not disable_path_conversion:
            # Add pathconverter extension if not already set.
            if "pymdownx.pathconverter" not in extensions:
                extensions["pymdownx.pathconverter"] = {
                    "base_path": "${BASE_PATH}",
                    "relative_path": "${REL_PATH}" if not self.preview else "${OUTPUT}",
                    "absolute": path_conversion_absolute
                }
            elif self.preview and "pymdownx.pathconverter" in extensions:
                if extensions["pymdownx.pathconverter"] is None:
                    extensions["pymdownx.pathconverter"] = {}
                extensions["pymdownx.pathconverter"]["relative_path"] = "${OUTPUT}"

        # Add critic to the end since it is most reliable when applied to the end.
        if critic_mode != "ignore":
            extensions["pymdownx.critic"] = {"mode": critic_mode}

        # Append plainhtml.
        # Most reliable when applied to the end. Okay to come after critic.
        if self.plain:
            extensions['pymdownx.plainhtml'] = None

        # Set extensions to its own key
        settings["settings"]["extensions"] = extensions

        # Set style
        self.set_style(extensions, settings)
