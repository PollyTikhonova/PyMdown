#!/usr/bin/env python
"""
resources

Load resources from project normally or when it
is packaged via Pyinstaller

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import print_function
import sys
from os.path import join, exists, abspath, dirname, isfile, expanduser
from os import listdir, mkdir
from .logger import Logger
import codecs
import traceback

RESOURCE_PATH = abspath(join(dirname(__file__), ".."))
DEFAULT_CSS = "default-markdown.css"
DEFAULT_TEMPLATE = "default-template.html"
DEFAULT_SETTINGS = "pymdown.cfg"

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def get_encoding(enc):
    try:
        codecs.lookup(enc)
    except LookupError:
        enc = 'utf-8'
    return enc


def get_user_path():
    """
    Get user data path
    """

    if _PLATFORM == "windows":
        folder = expanduser("~\\.PyMdown")
    elif _PLATFORM == "osx":
        folder = expanduser("~/Library/Application Support/PyMdown")
    elif _PLATFORM == "linux":
        folder = expanduser("~/.config/PyMdown")

    if not exists(folder):
        try:
            mkdir(folder)
        except:
            pass

    return folder


def unpack_user_files():
    user_path = get_user_path()
    for resource in (DEFAULT_SETTINGS, DEFAULT_TEMPLATE, DEFAULT_CSS):
        text = load_text_resource(resource, internal=True)
        if text is not None:
            try:
                with codecs.open(join(user_path, resource), "w", encoding='utf-8') as f:
                    f.write(text)
            except:
                pass


def splitenc(entry, default='utf-8'):
    parts = entry.split(';')
    if len(parts) > 1:
        entry = ';'.join(parts[:-1])
        encoding = get_encoding(parts[-1])
    else:
        encoding = get_encoding(default)
    return entry, encoding


def load_egg_resources():
    """
    Add egg to system path if the name indicates it
    is for the current python version and for pymdown.
    This only runs if we are not in a pyinstaller environment.
    """
    if (
        not bool(getattr(sys, "frozen", 0)) and
        exists('eggs') and not isfile('eggs')
    ):
        egg_extension = "py%d.%d.egg" % (
            sys.version_info.major, sys.version_info.minor
        )
        egg_start = "pymdown"
        for f in listdir("eggs"):
            target = abspath(join('eggs', f))
            if (
                isfile(target) and f.endswith(egg_extension) and
                f.startswith(egg_start)
            ):
                sys.path.append(target)


def resource_exists(*args, **kwargs):
    """ If resource could be found return path else None """

    if kwargs.get('internal', False):
        base = None
        if getattr(sys, "frozen", 0):
            base = sys._MEIPASS
        else:
            base = RESOURCE_PATH

        path = join(base, *args)
    else:
        path = join(*args)

    if not exists(path) or not isfile(path):
        path = None

    return path


def load_text_resource(*args, **kwargs):
    """ Load text resource from either the package source location """
    path = resource_exists(*args, **kwargs)

    encoding = get_encoding(kwargs.get('encoding', 'utf-8'))

    data = None
    if path is not None:
        try:
            with codecs.open(path, "rb") as f:
                data = f.read().decode(encoding).replace('\r', '')
        except:
            Logger.debug(traceback.format_exc())
            pass
    return data
